"""API tests for order endpoints."""

from fastapi import status


def test_create_order(client, create_user, create_event):
    """Test creating an order via API."""
    user = create_user()
    event = create_event(capacity=10)
    
    response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [
                {
                    "event_id": event.id,
                    "quantity": 2,
                    "ticket_type": "GENERAL",
                }
            ],
        },
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == user.id
    assert data["status"] == "HELD"
    assert len(data["items"]) == 2
    assert data["expires_at"] is not None


def test_create_order_insufficient_capacity(client, create_user, create_event):
    """Test that creating an order exceeding capacity fails."""
    user = create_user()
    event = create_event(capacity=1)
    
    response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [
                {
                    "event_id": event.id,
                    "quantity": 5,  # More than capacity
                    "ticket_type": "GENERAL",
                }
            ],
        },
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "capacity" in response.json()["detail"].lower()


def test_create_order_sales_closed(client, create_user, create_event):
    """Test that creating an order for closed event fails."""
    user = create_user()
    event = create_event(sales_open=False)
    
    response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [
                {
                    "event_id": event.id,
                    "quantity": 1,
                }
            ],
        },
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "closed" in response.json()["detail"].lower()


def test_get_order(client, create_user, create_event):
    """Test getting an order by ID."""
    user = create_user()
    event = create_event()
    
    # Create order
    create_response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [{"event_id": event.id, "quantity": 1}],
        },
    )
    order_id = create_response.json()["id"]
    
    # Get order
    response = client.get(f"/api/v1/orders/{order_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == order_id


def test_confirm_order(client, create_user, create_event, fake_email_service):
    """Test confirming an order with payment."""
    user = create_user()
    event = create_event()
    
    # Create order
    create_response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [{"event_id": event.id, "quantity": 1}],
        },
    )
    order_id = create_response.json()["id"]
    
    # Confirm order
    response = client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_token": "success"},  # FakePaymentGateway accepts "success"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "CONFIRMED"
    
    # Verify email was sent
    assert len(fake_email_service.sent_emails) == 1
    assert fake_email_service.sent_emails[0]["order_id"] == order_id


def test_confirm_order_payment_failed(client, create_user, create_event):
    """Test confirming an order with failed payment."""
    user = create_user()
    event = create_event()
    
    # Create order
    create_response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [{"event_id": event.id, "quantity": 1}],
        },
    )
    order_id = create_response.json()["id"]
    
    # Try to confirm with bad token
    response = client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_token": "invalid"},  # Will fail
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in response.json()["detail"].lower()


def test_cancel_order(client, create_user, create_event):
    """Test cancelling an order."""
    user = create_user()
    event = create_event()
    
    # Create order
    create_response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [{"event_id": event.id, "quantity": 1}],
        },
    )
    order_id = create_response.json()["id"]
    
    # Cancel order
    response = client.post(f"/api/v1/orders/{order_id}/cancel")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "CANCELLED"


def test_cancel_confirmed_order_fails(client, create_user, create_event):
    """Test that cancelling a confirmed order fails."""
    user = create_user()
    event = create_event()
    
    # Create and confirm order
    create_response = client.post(
        "/api/v1/orders/",
        json={
            "user_id": user.id,
            "items": [{"event_id": event.id, "quantity": 1}],
        },
    )
    order_id = create_response.json()["id"]
    
    client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_token": "success"},
    )
    
    # Try to cancel
    response = client.post(f"/api/v1/orders/{order_id}/cancel")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot cancel" in response.json()["detail"].lower()

