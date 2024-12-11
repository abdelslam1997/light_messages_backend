from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Message

# Define message read signal
messages_read = Signal()

@receiver(post_save, sender=Message)
def send_websocket_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        receiver_group_name = f"user_{instance.receiver.id}"
        message_data = {
            'type': 'new_message',
            'message': {
                'id': instance.id,
                'sender': instance.sender.id,
                'message': instance.message,
                'timestamp': instance.timestamp.isoformat(),
            }
        }
        async_to_sync(channel_layer.group_send)(
            receiver_group_name,
            message_data
        )


@receiver(messages_read)
def send_read_message_notification(sender, reader_id, sender_id, last_message, **kwargs):
    print('send_read_message_notification called')
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            print('Channel layer is None')
            return
        sender_group_name = f"user_{sender_id}"
        message_data = {
            'type': 'read_message',
            'message': {
                'last_read_message_id': last_message.id,
                'reader_id': reader_id,
            }
        }
        print('Sending read message notification:', message_data)
        async_to_sync(channel_layer.group_send)(
            sender_group_name,
            message_data
        )
    except Exception as e:
        print('Exception in send_read_message_notification:', e)