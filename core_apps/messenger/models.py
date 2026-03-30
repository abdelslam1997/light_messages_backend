from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .utils.conversations import get_conversation_id

User = get_user_model()


class Conversation(models.Model):
    """
    Denormalized conversation model that is atomically maintained
    on every message creation and read event.  Turns the conversation
    list into a single indexed query and unread counts into column reads.
    """
    conversation_id = models.CharField(max_length=255, unique=True)
    participant_1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_as_p1",
    )
    participant_2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_as_p2",
    )
    last_message = models.ForeignKey(
        "Message", on_delete=models.SET_NULL, null=True, related_name="+",
    )
    last_message_text = models.CharField(max_length=2048, default="")
    last_message_timestamp = models.DateTimeField(null=True, db_index=True)
    # unread_count for participant_1 / participant_2 respectively
    unread_count_p1 = models.PositiveIntegerField(default=0)
    unread_count_p2 = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        indexes = [
            models.Index(
                fields=["participant_1", "-last_message_timestamp"],
                name="conv_p1_latest_idx",
            ),
            models.Index(
                fields=["participant_2", "-last_message_timestamp"],
                name="conv_p2_latest_idx",
            ),
        ]

    # ── helper methods ──────────────────────────────────────────

    def get_other_user(self, user_id):
        """Return (other_participant FK, is_p1) for the given user."""
        if self.participant_1_id == user_id:
            return self.participant_2, True
        return self.participant_1, False

    def get_other_user_id(self, user_id):
        if self.participant_1_id == user_id:
            return self.participant_2_id
        return self.participant_1_id

    def get_unread_count(self, user_id):
        if self.participant_1_id == user_id:
            return self.unread_count_p1
        return self.unread_count_p2

    def __str__(self):
        return self.conversation_id


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    message = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    conversation_id = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ["-timestamp"]

        constraints = [
            models.CheckConstraint(
                check=~models.Q(sender=models.F("receiver")),
                name="different_sender_receiver_constraint",
                violation_error_message="Sender and receiver must be different users"
            ),
        ]

        indexes = [
            # Primary index for fetching messages in a conversation
            models.Index(
                fields=["conversation_id", "-timestamp"],
                name="conversation_timestamp_idx"
            ),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.conversation_id = get_conversation_id(self.sender_id, self.receiver_id)
        super().save(*args, **kwargs)
        if is_new:
            self._update_conversation()

    def _update_conversation(self):
        """Atomically upsert the Conversation row after a new message."""
        from django.db import transaction

        p1_id = min(self.sender_id, self.receiver_id)
        p2_id = max(self.sender_id, self.receiver_id)
        receiver_is_p1 = self.receiver_id == p1_id
        unread_field = "unread_count_p1" if receiver_is_p1 else "unread_count_p2"

        with transaction.atomic():
            try:
                conv = (
                    Conversation.objects
                    .select_for_update()
                    .get(conversation_id=self.conversation_id)
                )
                conv.last_message = self
                conv.last_message_text = self.message
                conv.last_message_timestamp = self.timestamp
                setattr(conv, unread_field, getattr(conv, unread_field) + 1)
                conv.save(update_fields=[
                    "last_message", "last_message_text",
                    "last_message_timestamp", unread_field,
                ])
            except Conversation.DoesNotExist:
                Conversation.objects.create(
                    conversation_id=self.conversation_id,
                    participant_1_id=p1_id,
                    participant_2_id=p2_id,
                    last_message=self,
                    last_message_text=self.message,
                    last_message_timestamp=self.timestamp,
                    **{unread_field: 1},
                )

    def __str__(self):
        return self.message