import uuid
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class BaseModelWithCreatedInfo(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	index = models.PositiveBigIntegerField(default = 0)
	created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="+", editable=False, blank=True, null=True, verbose_name=_('Created By'))

	class Meta:
		abstract = True
		ordering = ['created_at']


class UserProfile(BaseModelWithCreatedInfo):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name = "user_profile")
	gender = models.CharField(max_length=32, blank=True, null=True)
	mobile_number = models.CharField(max_length=32, null = True, blank = True)

	class Meta:
		verbose_name = "User Profile"
		verbose_name_plural = "User Profiles"

	def __str__(self):return self.user.username.__str__()


	@property
	def user_id(self):
		try:
			return self.user.id
		except Exception as e:
			return None


class Session(BaseModelWithCreatedInfo):
	session_name = models.CharField(max_length=256, null = True, blank = True)
	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null = True, blank = True)
	end_timestamp = models.DateTimeField(null=True, blank=True, auto_now=True)

	def __str__(self):
		return f'Session ID: {self.id} - User: {self.user_profile.user.username}'
	

class Chat(BaseModelWithCreatedInfo):
	session = models.ForeignKey(Session, on_delete=models.CASCADE, null = True, blank = True)
	message_content = models.TextField(null = True, blank = True)
	message_type = models.CharField(max_length=20, null = True, blank = True)  # e.g., 'user', 'bot', 'system'
	
	class Meta:
		verbose_name = "Chat"
		verbose_name_plural = "Chats"

	def __str__(self):
		return f'{self.session.user_profile.user.username} - {self.created_at}'


@receiver(post_save, sender = User)
def execute_on_new_user_creation(sender, instance, created, **kwargs):
	# Execute some logic when new users get created.
	if created:
		UserProfile.objects.get_or_create(user = instance)