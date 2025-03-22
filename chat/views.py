from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Message
from django.shortcuts import render

# Send WhatsApp Message
@api_view(["POST"])
def send_whatsapp_message(request):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    sender = request.data.get("sender")
    message_content = request.data.get("message")
    recipient = request.data.get("recipient")  # Allow dynamic recipients

    if not (sender and message_content and recipient):
        return JsonResponse({"error": "Missing sender, message, or recipient."}, status=400)

    try:
        # Send message via Twilio
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{recipient}",
            body=message_content,
        )

        # Store the sent message in DB
        Message.objects.create(sender=sender, message_content=message_content, status="sent")
        return JsonResponse({"message": "Message sent!", "sid": message.sid})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Webhook for Incoming Messages
@csrf_exempt  # Skip CSRF for Twilio Webhook
def whatsapp_webhook(request):
    if request.method == "POST":
        sender = request.POST.get("From")
        message_content = request.POST.get("Body")

        if sender and message_content:
            # Store incoming message in DB
            Message.objects.create(sender=sender, message_content=message_content, status="received")
            print(f"New message from {sender}: {message_content}")
            return JsonResponse({"status": "received"})
        else:
            return JsonResponse({"error": "Missing sender or message"}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)


# Chat Home View
# def chat_home(request):
#     messages = Message.objects.all().order_by("-timestamp")  # Show latest first
#     return render(request, "chat.html", {"messages": messages})
def chat_home(request):
    messages = Message.objects.all().order_by("timestamp")  # Show oldest first
    return render(request, "chat.html", {"messages": messages})
