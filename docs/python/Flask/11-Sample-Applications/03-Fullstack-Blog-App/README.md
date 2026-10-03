# Flask 3.x Fullstack Blog Application

This is a complete, runnable Flask 3.x fullstack sample application demonstrating modern Flask practices:
- Application Factory pattern (`create_app()`)
- Pydantic/dataclasses configuration
- SQLAlchemy 2.0 declarative models
- Blueprints for modular routing (auth and blog)
- Pytest test suite with client fixtures

## Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run.py
   ```
   Or use the Flask CLI:
   ```bash
   flask --app run run --debug
   ```

## Running Tests

To run the test suite:
```bash
pytest
```
