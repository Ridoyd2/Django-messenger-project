from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from .models import Message, UserStatus, UserAISettings
from .forms import MessageForm, SignUpForm
from .ai_utils import create_bot_response

@login_required
def home(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/home.html', {'users': users})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'chat/signup.html', {'form': form})

@login_required
def chat_view(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    form = MessageForm()
    
    # Get messages between the two users
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) | 
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark all messages from the receiver as read
    unread_messages = messages.filter(sender=receiver, is_read=False)
    unread_messages.update(is_read=True)
    
    # Get or create AI settings for the receiver
    ai_settings, created = UserAISettings.objects.get_or_create(user=receiver)
    
    return render(request, 'chat/chat.html', {
        'receiver': receiver,
        'form': form,
        'messages': messages,
    })

@login_required
def get_messages(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    # Get messages between the two users
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) | 
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    unread_messages = messages.filter(sender=receiver, is_read=False)
    unread_messages.update(is_read=True)
    
    # Format messages for JSON response
    message_list = []
    for message in messages:
        message_list.append({
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%H:%M'),
            'is_bot_response': message.is_bot_response,
            'is_self': message.sender == request.user,
        })
    
    return JsonResponse({'messages': message_list})

@csrf_exempt
@login_required
def send_message(request, receiver_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message content is required'})
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        # Create and save the message
        message = Message(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        message.save()
        
        # Format response
        message_data = {
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%H:%M'),
            'is_self': True,
            'is_bot_response': False,
        }
        
        # Check if receiver is offline, then generate a bot response
        try:
            user_status = UserStatus.objects.get(user=receiver)
            if not user_status.is_online:
                bot_message = create_bot_response(request.user, receiver)
                if bot_message:
                    bot_message_data = {
                        'id': bot_message.id,
                        'sender': bot_message.sender.username,
                        'content': bot_message.content,
                        'timestamp': bot_message.timestamp.strftime('%H:%M'),
                        'is_self': False,
                        'is_bot_response': True,
                    }
                    return JsonResponse({
                        'status': 'success', 
                        'message': message_data,
                        'bot_response': bot_message_data
                    })
        except UserStatus.DoesNotExist:
            pass
        
        return JsonResponse({'status': 'success', 'message': message_data})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def toggle_ai_bot(request, receiver_id):
    if request.method == 'POST':
        receiver = get_object_or_404(User, id=receiver_id)
        enabled = request.POST.get('enabled') == 'true'
        
        # Get or create AI settings for the receiver
        ai_settings, created = UserAISettings.objects.get_or_create(user=receiver)
        ai_settings.ai_bot_enabled = enabled
        ai_settings.save()
        
        return JsonResponse({
            'status': 'success',
            'enabled': enabled
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def get_users(request):
    users = User.objects.exclude(id=request.user.id)
    user_list = []
    
    for user in users:
        try:
            status = UserStatus.objects.get(user=user)
            is_online = status.is_online
        except UserStatus.DoesNotExist:
            is_online = False
            
        # Count unread messages
        unread_count = Message.objects.filter(
            sender=user, 
            receiver=request.user, 
            is_read=False
        ).count()
        
        user_list.append({
            'id': user.id,
            'username': user.username,
            'is_online': is_online,
            'unread_count': unread_count
        })
    
    return JsonResponse({'users': user_list})
