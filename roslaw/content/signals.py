from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import (
    Chapter,
    Section,
    Subsection,
    QA,
    RevisionHistory,
    Log,
    MaterialReview,
)

User = get_user_model()


def get_changes(old, new, fields):
    changes = {}
    for field in fields:
        old_val = getattr(old, field, None)
        new_val = getattr(new, field, None)
        if old_val != new_val:
            changes[field] = {"old": old_val, "new": new_val}
    return changes


def log_action(user, action_type, model_name, obj_id, details=None):
    Log.objects.create(
        user=user,
        action_type=action_type,
        action_details={
            "model": model_name,
            "id": obj_id,
            "details": details or {},
        },
    )


# --- RevisionHistory signals ---


@receiver(pre_save, sender=Chapter)
def chapter_revision_history(sender, instance, **kwargs):
    if instance.pk:
        old = Chapter.objects.get(pk=instance.pk)
        changes = get_changes(
            old, instance, ["title", "status", "is_published", "is_deleted"]
        )
        if changes:
            RevisionHistory.objects.create(
                material_type="chapter",
                material_id=instance.pk,
                editor=instance.author,
                written_at=instance.written_at,
                changes=changes,
            )


@receiver(pre_save, sender=Section)
def section_revision_history(sender, instance, **kwargs):
    if instance.pk:
        old = Section.objects.get(pk=instance.pk)
        changes = get_changes(
            old, instance, ["title", "status", "is_published", "is_deleted"]
        )
        if changes:
            RevisionHistory.objects.create(
                material_type="section",
                material_id=instance.pk,
                editor=instance.author,
                written_at=instance.written_at,
                changes=changes,
            )


@receiver(pre_save, sender=Subsection)
def subsection_revision_history(sender, instance, **kwargs):
    if instance.pk:
        old = Subsection.objects.get(pk=instance.pk)
        changes = get_changes(
            old, instance, ["title", "status", "is_published", "is_deleted"]
        )
        if changes:
            RevisionHistory.objects.create(
                material_type="subsection",
                material_id=instance.pk,
                editor=instance.author,
                written_at=instance.written_at,
                changes=changes,
            )


@receiver(pre_save, sender=QA)
def qa_revision_history(sender, instance, **kwargs):
    if instance.pk:
        old = QA.objects.get(pk=instance.pk)
        changes = get_changes(
            old,
            instance,
            ["question", "answer", "status", "is_published", "is_deleted"],
        )
        if changes:
            RevisionHistory.objects.create(
                material_type="qa",
                material_id=instance.pk,
                editor=instance.author,
                written_at=instance.written_at,
                changes=changes,
            )


# --- Log signals for create/update/delete ---


@receiver(post_save, sender=Chapter)
def chapter_log(sender, instance, created, **kwargs):
    user = instance.author
    action = "create" if created else "update"
    log_action(user, action, "Chapter", instance.pk)


@receiver(post_save, sender=Section)
def section_log(sender, instance, created, **kwargs):
    user = instance.author
    action = "create" if created else "update"
    log_action(user, action, "Section", instance.pk)


@receiver(post_save, sender=Subsection)
def subsection_log(sender, instance, created, **kwargs):
    user = instance.author
    action = "create" if created else "update"
    log_action(user, action, "Subsection", instance.pk)


@receiver(post_save, sender=QA)
def qa_log(sender, instance, created, **kwargs):
    user = instance.author
    action = "create" if created else "update"
    log_action(user, action, "QA", instance.pk)


@receiver(post_delete, sender=Chapter)
def chapter_delete_log(sender, instance, **kwargs):
    user = instance.author
    log_action(user, "delete", "Chapter", instance.pk)


@receiver(post_delete, sender=Section)
def section_delete_log(sender, instance, **kwargs):
    user = instance.author
    log_action(user, "delete", "Section", instance.pk)


@receiver(post_delete, sender=Subsection)
def subsection_delete_log(sender, instance, **kwargs):
    user = instance.author
    log_action(user, "delete", "Subsection", instance.pk)


@receiver(post_delete, sender=QA)
def qa_delete_log(sender, instance, **kwargs):
    user = instance.author
    log_action(user, "delete", "QA", instance.pk)


# --- MaterialReview log ---


@receiver(post_save, sender=MaterialReview)
def material_review_log(sender, instance, created, **kwargs):
    if created:
        log_action(
            instance.reviewer,
            "review",
            instance.material_type.capitalize(),
            instance.material_id,
            details={
                "decision": instance.decision,
                "comment": instance.comment,
            },
        )


# --- User login/logout log ---


@receiver(user_logged_in)
def user_login_log(sender, request, user, **kwargs):
    log_action(user, "login", "User", user.pk)


@receiver(user_logged_out)
def user_logout_log(sender, request, user, **kwargs):
    log_action(user, "logout", "User", user.pk)
