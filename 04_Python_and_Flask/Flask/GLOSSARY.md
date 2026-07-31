# Glossary

> Definitions of all technical terms used throughout this handbook.

---

## A

**Alembic**
A lightweight database migration tool for SQLAlchemy. It manages changes to your database schema over time using revision scripts. See [[03-Database/SQLAlchemy-Migrations]] and [[Appendix/Alembic]].

**Application Context**
Flask's context that tracks the application-level data during a request, CLI command, or other activity. Makes `current_app` and `g` available. See [[01-Flask-Core/Application-Context]].

**Application Factory**
A design pattern where a function creates and configures the Flask application instance, enabling multiple app instances with different configurations. See [[06-Blueprints/Application-Factory]].

**API (Application Programming Interface)**
A set of rules and protocols that allows different software applications to communicate with each other. In web development, typically refers to HTTP endpoints that return data (usually JSON) rather than HTML. See [[00-Foundations/REST-APIs]].

**Argument (URL Argument)**
A variable part of a URL pattern in Flask routing. Defined with `<converter:variable_name>` syntax in route decorators. See [[01-Flask-Core/Routing]].

**Async (Asynchronous)**
A programming pattern where operations can be paused and resumed, allowing other work to proceed during waiting periods (like database queries or HTTP requests). See [[10-Advanced/Async-Flask]].

**Authentication**
The process of verifying the identity of a user, typically through credentials like username and password. See [[04-Authentication/Authentication-Overview]].

**Authorization**
The process of determining what an authenticated user is allowed to do. Distinct from authentication — a user may be logged in (authenticated) but not have permission to access an admin page (not authorized).

## B

**Blueprint**
A Flask feature for organizing related routes, templates, static files, and other code into reusable components. Enables modular application architecture. See [[06-Blueprints/Blueprints]].

**Browser**
A software application used to access and display web pages. Examples include Chrome, Firefox, Safari, and Edge. Handles HTML parsing, CSS rendering, and JavaScript execution. See [[00-Foundations/Browser]].

## C

**Caching**
Storing copies of expensive-to-generate data in fast storage (usually memory) to reduce response times and server load. See [[10-Advanced/Caching]].

**CDN (Content Delivery Network)**
A geographically distributed network of proxy servers that deliver content to users from the nearest location, reducing latency.

**CGI (Common Gateway Interface)**
An early standard for web servers to execute external programs and return their output as web pages. Superseded by WSGI in Python web development.

**CLI (Command Line Interface)**
A text-based interface for interacting with software. Flask provides its own CLI through the `flask` command. See [[01-Flask-Core/Flask-CLI]].

**Context Locals**
Thread-local storage mechanisms in Flask that make certain objects (like `request`, `session`, `g`, `current_app`) globally accessible while remaining isolated per request. Implemented using Werkzeug's `Local` and `LocalStack`. See [[01-Flask-Core/Request-Context]].

**Cookie**
A small piece of data stored by the browser and sent with subsequent requests to the same domain. Used for session identification, preferences, and tracking. See [[00-Foundations/Cookies-Sessions]] and [[01-Flask-Core/Cookies]].

**CRUD**
Create, Read, Update, Delete — the four basic operations for persistent storage. Most web applications implement CRUD for their primary data models. See [[05-Blog-Application/CRUD-Operations]].

**CSRF (Cross-Site Request Forgery)**
An attack where a malicious website tricks a user's browser into performing unwanted actions on a trusted site where the user is authenticated. Prevented using CSRF tokens. See [[08-Security/CSRF-Protection]].

**CSS (Cascading Style Sheets)**
A stylesheet language used to describe the presentation of HTML documents, including colors, layout, and fonts. See [[00-Foundations/Web-Technologies]].

## D

**Database**
An organized collection of structured data stored electronically. Relational databases (like PostgreSQL, MySQL, SQLite) store data in tables with predefined schemas. See [[03-Database/Database-Fundamentals]].

**Database Migration**
A controlled way to change a database schema over time. Each migration represents a set of changes (add table, add column, etc.) that can be applied or reverted. See [[03-Database/SQLAlchemy-Migrations]].

**Decorator**
A Python feature that allows modifying or enhancing functions. Flask uses decorators extensively, most notably `@app.route()` for URL routing. See [[01-Flask-Core/Routing]].

**DNS (Domain Name System)**
The hierarchical system that translates human-readable domain names (like `google.com`) into IP addresses that computers use to identify each other. See [[00-Foundations/DNS]].

**Docker**
A platform for developing, shipping, and running applications in containers — lightweight, portable, self-sufficient environments. See [[10-Advanced/Docker]].

**DOM (Document Object Model)**
A programming interface for HTML documents that represents the page structure as a tree of objects, allowing JavaScript to manipulate content and styles.

## E

**Endpoint**
The internal name for a URL rule in Flask. Defaults to the function name but can be customized. Used with `url_for()` to generate URLs. See [[01-Flask-Core/Routing]].

**Environment Variable**
A dynamic-named value on the operating system that can affect the behavior of running processes. Used to configure Flask applications without changing code. See [[01-Flask-Core/Configuration]] and [[07-Deployment/Environment-Variables]].

**Extension**
A Python package that adds functionality to Flask. Extensions follow naming conventions (`Flask-*`) and integrate with Flask's application and request contexts. Examples: `Flask-SQLAlchemy`, `Flask-Login`.

## F

**Filter (Jinja2)**
A Jinja2 feature that transforms a value into another format. Example: `{{ name|title }}` capitalizes the first letter of each word. See [[02-Jinja2/Filters]] and [[02-Jinja2/Custom-Filters]].

**Flask**
A lightweight Python web framework that provides the essentials for building web applications without imposing specific tools or libraries. See [[01-Flask-Core/Flask-Architecture]].

**Foreign Key**
A database column that references the primary key of another table, establishing a relationship between the two tables. See [[03-Database/Relationships]].

**Form**
An HTML element that collects user input and sends it to a server via HTTP POST request. Flask-WTF and WTForms provide server-side form validation. See [[04-Authentication/Forms]].

## G

**g (Flask)**
A namespace object in Flask's application context used to store data during an application context lifetime. Survives for the duration of a request or CLI command. See [[01-Flask-Core/Application-Context]].

**Generator (Python)**
A function that returns an iterator using the `yield` keyword, producing a sequence of values lazily. Used in Flask for streaming responses. See [[01-Flask-Core/Request-Response]].

**GET**
An HTTP method used to retrieve resources from a server. GET requests should not have side effects on server state. See [[00-Foundations/HTTP]].

**Gunicorn**
A production-grade WSGI HTTP server for Python web applications. Stands for "Green Unicorn." See [[07-Deployment/Gunicorn]] and [[Appendix/Gunicorn]].

## H

**Hashing (Password)**
The process of transforming a password into a fixed-length string of characters using a one-way mathematical function. Makes it computationally infeasible to recover the original password. See [[04-Authentication/Password-Hashing]].

**HTML (HyperText Markup Language)**
The standard markup language for documents designed to be displayed in a web browser. Defines the structure and content of web pages. See [[00-Foundations/Web-Technologies]].

**HTTP (HyperText Transfer Protocol)**
The foundation protocol of the World Wide Web, defining how messages are formatted and transmitted between browsers and servers. See [[00-Foundations/HTTP]].

**HTTP Method (Verb)**
An operation indicating the desired action to be performed on a resource. Common methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS. See [[00-Foundations/HTTP]].

**HTTP Status Code**
A three-digit number in an HTTP response indicating the result of the request. Categories: 1xx (informational), 2xx (success), 3xx (redirection), 4xx (client error), 5xx (server error). See [[00-Foundations/HTTP]].

**HTTPS (HTTP Secure)**
HTTP encrypted with TLS/SSL. Protects against eavesdropping and man-in-the-middle attacks. See [[00-Foundations/TLS-HTTPS]].

## I

**IDLE**
Python's Integrated Development and Learning Environment, included with standard Python installations.

**IP Address (Internet Protocol Address)**
A numerical label assigned to each device connected to a computer network. IPv4 uses 32-bit addresses (e.g., `192.168.1.1`); IPv6 uses 128-bit addresses. See [[00-Foundations/IP-Addresses]].

**itsdangerous**
A Python library used by Flask for signing data to ensure its integrity. Used for session cookies and token generation. See [[Appendix/itsdangerous]].

**Iterator**
A Python object that produces values one at a time when iterated over, using the `__iter__()` and `__next__()` methods.

## J

**JavaScript**
A programming language that enables interactive web pages. Runs in the browser and can manipulate the DOM, handle events, and make HTTP requests. See [[00-Foundations/Web-Technologies]].

**Jinja2**
A modern and powerful templating engine for Python, used by Flask to generate HTML from templates. Supports template inheritance, filters, macros, and control structures. See [[02-Jinja2/Jinja2-Overview]] and [[Appendix/Jinja2]].

**JSON (JavaScript Object Notation)**
A lightweight data-interchange format that is easy for humans to read and write and easy for machines to parse and generate. The standard data format for modern web APIs. See [[00-Foundations/JSON]].

**JWT (JSON Web Token)**
A compact, self-contained way of transmitting information between parties as a JSON object, digitally signed using a secret or public/private key pair. Used for stateless authentication. See [[10-Advanced/JWT-Authentication]].

## K

**Keyword Argument**
In Python, an argument passed to a function by explicitly naming the parameter. Flask's `url_for()` uses keyword arguments to pass URL variables.

## L

**Lambda Function**
An anonymous function in Python defined with the `lambda` keyword. Often used for simple operations in Jinja2 templates or sorting operations.

**Linux**
A family of open-source Unix-like operating systems based on the Linux kernel. The dominant OS for web servers. See [[07-Deployment/Linux-Server]].

**LocalStack (Werkzeug)**
Werkzeug's thread-local storage implementation that keeps objects isolated per thread (or async task). Powers Flask's context locals. See [[Appendix/Werkzeug]].

**Logging**
The practice of recording events, errors, and information during application execution. Essential for debugging and monitoring production applications. See [[10-Advanced/Logging]].

## M

**Macro (Jinja2)**
A reusable template fragment in Jinja2, similar to a function. Defined with `{% macro %}` and called like a function. See [[02-Jinja2/Macros]].

**Many-to-Many Relationship**
A database relationship where multiple records in one table can relate to multiple records in another table, implemented via a junction/association table. See [[03-Database/Relationships]].

**Middleware**
Software that sits between the web server and application, processing requests and responses. In Flask, implemented as WSGI middleware or `before_request`/`after_request` handlers. See [[10-Advanced/Middleware]].

**Migration**
See Database Migration.

**Model (MVC)**
The data layer of an application, responsible for business logic and database interactions. In Flask with SQLAlchemy, models are Python classes that map to database tables. See [[03-Database/Models]].

**Model-View-Controller (MVC)**
A software architectural pattern separating an application into three components: Model (data), View (presentation), and Controller (logic). Flask follows a variation called Model-View-Template (MVT). See [[01-Flask-Core/Flask-Architecture]].

## N

**Namespace Package**
A Python package spread across multiple directories, useful for organizing large Flask applications with blueprints.

**Nginx**
A high-performance web server, reverse proxy, and load balancer. Commonly used in front of Gunicorn to serve Flask applications. See [[07-Deployment/Nginx]].

**NoSQL**
A category of database management systems that store data in formats other than relational tables (e.g., document stores, key-value stores, graph databases). Contrast with relational (SQL) databases.

## O

**One-to-Many Relationship**
A database relationship where one record in a table can relate to multiple records in another table (e.g., one user has many posts). See [[03-Database/Relationships]].

**ORM (Object-Relational Mapping)**
A technique that lets you interact with a relational database using object-oriented programming. SQLAlchemy is the most popular Python ORM. See [[03-Database/SQLAlchemy-ORM]].

## P

**Pagination**
The practice of dividing a large set of data into discrete pages for display. Reduces database load and improves user experience. See [[05-Blog-Application/Pagination]].

**PATCH**
An HTTP method used to apply partial modifications to a resource. Contrast with PUT, which replaces the entire resource. See [[00-Foundations/HTTP]].

**Path (URL Path)**
The part of a URL that comes after the domain name, identifying a specific resource. Example: in `https://example.com/users/123`, the path is `/users/123`.

**PEP 8**
Python's official style guide for writing clean, readable Python code. Flask follows PEP 8 conventions.

**Pillow**
A Python imaging library (fork of PIL) used for image processing in Flask applications, such as resizing uploaded profile pictures. See [[Appendix/Pillow]].

**PIP**
Python's package installer. Used to install Flask and its extensions: `pip install flask`. See [[01-Flask-Core/Flask-Architecture]].

**Port**
A logical endpoint for network communication. Different services on the same server listen on different ports (HTTP: 80, HTTPS: 443, Flask dev: 5000). See [[00-Foundations/Ports]].

**POST**
An HTTP method used to submit data to a server, typically causing a change in server state (creating a resource, submitting a form). See [[00-Foundations/HTTP]].

**Primary Key**
A database column (or set of columns) that uniquely identifies each row in a table. Usually an auto-incrementing integer. See [[03-Database/Models]].

**Query Parameter**
Key-value pairs appended to a URL after a `?` character, used to pass additional data to the server. Example: `/search?q=flask`. See [[01-Flask-Core/Request-Response]].

**Query String**
The part of a URL containing query parameters. Everything after the `?` character. See [[00-Foundations/HTTP]].

## R

**Redirect**
An HTTP response that tells the browser to request a different URL. Flask provides `redirect()` and `url_for()` for this. Status codes: 301 (permanent), 302 (temporary). See [[01-Flask-Core/Request-Response]].

**Referer (HTTP Header)**
An HTTP header that indicates the address of the previous web page from which a link was followed. Commonly misspelled "Referrer" in the spec.

**Relationship (Database)**
A connection between two database tables based on foreign keys. Types: one-to-one, one-to-many, many-to-many. See [[03-Database/Relationships]].

**Request**
An HTTP message sent by a client (usually a browser) to a server, asking for a resource or action. Flask provides the `request` object to access request data. See [[01-Flask-Core/Request-Response]].

**Request Context**
The context that tracks the request-level data during a single HTTP request. Makes `request` and `session` available. See [[01-Flask-Core/Request-Context]].

**Response**
An HTTP message sent by a server back to a client in reply to a request. Flask provides the `Response` class and helpers like `make_response()`. See [[01-Flask-Core/Request-Response]].

**REST (Representational State Transfer)**
An architectural style for designing networked applications using HTTP methods and resource-based URLs. The foundation of modern API design. See [[00-Foundations/REST-APIs]].

**Reverse Proxy**
A server that sits between clients and backend servers, forwarding client requests to the appropriate backend. Nginx commonly serves this role for Flask apps. See [[07-Deployment/Nginx]].

**Route**
A URL pattern mapped to a Python function in Flask. Defined using the `@app.route()` decorator. See [[01-Flask-Core/Routing]].

**Routing**
The process of matching an incoming request URL to the appropriate handler function. See [[01-Flask-Core/Routing]].

## S

**SameSite (Cookie Attribute)**
A cookie attribute that controls whether cookies are sent with cross-site requests. Values: `Strict`, `Lax`, `None`. Important for CSRF protection. See [[08-Security/CSRF-Protection]].

**Scaffold (Project)**
The initial directory structure and files for a Flask project, typically including application code, templates, static files, and configuration.

**Secret Key**
A cryptographic key used by Flask for signing session cookies and other security features. Must be kept secret and be cryptographically random. See [[01-Flask-Core/Configuration]] and [[08-Security/Session-Security]].

**Session**
A mechanism for storing user-specific data across multiple requests. Flask supports client-side sessions (signed cookies) and server-side sessions. See [[00-Foundations/Cookies-Sessions]] and [[01-Flask-Core/Sessions]].

**Session Hijacking**
An attack where an attacker steals a user's session identifier to impersonate them. See [[08-Security/Session-Security]].

**Shell (Flask)**
An interactive Python session preloaded with your Flask application context. Accessed via `flask shell`. See [[01-Flask-Core/Flask-CLI]].

**Signal**
A notification system in Flask that allows decoupled components to react to events (e.g., `template_rendered`, `request_started`). See [[10-Advanced/Signals]].

**SQL (Structured Query Language)**
A standard language for managing and querying relational databases. See [[03-Database/SQL-Fundamentals]].

**SQLAlchemy**
The most popular Python SQL toolkit and Object-Relational Mapping (ORM) library. Provides a full suite of well-known enterprise-level persistence patterns. See [[03-Database/SQLAlchemy-ORM]] and [[Appendix/SQLAlchemy]].

**SQL Injection**
A code injection attack where malicious SQL statements are inserted into application queries through user input. See [[08-Security/SQL-Injection]].

**SSL (Secure Sockets Layer)**
The predecessor to TLS. The terms are often used interchangeably, though SSL is technically deprecated. See [[00-Foundations/TLS-HTTPS]].

**Static Files**
Files served directly to the client without server-side processing: CSS, JavaScript, images, fonts. Flask serves them from the `static/` folder. See [[01-Flask-Core/Static-Files]].

## T

**TCP (Transmission Control Protocol)**
A connection-oriented, reliable transport protocol that ensures data arrives completely and in order. The foundation of HTTP communication. See [[00-Foundations/TCP-UDP]].

**Template**
An HTML file with special syntax that allows dynamic content insertion. Flask uses Jinja2 as its template engine. See [[01-Flask-Core/Templates]] and [[02-Jinja2/Jinja2-Overview]].

**Template Context**
The set of variables available in a template during rendering. Includes variables passed from the view and those added by context processors. See [[02-Jinja2/Jinja2-Overview]].

**Template Inheritance**
A Jinja2 feature that allows a base template to define blocks that child templates can override. Enables consistent page layouts. See [[02-Jinja2/Template-Inheritance]].

**Thread-Local Storage**
A programming pattern where data is stored in a way that each thread sees only its own copy. Flask uses this for `request`, `session`, `g`, and `current_app`. See [[01-Flask-Core/Request-Context]].

**TLS (Transport Layer Security)**
A cryptographic protocol that provides secure communication over a network. The modern successor to SSL. See [[00-Foundations/TLS-HTTPS]].

**Token (CSRF)**
A random, unguessable value embedded in forms to prevent CSRF attacks. Verified by the server on form submission. See [[08-Security/CSRF-Protection]].

**Tuple**
An immutable ordered sequence of elements in Python. Flask routes can return tuples of `(body, status_code)` or `(body, status_code, headers)`.

## U

**UDP (User Datagram Protocol)**
A connectionless, unreliable transport protocol. Faster than TCP but does not guarantee delivery or order. Used for DNS queries, streaming video, and online gaming. See [[00-Foundations/TCP-UDP]].

**URL (Uniform Resource Locator)**
The address of a resource on the internet. Format: `scheme://host:port/path?query#fragment`. See [[00-Foundations/HTTP]].

**URL Converter**
A Flask feature that converts URL path segments to Python types. Built-in converters: `string`, `int`, `float`, `path`, `uuid`. Custom converters can be created. See [[01-Flask-Core/URL-Converters]].

**URL Endpoint**
See Endpoint.

**URL Prefix**
A string prepended to all routes in a Blueprint. Useful for grouping related routes under a common path. See [[06-Blueprints/Blueprints]].

**User Agent**
A string in the HTTP request headers that identifies the client software (browser, operating system). Format: `Mozilla/5.0 (Windows NT 10.0; Win64; x64)...`.

## V

**Venv (Virtual Environment)**
An isolated Python environment that allows different projects to have different dependencies without conflicts. See [[01-Flask-Core/Flask-Architecture]].

**View (MVC)**
In Flask, a Python function that handles a request and returns a response. Often called a "view function." See [[01-Flask-Core/Routing]].

**View (Template)**
In Django-style terminology, the presentation layer. In Flask, Jinja2 templates serve this role. See [[01-Flask-Core/Templates]].

**VPS (Virtual Private Server)**
A virtual machine sold as a service, providing dedicated server resources at a lower cost than physical servers. Common for hosting Flask applications. See [[07-Deployment/Linux-Server]].

## W

**Web Server**
Software that serves content to clients over HTTP. Examples: Nginx, Apache, IIS. In development, Flask's built-in server is used, but it is not suitable for production. See [[07-Deployment/Deployment-Overview]].

**WebSocket**
A protocol providing full-duplex, bidirectional communication over a single TCP connection. Enables real-time features like chat and live updates. See [[10-Advanced/WebSockets]].

**Werkzeug**
A comprehensive WSGI utility library that powers Flask. Provides request and response objects, routing, development server, and debugging. See [[Appendix/Werkzeug]].

**WSGI (Web Server Gateway Interface)**
A Python standard (PEP 3333) that defines how web servers communicate with web applications. Flask implements WSGI on the application side; Gunicorn implements it on the server side. See [[01-Flask-Core/Flask-Architecture]].

**WTForms**
A flexible forms validation and rendering library for Python. Flask-WTF integrates WTForms with Flask. See [[04-Authentication/WTForms]] and [[Appendix/WTForms]].

## X

**XSS (Cross-Site Scripting)**
A security vulnerability where an attacker injects malicious scripts into web pages viewed by other users. Prevented by escaping output and validating input. See [[08-Security/XSS-Prevention]].

## Z

**ZIP File**
A compressed archive file format. Flask apps can be distributed as ZIP files, and Python can import modules directly from ZIP archives.

---

*Return to [[README]] | Browse the [[INDEX]]*