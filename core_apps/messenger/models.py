from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender", db_index=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", db_index=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["sender", "receiver", "timestamp"], name="sender_receiver_timestamp_idx"),
            models.Index(fields=["receiver", "sender", "timestamp"], name="receiver_sender_timestamp_idx"),
        ]

    def __str__(self):
        return self.message