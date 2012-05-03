import logging

from django.db.models.signals import post_save
from django.contrib.auth.models import User, check_password
import pylibmc

from lilysvc.account.models import LilyProfile
from lilysvc.lilybbs import Lily
from lilysvc.lilybbs.models import Session

logger = logging.getLogger(__name__)
mc = pylibmc.Client(['127.0.0.1'])

def create_profile(*args, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        profile, created = LilyProfile.objects.get_or_create(user=user)
        if created:
            logger.info('Created LilyProfile for {0}'.format(user))

post_save.connect(create_profile, sender=User)

def get_active_connection(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    profile = user.get_profile()

    lily = Lily(profile.last_session)
    if mc.get('act.{0}'.format(user.id)) or lily.is_logged_in():
        logger.debug('{0}: last_session valid. Success'.format(user))
        mc.set('act.{0}'.format(user.id), 1, time=60)
        return lily
    if profile.lily_password is not None:
        lily = Lily()
        session = lily.login(user.username, profile.lily_password)
        if session:
            profile.last_session = session.dumps()
            profile.save()
            logger.debug('{0}: saved password valid. Success'.format(user))
            mc.set('act.{0}'.format(user.id), 1, time=60)
            return lily
        else:
            profile.lily_password = None
            profile.save()
            logger.debug('{0}: password changed. Failure'.format(user))
            return None
    else:
        profile.last_session = None
        profile.save()
        logger.debug('{0}: no saved password. Failure'.format(user))
        return None

class LilyAuthBackend:
    
    def authenticate(self, username=None, password=None, save_password=False):
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
                logger.info('Created new {0}'.format(user))
            profile, created = LilyProfile.objects.get_or_create(user=user, defaults={'display_name': session.uid})
            if save_password:
                profile.lily_password = password
            else:
                profile.lily_password = None
            profile.last_session = session.dumps()
            profile.save()
            return user
        else:
            return None

    def get_user(self, user_id):
        logger.debug('get_user id={0}'.format(user_id))
        try:
            ret = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.debug('User with id {0} does not exist. Failure'.format(user_id))
            return None
        lily = get_active_connection(ret.username)
        if lily:
            return ret
        else:
            return None

