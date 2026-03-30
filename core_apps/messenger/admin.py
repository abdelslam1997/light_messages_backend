from django.contrib import admin
from .models import Message, Conversation


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp')
    list_filter = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender', 'receiver', 'message', 'timestamp')
    ordering = ('-timestamp',)


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'participant_1', 'participant_2', 'last_message_timestamp', 'unread_count_p1', 'unread_count_p2')
    list_filter = ('participant_1', 'participant_2')
    search_fields = ('conversation_id',)
    ordering = ('-last_message_timestamp',)


admin.site.register(Message, MessageAdmin)
admin.site.register(Conversation, ConversationAdmin)

