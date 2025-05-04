# Django Environment Setup

## Setting up a Virtual Environment

### Windows
```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### macOS/Linux
```
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Create a file named `.env` in the project root with the following content:

```
# Django secret key
SECRET_KEY=django-insecure-secret-key-for-development-only

# Debug mode
DEBUG=True

# Hugging Face API Key
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

## Setting up the Database

```
# Apply migrations
python manage.py migrate
```

## Creating a Demo User

You can create a demo user with admin privileges for testing:

```
# Create a demo user
python create_demo_user.py
```

This will create a user with the following credentials:
- Username: demo
- Password: demo1234
- Status: Offline by default
- AI Bot: Enabled by default
- Staff access: Yes (can view active sessions page)

## Running the Development Server

```
# Start the development server
python manage.py runserver
```

Access the application at http://127.0.0.1:8000/

## Online/Offline Status

- Users are automatically set to "Online" when they log in
- Users are automatically set to "Offline" when they log out
- Staff users can view and manage user statuses on the Active Sessions page (/active-sessions/)

## AI Response System

The application uses a context-aware AI response system:

1. The AI system analyzes the last message to determine the appropriate response type
2. Different response types are provided for:
   - Questions (with special handling for how/what/why questions)
   - Greetings (hello, hi, hey)
   - Expressions of gratitude (thanks, thank you)
   - Availability inquiries
3. The system includes the username in responses to make them feel more personal
4. Responses are always contextually appropriate to the conversation 