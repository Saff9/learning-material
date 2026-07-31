---
title: Web Technologies
description: HTML, CSS, and JavaScript — the three pillars of front-end development that every Flask developer needs to understand
chapter: 00-Foundations
tags:
  - html
  - css
  - javascript
  - frontend
  - web-technologies
  - foundations
difficulty: Beginner
prerequisites:
  - [[00-Foundations/Browser]]
  - [[00-Foundations/HTTP]]
---

# Web Technologies

> Flask generates HTML that browsers render. Understanding HTML, CSS, and JavaScript — even as a backend developer — enables you to build complete web applications, debug rendering issues, and collaborate effectively with frontend developers.

## Learning Objectives

After completing this chapter, you will be able to:

- Write semantic HTML that structures content meaningfully
- Style web pages with CSS using selectors, the box model, and layout systems
- Understand how JavaScript adds interactivity to web pages
- Use Flask's template system to generate dynamic HTML
- Debug common frontend issues using browser Developer Tools
- Integrate frontend frameworks with Flask backends

## HTML — HyperText Markup Language

HTML is the structural layer of the web. It defines the meaning and structure of content.

### Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Flask App</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    
    <main>
        <h1>Welcome</h1>
        <p>This is my Flask application.</p>
    </main>
    
    <footer>
        <p>&copy; 2024 My Flask App</p>
    </footer>
    
    <script src="/static/app.js"></script>
</body>
</html>
```

### Semantic HTML

Use semantic elements that describe their meaning to browsers and assistive technologies:

| Element | Purpose |
|---------|---------|
| `<header>` | Introductory content, navigation |
| `<nav>` | Navigation links |
| `<main>` | Primary content (one per page) |
| `<article>` | Self-contained content (blog post, comment) |
| `<section>` | Thematic grouping of content |
| `<aside>` | Tangentially related content (sidebar) |
| `<footer>` | Footer for section or page |
| `<figure>` / `<figcaption>` | Self-contained media with caption |
| `<time>` | Machine-readable dates/times |

> [!TIP]
> Semantic HTML improves accessibility (screen readers), SEO (search engines understand structure), and maintainability (code is self-documenting).

### Common HTML Elements

```html
<!-- Headings -->
<h1>Page Title</h1>
<h2>Section Heading</h2>
<h3>Subsection</h3>

<!-- Paragraphs and text -->
<p>A paragraph of text with <strong>bold</strong> and <em>italic</em> text.</p>

<!-- Links -->
<a href="https://example.com">External link</a>
<a href="/about">Internal link</a>
<a href="mailto:user@example.com">Email link</a>

<!-- Images -->
<img src="/static/photo.jpg" alt="Description for accessibility" width="400" height="300">

<!-- Lists -->
<ul>
    <li>Unordered item</li>
    <li>Another item</li>
</ul>

<ol>
    <li>First step</li>
    <li>Second step</li>
</ol>

<!-- Forms -->
<form action="/submit" method="POST">
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" required>
    
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
    
    <button type="submit">Submit</button>
</form>

<!-- Tables -->
<table>
    <thead>
        <tr><th>Name</th><th>Email</th></tr>
    </thead>
    <tbody>
        <tr><td>John</td><td>john@example.com</td></tr>
    </tbody>
</table>
```

### HTML Forms and Flask

Forms are the primary mechanism for submitting data to Flask applications:

```html
<form action="/register" method="POST">
    <!-- CSRF token (required with Flask-WTF) -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    
    <div>
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" 
               minlength="3" maxlength="20" required>
    </div>
    
    <div>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" 
               minlength="8" required>
    </div>
    
    <div>
        <label for="role">Role:</label>
        <select id="role" name="role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
        </select>
    </div>
    
    <div>
        <label>
            <input type="checkbox" name="newsletter" value="yes">
            Subscribe to newsletter
        </label>
    </div>
    
    <button type="submit">Register</button>
</form>
```

In Flask:

```python
from flask import request

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    newsletter = request.form.get('newsletter') == 'yes'
    # Process registration...
```

## CSS — Cascading Style Sheets

CSS controls the presentation of HTML — colors, fonts, layout, and animations.

### Selectors

```css
/* Element selector */
p { line-height: 1.6; }

/* Class selector */
.container { max-width: 1200px; margin: 0 auto; }

/* ID selector */
#header { background: #333; color: white; }

/* Descendant selector */
nav a { text-decoration: none; }

/* Child selector */
ul > li { margin-bottom: 0.5rem; }

/* Attribute selector */
input[type="text"] { border: 1px solid #ccc; }

/* Pseudo-class */
a:hover { color: #0066cc; }
button:disabled { opacity: 0.5; }

/* Pseudo-element */
p::first-line { font-weight: bold; }
```

### The Box Model

Every HTML element is a rectangular box:

```
+-------------------------------------------+
|                  Margin                   |
|   +-----------------------------------+   |
|   |              Border               |   |
|   |   +---------------------------+   |   |
|   |   |          Padding          |   |   |
|   |   |   +-------------------+   |   |   |
|   |   |   |     Content       |   |   |   |
|   |   |   |  (width x height) |   |   |   |
|   |   |   +-------------------+   |   |   |
|   |   +---------------------------+   |   |
|   +-----------------------------------+   |
+-------------------------------------------+
```

```css
.box {
    width: 300px;           /* Content width */
    padding: 20px;          /* Space inside border */
    border: 2px solid #333; /* Border */
    margin: 15px;           /* Space outside border */
    box-sizing: border-box; /* Width includes padding + border */
}
```

> [!TIP]
> Always use `box-sizing: border-box`. It makes width calculations intuitive — `width: 300px` means the visible box is 300px wide, including padding and border.

### Layout Systems

#### Flexbox (One-Dimensional Layout)

```css
.container {
    display: flex;
    justify-content: space-between;  /* Horizontal alignment */
    align-items: center;              /* Vertical alignment */
    gap: 1rem;                        /* Space between items */
    flex-wrap: wrap;                  /* Allow wrapping */
}

.item {
    flex: 1;           /* Grow to fill space */
    flex: 0 0 300px;   /* Fixed width, no grow/shrink */
}
```

#### Grid (Two-Dimensional Layout)

```css
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}
```

#### Common CSS Patterns for Flask Apps

```css
/* Reset and base styles */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
body { font-family: system-ui, sans-serif; line-height: 1.6; color: #333; }

/* Container */
.container { max-width: 1100px; margin: 0 auto; padding: 0 1rem; }

/* Flash messages */
.flash { padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
.flash.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.flash.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

/* Form styling */
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.25rem; font-weight: 500; }
.form-group input, .form-group select, .form-group textarea {
    width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px;
}
.form-group input:focus { outline: none; border-color: #0066cc; }

/* Button */
.btn { display: inline-block; padding: 0.5rem 1rem; background: #0066cc; 
       color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }
.btn:hover { background: #0052a3; }
```

## JavaScript

JavaScript adds interactivity to web pages. It runs in the browser, not on your Flask server.

### Core Concepts

```javascript
// DOM manipulation
document.getElementById('my-element').textContent = 'Hello';
document.querySelectorAll('.item').forEach(el => el.classList.add('active'));

// Event handling
document.getElementById('submit-btn').addEventListener('click', function(event) {
    event.preventDefault();  // Prevent form submission
    console.log('Clicked!');
});

// Fetch API - making HTTP requests from JavaScript
fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));

// Async/await
async function loadUser(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const user = await response.json();
        document.getElementById('username').textContent = user.name;
    } catch (error) {
        console.error('Failed to load user:', error);
    }
}
```

### JavaScript and Flask APIs

Modern Flask applications often serve as JSON APIs consumed by JavaScript frontends:

```javascript
// Submit a form via JavaScript (no page reload)
async function submitForm(formData) {
    const response = await fetch('/api/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()  // Flask-WTF CSRF protection
        },
        body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
        const error = await response.json();
        displayErrors(error);
        return;
    }
    
    const result = await response.json();
    window.location.href = `/posts/${result.id}`;
}
```

## Flask Template Integration

Flask uses Jinja2 for generating HTML (covered in depth in [[02-Jinja2/Jinja2-Overview]]):

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('index') }}">Home</a>
            {% if current_user.is_authenticated %}
                <a href="{{ url_for('profile') }}">{{ current_user.username }}</a>
                <a href="{{ url_for('logout') }}">Logout</a>
            {% else %}
                <a href="{{ url_for('login') }}">Login</a>
                <a href="{{ url_for('register') }}">Register</a>
            {% endif %}
        </div>
    </nav>
    
    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

## Common Mistakes

**Mistake: Using `<div>` for everything**
Use semantic elements (`<header>`, `<nav>`, `<main>`, `<article>`) instead of generic `<div>` soup.

**Mistake: Inline styles**
Avoid `style="..."` attributes. Use external stylesheets for maintainability.

**Mistake: Not validating HTML**
Invalid HTML causes unpredictable rendering. Use the W3C validator.

**Mistake: Forgetting `name` attributes on form inputs**
Flask's `request.form` uses the `name` attribute, not `id`. Without `name`, the data is not submitted.

## Best Practices

- Write semantic HTML for accessibility and SEO
- Use `box-sizing: border-box` universally
- Separate concerns: HTML for structure, CSS for presentation, JavaScript for behavior
- Use Flexbox and Grid for layouts instead of floats
- Make forms accessible with proper labels and ARIA attributes
- Test your application with keyboard-only navigation
- Use responsive design (`@media` queries) for mobile support

## Exercises

1. **Semantic HTML**: Take a webpage built with only `<div>` elements. Rewrite it using semantic HTML5 elements.

2. **CSS Layout**: Create a responsive two-column layout using CSS Grid that stacks on mobile.

3. **Fetch API**: Write JavaScript that fetches data from a Flask `/api/users` endpoint and displays it in an HTML table.

4. **Form Validation**: Implement client-side form validation using JavaScript before submitting to Flask.

## Quiz

**Question 1**: What is the difference between `<section>` and `<article>`?

**Question 2**: Why is `box-sizing: border-box` recommended?

**Question 3**: What is the difference between Flexbox and CSS Grid?

**Question 4**: Why must form inputs have a `name` attribute for Flask to receive their data?

**Question 5**: How does JavaScript's `fetch()` interact with your Flask backend?

## Interview Questions

1. "What is semantic HTML, and why is it important?"

2. "Explain the CSS box model. How does `box-sizing: border-box` change it?"

3. "A Flask form submits but `request.form` is empty. What are the likely causes?"

4. "How would you make a Flask application responsive for mobile devices?"

## Related Chapters

- Previous: [[00-Foundations/JSON]]
- [[02-Jinja2/Jinja2-Overview]] — Flask's template engine
- [[01-Flask-Core/Templates]] — Template rendering in Flask
- [[01-Flask-Core/Static-Files]] — Serving CSS and JavaScript

## Official Documentation References

- [MDN HTML Reference](https://developer.mozilla.org/en-US/docs/Web/HTML)
- [MDN CSS Reference](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [MDN JavaScript Reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [HTML Specification - WHATWG](https://html.spec.whatwg.org/)
- [CSS Specification - W3C](https://www.w3.org/Style/CSS/)

---

*Previous: [[00-Foundations/JSON]] | Next: [[01-Flask-Core/Flask-Architecture]]*