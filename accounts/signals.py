from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from accounts.models import Profile
from .cart_utils import migrate_session_cart_to_user


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(user_logged_in)
def migrate_cart_on_login(sender, request, user, **kwargs):
    """
    Migrate anonymous user's cart to authenticated user when they log in.
    """
    try:
        migrate_session_cart_to_user(request, user)
    except Exception as e:
        # Log the error but don't break the login process
        print(f"Error migrating cart on login: {e}")
