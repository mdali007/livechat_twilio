from django.urls import path
from .views import send_whatsapp_message, whatsapp_webhook, chat_home

urlpatterns = [
    path("send-message/", send_whatsapp_message, name="send_whatsapp_message"),
    path("whatsapp/webhook/", whatsapp_webhook, name="whatsapp_webhook"),
 
]
