"""API tests for event endpoints."""

from datetime import datetime, timedelta, timezone

from fastapi import status


def test_create_event(client, create_venue):
    """Test creating an event via API."""
    venue = create_venue()
    start_time = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    response = client.post(
        "/api/v1/events/",
        json={
            "venue_id": venue.id,
            "name": "Test Concert",
            "start_at": start_time,
            "capacity": 100,
            "sales_open": True,
        },
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Concert"
    assert data["capacity"] == 100
    assert data["sales_open"] is True


def test_create_event_invalid_capacity(client, create_venue):
    """Test that creating an event with zero/negative capacity fails."""
    venue = create_venue()
    start_time = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    response = client.post(
        "/api/v1/events/",
        json={
            "venue_id": venue.id,
            "name": "Bad Event",
            "start_at": start_time,
            "capacity": 0,
        },
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_event_past_date(client, create_venue):
    """Test that creating an event in the past fails."""
    venue = create_venue()
    past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    response = client.post(
        "/api/v1/events/",
        json={
            "venue_id": venue.id,
            "name": "Past Event",
            "start_at": past_time,
            "capacity": 100,
        },
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "future" in response.json()["detail"].lower()


def test_list_events(client, create_event):
    """Test listing all events."""
    create_event(name="Event 1")
    create_event(name="Event 2")
    create_event(name="Event 3")
    
    response = client.get("/api/v1/events/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3


def test_list_events_sales_open_only(client, create_event):
    """Test listing only events with sales open."""
    create_event(name="Open Event 1", sales_open=True)
    create_event(name="Open Event 2", sales_open=True)
    create_event(name="Closed Event", sales_open=False)
    
    response = client.get("/api/v1/events/?sales_open_only=true")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_get_event_by_id(client, create_event):
    """Test getting a specific event by ID."""
    event = create_event(name="Specific Event")
    
    response = client.get(f"/api/v1/events/{event.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == event.id
    assert data["name"] == "Specific Event"


def test_get_event_not_found(client):
    """Test getting non-existent event returns 404."""
    response = client.get("/api/v1/events/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_event_close_sales(client, create_event):
    """Test closing sales for an event."""
    event = create_event(sales_open=True)
    
    response = client.patch(
        f"/api/v1/events/{event.id}",
        json={"sales_open": False},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["sales_open"] is False

