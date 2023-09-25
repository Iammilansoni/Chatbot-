from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from .models import UserProfile, Session, Chat
from .forms import ChatForm, SessionForm, RegistrationForm
from .privateGPT import prompt_ai  # Import the function

def login_view(request):
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('chatbot')
	else:
		form = AuthenticationForm()
	return render(request, 'actmasterbot/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

def register_view(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user_profile = form.save(commit=False)
			user_profile.user.set_password(form.cleaned_data['password1'])
			user_profile.user.save()
			login(request, user_profile.user)
			return redirect('chatbot')
	else:
		form = RegistrationForm()
	return render(request, 'actmasterbot/register.html', {'form': form})



@login_required
def chatbot_view(request):
	if request.method == 'POST':
		chat_form = ChatForm(request.POST)
		if chat_form.is_valid():
			message_content = chat_form.cleaned_data['message_content']
			session_id = chat_form.cleaned_data['session']
			session = Session.objects.get(id=session_id)
			Chat.objects.create(
				user_profile=request.user.user_profile,
				session=session,
				message_content=message_content,
				message_type='user'
			)

			# Call your AI function here
			bot_response = prompt_ai(message_content)
			# { "ai_answer" : answer, "doc_answer" : [document.page_content for document in docs] }
			overall_string_message = ""
			overall_string_message += bot_response['ai_answer'] + "\n\n"
			overall_string_message += "```" + "\n\n".join(bot_response['doc_answer']) + "```"

			Chat.objects.create(
				user_profile=request.user.user_profile,
				session=session,
				message_content=bot_response,
				message_type='bot'
			)
			return redirect('chatbot')
	else:
		chat_form = ChatForm()
		session_form = SessionForm()
		sessions = Session.objects.filter(user_profile=request.user.user_profile)
	return render(request, 'actmasterbot/chatbot.html', {'chat_form': chat_form, 'session_form': session_form, 'sessions': sessions})


@login_required
def create_session(request):
	if request.method == 'POST':
		session_form = SessionForm(request.POST)
		if session_form.is_valid():
			session_name = session_form.cleaned_data['session_name']
			Session.objects.create(user_profile=request.user.user_profile, session_name=session_name)
			return redirect('chatbot')
	return redirect('chatbot')

@login_required
def delete_session(request, session_id):
	session = Session.objects.get(id=session_id)
	session.delete()
	return redirect('chatbot')
