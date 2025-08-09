from django.urls import path
from .views import ResumeParserAPIView,RegenerateSummaryAPIView
from .views import ApolloLinkedInLookupAPIView

urlpatterns = [
    path('parse/', ResumeParserAPIView.as_view(), name='parse-resume'),
    path('regenerate-summary/', RegenerateSummaryAPIView.as_view()), 
     path('apollo/profile-match/', ApolloLinkedInLookupAPIView.as_view(), name='apollo-profile-match'),
    #  path('linkedin-info/', LinkedInDataCombinedAPIView.as_view(), name='serp-profile-match'),
    #  path('rocketreachapi/', RocketReachLookupAPIView.as_view(), name='serp-profile-match'),
]



