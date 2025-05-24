from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json

from .models import Message, UserStatus
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
        
        # Check if receiver is offline and has AI bot enabled
        try:
            user_status = UserStatus.objects.get(user=receiver)
            
            # Only generate AI response if user is offline AND has AI bot enabled
            if not user_status.is_online and user_status.ai_bot_enabled:
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
            # Create a user status for the receiver if it doesn't exist
            UserStatus.objects.create(user=receiver, is_online=False, ai_bot_enabled=False)
        
        return JsonResponse({'status': 'success', 'message': message_data})
    
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

@csrf_exempt
@login_required
def toggle_ai_bot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enabled = data.get('enabled', False)
        
        try:
            user_status, created = UserStatus.objects.get_or_create(user=request.user)
            user_status.ai_bot_enabled = enabled
            user_status.save()
            return JsonResponse({'status': 'success', 'enabled': enabled})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# New view for debugging user statuses
@login_required
def active_sessions(request):
    # Only allow staff/admin to view this page
    if not request.user.is_staff:
        return redirect('home')
        
    # Get all user statuses
    all_statuses = UserStatus.objects.all().select_related('user')
    
    return render(request, 'chat/active_sessions.html', {
        'statuses': all_statuses
    })

# Force set a user's status to offline (for admins/staff only)
@login_required
def force_logout(request, user_id):
    # Only allow staff/admin to perform this action
    if not request.user.is_staff:
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        user_status, created = UserStatus.objects.get_or_create(user=user)
        user_status.is_online = False
        user_status.last_online = timezone.now()
        user_status.save()
        
        return redirect('active_sessions')
    except Exception as e:
        return render(request, 'chat/active_sessions.html', {
            'statuses': UserStatus.objects.all().select_related('user'),
            'error': f"Error setting user offline: {str(e)}"
        })
