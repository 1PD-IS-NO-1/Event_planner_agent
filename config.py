import os

# Flask Config
SECRET_KEY = os.environ.get('SECRET_KEY') or 'f9e173ed7bba9135a850323f04f02428'

# API Keys
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')

# Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}