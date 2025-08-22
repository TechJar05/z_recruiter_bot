from django.urls import path
from .views import ResumeParserAPIView
# from .views import ApolloLinkedInLookupAPIView

urlpatterns = [
    path('parse/', ResumeParserAPIView.as_view(), name='parse-resume'),
    # path('regenerate-summary/', RegenerateSummaryAPIView.as_view()), 
   
]



