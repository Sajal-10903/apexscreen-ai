# Backend Engineering Knowledge Base

## Python Best Practices

Python is a versatile, dynamically-typed programming language widely used for backend development. Key features include readable syntax, extensive standard library, and a large ecosystem of third-party packages.

### Type Hints and Modern Python

Type hints (PEP 484) improve code readability and enable static analysis with tools like mypy. Modern Python (3.10+) supports pattern matching, structural typing, and union types with the `|` operator. Dataclasses and Pydantic models provide structured data with validation. Context managers (`with` statements) handle resource cleanup.

### Generators and Iterators

Generators produce values lazily using `yield`, which is memory-efficient for large datasets. Generator expressions provide a concise syntax. The `itertools` module offers powerful tools for working with iterators. Async generators (PEP 525) enable asynchronous lazy evaluation.

### Concurrency in Python

The GIL (Global Interpreter Lock) prevents true multi-threaded parallelism for CPU-bound tasks. `threading` is suitable for I/O-bound tasks. `multiprocessing` enables CPU-bound parallelism. `asyncio` provides cooperative multitasking for I/O-bound operations. `concurrent.futures` offers a high-level interface for asynchronous execution.

## API Design

### REST API Principles

REST (Representational State Transfer) uses HTTP methods for CRUD operations: GET (read), POST (create), PUT/PATCH (update), DELETE (remove). Resources are identified by URLs. Statelessness means each request contains all information needed. HTTP status codes communicate results: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Internal Server Error).

### API Versioning

Common approaches include URL versioning (/api/v1/), header versioning, and query parameter versioning. URL versioning is the most common and explicit approach. APIs should be backward compatible within a version.

### Request/Response Design

Use consistent naming conventions (snake_case or camelCase). Include pagination for list endpoints (offset/limit or cursor-based). Filter and sort capabilities via query parameters. HATEOAS (Hypermedia as the Engine of Application State) includes links to related resources.

### Rate Limiting and Throttling

Rate limiting protects APIs from abuse. Common algorithms include token bucket, sliding window, and fixed window. Implement using middleware or API gateways. Return appropriate headers (X-RateLimit-Limit, X-RateLimit-Remaining).

## Databases

### Relational Databases

Relational databases store data in tables with rows and columns. ACID properties ensure data integrity: Atomicity (all-or-nothing transactions), Consistency (data remains valid), Isolation (concurrent transactions don't interfere), Durability (committed data persists). SQL (Structured Query Language) is used for querying and manipulation. PostgreSQL and MySQL are popular open-source relational databases.

### SQL Fundamentals

JOINs combine rows from multiple tables: INNER JOIN (matching rows only), LEFT JOIN (all left rows), RIGHT JOIN (all right rows), FULL OUTER JOIN (all rows). Aggregate functions (COUNT, SUM, AVG, MAX, MIN) summarize data. GROUP BY groups rows for aggregation. HAVING filters grouped results. Subqueries can be used in WHERE, FROM, and SELECT clauses.

### Indexing

Indexes speed up queries by creating efficient data structures (B-tree, Hash, GiST). Primary keys are automatically indexed. Create indexes on columns frequently used in WHERE, JOIN, and ORDER BY clauses. Composite indexes cover multiple columns. Over-indexing slows writes and increases storage. EXPLAIN ANALYZE helps identify query performance issues.

### Database Normalization

Normalization reduces data redundancy through normal forms. 1NF: atomic values. 2NF: no partial dependencies. 3NF: no transitive dependencies. BCNF: every determinant is a candidate key. Denormalization is sometimes used for read performance, trading redundancy for query speed.

### ORM (Object-Relational Mapping)

ORMs map database tables to programming language objects. SQLAlchemy (Python) provides both ORM and Core (SQL expression language) interfaces. Benefits include database abstraction, migration support, and type safety. Drawbacks include potential N+1 query problems and complexity for advanced queries. Use eager loading (joinedload) to prevent N+1 queries.

### NoSQL Databases

NoSQL databases include document stores (MongoDB), key-value stores (Redis), column-family stores (Cassandra), and graph databases (Neo4j). They offer schema flexibility, horizontal scaling, and high write throughput. CAP theorem states that a distributed system can guarantee at most two of: Consistency, Availability, Partition tolerance.

## Authentication and Authorization

### Authentication Methods

Session-based authentication stores session data server-side with a session ID in cookies. Token-based authentication (JWT - JSON Web Tokens) includes claims in a signed token. OAuth 2.0 provides delegated authorization with flows like Authorization Code, Client Credentials, and PKCE. API keys are simple but less secure for user authentication.

### JWT (JSON Web Tokens)

JWTs consist of Header (algorithm), Payload (claims), and Signature. Access tokens should be short-lived (15-60 minutes). Refresh tokens enable token renewal without re-authentication. Store tokens securely (HttpOnly cookies, not localStorage). Validate signature, expiration, and issuer on every request.

### Authorization Patterns

RBAC (Role-Based Access Control) assigns permissions to roles, which are assigned to users. ABAC (Attribute-Based Access Control) makes decisions based on attributes of users, resources, and environment. Policy-based authorization centralizes access control logic.

## System Design

### Scalability Patterns

Horizontal scaling adds more machines (scale out). Vertical scaling adds more resources to existing machines (scale up). Load balancers distribute traffic across servers (round-robin, least connections, IP hash). Database read replicas handle read-heavy workloads. Sharding partitions data across multiple databases.

### Caching Strategies

Cache-aside (lazy loading): check cache first, load from database on miss. Write-through: write to cache and database simultaneously. Write-behind: write to cache, asynchronously persist. Cache invalidation strategies include TTL (time-to-live), event-based, and cache-aside refresh. Redis is commonly used for caching with support for data structures, pub/sub, and Lua scripting.

### Message Queues

Message queues enable asynchronous communication between services. RabbitMQ supports complex routing patterns. Apache Kafka provides distributed streaming with partitions and consumer groups. Common patterns include publish-subscribe, work queues, and request-reply. Message queues help decouple services, handle traffic spikes, and ensure reliability.

### Microservices Architecture

Microservices decompose applications into small, independently deployable services. Each service owns its data and communicates via APIs or events. Benefits include independent scaling, technology diversity, and team autonomy. Challenges include distributed transactions, network latency, and operational complexity. Service mesh (Istio, Linkerd) handles cross-cutting concerns.

## Docker and Containers

### Container Fundamentals

Containers package applications with their dependencies in isolated environments. Docker images are built from Dockerfiles using layers. Each instruction creates a layer that is cached for efficient builds. Multi-stage builds reduce final image size by separating build and runtime environments.

### Docker Best Practices

Use specific base image tags (not `latest`). Minimize layers and image size. Use .dockerignore to exclude unnecessary files. Run as non-root user for security. Health checks monitor container health. Environment variables configure runtime behavior. Docker Compose orchestrates multi-container applications.

### Container Orchestration

Kubernetes manages containerized applications at scale. Key concepts include Pods (smallest deployable units), Services (network abstraction), Deployments (declarative updates), ConfigMaps and Secrets (configuration), and Ingress (external access). Kubernetes handles scaling, self-healing, rolling updates, and service discovery.

## Async Processing

### Event-Driven Architecture

Event-driven architecture uses events to trigger and communicate between services. Event producers publish events without knowing consumers. Event consumers react to events independently. Event sourcing stores the state as a sequence of events. CQRS (Command Query Responsibility Segregation) separates read and write models.

### Background Task Processing

Celery is a distributed task queue for Python that supports task scheduling, result backends, and task chains. Tasks can be retried on failure with exponential backoff. Priority queues handle urgent tasks first. Task monitoring and alerting ensure reliability.

## Testing

### Testing Pyramid

Unit tests verify individual components in isolation. Integration tests verify interactions between components. End-to-end tests verify the complete system. Unit tests should be the most numerous, followed by integration, then e2e. Mock external dependencies in unit tests using unittest.mock or pytest-mock.

### Testing Best Practices

Follow Arrange-Act-Assert pattern. Test behavior, not implementation. Use fixtures for test setup. Parameterized tests cover multiple cases efficiently. Test edge cases and error scenarios. Measure code coverage but don't optimize solely for coverage percentage. Use factories for test data creation.

## Security

### Web Security Fundamentals

OWASP Top 10 covers common vulnerabilities. SQL injection is prevented by parameterized queries. XSS (Cross-Site Scripting) is prevented by output encoding. CSRF (Cross-Site Request Forgery) is prevented by tokens. Input validation and sanitization on all user inputs. HTTPS encrypts data in transit. Content Security Policy headers prevent unauthorized script execution.

### Secrets Management

Never commit secrets to version control. Use environment variables or secrets management services (AWS Secrets Manager, HashiCorp Vault). Rotate secrets regularly. Principle of least privilege for API keys and credentials.
