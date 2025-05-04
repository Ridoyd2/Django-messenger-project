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

1. Copy the example environment file:
```
cp .env.example .env
```

2. Edit the `.env` file to set your own secret key (or keep the one provided for development only)

## Setting up the Database

```
# Apply migrations
python manage.py migrate

# Create demo users
python create_users.py
```

## Running the Development Server

```
# Start the development server
python manage.py runserver
```

Access the application at http://127.0.0.1:8000/

## Demo Users

Five demo users are created when you run the `create_users.py` script:

- john@example.com
- alice@example.com
- bob@example.com
- emma@example.com
- michael@example.com

All users have the password: `password123` 