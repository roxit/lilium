import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, check_password

from lilysvc.lilybbs import Lily

class LilyProfile(models.Model):
    user = models.OneToOneField(User)
    display_name = models.CharField(max_length=12)
    lily_password = models.CharField(max_length=12, null=True, blank=True)
    last_session = models.CharField(max_length=50)

'''
def create_profile(*args, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        profile, created = LilyProfile.objects.get_or_create(user=user)
        if created:
            logger.info('Created LilyProfile for {0}'.format(user.username))

post_save.connect(create_profile, sender=User)
'''

class LilyAuthBackend:
    
    def authenticate(self, username=None, password=None):
        logger.debug('Authenticating {0}'.format(username))
        lily = Lily()
        username = username.lower()
        session = lily.login(username, password)
        if session:
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                user = User(username=username, password=password)
                user.save()
            profile, created = LilyProfile.objects.get_or_create(user=user)
            if created:
                profile.display_name = session.uid
            #profile.lily_password = password
            profile.last_session = session.dumps()
            profile.save() 
            return user
        else:
            return None

    def get_user(self, user_id):
        logger.debug('get_user id={0}'.format(user_id))
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

