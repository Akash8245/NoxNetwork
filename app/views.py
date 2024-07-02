from datetime import timezone
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserSerializers
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from .models import User
import uuid
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.views import View
from .models import User
from django.shortcuts import render
from django.views import View
from .models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import os 
from dotenv import load_dotenv
import logger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

load_dotenv()

# Home Page
class Home(APIView):
    def get(self, request):
        return render(request, 'index.html')

# Signup
class Signup(APIView):
    def get(self, request):
        referred_by = request.GET.get('referred_by', '')
        return render(request, 'signup/signup.html', {'referred_by': referred_by})

    def post(self, request):
        referred_by = request.data.get('referred_by', '')
        serializer = UserSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.verification_token = str(uuid.uuid4())
            user.token_created_at = timezone.now()
            user.referred_by = referred_by
            user.save()
            base_url = settings.BASE_URL
            verification_link = f"{base_url}/verify-email/?token={user.verification_token}"
            send_mail(
                'Verify your email address',
                f'Welcome to NoxNetwork! Please verify your email by clicking the following link: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return render(request, 'signup/signup_success.html')
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        


# Verification 
class VerifyEmail(APIView):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return Response({"error": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(verification_token=token)
        except User.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        if (timezone.now() - user.token_created_at).days > 1:
            return Response({"error": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.verification_token = ''
        user.token_created_at = None
        user.save()
        return render(request, 'signup/verification_success.html')

# Login 
class Login(APIView):
    def get(self, request):
        token = request.COOKIES.get('access')
        if not token:
            return render(request, 'login/login.html')
        else:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = User.objects.get(pk=user_id)
                return redirect('/dashboard/')
            except (TokenError, User.DoesNotExist):
                response = render(request, 'login/login.html')
                response.delete_cookie('access')
                return response

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if user is None or not check_password(password, user.password):
            return render(request, 'login/login_error.html', {"error": "Invalid email or password"})
        
        if not user.is_verified:
            return render(request, 'login/login_error.html', {"error": "Email not verified"})
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        response = redirect('/dashboard/')
        response.set_cookie(key='access', value=access_token, httponly=True)
        return response
    
# Logout Logic
class Logout(APIView):
    def get(self, request):
        try:
            response = redirect('/login/')
            response.delete_cookie('access')
            
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Forgot Password Request View
class ForgotPasswordRequest(View):
    def get(self, request):
        return render(request, 'forgot_password/forgot_password_request.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = secrets.token_urlsafe(24)
            user.reset_password_token = token
            user.save()

            base_url = settings.BASE_URL
            reset_link = f"{base_url}/reset-password/?token={token}&uid={user.id}"
            send_mail(
                'Password Reset Request',
                f'Please reset your password by clicking the following link: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return render(request, 'forgot_password/forgot_password_email_sent.html')
        except User.DoesNotExist:
            return render(request, 'forgot_password/forgot_password_request.html', {"error": "Email address not found"})


# Reset Password View
class ResetPassword(APIView):
    def get(self, request):
        token = request.GET.get('token')
        uid = request.GET.get('uid')
        if not token or not uid:
            return render(request, 'forgot_password/reset_password.html', {"error": "Token or user ID is missing"})
        return render(request, 'forgot_password/reset_password.html', {"token": token, "uid": uid})

    def post(self, request):
        token = request.POST.get('token')
        uid = request.POST.get('uid')
        new_password = request.POST.get('password')

        try:
            user = User.objects.get(pk=uid)
            if user.reset_password_token == token:  
                user.password = make_password(new_password)  
                user.reset_password_token = None  
                user.save()
                return render(request, 'forgot_password/reset_password_success.html')
            else:
                return render(request, 'forgot_password/reset_password.html', {"error": "Invalid token", "token": token, "uid": uid})
        except User.DoesNotExist:
            return render(request, 'forgot_password/reset_password.html', {"error": "User not found", "token": token, "uid": uid})
        
# About page
class About(APIView):
    def get(self,request):
        return render(request ,'extras/about.html')

# Contact Us
class ContactUs(APIView):
    def get(self,request):
        return render(request,'extras/contact.html')
    
# Return Policy
class ReturnPolicy(APIView):
    def get(self,request):
        return render(request,'extras/return_policy.html')
    
# Terms and Condition
class TermsAndCondition(APIView):
    def get(self,request):
        return render(request,'extras/terms_and_conditions.html')
    
# Privacy Policy
class PrivacyPolicy(APIView):
    def get(self,request):
        return render(request,'extras/privacy_policy.html')
    
#Shipping
class Shipping(APIView):
    def get(self,request):
        return render(request,'extras/shipping.html')

    
# User Dashboard
class Dashboard(APIView):
    def get(self, request):
        token = request.COOKIES.get('access')
        if not token:
            return redirect('/login/')
        
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)
            
            referred_by_user = None
            if user.referred_by:
                try:
                    referred_by_user = User.objects.get(referral_code=user.referred_by).name
                except User.DoesNotExist:
                    referred_by_user = "Unknown"
            
            context = {
                "user": user,
                "referred_by_user": referred_by_user,
                "base_url": settings.BASE_URL  # Add base_url to the context
            }
            return render(request, 'dashboard/dashboard.html', context)
        except (TokenError, User.DoesNotExist):
            response = redirect('/login/')
            response.delete_cookie('access')
            return response
        
# Course View
class CourseView(APIView):
    def get(self, request, course_id):
        token = request.COOKIES.get('access')
        if not token:
            return redirect('/login/')
        
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)
            
            # Course 1
            if course_id == 1:
                if user.course1_purchased:
                    return render(request, 'courses/course1.html', {"user": user})
                elif user.razorpay_payment_id_1:
                    user.course1_purchased = True
                    user.save()
                    return render(request, 'courses/course1.html', {"user": user})
                elif user.razorpay_payment_id_2:
                    user.course1_purchased = True
                    user.save()
                    return render(request, 'courses/course1.html', {"user": user})
                elif user.razorpay_payment_id_3:
                    user.course1_purchased = True
                    user.save()
                    return render(request, 'courses/course1.html', {"user": user})
                else:
                    return render(request, 'payment/payment_page.html')
            
            # Course 2
            elif course_id == 2:
                if user.course2_purchased:
                    return render(request, 'courses/course2.html', {"user": user})
                elif user.razorpay_payment_id_2:
                    user.course2_purchased = True 
                    user.save()
                    return render(request, 'courses/course2.html', {"user": user})
                elif user.razorpay_payment_id_3:
                    user.course2_purchased = True 
                    user.save()
                    return render(request, 'courses/course2.html', {"user": user})
                else:
                    return render(request, 'payment/payment_page_2.html')
            
            # Course 3
            elif course_id == 3:
                if user.course3_purchased:
                    return render(request, 'courses/course3.html', {"user": user})
                elif user.razorpay_payment_id_3:
                    user.course3_purchased = True  
                    user.save()
                    return render(request, 'courses/course3.html', {"user": user})
                else:
                    return render(request, 'payment/payment_page_3.html')
        
        except (TokenError, User.DoesNotExist):
            response = redirect('/login/')
            response.delete_cookie('access')
            return response

razorpay_client = razorpay.Client(auth=(os.getenv('KEY_ID'), os.getenv('KEY_SECRET')))

# Payment 
class Payment(APIView):
    def get(self,request):
        return render(request, 'payment/payment_page.html')
    
    def post(self,request):
        amount = 50000
        currency = 'INR'
        payment = razorpay_client.order.create({'amount':amount,'currency':currency,'payment_capture':'1'})

        return render(request,'payment/payment_page.html')
    
    
# Payment Success Callback 
class Payment_success(APIView):
    def get(self, request):
        return render(request, 'payment/payment_success.html')

    def post(self, request):
        razorpay_payment_id = request.data.get('razorpay_payment_id')

        token = request.COOKIES.get('access')
        if not token:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)
            
            # Update user's payment ID
            user.razorpay_payment_id_1 = razorpay_payment_id
            user.save()

            # Update MLM earnings
            if user.referred_by:
                try:
                    referring_user = User.objects.get(referral_code=user.referred_by)
                    referring_user.settlement_amt += 300
                    referring_user.overall_earnings += 300
                    referring_user.save()

                    if referring_user.referred_by:
                        try:
                            second_level_user = User.objects.get(referral_code=referring_user.referred_by)
                            second_level_user.overall_earnings += 100
                            second_level_user.save()
                        except User.DoesNotExist:
                            pass
                except User.DoesNotExist:
                    pass

            return render(request, 'payment/payment_success.html')  
        except (TokenError, User.DoesNotExist):
            return Response({"error": "Invalid token or user does not exist"}, status=status.HTTP_401_UNAUTHORIZED)
    
# Payment Success Callback 2nd Course
class Payment_success_2nd(APIView):  
    def get(self, request):
        return render(request, 'payment/payment_success.html')

    def post(self, request):
        razorpay_payment_id = request.data.get('razorpay_payment_id')

        token = request.COOKIES.get('access')
        if not token:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)
            
            # Update user's payment ID
            user.razorpay_payment_id_2 = razorpay_payment_id
            user.course2_purchased = True 
            user.save()

            # Update MLM earnings
            if user.referred_by:
                try:
                    referring_user = User.objects.get(referral_code=user.referred_by)
                    referring_user.settlement_amt += 300
                    referring_user.overall_earnings += 300
                    referring_user.save()

                    if referring_user.referred_by:
                        try:
                            second_level_user = User.objects.get(referral_code=referring_user.referred_by)
                            second_level_user.overall_earnings += 100
                            second_level_user.save()
                        except User.DoesNotExist:
                            pass
                except User.DoesNotExist:
                    pass

            return render(request, 'payment/payment_success.html')  
        except (TokenError, User.DoesNotExist):
            return Response({"error": "Invalid token or user does not exist"}, status=status.HTTP_401_UNAUTHORIZED)
        
# Payment Success Callback 3rd Course
class Payment_success_3rd(APIView): 
    def get(self, request):
        return render(request, 'payment/payment_success.html')

    def post(self, request):
        razorpay_payment_id = request.data.get('razorpay_payment_id')

        token = request.COOKIES.get('access')
        if not token:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)
            
            # Update user's payment ID
            user.razorpay_payment_id_3 = razorpay_payment_id
            user.course3_purchased = True  # Update purchase status
            user.save()

            # Update MLM earnings
            if user.referred_by:
                try:
                    referring_user = User.objects.get(referral_code=user.referred_by)
                    referring_user.settlement_amt += 300
                    referring_user.overall_earnings += 300
                    referring_user.save()

                    if referring_user.referred_by:
                        try:
                            second_level_user = User.objects.get(referral_code=referring_user.referred_by)
                            second_level_user.overall_earnings += 100
                            second_level_user.save()
                        except User.DoesNotExist:
                            pass
                except User.DoesNotExist:
                    pass

            return render(request, 'payment/payment_success.html')  
        except (TokenError, User.DoesNotExist):
            return Response({"error": "Invalid token or user does not exist"}, status=status.HTTP_401_UNAUTHORIZED)