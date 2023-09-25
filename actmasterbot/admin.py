from django.contrib import admin
from .models import UserProfile, Session, Chat
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Session)
admin.site.register(Chat)