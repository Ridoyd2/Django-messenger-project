import os
import sys
from .models import Message
from django.db import models
from django.conf import settings

# Import transformers
try:
    from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("ERROR: Transformers library is not available")

def create_bot_response(sender, receiver):
    """
    Create a bot response using BlenderBot if AI bot is enabled
    """
    if not TRANSFORMERS_AVAILABLE:
        return None
    
    # Check if the receiver has AI bot enabled
    try:
        if not receiver.userstatus.ai_bot_enabled:
            return None
    except Exception:
        return None

        
    
    # Get the last message from sender to receiver
    last_message = Message.objects.filter(
        sender=sender,
        receiver=receiver
    ).order_by('-timestamp').first()
    
    # If no message found, don't respose

    if not last_message:
        return None
    
    try:

        # Load BlenderBot model
        model_name = "facebook/blenderbot-400M-distill"
        tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
        model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
        
        # Generate response
        inputs = tokenizer([last_message.content], return_tensors="pt")
        reply_ids = model.generate(**inputs, max_length=100)
        response = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        
        # If response is valid, create a message
        if response and len(response.strip()) > 2:
            bot_message = Message(
                sender=receiver,
                receiver=sender,
                content=response,
                is_bot_response=True
            )
            bot_message.save()
            return bot_message
    except Exception:
        pass
        
    return None 