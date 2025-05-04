import requests
import json
import random
from django.conf import settings
from .models import Message
from django.db import models
import os

# Fallback responses when the API fails
FALLBACK_RESPONSES = [
    "Hey there! I'm not available right now, but I'll check this message later.",
    "Thanks for your message! I'll get back to you when I'm online.",
    "I'm currently away. I'll respond as soon as I can!",
    "I appreciate you reaching out. I'll reply when I'm back online.",
    "Sorry I missed your message. I'll take a look at it soon!",
    "Thanks for the message! I'll check it out later.",
    "I'm not around at the moment, but I'll read this when I get back.",
    "I'll respond to this as soon as possible.",
    "I'll check this conversation when I return. Thanks for your message!",
    "I'll get back to you on this shortly."
]

def get_ai_response(sender, receiver, message_history):
    """
    Generate AI response based on the last 10 messages using Hugging Face API
    with a fallback to simple responses if the API fails
    
    Args:
        sender: User sending the message
        receiver: User who is offline
        message_history: List of the last 10 messages between users
    
    Returns:
        str: AI generated response
    """
    # Format last 10 messages for the AI
    conversation = []
    for msg in message_history:
        if msg.sender == receiver:
            conversation.append(f"{receiver.username}: {msg.content}")
        else:
            conversation.append(f"{sender.username}: {msg.content}")
    
    # Create context for the AI
    context = f"""
This is a conversation between {sender.username} and {receiver.username}.
I am {receiver.username} and I should respond to {sender.username}'s last message.
Here's our conversation so far:

{' '.join(conversation)}

{sender.username}'s last message was: {message_history[-1].content if message_history else "Hello!"}

As {receiver.username}, my response is:
"""
    
    try:
        # Make API call to Hugging Face API with a short timeout
        API_KEY = settings.HUGGINGFACE_API_KEY
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # Use a text generation API that doesn't require message format
        payload = {
            "inputs": context,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        # Try the most lightweight model first
        model = "microsoft/phi-2"
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}", 
                headers=headers,
                json=payload,
                timeout=5  # Short timeout to avoid hanging
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # Parse the response
                    if isinstance(response_data, list) and len(response_data) > 0:
                        generated_text = response_data[0].get("generated_text", "")
                    elif isinstance(response_data, dict):
                        generated_text = response_data.get("generated_text", "")
                    else:
                        generated_text = str(response_data)
                    
                    # Clean up the response to get just the AI's part
                    if "As" in generated_text and "response is:" in generated_text:
                        # Extract only what comes after "my response is:"
                        parts = generated_text.split("response is:", 1)
                        if len(parts) > 1:
                            ai_response = parts[1].strip()
                        else:
                            ai_response = generated_text
                    else:
                        ai_response = generated_text
                    
                    # Ensure response isn't too long
                    if len(ai_response) > 150:
                        ai_response = ai_response[:150] + "..."
                    
                    return ai_response
                except Exception as e:
                    print(f"Error processing AI response: {e}")
                    # Fall through to using fallback response
            
        except Exception as e:
            print(f"Error with Hugging Face API: {e}")
            # Fall through to using fallback response
            
        # If we got here, the API failed - use fallback response
        last_msg = message_history[-1].content if message_history else ""
        
        # Select different types of fallback responses based on the message content
        if "?" in last_msg:
            return random.choice([
                "That's an interesting question. Let me think about it and get back to you.",
                "Good question! I'll have to respond when I'm back online.",
                "I'll need some time to think about that question. I'll answer when I return."
            ])
        elif any(greeting in last_msg.lower() for greeting in ["hi", "hello", "hey", "what's up", "sup"]):
            return random.choice([
                f"Hey {sender.username}! I'm not available right now, but I'll chat with you later.",
                f"Hello there {sender.username}! I'll catch up with you when I'm back online.",
                f"Hi {sender.username}! I'll be available to chat soon."
            ])
        else:
            return random.choice(FALLBACK_RESPONSES)
            
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return random.choice(FALLBACK_RESPONSES)

def create_bot_response(sender, receiver):
    """
    Create a bot response based on the last 10 messages if AI bot is enabled for receiver
    
    Args:
        sender: User sending the message
        receiver: User who is offline
    
    Returns:
        Message: New message object with AI response or None if AI bot is disabled
    """
    # Check if the receiver has AI bot enabled
    try:
        user_status = receiver.userstatus
        if not user_status.ai_bot_enabled:
            return None
    except Exception:
        return None
    
    # Get last 10 messages between these two users
    messages = Message.objects.filter(
        (
            (models.Q(sender=sender) & models.Q(receiver=receiver)) | 
            (models.Q(sender=receiver) & models.Q(receiver=sender))
        )
    ).order_by('-timestamp')[:10][::-1]  # Reverse to get chronological order
    
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