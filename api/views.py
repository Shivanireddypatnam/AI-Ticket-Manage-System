import uuid

from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Complaint, Ticket, TicketResponse, FAQ
from .serializers import (
    ComplaintSerializer,
    TicketResponseSerializer,
    CustomerTicketSerializer,
    AdminTicketSerializer
)
from accounts.permissions import IsCustomerRole, IsAgentRole, IsAdminRole

from .ai_service import get_faq_answer , generate_agent_reply


# Create your views here.

class ProtectedTestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Authentication successful!',
            'username': request.user.username,
            'email': request.user.email
        })


class CustomerComplaintCreateView(generics.CreateAPIView):

    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsCustomerRole
    ]




class AgentComplaintListView(generics.ListAPIView):

    serializer_class = ComplaintSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsAgentRole
    ]

    def get_queryset(self):
        return Complaint.objects.filter(
            status='PENDING'
        ).order_by('-created_at')



class AgentAcceptComplaintView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
        IsAgentRole
    ]

    def post(self, request, complaint_id):

        complaint = get_object_or_404(
            Complaint,
            id=complaint_id
        )

        if complaint.status != 'PENDING':
            return Response(
                {'error': 'This complaint has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            ticket = Ticket.objects.create(
                complaint=complaint,
                ticket_number=f"TEMP-{uuid.uuid4().hex[:8]}",
                customer=complaint.customer,
                assigned_agent=request.user
            )

            ticket.ticket_number = (
                f"TKT-{timezone.now().strftime('%Y%m%d')}-{ticket.id:05d}"
            )

            ticket.save()

            complaint.status = 'ACCEPTED'
            complaint.save()

        return Response({
            'message': 'Complaint accepted successfully!',
            'complaint_id': complaint.id,
            'ticket_id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'status': ticket.status,
            'assigned_agent': request.user.username
        }, status=status.HTTP_201_CREATED)


class AgentTicketResponseView(generics.CreateAPIView):

    serializer_class = TicketResponseSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsAgentRole
    ]

    def perform_create(self, serializer):
        ticket = get_object_or_404(
            Ticket,
            id=self.kwargs['ticket_id'],
            assigned_agent=self.request.user
        )

        serializer.save(
            ticket=ticket,
            agent=self.request.user
        )


class AgentSuggestedReplyView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
        IsAgentRole
    ]

    def get(self, request, ticket_id):

        ticket = get_object_or_404(
            Ticket,
            id=ticket_id,
            assigned_agent=request.user
        )

        complaint = ticket.complaint

        suggested_reply = generate_agent_reply(
            complaint.category,
            complaint.subject,
            complaint.description
        )

        return Response({
            'ticket_id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'suggested_reply': suggested_reply
        })


class CustomerTicketListView(generics.ListAPIView):

    serializer_class = CustomerTicketSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsCustomerRole
    ]

    def get_queryset(self):
        return Ticket.objects.filter(
            customer=self.request.user
        ).order_by('-created_at')

class AdminTicketListView(generics.ListAPIView):

    serializer_class = AdminTicketSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminRole
    ]

    def get_queryset(self):
        return Ticket.objects.all().order_by('-created_at')

class AdminComplaintListView(generics.ListAPIView):

    serializer_class = ComplaintSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminRole
    ]

    def get_queryset(self):
        return Complaint.objects.all().order_by('-created_at')

class FAQChatbotView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
        IsCustomerRole
    ]

    def post(self, request):

        question = request.data.get('question', '').strip()

        if not question:
            return Response(
                {'error': 'Please enter a question.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        faqs = FAQ.objects.filter(
            is_active=True
        ).order_by('id')

        answer = get_faq_answer(question, faqs)

        if answer is None:
            return Response({
                'question': question,
                'answer': 'Sorry, I could not find a suitable answer. Please contact customer support.'
            })

        return Response({
            'question': question,
            'answer': answer
        })


class AdminAnalyticsView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminRole
    ]

    def get(self, request):

        total_complaints = Complaint.objects.count()

        total_tickets = Ticket.objects.count()

        pending_complaints = Complaint.objects.filter(
            status='PENDING'
        ).count()

        accepted_complaints = Complaint.objects.filter(
            status='ACCEPTED'
        ).count()
        category_wise_complaints = Complaint.objects.values(
         'category'
        ).annotate(
            total=Count('id')
        ).order_by('category')
        ticket_status_statistics = Ticket.objects.values(
            'status'
        ).annotate(
         total=Count('id')
        ).order_by('status')
        return Response({
            'total_complaints': total_complaints,
            'total_tickets': total_tickets,
            'pending_complaints': pending_complaints,
            'accepted_complaints': accepted_complaints,
            'category_wise_complaints': category_wise_complaints,
            'ticket_status_statistics': ticket_status_statistics
        })