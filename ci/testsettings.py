# minimal django settings needed to run django tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

INSTALLED_APPS = (
    'dal',
    'dal_alight',
    'loc_authorities',
)

ROOT_URLCONF = 'loc_authorities.test_urls'

LANGUAGE_CODE = 'en-us'

# add manually
# SECRET_KEY = ''
