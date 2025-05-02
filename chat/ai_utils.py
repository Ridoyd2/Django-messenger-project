import os
from transformers import pipeline
from django.conf import settings
from .models import Message, UserAISettings
from django.db import models

def get_ai_response(sender, receiver, message_history):
    """
    Generate AI response based on the last 10 messages using Hugging Face models
    
    Args:
        sender: User sending the message
        receiver: User who is offline
        message_history: List of the last 10 messages between users
    
    Returns:
        str: AI generated response
    """
    try:
        # Check if AI bot is enabled for the receiver
        ai_settings = UserAISettings.objects.get(user=receiver)
        if not ai_settings.ai_bot_enabled:
            return None

        # Format last 10 messages for the AI
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

        # Initialize the text generation pipeline with a smaller model
        generator = pipeline(
            "text-generation",
            model="distilgpt2",  # Using a smaller, faster model
            max_length=150,
            temperature=0.7,
            do_sample=True
        )

        # Format the conversation for the model
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in formatted_history])
        
        # Generate response
        response = generator(conversation, max_length=150, num_return_sequences=1)[0]['generated_text']
        
        # Extract only the assistant's response
        response = response.split("assistant:")[-1].strip()
        return response if response else "Sorry, I'm currently unavailable. I'll get back to you soon."
            
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Sorry, I'm currently unavailable. I'll get back to you soon."

def create_bot_response(sender, receiver):
    """
    Create a bot response based on the last 10 messages
    
    Args:
        sender: User sending the message
        receiver: User who is offline
    
    Returns:
        Message: New message object with AI response
    """
    # Get last 10 messages between these two users
    messages = Message.objects.filter(
        (
            (models.Q(sender=sender) & models.Q(receiver=receiver)) | 
            (models.Q(sender=receiver) & models.Q(receiver=sender))
        )
    ).order_by('-timestamp')[:10][::-1]  # Reverse to get chronological order
    
    # Generate AI response
    ai_response = get_ai_response(sender, receiver, messages)
    
    if not ai_response:
        return None
    
    # Create and save the bot response message
    bot_message = Message(
        sender=receiver,
        receiver=sender,
        content=ai_response,
        is_bot_response=True
    )
    bot_message.save()
    
    return bot_message 