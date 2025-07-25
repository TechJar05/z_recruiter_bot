from django.urls import path
from .views import ResumeParserAPIView, linkedin_exchange_view

urlpatterns = [
    path('parse/', ResumeParserAPIView.as_view(), name='parse-resume'),
    path('linkedin/exchange/', linkedin_exchange_view, name='linkedin-exchange'),  # LinkedIn OAuth exchange
]
