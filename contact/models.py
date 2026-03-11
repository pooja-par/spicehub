from datetime import timedelta
from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # Track submission source
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(default=timezone.now)
    
    replied_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f'{self.subject} - {self.email}'

    @property
    def response_due_at(self):
        return self.created_at + timedelta(hours=48)

    @property
    def is_overdue(self):
        return self.status == 'new' and timezone.now() > self.response_due_at

    def mark_as_read(self):
        if self.status == 'new':
            self.status = 'read'
            self.save(update_fields=['status'])