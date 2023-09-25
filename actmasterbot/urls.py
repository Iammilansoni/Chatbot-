from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('create_session/', views.create_session, name='create_session'),
    path('delete_session/<str:session_id>/', views.delete_session, name='delete_session'),

]
