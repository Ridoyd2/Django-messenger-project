from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('chat/<int:receiver_id>/', views.chat_view, name='chat'),
    path('api/messages/<int:receiver_id>/', views.get_messages, name='get_messages'),
    path('api/send_message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('api/users/', views.get_users, name='get_users'),
    path('api/toggle_ai_bot/', views.toggle_ai_bot, name='toggle_ai_bot'),
]
