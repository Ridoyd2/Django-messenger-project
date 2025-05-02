# Simple Django Messenger with AI Response

A beginner-friendly messenger application built with Django that uses AI to respond to messages when users are offline.

## Features

- User login and registration
- Send and receive messages
- Online/offline status tracking
- AI responses when recipients are offline
- Simple, clean interface

## Installation

1. Clone the repository
2. Create a virtual environment:
```
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run migrations:
```
python manage.py migrate
```

5. Start the development server:
```
python manage.py runserver
```

6. Visit http://127.0.0.1:8000 in your browser

## How It Works

- Register a new account or log in with existing credentials
- Click on a user from the contacts list to start a conversation
- When a user is offline, AI will automatically respond based on conversation context
- The AI analyzes previous messages to provide contextually relevant responses

## Technologies

- Django 5.1+
- SQLite database
- Bootstrap for UI
- JavaScript/jQuery for dynamic content
- Gemini API for AI responses 