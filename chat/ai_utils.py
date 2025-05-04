import requests
import json
from django.conf import settings
from .models import Message
from django.db import models

def get_ai_response(sender, receiver, message_history):
    """
    Generate AI response based on the last 5 messages
    
    Args:
        sender: User sending the message
        receiver: User who is offline
        message_history: List of the last 5 messages between users
    
    Returns:
        str: AI generated response
    """
    # Format last 5 messages for the AI
    formatted_history = []
    for msg in message_history:
        role = "assistant" if msg.sender == receiver else "user"
        formatted_history.append({
            "role": role,
            "content": msg.content
        })
    
    # Add a system message to guide the AI
    formatted_history.insert(0, {
        "role": "system", 
        "content": f"You are {receiver.username}. Reply as if you were them, in a casual conversation style. Keep your response short and conversational."
    })
    
    try:
        # Make API call to AimlAPI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.AIML_API_KEY}"
        }
        
        data = {
            "messages": formatted_history,
            "max_tokens": 150
        }
        
        response = requests.post(
            "https://aimlapi.com/api/chat", 
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return ai_response if ai_response else "Sorry, I'm currently unavailable. I'll get back to you soon."
        else:
            return "Sorry, I'm currently unavailable. I'll get back to you soon."
            
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Sorry, I'm currently unavailable. I'll get back to you soon."

def create_bot_response(sender, receiver):
    """
    Create a bot response based on the last 5 messages
    
    Args:
        sender: User sending the message
        receiver: User who is offline
    
    Returns:
        Message: New message object with AI response
    """
    # Get last 5 messages between these two users
    messages = Message.objects.filter(
        (
            (models.Q(sender=sender) & models.Q(receiver=receiver)) | 
            (models.Q(sender=receiver) & models.Q(receiver=sender))
        )
    ).order_by('-timestamp')[:5][::-1]  # Reverse to get chronological order
    
    # Generate AI response
    ai_response = get_ai_response(sender, receiver, messages)
    
    # Create and save the bot response message
    bot_message = Message(
        sender=receiver,
        receiver=sender,
        content=ai_response,
        is_bot_response=True
    )
    bot_message.save()
    
    return bot_message 