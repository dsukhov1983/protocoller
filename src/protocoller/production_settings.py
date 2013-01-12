from settings import *
DEBUG = False
TEMPLATE_DEBUG = DEBUG
FORCE_SCRIPT_NAME = ""

UPLOAD_ROOT = "/home/quoter/upload"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'protocoller@protocoller.ru'
