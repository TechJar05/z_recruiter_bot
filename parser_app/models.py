from django.db import models

class LinkedInProfile(models.Model):
    linkedin_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    state = models.CharField(max_length=200, blank=True, help_text="Used to track resume or user ID")
    profile_data = models.JSONField()  # Stores full LinkedIn profile JSON
    access_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
