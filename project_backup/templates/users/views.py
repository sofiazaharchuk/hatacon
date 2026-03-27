"""Views for user registration and authentication."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView, TemplateView

from templates.users.forms import LoginStep1Form, RegisterForm

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(FormView):
    """CBV for user registration with ECP keypair generation.

    GET: Show registration form.
    POST: Validate form, generate EC keypair derived from password,
          store public key in DB, return private key to user.

    The private key is NEVER stored in DB — only returned once to user.

    Example:
        path('register/', RegisterView.as_view(), name='register'),
    """

    template_name = 'auth/register.html'
    form_class = RegisterForm

    def form_valid(self, form: RegisterForm) -> HttpResponse:
        """Handle valid registration — create user and generate ECP keys.

        Uses derive_key_from_password() to derive encryption key from
        user password, then generate_key_pair() to create EC keypair.
        Public key is stored in DB. Private key is returned to user only.

        Args:
            form: Validated RegisterForm with email and password fields.

        Returns:
            Rendered register_success.html with private_key for download.
        """
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        from django_ecp_auth.utils.crypto_utils import derive_key_from_password, generate_key_pair

        derived_key, _ = derive_key_from_password(password.encode('utf-8'))
        private_key_pem, public_key_pem = generate_key_pair(password=derived_key)

        user = User.objects.create_user(
            email=email,
            username=email,
            password=password,
        )
        user.public_key = public_key_pem
        user.save()

        logger.info('New user registered: %s', email)

        self.request.session['registration_private_key_pem'] = private_key_pem
        self.request.session['registration_email'] = email
        self.request.session.set_expiry(10 * 60)

        return redirect('register-success')


class RegisterSuccessView(TemplateView):
    """Show registration success + one-time download CTA."""

    template_name = 'auth/register_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('registration_email', '')
        return context


class DownloadPrivateKeyView(View):
    """Return the generated private key as an attachment once."""

    def get(self, request: HttpRequest) -> HttpResponse:
        private_key_pem = request.session.get('registration_private_key_pem')
        email = request.session.get('registration_email', 'user')

        if not private_key_pem:
            messages.error(request, 'Private key is no longer available for download.')
            return redirect('register')

        request.session.pop('registration_private_key_pem', None)

        filename_email = ''.join(ch if ch.isalnum() else '_' for ch in email) or 'user'
        filename = f'{filename_email}_private_key.pem'

        response = HttpResponse(private_key_pem, content_type='application/x-pem-file; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
        response['Cache-Control'] = 'no-store, max-age=0'
        response['Pragma'] = 'no-cache'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class LoginStep1View(FormView):
    """CBV for step 1 of two-factor login — email and password.

    On success stores user pk in session under 'partial_auth_user_id'
    and redirects to ECP login step for signature verification.

    Example:
        path('login/', LoginStep1View.as_view(), name='login'),
    """

    template_name = 'auth/login.html'
    form_class = LoginStep1Form

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Redirect authenticated users to dashboard.

        Args:
            request: HTTP request.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Redirect to dashboard if already authenticated, else normal dispatch.
        """
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: LoginStep1Form) -> HttpResponse:
        """Authenticate with email+password and store pending user in session.

        Args:
            form: Validated LoginStep1Form with email and password.

        Returns:
            Redirect to ECP login on success, or form with error on failure.
        """
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(
            self.request,
            username=email,
            password=password,
        )

        if user is None:
            messages.error(self.request, 'Invalid email or password.')
            return self.form_invalid(form)

        self.request.session['partial_auth_user_id'] = user.pk
        logger.info('Step 1 login success for %s', email)
        return redirect('ecp-login')


class LogoutView(View):
    """CBV for user logout.

    Example:
        path('logout/', LogoutView.as_view(), name='logout'),
    """

    def post(self, request: HttpRequest) -> HttpResponse:
        """Logout current user and redirect to login page.

        Args:
            request: Authenticated HTTP request.

        Returns:
            Redirect to login page with info message.
        """
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    """CBV for authenticated user dashboard.

    Requires authentication. Redirects unauthenticated users to login.

    Example:
        path('dashboard/', DashboardView.as_view(), name='dashboard'),
    """

    template_name = 'auth/dashboard.html'
    login_url = 'login'