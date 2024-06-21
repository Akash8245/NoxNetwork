from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User
from django.contrib.auth.hashers import make_password
import random
import string

def generate_referral_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    if not instance.referral_code:
        instance.referral_code = generate_referral_code()

    if not instance.pk and instance.password:
        instance.password = make_password(instance.password)

@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if not created:  # Check if it's an existing user being updated
        if not instance.course1_purchased:  # Check if course1 was not purchased before
            if instance.course1_purchased:  # Check if course1 is now purchased
                instance.handle_mlm_earnings()
