
from rest_framework import serializers
from .models import Complaint, Ticket, TicketResponse
from .ai_service import classify_complaint, summarize_complaint


class ComplaintSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = [
            'id',
            'subject',
            'description',
            'summary',
            'category',
            'status',
            'created_at'
        ]

        read_only_fields = [
            'id',
            'summary',
            'category',
            'status',
            'created_at'
        ]

    def create(self, validated_data):

        subject = validated_data['subject']
        description = validated_data['description']

        try:
            category = classify_complaint(subject, description)

        except Exception as exc:
            print("AI CLASSIFICATION ERROR:", repr(exc))

            raise serializers.ValidationError(
                "AI classification failed. Please try again later."
            ) from exc

        validated_data['category'] = category
        summary = summarize_complaint(subject, description)

        validated_data['summary'] = summary
        validated_data['customer'] = self.context['request'].user

        return Complaint.objects.create(**validated_data)

class TicketResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketResponse
        fields = [
            'id',
            'ticket',
            'agent',
            'message',
            'created_at'
        ]

        read_only_fields = [
            'id',
            'ticket',
            'agent',
            'created_at'
        ]

class CustomerTicketSerializer(serializers.ModelSerializer):

    responses = TicketResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'complaint',
            'status',
            'created_at',
            'responses'
        ]

class AdminTicketSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source='customer.username',
        read_only=True
    )

    agent_name = serializers.CharField(
        source='assigned_agent.username',
        read_only=True
    )

    responses = TicketResponseSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'complaint',
            'customer_name',
            'agent_name',
            'status',
            'created_at',
            'responses'
        ]