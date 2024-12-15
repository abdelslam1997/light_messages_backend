from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .utils.conversations import get_conversation_id

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="sender", 
        db_index=True
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="receiver", 
        db_index=True
    )
    message = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False)
    conversation_id = models.CharField(max_length=255, db_index=True)

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ["-timestamp"]
        
        # Database Level Validation that sender and receiver are not the same
        constraints = [
            models.CheckConstraint(
                check=~models.Q(sender=models.F("receiver")),
                name="different_sender_receiver_constraint",
                violation_error_message="Sender and receiver must be different users"
            ),
        ]

        # Database Level Indexes
        indexes = [
            models.Index(
                fields=["conversation_id", "timestamp"], 
                name="conversation_timestamp_idx"
            ),
            models.Index(
                fields=["sender", "read", "timestamp"], 
                name="sender_read_timestamp_idx"
            ),
            models.Index(
                fields=["receiver", "sender", "read"],
            )
        ]

    def save(self, *args, **kwargs):
        # Generate the conversation_id
        if self.pk is None:
            self.conversation_id = get_conversation_id(self.sender_id, self.receiver_id)
        super().save(*args, **kwargs)

    def get_other_user_id(self, user_id):
        ''' Get the other user ID '''
        if self.sender_id == user_id:
            return self.receiver_id
        return self.sender_id
    
    def get_other_user_first_name(self, user_id):
        ''' Get the other user first name '''
        if self.sender_id == user_id:
            return self.receiver.first_name
        return self.sender.first_name
    
    def get_other_user_profile_image(self, user_id):
        ''' Get the other user profile image '''
        if self.sender_id == user_id and self.receiver.profile_image:
            return self.receiver.profile_image.url
        elif self.sender.profile_image:
            return self.sender.profile_image.url

    def __str__(self):
        return self.message