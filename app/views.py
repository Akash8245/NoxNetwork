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
from django.contrib.auth.hashers import make_password
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
            verification_link = request.build_absolute_uri(
                f"/verify-email/?token={user.verification_token}"
            )
            send_mail(
                'Verify your email address',
                f'Welcome to NoxNetwork Please verify your email by clicking the following link: {verification_link}',
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
            # Generate a unique token
            token = secrets.token_urlsafe(24)
            # Save the token in the user's record
            user.reset_password_token = token
            user.save()

            reset_link = request.build_absolute_uri(f"/reset-password/?token={token}&uid={user.id}")
            # Send an email to the user with the password reset link
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
            
            return render(request, 'dashboard/dashboard.html', {
                "user": user,
                "referred_by_user": referred_by_user
            })
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
            
            if course_id == 1 and user.course1_purchased:
                return render(request, 'courses/course1.html', {"user": user})
            elif course_id == 2 and user.course2_purchased:
                return render(request, 'courses/course2.html', {"user": user})
            elif course_id == 3 and user.course3_purchased:
                return render(request, 'courses/course3.html', {"user": user})
            else:
                return render(request,'courses/course_error.html')
        except TokenError:
            return redirect('/login/')
