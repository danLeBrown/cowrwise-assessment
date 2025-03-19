# Library Management System

A microservices-based library management system built with FastAPI, PostgreSQL, and Redis for event-driven communication between services.

## Architecture

The system consists of two independent microservices:

1. **Frontend API** (Public-facing service)
   - PostgreSQL database
   - Redis for event subscription
   - User enrollment and book borrowing

2. **Admin API** (Administrative service)
   - PostgreSQL database
   - Redis for event publishing
   - Book and user management

## Technology Stack

- **Framework**: FastAPI
- **Databases**:
  - PostgreSQL (Admin API)
  - PostgreSQL (Frontend API)
- **Event Bus**: Redis Pub/Sub
- **Testing**: pytest
- **Container Runtime**: Docker
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic

## Setup

### Prerequisites

- Python 3.8+
- Docker
- Redis

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd library-management-system
   ```

2. Run setup script (also useful for running tests):
   ```bash
   bash setup_dev.sh
   ```

3. Start the services:
   ```bash
   docker-compose up --build
   ```

## API Documentation

### Frontend API (Port 8001)

#### Users
- `POST /users` - Enroll a new user
  ```json
  {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```

#### Books
- `GET /books` - List all available books
  - Query params: `publisher`, `category`
- `GET /books/{book_id}` - Get a specific book
- `PUT /books/borrow` - Borrow a book
  ```json
  {
    "book_id": "uuid",
    "user_id": "uuid",
    "days": 7
  }
  ```

### Admin API (Port 8000)

#### Users
- `GET /users` - List all users
- `GET /users/borrowed-books` - List all users with their borrowed books
- `GET /users/{user_id}/borrowed-books` - Get a specific user's borrowed books

#### Books
- `POST /books` - Add a new book
  ```json
  {
    "title": "Clean Code",
    "author": "Robert Martin",
    "category": "technology",
    "publisher": "Prentice Hall"
  }
  ```
- `GET /books` - List all books
- `GET /books/borrowed` - List all borrowed books
- `PUT /books` - Update book status
  ```json
  {
    "book_id": "uuid",
    "status": "available|borrowed|unavailable"
  }
  ```

## Testing

Run the test suite:
```bash
# activate virtual environment
cd tests
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
# pytest --cov=app tests/
```

## Event-Driven Communication

The system uses Redis Pub/Sub for real-time synchronization between services:

- Book events:
  - `book.created` - When a new book is added
  - `book.updated` - When a book's status changes
  - `book.borrowed` - When a book is borrowed

- User events:
  - `user.created` - When a new user is enrolled

## Original Requirements

### Frontend API Requirements
- Enroll users (email, firstname, lastname)
- List available books
- Get book by ID
- Filter books by publisher and category
- Borrow books with specified duration

### Admin API Requirements
- Manage book catalogue (add/remove)
- List enrolled users
- Track borrowed books
- Monitor book availability

### Technical Requirements
- Unauthenticated endpoints
- Python-based framework
- Separate data stores for services
- Event-driven communication
- Docker containerization
- Comprehensive test coverage