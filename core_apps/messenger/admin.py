from django.contrib import admin
from .models import Message
# Register your models here.


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp')
    list_filter = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender', 'receiver', 'message', 'timestamp')
    ordering = ('-timestamp',)


admin.site.register(Message, MessageAdmin)

