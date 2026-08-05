from django.urls import path

from .views import (
    LocLookup,
    LocNameLookup,
    LocSubjectLookup,
    LocNameSearch,
    LocSubjectSearch,
)

app_name = 'loc_authorities'

urlpatterns = [
    path('suggest/', LocLookup.as_view(), name='suggest'),
    path('suggest/names/', LocNameLookup.as_view(), name='name-suggest'),
    path('suggest/subjects/', LocSubjectLookup.as_view(), name='subject-suggest'),
    path('search/names/', LocNameSearch.as_view(), name='name-search'),
    path('search/subjects/', LocSubjectSearch.as_view(), name='subject-search'),
]
