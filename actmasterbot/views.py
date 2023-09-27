from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, Session, Chat
from .forms import ChatForm, SessionForm, RegistrationForm
from .privateGPT import prompt_ai  # Import the function


def register_view(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=True)
			user.set_password(form.cleaned_data['password1'])
			user.save()
			login(request, user)
			return redirect('create_session')
	else:
		logout(request)
		form = RegistrationForm()
	return render(request, 'actmasterbot/register.html', {'form': form})

def login_view(request):
	logout(request)
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('create_session')
	else:
		form = AuthenticationForm()
	return render(request, 'actmasterbot/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout


@login_required
def create_session(request):
	if request.method == 'POST':
		session_form = SessionForm(request.POST)
		if session_form.is_valid():
			session_name = session_form.cleaned_data['session_name']
			new_session = Session.objects.create(user_profile=request.user.user_profile, session_name=session_name)
            # Pass session_id as a query parameter
			# return render(request, 'actmasterbot/chatbot.html', { 'chat_form': chat_form, 'session': new_session })
			return redirect(f"/chatbot/?session_id={new_session.id}")
	session_form = SessionForm()
	sessions = Session.objects.filter(user_profile=request.user.user_profile)
	return render(request, 'actmasterbot/session_info.html', { 'session_form': session_form, 'sessions': sessions })


@login_required
def delete_session(request, session_id):
	session = Session.objects.get(id=session_id)
	session.delete()
	return redirect('create_session')


@login_required
def chatbot_view(request):
	print("Inside chatbot_view function ....")
	print('\trequest:', request)
	print('\trequest.GET:', request.GET)
	print('\trequest.POST:', request.POST)

	if request.method == 'POST' and request.POST.get('session_id'):
		chat_form = ChatForm(request.POST)
		if chat_form.is_valid():
			session_id = request.POST.get('session_id')
			print("\tsession_id:", session_id)
			message_content = chat_form.cleaned_data['message_content']
			print("\tmessage_content: ", message_content)
			# session_id = chat_form.cleaned_data['session']
			session = Session.objects.get(id=session_id)
			print("\tsession:", session)
			Chat.objects.create(
				session=session,
				message_content=message_content,
				message_type='user'
			)

			# Call your AI function here
			bot_response = prompt_ai(message_content)
			print("\tbot_response:", bot_response)
			# { "ai_answer" : answer, "doc_answer" : [document.page_content for document in docs] }
			overall_string_message = ""
			overall_string_message += bot_response['ai_answer'] + "\n\n"
			overall_string_message += "```" + "\n\n".join(bot_response['doc_answer']) + "```"
			print("\tOverall_string_message:", overall_string_message)

			Chat.objects.create(
				session=session,
				message_content=overall_string_message,
				message_type='bot'
			)
			response_data = {
	            'messages': render_to_string('actmasterbot/partials/_messages.html', {'session': session}),
        	}
			return JsonResponse(response_data) # return redirect('chatbot')
	if session_id := request.GET.get('session_id'):
		print("session_id:", session_id)
		chat_form = ChatForm()

		print("session_id:", session_id)
		session = Session.objects.get(id = session_id)

		return render(request, 'actmasterbot/chatbot.html', 
				{'note' : "Messages found.", 'session' : session , "nosession" : False, "chat_form" : chat_form })
	return render(request, 'actmasterbot/chatbot.html', {"note" : "No session found & Go back & create one", "nosession" : True })
