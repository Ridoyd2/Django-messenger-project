# Django Messenger with AI Bot Responses

This is a simple messenger web application built with Django that features an AI response system for offline users. When a user is offline, the system checks the last 5 messages in the conversation and generates an AI response based on that context.

## Features

- User authentication (login, logout, signup)
- Real-time message updates
- Online/offline status tracking
- Unread message counting
- AI-powered responses for offline users
- Clean, responsive UI

## Technology Stack

- Django 5.1.7
- jQuery for AJAX calls
- Bootstrap 5 for UI
- AIML API for AI responses

## Installation

1. Clone the repository
2. Install dependencies:
```
pip install django requests
```

## Configuration

The application uses AIML API for generating AI responses. The API key is already configured in the settings file.

## Running the Application

1. Apply migrations:
```
python manage.py migrate
```

2. Create demo users:
```
python create_users.py
```

3. Run the development server:
```
python manage.py runserver
```

4. Access the application at http://127.0.0.1:8000/

## Demo Users

Five demo users are created when you run the `create_users.py` script:

- john@example.com
- alice@example.com
- bob@example.com
- emma@example.com
- michael@example.com

All users have the password: `password123`

## How the AI Response Works

When a user sends a message to an offline user:
1. The system checks if the recipient is offline
2. If offline, it retrieves the last 5 messages between the two users
3. It sends these messages to the AIML API with context about the offline user
4. The API generates a response that mimics the offline user's conversational style
5. The response is saved as a bot message and sent back to the sender

## License

MIT 