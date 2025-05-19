from django.db import models
from django.conf import settings

class Notification(models.Model):
    MODERATION_APPROVED = 'moderation_approved'
    MODERATION_REJECTED = 'moderation_rejected'
    PUBLICATION_APPROVED = 'publication_approved'
    PUBLICATION_REJECTED = 'publication_rejected'

    TYPE_CHOICES = [
        (MODERATION_APPROVED, 'Moderation Approved'),
        (MODERATION_REJECTED, 'Moderation Rejected'),
        (PUBLICATION_APPROVED, 'Publication Approved'),
        (PUBLICATION_REJECTED, 'Publication Rejected'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    content_id = models.IntegerField()  # QA item ID
    content_title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']