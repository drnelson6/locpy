"""URL configurations for running loc-authorities tests"""

try:
    from django.urls import include, path

    from loc_authorities import urls as loc_urls

    urlpatterns = [
        path(r'loc_authorities', include(loc_urls, namespace='loc_authorities'))
    ]

except ImportError:
    pass
