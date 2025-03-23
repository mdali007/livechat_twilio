from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.decorators import api_view
from .models import Message
from django.shortcuts import render

# Send WhatsApp Message
@api_view(["POST"])
def send_whatsapp_message(request):
    try:
        
        client = Client("twilio sid", "twilio auth")

        sender = request.data.get("sender")
        message_content = request.data.get("message")
        recipient = request.data.get("recipient")
        

        if not (sender and message_content and recipient):
            return JsonResponse({"error": "Missing sender, message, or recipient."}, status=400)

        # Send message via Twilio
        message = client.messages.create(
            from_="whatsapp:twilio no",
            to=f"whatsapp:{recipient}",
            body=message_content,
        )

        # Save the message to the database
        Message.objects.create(sender=sender, message_content=message_content, status="sent")
        return JsonResponse({"message": "Message sent!", "sid": message.sid})

    except Exception as e:
        return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)



# Webhook for Incoming Messages
@csrf_exempt  
def whatsapp_webhook(request):
    if request.method == "POST":
        sender = request.POST.get("From")
        message_content = request.POST.get("Body")

        if sender and message_content:
            # Store incoming message in DB
            Message.objects.create(sender=sender, message_content=message_content, status="received")
            print(f"New message from {sender}: {message_content}")

            # Send the message to WebSocket clients
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "chat",  
                {
                    "type": "chat_message",
                    "sender": sender,
                    "message": message_content
                }
            )
            
            return JsonResponse({"status": "received"})
        else:
            return JsonResponse({"error": "Missing sender or message"}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

def chat_home(request):
    messages = Message.objects.all().order_by("timestamp") 
    return render(request, "chat.html", {"messages": messages})
