import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat"  # Match the group name in the webhook
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data["sender"]
        message_content = data["message"]
        status = data.get("status", "sent")  # Default status to 'sent' if not provided

        # Save message to the database asynchronously with the correct status
        message = await self.save_message(sender, message_content, status)

        # Send message to group instantly with status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "sender": sender,
                "status": message.status  # Use status from the saved message
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket with status
        status = event.get("status", "received")
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "status": status
        }))

    @sync_to_async
    def save_message(self, sender, message_content, status):
        # Save message with the provided status
        return Message.objects.create(sender=sender, message_content=message_content, status=status)
