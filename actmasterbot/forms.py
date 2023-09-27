from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, Chat, Session, User

class RegistrationForm(UserCreationForm):
    gender = forms.CharField(max_length=32, required=False)
    mobile_number = forms.CharField(max_length=32, required=False)

    class Meta(UserCreationForm.Meta):
        fields = list(UserCreationForm.Meta.fields) + ['gender', 'mobile_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        if User.objects.filter(username = user.username).exists():
            raise ValidationError( "username already exists." )
        if commit:
            user.save()
            UserProfile.objects.filter(user = user).update(
                gender = self.cleaned_data['gender'], 
                mobile_number = self.cleaned_data['mobile_number'])

        print("user:", user)
        print("self.cleaned_data:", self.cleaned_data)
        print("UserProfile.objects.all():", UserProfile.objects.all())
        return user


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message_content']

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session_name']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['session_name'].required = True
