from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from content.models import QA

from .forms import (
    CustomAuthenticationForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomUserCreationForm,
    UserProfileForm,
)
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:waiting_approval")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.approved = False
        user.save()

        messages.success(
            self.request,
            "Ваша учетная запись успешно создана и ожидает подтверждения администратором",
        )
        return super().form_valid(form)


class WaitingApprovalView(TemplateView):
    template_name = "accounts/waiting_approval.html"


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect("accounts:login")


class PendingApprovalsView(UserPassesTestMixin, ListView):
    model = User
    template_name = "accounts/pending_approvals.html"
    context_object_name = "pending_users"

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and (self.request.user.role == User.SUPERADMIN or self.request.user.role == User.ADMIN)
        )

    def get_queryset(self):
        return User.objects.filter(approved=False)


class ApproveUserView(UserPassesTestMixin, UpdateView):
    model = User
    fields = []  # No fields needed
    template_name = "accounts/approve_user.html"
    success_url = reverse_lazy("accounts:pending_approvals")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and (self.request.user.role == User.SUPERADMIN or self.request.user.role == User.ADMIN)
        )

    def get(self, request, *args, **kwargs):
        # for GET request - just display the confirmation page
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # for POST request - approve the user
        self.object = self.get_object()
        self.object.approved = True
        self.object.is_active = True
        self.object.approval_date = timezone.now()
        self.object.save()

        messages.success(
            request, f"Пользователь {self.object.get_full_name()} успешно подтвержден."
        )

        return redirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class ProfileView(DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["published_count"] = QA.objects.filter(
            author=user, status=QA.STATUS_PUBLISHED
        ).count()
        context["in_review_count"] = QA.objects.filter(
            author=user, status=QA.STATUS_IN_REVIEW
        ).count()
        context["rejected_count"] = QA.objects.filter(
            author=user, status=QA.STATUS_REJECTED
        ).count()
        context["unread_notifications"] = user.notifications.filter(is_read=False).count()
        return context


@method_decorator(login_required, name="dispatch")
class EditProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/edit_profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен")
        return super().form_valid(form)


# Password change views
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class UserPostsView(LoginRequiredMixin, ListView):
    template_name = 'accounts/user_posts.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        # Get user's QA posts
        return QA.objects.filter(author=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['published_count'] = self.get_queryset().filter(status=QA.STATUS_PUBLISHED).count()
        context['in_review_count'] = self.get_queryset().filter(status=QA.STATUS_IN_REVIEW).count()
        context['rejected_count'] = self.get_queryset().filter(status=QA.STATUS_REJECTED).count()
        return context
