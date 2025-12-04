# Ticketing System - Software Testing Course Project

A ticketing system built with FastAPI, PostgreSQL, and extensive test coverage. This project demonstrates modern software testing practices including unit tests, integration tests, API tests, and concurrency tests.

Developed for the Fundamentals of Software Design Course at Amirkabir University of Technology.

## 🎯 Learning Objectives

Students will learn to:

1. **Understand test types and purposes**
   - Unit tests for pure business logic
   - Integration tests for database interactions
   - API tests for end-to-end behavior
   - Concurrency tests for race conditions

2. **Practice test design patterns**
   - Fixtures for test setup and teardown
   - Factory patterns for test data
   - Dependency injection and mocking
   - Test isolation with transactions

3. **Work with real infrastructure**
   - PostgreSQL database with transactions
   - GitHub Actions CI/CD pipeline
   - Docker containerization
   - Database migrations with Alembic

4. **Prevent common bugs**
   - Race conditions in concurrent bookings
   - Overbooking prevention
   - Transaction isolation
   - Business logic validation

## 🏗️ Architecture

The project follows a clean/hexagonal architecture:

```
┌─────────────────────────────────────────┐
│         FastAPI API Layer               │
│  (Routes, Pydantic schemas, deps)       │
└─────────────────────────────────────────┘
              ▲
              │
┌─────────────────────────────────────────┐
│    Application / Services Layer         │
│  (Business logic, use cases)            │
└─────────────────────────────────────────┘
              ▲
              │
┌─────────────────────────────────────────┐
│    Repository / Data Access Layer       │
│  (Database operations, abstractions)    │
└─────────────────────────────────────────┘
              ▲
              │
┌─────────────────────────────────────────┐
│         Database (PostgreSQL)           │
└─────────────────────────────────────────┘
```

**Key Benefits:**
- **Testability**: Each layer can be tested in isolation
- **Flexibility**: Easy to mock dependencies
- **Maintainability**: Clear separation of concerns

## 📁 Project Structure

```
ticketer/
├── api/                    # FastAPI routes and dependencies
│   └── v1/
│       ├── routes.py      # API endpoints
│       └── deps.py        # Dependency injection
├── core/
│   └── config.py          # Configuration settings
├── models/                # SQLAlchemy ORM models
│   ├── user.py
│   ├── venue.py
│   ├── event.py
│   ├── seat.py
│   ├── order.py
│   └── payment.py
├── schemas/               # Pydantic request/response schemas
├── repositories/          # Data access layer with interfaces
│   ├── user_repository.py
│   ├── event_repository.py
│   ├── order_repository.py
│   └── ...
├── services/              # Business logic layer
│   ├── auth_service.py
│   ├── event_service.py
│   ├── order_service.py
│   ├── payment_gateway.py
│   └── email_service.py
├── db/
│   ├── base.py           # SQLAlchemy base
│   └── session.py        # Session management
└── main.py               # FastAPI application

tests/
├── conftest.py           # Pytest fixtures and configuration
├── unit/                 # Unit tests (no database)
│   ├── test_seat_allocator.py
│   ├── test_price_calculation.py
│   └── test_auth_service.py
├── integration/          # Integration tests (with database)
│   ├── test_order_repository.py
│   ├── test_event_repository.py
│   └── test_seat_repository.py
└── api/                  # End-to-end API tests
    ├── test_users.py
    ├── test_events.py
    ├── test_orders.py
    └── test_concurrency.py
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Poetry (Python package manager)
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd learning-software-testing
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up the database**
   
   Option A: Using Docker Compose (recommended)
   ```bash
   docker-compose up -d db test_db
   ```
   
   Option B: Manual PostgreSQL setup
   ```bash
   createdb ticketing
   createdb ticketing_test
   ```

4. **Run migrations**
   ```bash
   poetry run alembic upgrade head
   ```

5. **Run the application**
   ```bash
   poetry run uvicorn ticketer.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   
   API documentation: `http://localhost:8000/docs`

## 🧪 Running Tests

### Run all tests with coverage
```bash
poetry run pytest --cov=ticketer --cov-report=html --cov-report=term
```

### Run specific test types
```bash
# Unit tests only (fast, no database)
poetry run pytest tests/unit/ -v

# Integration tests (requires database)
poetry run pytest tests/integration/ -v

# API tests (end-to-end)
poetry run pytest tests/api/ -v

# Concurrency tests (demonstrates race conditions)
poetry run pytest tests/api/test_concurrency.py -v
```

### Watch coverage report
```bash
poetry run pytest --cov=ticketer --cov-report=html
open htmlcov/index.html  # Opens coverage report in browser
```

## 🐳 Docker

### Run the entire stack
```bash
docker-compose up
```

### Run tests in Docker
```bash
docker-compose run --rm app pytest
```

## 🔧 Configuration

Configuration is managed via environment variables or `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ticketing
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
HOLD_EXPIRATION_MINUTES=15
```