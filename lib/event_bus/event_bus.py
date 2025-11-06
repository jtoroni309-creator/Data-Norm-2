"""
Redis-based Event Bus Implementation

Provides pub/sub messaging for microservices coordination
"""

import asyncio
import json
import logging
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4
import redis.asyncio as redis

from .schemas import BaseEvent

logger = logging.getLogger(__name__)


# Type alias for event handlers
EventHandler = Callable[[BaseEvent], None]


class Event:
    """Wrapper for events with metadata"""

    def __init__(self, data: BaseEvent, retry_count: int = 0):
        self.data = data
        self.retry_count = retry_count
        self.event_id = data.event_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "data": self.data.model_dump(),
            "retry_count": self.retry_count,
            "event_id": self.event_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], event_class: type) -> "Event":
        """Create event from dictionary"""
        event_data = event_class(**data["data"])
        return cls(data=event_data, retry_count=data.get("retry_count", 0))


class EventBus:
    """
    Redis-based event bus for service-to-service communication

    Features:
    - Publish events to specific channels
    - Subscribe to events with handlers
    - Automatic retry on failure
    - Dead letter queue for failed events
    - Event persistence (optional)

    Usage:
        # Initialize
        event_bus = EventBus(redis_url="redis://localhost:6379")
        await event_bus.connect()

        # Publish event
        event = EngagementCreatedEvent(
            event_id=str(uuid4()),
            service="engagement",
            engagement_id=engagement_id,
            client_id=client_id,
            fiscal_year_end="2024-12-31",
            engagement_type="audit"
        )
        await event_bus.publish("engagement.created", event)

        # Subscribe to events
        async def handle_engagement_created(event: EngagementCreatedEvent):
            print(f"Engagement created: {event.engagement_id}")

        await event_bus.subscribe(
            "engagement.created",
            EngagementCreatedEvent,
            handle_engagement_created
        )

        # Start listening
        await event_bus.start_listening()
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_retries: int = 3,
        persist_events: bool = True,
        event_ttl: int = 86400 * 7  # 7 days
    ):
        self.redis_url = redis_url
        self.max_retries = max_retries
        self.persist_events = persist_events
        self.event_ttl = event_ttl

        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

        # Registry of event handlers
        self._handlers: Dict[str, List[tuple[type, EventHandler]]] = {}

        # Background tasks
        self._listener_task: Optional[asyncio.Task] = None
        self._is_listening = False

    async def connect(self):
        """Connect to Redis"""
        self.redis_client = await redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        logger.info(f"EventBus connected to Redis at {self.redis_url}")

    async def disconnect(self):
        """Disconnect from Redis"""
        self._is_listening = False

        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.close()

        if self.redis_client:
            await self.redis_client.close()

        logger.info("EventBus disconnected")

    async def publish(self, channel: str, event: BaseEvent):
        """
        Publish event to channel

        Args:
            channel: Channel name (e.g., "engagement.created")
            event: Event to publish
        """
        if not self.redis_client:
            raise RuntimeError("EventBus not connected. Call connect() first.")

        # Wrap event
        wrapped_event = Event(data=event)

        # Serialize to JSON
        message = json.dumps(wrapped_event.to_dict())

        # Publish to channel
        await self.redis_client.publish(channel, message)

        logger.info(f"Published event {event.event_id} to channel {channel}")

        # Persist event (optional)
        if self.persist_events:
            await self._persist_event(channel, wrapped_event)

    async def subscribe(
        self,
        channel: str,
        event_class: type,
        handler: EventHandler
    ):
        """
        Subscribe to events on a channel

        Args:
            channel: Channel name to subscribe to
            event_class: Event class for deserialization
            handler: Async function to handle events
        """
        if not self.pubsub:
            raise RuntimeError("EventBus not connected. Call connect() first.")

        # Register handler
        if channel not in self._handlers:
            self._handlers[channel] = []

        self._handlers[channel].append((event_class, handler))

        # Subscribe to channel
        await self.pubsub.subscribe(channel)

        logger.info(f"Subscribed to channel: {channel}")

    async def start_listening(self):
        """Start listening for events"""
        if self._is_listening:
            logger.warning("Already listening for events")
            return

        self._is_listening = True
        self._listener_task = asyncio.create_task(self._listen_loop())

        logger.info("Started listening for events")

    async def _listen_loop(self):
        """Main event listening loop"""
        try:
            while self._is_listening:
                try:
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1.0
                    )

                    if message and message["type"] == "message":
                        await self._handle_message(message)

                except Exception as e:
                    logger.error(f"Error in listen loop: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Listen loop cancelled")
            raise

    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        channel = message["channel"]
        data = message["data"]

        try:
            # Parse message
            message_dict = json.loads(data)

            # Get handlers for this channel
            if channel not in self._handlers:
                logger.warning(f"No handlers registered for channel: {channel}")
                return

            # Execute all handlers
            for event_class, handler in self._handlers[channel]:
                try:
                    # Deserialize event
                    event = Event.from_dict(message_dict, event_class)

                    # Execute handler
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event.data)
                    else:
                        handler(event.data)

                    logger.debug(f"Handler executed for event {event.event_id}")

                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

                    # Retry logic
                    if event.retry_count < self.max_retries:
                        await self._retry_event(channel, event, event_class)
                    else:
                        await self._send_to_dlq(channel, event, str(e))

        except Exception as e:
            logger.error(f"Error handling message from {channel}: {e}")

    async def _retry_event(self, channel: str, event: Event, event_class: type):
        """Retry failed event"""
        event.retry_count += 1

        # Exponential backoff
        delay = 2 ** event.retry_count

        logger.info(
            f"Retrying event {event.event_id} (attempt {event.retry_count}/{self.max_retries}) "
            f"after {delay}s"
        )

        await asyncio.sleep(delay)

        # Re-publish event
        message = json.dumps(event.to_dict())
        await self.redis_client.publish(channel, message)

    async def _send_to_dlq(self, channel: str, event: Event, error: str):
        """Send failed event to dead letter queue"""
        dlq_key = f"dlq:{channel}"

        dlq_entry = {
            "event": event.to_dict(),
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "channel": channel
        }

        await self.redis_client.lpush(dlq_key, json.dumps(dlq_entry))
        await self.redis_client.expire(dlq_key, self.event_ttl)

        logger.error(
            f"Event {event.event_id} sent to DLQ after {self.max_retries} retries. "
            f"Error: {error}"
        )

    async def _persist_event(self, channel: str, event: Event):
        """Persist event to Redis for audit trail"""
        key = f"events:{channel}:{event.event_id}"

        await self.redis_client.set(
            key,
            json.dumps(event.to_dict()),
            ex=self.event_ttl
        )

    async def get_event_history(
        self,
        channel: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get event history for a channel"""
        pattern = f"events:{channel}:*"
        events = []

        async for key in self.redis_client.scan_iter(match=pattern, count=limit):
            event_json = await self.redis_client.get(key)
            if event_json:
                events.append(json.loads(event_json))

        return events[:limit]

    async def get_dlq_messages(self, channel: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get dead letter queue messages for a channel"""
        dlq_key = f"dlq:{channel}"
        messages = await self.redis_client.lrange(dlq_key, 0, limit - 1)
        return [json.loads(msg) for msg in messages]

    async def clear_dlq(self, channel: str):
        """Clear dead letter queue for a channel"""
        dlq_key = f"dlq:{channel}"
        await self.redis_client.delete(dlq_key)
        logger.info(f"Cleared DLQ for channel: {channel}")


# Singleton instance
_event_bus_instance: Optional[EventBus] = None


async def get_event_bus() -> EventBus:
    """Get or create EventBus singleton"""
    global _event_bus_instance

    if _event_bus_instance is None:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _event_bus_instance = EventBus(redis_url=redis_url)
        await _event_bus_instance.connect()

    return _event_bus_instance
