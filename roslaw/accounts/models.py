from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "admin"
    CURATOR = "curator"
    MODERATOR = "moderator"
    SPECIALIST = "specialist"
    VOLUNTEER = "volunteer"
    BLOCKED = "blocked"

    ROLE_CHOICES = [
        (ADMIN, "Админ"),
        (CURATOR, "Куратор"),
        (MODERATOR, "Модератор"),
        (SPECIALIST, "Специалист"),
        (VOLUNTEER, "Волонтер"),
        (BLOCKED, "Заблокированный"),
    ]

    MALE = "M"
    FEMALE = "F"
    SEX_CHOICES = [
        (MALE, "Мужской"),
        (FEMALE, "Женский"),
    ]

    # TZ fields
    patronymic = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Отчество"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SPECIALIST)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        blank=True,
        null=True,
        verbose_name="Пол",
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    region = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Регион"
    )
    address = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Адрес"
    )
    organization = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Организация"
    )
    position = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Должность"
    )
    phone = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Телефон"
    )
    approved = models.BooleanField(default=False, verbose_name="Одобрен")
    approval_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата одобрения"
    )

    # The following fields are already present in AbstractUser:
    # id (user_id), first_name, last_name, email, password, last_login, is_active, date_joined (registration_date)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def is_content_admin(self):
        """Check if the user has content admin permissions."""
        # Check both the role and group membership
        is_admin_role = self.role in [self.ADMIN, self.CURATOR]
        is_admin_group = self.is_staff or self.groups.filter(name='content_admin').exists()
        return is_admin_role or is_admin_group or self.is_superuser

    def is_moderator(self):
        """Check if the user has moderator permissions."""
        # Check both the role and group membership
        is_moderator_role = self.role in [self.ADMIN, self.CURATOR, self.MODERATOR]
        is_moderator_group = self.groups.filter(name='moderator').exists()
        return is_moderator_role or is_moderator_group

    def can_access_moderation(self):
        """Check if user can access moderation area."""
        return self.is_superuser or self.is_content_admin() or self.is_moderator()
