from django.urls import path, include
from .views import (
    ProtectedTestView,
    CustomerComplaintCreateView,
    AgentComplaintListView,
    AgentAcceptComplaintView,
    AgentTicketResponseView,
    CustomerTicketListView,
    AdminTicketListView,
    AdminComplaintListView,
    FAQChatbotView,
    AgentSuggestedReplyView
)



urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('protected/', ProtectedTestView.as_view(), name='protected-api'),

    # Customer complaint API
    path(
        'complaints/',
        CustomerComplaintCreateView.as_view(),
        name='customer-complaints'
    ),

    path(
    'agent/complaints/',
    AgentComplaintListView.as_view(),
    name='agent-complaints'
    ),
    path(
    'agent/complaints/<int:complaint_id>/accept/',
    AgentAcceptComplaintView.as_view(),
    name='agent-accept-complaint'
   ),
   path(
    'agent/tickets/<int:ticket_id>/respond/',
    AgentTicketResponseView.as_view(),
    name='agent-ticket-response'
   ),
   path(
    'customer/tickets/',
    CustomerTicketListView.as_view(),
    name='customer-tickets'
   ),
   path(
    'admin/tickets/',
    AdminTicketListView.as_view(),
    name='admin-tickets'
   ),
   path(
    'admin/complaints/',
    AdminComplaintListView.as_view(),
    name='admin-complaints'
   ),
   path(
    'chatbot/',
    FAQChatbotView.as_view(),
    name='faq-chatbot'
    ),
    path(
    'agent/tickets/<int:ticket_id>/suggest-reply/',
    AgentSuggestedReplyView.as_view(),
    name='agent-suggested-reply'
    ),
]
