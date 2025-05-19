from django.contrib import admin
from django.utils import timezone
from .models import (
    Chapter,
    Section,
    Subsection,
    QA,
    QA_Subsection,
    QAReference,
    QARevision,
    ChapterRevision,
    SectionRevision,
    SubsectionRevision,
    RevisionHistory,
    MaterialReview,
    PendingStatusLevels,
    Log,
)


def track_revision(instance, request, model_type, fields):
    if instance.pk:
        old = type(instance).objects.get(pk=instance.pk)
        changes = {}
        for field in fields:
            old_val = getattr(old, field)
            new_val = getattr(instance, field)
            if old_val != new_val:
                changes[field] = {"old": old_val, "new": new_val}
        if changes:
            RevisionHistory.objects.create(
                material_type=model_type,
                material_id=instance.pk,
                editor=request.user,  # actual user
                written_at=timezone.now(),
                changes=changes,
            )


class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "author", "status", "is_published")
    search_fields = ("title",)
    readonly_fields = ("author", "created_at", "written_at")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if not obj.created_at:
            obj.created_at = timezone.now()
        if change:
            track_revision(
                obj,
                request,
                "chapter",
                ["title", "status", "is_published", "is_deleted"],
            )
        super().save_model(request, obj, form, change)
        Log.objects.create(
            user=request.user,
            action_type="update" if change else "create",
            action_details={"model": "Chapter", "id": obj.pk},
        )


class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "chapter", "author", "status", "is_published")
    search_fields = ("title",)
    readonly_fields = ("author", "created_at", "written_at")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if not obj.created_at:
            obj.created_at = timezone.now()
        if change:
            track_revision(
                obj,
                request,
                "section",
                ["title", "status", "is_published", "is_deleted"],
            )
        super().save_model(request, obj, form, change)
        Log.objects.create(
            user=request.user,
            action_type="update" if change else "create",
            action_details={"model": "Section", "id": obj.pk},
        )


class SubsectionAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "section", "author", "status", "is_published")
    search_fields = ("title",)
    readonly_fields = ("author", "created_at", "written_at")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if not obj.created_at:
            obj.created_at = timezone.now()
        if change:
            track_revision(
                obj,
                request,
                "subsection",
                ["title", "status", "is_published", "is_deleted"],
            )
        super().save_model(request, obj, form, change)
        Log.objects.create(
            user=request.user,
            action_type="update" if change else "create",
            action_details={"model": "Subsection", "id": obj.pk},
        )


class QAAdmin(admin.ModelAdmin):
    list_display = ("question", "status", "author", "created_at", "is_published")
    list_filter = ("status", "is_published")
    search_fields = ("question", "answer")
    readonly_fields = ("author", "created_at", "written_at")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if not obj.created_at:
            obj.created_at = timezone.now()
        if change:
            track_revision(
                obj,
                request,
                "qa",
                ["question", "answer", "status", "is_published", "is_deleted"],
            )
        super().save_model(request, obj, form, change)
        Log.objects.create(
            user=request.user,
            action_type="update" if change else "create",
            action_details={"model": "QA", "id": obj.pk},
        )


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Subsection, SubsectionAdmin)
admin.site.register(QA, QAAdmin)
admin.site.register(QA_Subsection)
admin.site.register(QAReference)
admin.site.register(QARevision)
admin.site.register(ChapterRevision)
admin.site.register(SectionRevision)
admin.site.register(SubsectionRevision)
admin.site.register(RevisionHistory)
admin.site.register(MaterialReview)
admin.site.register(PendingStatusLevels)
admin.site.register(Log)
