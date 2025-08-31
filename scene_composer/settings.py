import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'composer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scene_composer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media files settings - Updated for local image storage
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# API Keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
POLLINATIONS_API_URL = 'https://image.pollinations.ai/prompt/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication backends for email/username login
AUTHENTICATION_BACKENDS = [
    'composer.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Redirect after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Logging configuration for better debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'composer': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Create media directories on startup
def ensure_media_directories():
    """Ensure media directories exist"""
    directories = [
        MEDIA_ROOT,
        MEDIA_ROOT / 'generated_images',
        MEDIA_ROOT / 'backgrounds',
        MEDIA_ROOT / 'characters',
        BASE_DIR / 'static'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Create directories when settings are loaded
ensure_media_directories()
