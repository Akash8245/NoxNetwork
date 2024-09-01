from .settings import *  # Import everything from the base settings file

# Enable debug mode for development
DEBUG = True

# Set allowed hosts for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use the console email backend for development to print emails to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Override database settings for development (if using SQLite or any other local database)

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('PGDATABASE'),
    'USER': os.getenv('PGUSER'),
    'PASSWORD': os.getenv('PGPASSWORD'),
    'HOST': os.getenv('PGHOST'),
    'PORT': os.getenv('PGPORT', 5432),
    'OPTIONS': {
      'sslmode': 'require',
    },
  }
}

# Override static files settings for development (optional)
STATICFILES_DIRS = [
    BASE_DIR / "app/static",
]

# Optionally, add any other settings specific to the development environment
