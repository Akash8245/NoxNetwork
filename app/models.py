from django.db import models
import random
import string
from django.contrib.auth.hashers import make_password
from django.db.models.signals import pre_save
from django.dispatch import receiver
 
def generate_referral_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
    
class User(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField(max_length=225, unique=True)
    phone_no = models.CharField(max_length=14, unique=True)  
    password = models.CharField(max_length=100)
    city = models.CharField(max_length=150)
    referred_by = models.CharField(max_length=100, blank=True)
    referral_code = models.CharField(max_length=8, unique=True, editable=False, blank=True)
    no_people_refered = models.IntegerField(default=0)  
    course1_purchased = models.BooleanField(default=False)
    course2_purchased = models.BooleanField(default=False)
    course3_purchased = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    settlement_amt = models.IntegerField(default=0)
    overall_earnings = models.IntegerField(default=0)

    razorpay_payment_id_1 = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id_2 = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id_3 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title}" 

@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    if not instance.referral_code:
        instance.referral_code = generate_referral_code()

    if not instance.pk and instance.password:
        instance.password = make_password(instance.password)

    if instance.pk is None:
        if instance.referred_by:
            try:
                referring_user = User.objects.get(referral_code=instance.referred_by)
                referring_user.no_people_refered += 1
                referring_user.save()
            except User.DoesNotExist:
                pass 
