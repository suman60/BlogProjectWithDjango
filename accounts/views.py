from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm, CustomUserChangeForm
from .models import CustomUser, UserProfile
from django.views.decorators.csrf import csrf_exempt
# from blogs.views import index

# def user_dashboard(request):
#     print(request.user)
#     return render(request, 'accounts/user_dashboard.html')
def home(request):
    return render(request, 'accounts/home.html')

@login_required
def user_dashboard(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        user_profile.mobile = request.POST.get('mobile', user_profile.mobile)
        user_profile.address_line_1 = request.POST.get('address_line_1', user_profile.address_line_1)
        user_profile.address_line_2 = request.POST.get('address_line_2', user_profile.address_line_2)
        user_profile.city = request.POST.get('city', user_profile.city)
        user_profile.state = request.POST.get('state', user_profile.state)
        user_profile.country = request.POST.get('country', user_profile.country)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            try:
                user_profile.profile_picture = request.FILES['profile_picture']
                messages.success(request, 'Profile picture updated successfully!')
            except Exception as e:
                messages.error(request, f'Error uploading profile picture: {str(e)}')
        
        user_profile.save()

        return redirect('user_dashboard')

    context = {
        'user_info': user,
    }
    return render(request, 'accounts/user_dashboard.html', context)



def signup(request):
    if request.method == 'POST':
        # Extract data from POST request using IDs
        full_name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        #terms_agreed = request.POST.get('flexCheckDefault')
        

        # Validate the data
        if not full_name or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect('signup')

        # if not terms_agreed:
        #     messages.error(request, "You must agree to the terms and privacy policy.")
        #     print("Error: You must agree to the terms and privacy policy.")
        #     return redirect('signup')

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "A user with that email already exists.")
            print("Error: A user with that email already exists.\n\n")
            return redirect('signup')

        try:
            # Create a new user
            user = CustomUser.objects.create_user(username=full_name, email=email, password=password)
            user.is_verified = False  # Assuming you have an email verification process
            user.save()

            messages.success(request, "Registration successful. Please verify your email.")
            
            current_site = get_current_site(request)
            verification_link = f"http://{current_site.domain}/accounts/verify/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}"
            
            send_verification_email(user,verification_link)
            return redirect('login')
        except Exception as e:
            # Log the exception and show an error message
            print(f"Error creating user: {e}")
            messages.error(request, "An error occurred while creating the account. Please try again.")
            return redirect('signup')

    return render(request, 'accounts/sign-up.html')

from django.core.mail import EmailMessage
from django.conf import settings
def send_verification_email(user, verification_link):
    # Render the email template with context
    email_subject = 'Verify Your Email Address'
    email_body = render_to_string('accounts/verification_email.html', {
        'user': user,
        'verification_link': verification_link
    })

    # Create the email message
    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    # Send the email
    email.content_subtype = 'html'  # Ensure the email is sent as HTML
    email.send()


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified successfully.')
        return redirect('login')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('signup')
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.is_verified:
            login(request, user)
            return redirect('index')

    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = None  # Initialize the user variable
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Handle the case where the user does not exist
            print("User does not exist.")
            messages.error(request, "User does not exist.")
            return redirect('password_reset')  # Redirect to the forgot password page or another appropriate page

        if user:
            current_site = get_current_site(request)
            subject = 'Reset your password'
            verification_link = f"http://{current_site.domain}/accounts/password_reset_confirm/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}"
    
            send_password_reset_email( user,verification_link)
            print("Email sent")
            return redirect('login')

    return render(request, 'accounts/forgot.html')

def send_password_reset_email(user, verification_link):
    # Render the email template with context
    email_subject = 'Reset you password'
    email_body = render_to_string('accounts/verification_email.html', {
        'user': user,
        'verification_link': verification_link
    })

    # Create the email message
    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    # Send the email
    email.content_subtype = 'html'  # Ensure the email is sent as HTML
    email.send()

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        return redirect('newpassword')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('signup')
def newpassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        user.set_password(password)
        user.save()
        messages.success(request, 'Password updated successfully.')
        return redirect('login')
    return render(request, 'accounts/newpassword.html')
@login_required
def update_profile(request):
    user = request.user
    user_profile = user.userprofile

    if request.method == 'POST':
        # Update user fields
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile fields
        user_profile.mobile = request.POST.get('mobile', user_profile.mobile)
        user_profile.address_line_1 = request.POST.get('address_line_1', user_profile.address_line_1)
        user_profile.address_line_2 = request.POST.get('address_line_2', user_profile.address_line_2)
        user_profile.city = request.POST.get('city', user_profile.city)
        user_profile.state = request.POST.get('state', user_profile.state)
        user_profile.country = request.POST.get('country', user_profile.country)
        user_profile.save()

        return redirect('profile')  # Redirect to profile page after updating

    user_info = CustomUser.objects.get(id=user.id)

    # Pass the user information to the template
    context = {
        'user_info': user_info,
    }

    return render(request, 'accounts/user_dashboard.html', context)