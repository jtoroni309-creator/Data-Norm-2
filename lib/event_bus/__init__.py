"""
Event Bus for Service Coordination

Redis Pub/Sub based event system for asynchronous communication between microservices.

Features:
- Publish/Subscribe pattern
- Event schemas validation
- Retry mechanism
- Dead letter queue
- Event persistence (optional)
"""

from .event_bus import EventBus, Event, EventHandler
from .schemas import (
    EngagementCreatedEvent,
    EngagementFinalizedEvent,
    TrialBalanceUploadedEvent,
    AccountsMappedEvent,
    AnalyticsCompletedEvent,
    ReportGeneratedEvent,
    UserInvitedEvent,
    QPCReviewRequestedEvent
)

__all__ = [
    "EventBus",
    "Event",
    "EventHandler",
    "EngagementCreatedEvent",
    "EngagementFinalizedEvent",
    "TrialBalanceUploadedEvent",
    "AccountsMappedEvent",
    "AnalyticsCompletedEvent",
    "ReportGeneratedEvent",
    "UserInvitedEvent",
    "QPCReviewRequestedEvent",
]
