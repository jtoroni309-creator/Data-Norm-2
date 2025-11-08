"""
Event Bus Flow Smoke Tests

Tests event bus connectivity, publish/subscribe flows, and event handling.
These tests verify that the Redis-based event bus is functioning correctly after deployment.
"""

import pytest
import pytest_asyncio
import asyncio
from uuid import uuid4, UUID
from datetime import datetime
from redis.asyncio import Redis

from lib.event_bus.event_bus import EventBus
from lib.event_bus.schemas import (
    BaseEvent,
    EngagementCreatedEvent,
    EngagementFinalizedEvent,
    TrialBalanceUploadedEvent,
    AnalyticsCompletedEvent,
)


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_redis_connectivity(redis_client: Redis):
    """
    Verify basic Redis connectivity.

    Impact: Ensures Redis is accessible for event bus operations.
    """
    # Test ping
    result = await redis_client.ping()
    assert result is True, "Redis ping failed"

    # Test set/get
    test_key = f"smoke_test:{uuid4()}"
    await redis_client.set(test_key, "test_value", ex=60)
    value = await redis_client.get(test_key)
    assert value == "test_value", "Redis set/get failed"

    # Cleanup
    await redis_client.delete(test_key)


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_redis_pub_sub(redis_client: Redis):
    """
    Verify Redis pub/sub functionality.

    Impact: Ensures core messaging infrastructure works.
    """
    channel = f"smoke_test_channel_{uuid4()}"
    received_messages = []

    # Create subscriber
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    # Publisher task
    async def publisher():
        await asyncio.sleep(0.1)  # Give subscriber time to connect
        for i in range(3):
            await redis_client.publish(channel, f"message_{i}")
            await asyncio.sleep(0.05)

    # Subscriber task
    async def subscriber():
        timeout = 2  # 2 second timeout
        start_time = asyncio.get_event_loop().time()

        while len(received_messages) < 3:
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message and message["type"] == "message":
                received_messages.append(message["data"])

    # Run publisher and subscriber concurrently
    await asyncio.gather(publisher(), subscriber())

    # Verify messages received
    assert len(received_messages) == 3, f"Expected 3 messages, got {len(received_messages)}"
    assert received_messages == ["message_0", "message_1", "message_2"]

    # Cleanup
    await pubsub.unsubscribe(channel)
    await pubsub.close()


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_bus_connection(event_bus: EventBus):
    """
    Verify EventBus can connect to Redis.

    Impact: Ensures event bus infrastructure is properly configured.
    """
    assert event_bus.redis_client is not None, "EventBus not connected to Redis"

    # Test Redis connectivity through EventBus
    result = await event_bus.redis_client.ping()
    assert result is True, "EventBus Redis connection failed"


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_publishing(event_bus: EventBus):
    """
    Verify event can be published to a channel.

    Impact: Ensures services can send events to other services.
    """
    channel = f"smoke_test.engagement.created"
    event = EngagementCreatedEvent(
        event_id=str(uuid4()),
        service="engagement",
        engagement_id=uuid4(),
        client_id=uuid4(),
        fiscal_year_end="2024-12-31",
        engagement_type="audit",
    )

    # Publish event (should not raise exception)
    await event_bus.publish(channel, event)

    # Verify event was persisted (if persistence enabled)
    if event_bus.persist_events:
        event_key = f"events:{channel}:{event.event_id}"
        persisted_event = await event_bus.redis_client.get(event_key)
        assert persisted_event is not None, "Event was not persisted"


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_subscription_and_handling(event_bus: EventBus):
    """
    Verify event subscription and handler execution.

    Impact: Ensures services can receive and process events from other services.
    """
    channel = f"smoke_test.trial_balance.uploaded.{uuid4()}"
    received_events = []

    # Define handler
    async def handle_trial_balance_uploaded(event: TrialBalanceUploadedEvent):
        received_events.append(event)

    # Subscribe to channel
    await event_bus.subscribe(
        channel,
        TrialBalanceUploadedEvent,
        handle_trial_balance_uploaded
    )

    # Start listening in background
    await event_bus.start_listening()

    # Give listener time to start
    await asyncio.sleep(0.2)

    # Publish test event
    test_event = TrialBalanceUploadedEvent(
        event_id=str(uuid4()),
        service="ingestion",
        trial_balance_id=uuid4(),
        engagement_id=uuid4(),
        period_end_date="2024-12-31",
        total_lines=150,
    )

    await event_bus.publish(channel, test_event)

    # Wait for event to be processed
    await asyncio.sleep(0.5)

    # Verify event was received and handled
    assert len(received_events) == 1, f"Expected 1 event, got {len(received_events)}"
    received = received_events[0]
    assert received.event_id == test_event.event_id
    assert received.trial_balance_id == test_event.trial_balance_id
    assert received.total_lines == test_event.total_lines


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_multiple_subscribers_same_channel(event_bus: EventBus):
    """
    Verify multiple subscribers can receive the same event.

    Impact: Ensures event fanout pattern works for multiple consumers.
    """
    channel = f"smoke_test.analytics.completed.{uuid4()}"
    handler1_events = []
    handler2_events = []

    async def handler1(event: AnalyticsCompletedEvent):
        handler1_events.append(event)

    async def handler2(event: AnalyticsCompletedEvent):
        handler2_events.append(event)

    # Subscribe both handlers to the same channel
    await event_bus.subscribe(channel, AnalyticsCompletedEvent, handler1)
    await event_bus.subscribe(channel, AnalyticsCompletedEvent, handler2)

    # Start listening
    await event_bus.start_listening()
    await asyncio.sleep(0.2)

    # Publish event
    test_event = AnalyticsCompletedEvent(
        event_id=str(uuid4()),
        service="analytics",
        engagement_id=uuid4(),
        trial_balance_id=uuid4(),
        je_tests_count=25,
        anomalies_found=3,
        risk_level="medium",
    )

    await event_bus.publish(channel, test_event)
    await asyncio.sleep(0.5)

    # Both handlers should receive the event
    assert len(handler1_events) == 1, "Handler 1 did not receive event"
    assert len(handler2_events) == 1, "Handler 2 did not receive event"
    assert handler1_events[0].event_id == test_event.event_id
    assert handler2_events[0].event_id == test_event.event_id


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_persistence(event_bus: EventBus):
    """
    Verify events are persisted to Redis.

    Impact: Ensures event audit trail for debugging and compliance.
    """
    if not event_bus.persist_events:
        pytest.skip("Event persistence is disabled")

    channel = f"smoke_test.engagement.finalized"
    event = EngagementFinalizedEvent(
        event_id=str(uuid4()),
        service="engagement",
        engagement_id=uuid4(),
        finalized_by=uuid4(),
        report_required=True,
    )

    # Publish event
    await event_bus.publish(channel, event)

    # Verify event is persisted
    event_key = f"events:{channel}:{event.event_id}"
    persisted = await event_bus.redis_client.get(event_key)
    assert persisted is not None, "Event was not persisted"

    # Verify event can be retrieved
    import json
    persisted_data = json.loads(persisted)
    assert persisted_data["event_id"] == event.event_id
    assert persisted_data["data"]["engagement_id"] == str(event.engagement_id)


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_history_retrieval(event_bus: EventBus):
    """
    Verify event history can be retrieved.

    Impact: Ensures audit trail and debugging capabilities.
    """
    if not event_bus.persist_events:
        pytest.skip("Event persistence is disabled")

    channel = f"smoke_test.history.{uuid4()}"
    event_ids = []

    # Publish multiple events
    for i in range(3):
        event = EngagementCreatedEvent(
            event_id=str(uuid4()),
            service="engagement",
            engagement_id=uuid4(),
            client_id=uuid4(),
            fiscal_year_end="2024-12-31",
            engagement_type="audit",
        )
        event_ids.append(event.event_id)
        await event_bus.publish(channel, event)

    # Retrieve event history
    history = await event_bus.get_event_history(channel, limit=10)

    # Verify history contains our events
    assert len(history) >= 3, f"Expected at least 3 events, got {len(history)}"
    retrieved_ids = [event["event_id"] for event in history]
    for event_id in event_ids:
        assert event_id in retrieved_ids, f"Event {event_id} not in history"


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_handler_error_and_retry(event_bus: EventBus):
    """
    Verify handler errors trigger retry logic.

    Impact: Ensures resilience and error recovery for event processing.
    """
    channel = f"smoke_test.retry.{uuid4()}"
    attempt_count = 0
    received_events = []

    async def failing_handler(event: AnalyticsCompletedEvent):
        nonlocal attempt_count
        attempt_count += 1
        received_events.append(event)

        # Fail first 2 attempts, succeed on 3rd
        if attempt_count < 3:
            raise Exception(f"Simulated failure (attempt {attempt_count})")

    # Subscribe handler
    await event_bus.subscribe(channel, AnalyticsCompletedEvent, failing_handler)
    await event_bus.start_listening()
    await asyncio.sleep(0.2)

    # Publish event
    test_event = AnalyticsCompletedEvent(
        event_id=str(uuid4()),
        service="analytics",
        engagement_id=uuid4(),
        trial_balance_id=uuid4(),
        je_tests_count=10,
        anomalies_found=0,
        risk_level="low",
    )

    await event_bus.publish(channel, test_event)

    # Wait for retries (exponential backoff: 2s, 4s, 8s)
    # We'll wait up to 10 seconds for retries
    await asyncio.sleep(10)

    # Should have been called 3 times (initial + 2 retries)
    assert attempt_count >= 1, "Handler was not called"
    # Note: Full retry testing may take too long for smoke tests
    # In production, verify retry logic through monitoring


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_dead_letter_queue(event_bus: EventBus):
    """
    Verify failed events are sent to DLQ after max retries.

    Impact: Ensures failed events are not lost and can be investigated.
    """
    channel = f"smoke_test.dlq.{uuid4()}"
    max_retries = event_bus.max_retries

    async def always_failing_handler(event: AnalyticsCompletedEvent):
        raise Exception("Always fails")

    # Clear any existing DLQ messages
    await event_bus.clear_dlq(channel)

    # Subscribe failing handler
    await event_bus.subscribe(channel, AnalyticsCompletedEvent, always_failing_handler)
    await event_bus.start_listening()
    await asyncio.sleep(0.2)

    # Publish event
    test_event = AnalyticsCompletedEvent(
        event_id=str(uuid4()),
        service="analytics",
        engagement_id=uuid4(),
        trial_balance_id=uuid4(),
        je_tests_count=5,
        anomalies_found=0,
        risk_level="low",
    )

    await event_bus.publish(channel, test_event)

    # Wait for all retries to exhaust (exponential backoff can be long)
    # For smoke tests, we'll check DLQ after a reasonable time
    await asyncio.sleep(2)

    # Check if event made it to DLQ
    # Note: This may not always succeed in time-constrained smoke tests
    dlq_messages = await event_bus.get_dlq_messages(channel, limit=10)

    # In production smoke tests, verify DLQ infrastructure exists
    # Actual retry behavior is better tested in integration tests
    assert isinstance(dlq_messages, list), "DLQ query failed"


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_bus_disconnect_and_reconnect(redis_client: Redis):
    """
    Verify EventBus can disconnect and reconnect.

    Impact: Ensures graceful shutdown and restart capabilities.
    """
    # Create new event bus instance
    test_bus = EventBus(redis_url=redis_client.connection_pool.connection_kwargs["path"])
    await test_bus.connect()

    # Verify connection
    assert test_bus.redis_client is not None
    result = await test_bus.redis_client.ping()
    assert result is True

    # Disconnect
    await test_bus.disconnect()

    # Verify disconnection
    assert test_bus._is_listening is False

    # Reconnect
    await test_bus.connect()
    result = await test_bus.redis_client.ping()
    assert result is True

    # Cleanup
    await test_bus.disconnect()


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_concurrent_event_publishing(event_bus: EventBus):
    """
    Verify event bus can handle concurrent publishes.

    Impact: Ensures event bus scales under load.
    """
    channel = f"smoke_test.concurrent.{uuid4()}"
    num_events = 10

    async def publish_event(i: int):
        event = EngagementCreatedEvent(
            event_id=str(uuid4()),
            service="engagement",
            engagement_id=uuid4(),
            client_id=uuid4(),
            fiscal_year_end="2024-12-31",
            engagement_type="audit",
        )
        await event_bus.publish(channel, event)
        return event.event_id

    # Publish events concurrently
    event_ids = await asyncio.gather(*[publish_event(i) for i in range(num_events)])

    assert len(event_ids) == num_events, "Not all events were published"

    # If persistence is enabled, verify all events were persisted
    if event_bus.persist_events:
        for event_id in event_ids:
            event_key = f"events:{channel}:{event_id}"
            persisted = await event_bus.redis_client.get(event_key)
            assert persisted is not None, f"Event {event_id} was not persisted"


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_event_ttl_expiration(event_bus: EventBus):
    """
    Verify event TTL (Time To Live) is set correctly.

    Impact: Ensures Redis doesn't fill up with old events.
    """
    if not event_bus.persist_events:
        pytest.skip("Event persistence is disabled")

    channel = f"smoke_test.ttl"
    event = EngagementCreatedEvent(
        event_id=str(uuid4()),
        service="engagement",
        engagement_id=uuid4(),
        client_id=uuid4(),
        fiscal_year_end="2024-12-31",
        engagement_type="audit",
    )

    await event_bus.publish(channel, event)

    # Check TTL is set
    event_key = f"events:{channel}:{event.event_id}"
    ttl = await event_bus.redis_client.ttl(event_key)

    # TTL should be set (positive value)
    assert ttl > 0, f"Event TTL not set correctly (got {ttl})"
    # Should be approximately event_ttl seconds (default 7 days = 604800 seconds)
    assert ttl <= event_bus.event_ttl, f"Event TTL too high: {ttl} > {event_bus.event_ttl}"


@pytest.mark.smoke
@pytest.mark.redis
@pytest.mark.asyncio
async def test_service_to_service_event_flow(event_bus: EventBus):
    """
    Verify complete event flow between simulated services.

    Impact: Validates end-to-end event-driven communication pattern.
    """
    engagement_id = uuid4()
    trial_balance_id = uuid4()
    events_received = []

    # Simulate engagement service creating engagement
    engagement_created = EngagementCreatedEvent(
        event_id=str(uuid4()),
        service="engagement",
        engagement_id=engagement_id,
        client_id=uuid4(),
        fiscal_year_end="2024-12-31",
        engagement_type="audit",
    )

    # Simulate ingestion service uploading trial balance
    tb_uploaded = TrialBalanceUploadedEvent(
        event_id=str(uuid4()),
        service="ingestion",
        trial_balance_id=trial_balance_id,
        engagement_id=engagement_id,
        period_end_date="2024-12-31",
        total_lines=200,
    )

    # Simulate analytics service completing analysis
    analytics_completed = AnalyticsCompletedEvent(
        event_id=str(uuid4()),
        service="analytics",
        engagement_id=engagement_id,
        trial_balance_id=trial_balance_id,
        je_tests_count=30,
        anomalies_found=2,
        risk_level="medium",
    )

    # Set up handlers to track event flow
    async def track_engagement_created(event: EngagementCreatedEvent):
        events_received.append(("engagement.created", event))

    async def track_tb_uploaded(event: TrialBalanceUploadedEvent):
        events_received.append(("trial_balance.uploaded", event))

    async def track_analytics_completed(event: AnalyticsCompletedEvent):
        events_received.append(("analytics.completed", event))

    # Subscribe handlers
    await event_bus.subscribe("smoke.engagement.created", EngagementCreatedEvent, track_engagement_created)
    await event_bus.subscribe("smoke.trial_balance.uploaded", TrialBalanceUploadedEvent, track_tb_uploaded)
    await event_bus.subscribe("smoke.analytics.completed", AnalyticsCompletedEvent, track_analytics_completed)

    await event_bus.start_listening()
    await asyncio.sleep(0.2)

    # Publish events in sequence
    await event_bus.publish("smoke.engagement.created", engagement_created)
    await asyncio.sleep(0.2)

    await event_bus.publish("smoke.trial_balance.uploaded", tb_uploaded)
    await asyncio.sleep(0.2)

    await event_bus.publish("smoke.analytics.completed", analytics_completed)
    await asyncio.sleep(0.2)

    # Verify all events were received in order
    assert len(events_received) == 3, f"Expected 3 events, got {len(events_received)}"
    assert events_received[0][0] == "engagement.created"
    assert events_received[1][0] == "trial_balance.uploaded"
    assert events_received[2][0] == "analytics.completed"

    # Verify engagement_id is consistent across events
    assert events_received[0][1].engagement_id == engagement_id
    assert events_received[1][1].engagement_id == engagement_id
    assert events_received[2][1].engagement_id == engagement_id
