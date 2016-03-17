"""
Test settings for ``polymorphic_auth`` app.
"""

AUTH_USER_MODEL = 'polymorphic_auth.User'
POLYMORPHIC_AUTH = {
    'DEFAULT_CHILD_MODEL': 'polymorphic_auth_email.EmailUser',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_nose',
    'polymorphic',
    'polymorphic_auth',
    'polymorphic_auth.tests',
    'polymorphic_auth.usertypes.email',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'polymorphic_auth.tests.urls'
SECRET_KEY = 'secret-key'
STATIC_URL = '/static/'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
