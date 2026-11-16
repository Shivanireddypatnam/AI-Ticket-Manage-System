

from django.db import models
from django.contrib.auth.models import User


class Complaint(models.Model):

    CATEGORY_CHOICES = [
        ('TECHNICAL', 'Technical Issue'),
        ('PAYMENT', 'Payment Issue'),
        ('ACCOUNT', 'Account Issue'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    subject = models.CharField(max_length=200)

    description = models.TextField()
    summary = models.TextField(blank=True, default='')

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.id} - {self.subject}"


class Ticket(models.Model):

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    complaint = models.OneToOneField(
        Complaint,
        on_delete=models.CASCADE,
        related_name='ticket'
    )

    ticket_number = models.CharField(
        max_length=30,
        unique=True
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_tickets'
    )

    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tickets'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_number


class TicketResponse(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_responses'
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.ticket.ticket_number}"

class FAQ(models.Model):

    question = models.CharField(max_length=255, unique=True)

    answer = models.TextField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question