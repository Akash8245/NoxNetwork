from django.contrib import admin
from django.urls import path
from .views import Home,Signup,Login,Dashboard,CourseView,VerifyEmail,ForgotPasswordRequest,ResetPassword,Logout,About,ContactUs,ReturnPolicy,TermsAndCondition,PrivacyPolicy,Shipping,Payment,Payment_success,Payment_success_2nd,Payment_success_3rd

urlpatterns = [
    path('', Home.as_view()),
    path('signup/',Signup.as_view()),
    path('login/',Login.as_view()),
    path('logout/',Logout.as_view()),
    path('about/',About.as_view()),
    path('contact/',ContactUs.as_view()),
    path('returnpolicy/',ReturnPolicy.as_view()),
    path('termsandcondition/',TermsAndCondition.as_view()),
    path('privacypolicy/',PrivacyPolicy.as_view()),
    path('shipping/',Shipping.as_view()),
    path('dashboard/',Dashboard.as_view()),
    path('course/<int:course_id>/', CourseView.as_view(), name='course'),
    path('verify-email/', VerifyEmail.as_view(), name='verify_email'),
    path('forgot-password/', ForgotPasswordRequest.as_view(), name='forgot_password_request'),
    path('reset-password/', ResetPassword.as_view(), name='reset_password'),
    path('payment1/',Payment.as_view()),
    
    path('payment_success/', Payment_success.as_view()),
    path('payment_success_2nd/', Payment_success_2nd.as_view()),
    path('payment_success_3rd/', Payment_success_3rd.as_view()),
]
