from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Chat, Session

class RegistrationForm(UserCreationForm):
    gender = forms.CharField(max_length=32, required=False)
    mobile_number = forms.CharField(max_length=32, required=False)

    class Meta(UserCreationForm.Meta):
        fields = list(UserCreationForm.Meta.fields) + ['gender', 'mobile_number']

    def save(self, commit=True):
        user = super().save(commit=commit)
        print("user:", user)

        if commit:
            user.save()

        user_profile, created = UserProfile.objects.get_or_create(user=user, gender=self.cleaned_data['gender'], mobile_number=self.cleaned_data['mobile_number'])
        # Assuming a OneToOneField from UserProfile to User
        print("UserProfile.objects.all():", UserProfile.objects.all())
        return user_profile


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message_content', 'message_type', 'session']

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session_name'].required = False
