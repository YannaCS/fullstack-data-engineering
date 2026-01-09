# Unit Testing, CI/CD, and Deployment for FastAPI Note App

**Description:**

Extend the built the FastAPI "note app" in a previous assignment (see session-11-fast-api-2) with automated unit tests, configure a CI workflow with GitHub Actions, and deploy your app to a public service.

### Requirements

1. **Unit Tests**
    - Write unit tests that cover at least the following:
        - Models: Test creation of `User` and `Note` objects and their relationships.
        - API Endpoints: Test the main CRUD routes (create, read, update, delete notes).
        - Edge Cases: Try invalid input and assert error handling (e.g., duplicate users, unauthorized access).
    - Use `pytest` as your testing framework.
    - Aim for at least **80% code coverage**. Check coverage with `pytest-cov`.

2. **CI with GitHub Actions**
    - Create a `.github/workflows/ci.yaml` workflow file that does the following on every push and pull request:
        - Set up Python.
        - Install dependencies.
        - Run the tests and report coverage.
    - Ensure the workflow fails if tests fail or if coverage drops below your threshold.

3. **Deployment**
    - Deploy your FastAPI app to a public PaaS of your choice. You may use:
        - **Railway** (https://railway.app)
        - **Render** (https://render.com)
        - **Fly.io** (https://fly.io)
        - Or similar free service.
    - The service must be accessible via a public HTTP endpoint.
    - Use secrets for database credentials/API keys in your CI workflow.
