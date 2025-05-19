from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Chapter(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chapters",
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="edited_chapters", blank=True
    )
    written_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Черновик"),
            ("pending", "В ожидании"),
            ("review", "На проверке"),
            ("accepted", "Принято"),
            ("rejected", "Отказано"),
        ],
        default="draft",
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_chapters",
    )
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Главы"


class ChapterRevision(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="revisions"
    )
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chapter_revisions",
    )
    title = models.CharField(max_length=50)
    edited_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name = "Chapter Revision"
        verbose_name_plural = "Chapter Revisions"


class Section(models.Model):
    title = models.CharField(max_length=50)
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="sections"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sections"
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="edited_sections", blank=True
    )
    written_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Черновик"),
            ("pending", "В ожидании"),
            ("review", "На проверке"),
            ("accepted", "Принято"),
            ("rejected", "Отказано"),
        ],
        default="draft",
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_sections",
    )
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Разделы"


class SectionRevision(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="revisions"
    )
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="section_revisions",
    )
    title = models.CharField(max_length=50)
    edited_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name = "Section Revision"
        verbose_name_plural = "Section Revisions"


class Subsection(models.Model):
    title = models.CharField(max_length=50)
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="subsections"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="subsections"
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="edited_subsections", blank=True
    )
    written_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Черновик"),
            ("pending", "В ожидании"),
            ("review", "На проверке"),
            ("accepted", "Принято"),
            ("rejected", "Отказано"),
        ],
        default="draft",
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_subsections",
    )
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Подразделы"


class SubsectionRevision(models.Model):
    subsection = models.ForeignKey(
        Subsection, on_delete=models.CASCADE, related_name="revisions"
    )
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="subsection_revisions",
    )
    title = models.CharField(max_length=50)
    edited_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name = "Subsection Revision"
        verbose_name_plural = "Subsection Revisions"


class QA(models.Model):
    # Status constants - updated to match actual database values
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_IN_REVIEW = "in_review"  # Changed from "review" to "in_review"
    STATUS_REVIEW = "review"        # Added this for backward compatibility
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_PUBLISHED = "published"
    
    # Define status choices to match constants
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Черновик"),
        (STATUS_PENDING, "В ожидании"),
        (STATUS_IN_REVIEW, "На проверке"),  # Primary "in_review" status
        (STATUS_REVIEW, "На проверке"),     # Alternative "review" status
        (STATUS_ACCEPTED, "Принято"),
        (STATUS_REJECTED, "Отказано"),
        (STATUS_PUBLISHED, "Опубликовано"),
    ]
    
    question = models.CharField(max_length=100)
    answer = models.TextField(max_length=3000)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qas"
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="edited_qas", blank=True
    )
    written_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_qas",
    )
    max_links = models.PositiveSmallIntegerField(default=3)

    def __str__(self):
        return self.question


class QA_Subsection(models.Model):
    qa = models.ForeignKey(QA, on_delete=models.CASCADE, related_name="qa_subsections")
    subsection = models.ForeignKey(
        "Subsection", on_delete=models.CASCADE, related_name="qa_subsections"
    )
    copy_number = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("qa", "subsection", "copy_number")


class QAReference(models.Model):
    qa = models.ForeignKey(QA, on_delete=models.CASCADE, related_name="references")
    url = models.URLField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "QA Reference"
        verbose_name_plural = "QA References"


class QARevision(models.Model):
    qa = models.ForeignKey(QA, on_delete=models.CASCADE, related_name="revisions")
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="qa_revisions"
    )
    question = models.CharField(max_length=100)
    answer = models.TextField(max_length=3000)
    edited_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name = "QA Revision"
        verbose_name_plural = "QA Revisions"


class RevisionHistory(models.Model):
    MATERIAL_TYPES = [
        ("chapter", "Chapter"),
        ("section", "Section"),
        ("subsection", "Subsection"),
        ("qa", "QA"),
    ]
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    material_id = models.PositiveIntegerField()
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="revision_histories",
    )
    written_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField()

    class Meta:
        verbose_name = "История изменений"
        verbose_name_plural = "Истории изменений"


class MaterialReview(models.Model):
    MATERIAL_TYPES = [
        ("chapter", "Chapter"),
        ("section", "Section"),
        ("subsection", "Subsection"),
        ("qa", "QA"),
    ]
    DECISION_CHOICES = [
        ("accepted", "Принято"),
        ("accepted_with_changes", "Принято с изменениями"),
        ("rejected", "Отклонено"),
    ]
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    material_id = models.PositiveIntegerField()
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="material_reviews",
    )
    written_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES)
    comment = models.TextField(blank=True)
    edited_content = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Проверка материала"
        verbose_name_plural = "Проверки материалов"


class PendingStatusLevels(models.Model):
    level_name = models.CharField(max_length=20, unique=True)
    min_hours = models.PositiveIntegerField()
    max_hours = models.PositiveIntegerField()
    color_code = models.CharField(max_length=7)  # HEX, e.g. #FF0000

    class Meta:
        verbose_name = "Уровень ожидания"
        verbose_name_plural = "Уровни ожидания"


class Log(models.Model):
    ACTION_TYPES = [
        ("create", "Создание"),
        ("update", "Обновление"),
        ("delete", "Удаление"),
        ("review", "Проверка"),
        ("login", "Вход"),
        ("logout", "Выход"),
        # Add more as needed
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="logs"
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


# Example of using the custom manager in QA:
QA.add_to_class("objects", SoftDeleteManager())
Chapter.add_to_class("objects", SoftDeleteManager())
Section.add_to_class("objects", SoftDeleteManager())
Subsection.add_to_class("objects", SoftDeleteManager())
