from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender", db_index=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", db_index=True)
    message = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False)

    class Meta:
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
            models.Index(fields=["sender", "receiver", "timestamp"], name="sender_receiver_timestamp_idx"),
            models.Index(fields=["receiver", "sender", "timestamp"], name="receiver_sender_timestamp_idx"),
        ]

    def __str__(self):
        return self.message