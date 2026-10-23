# AI Prompt and Development Log — TrustVault

This file records my actual development process. I used ChatGPT for guidance and tested the application myself.

## Entry 1 — 23 October 2026: Authentication and document access

- **What I asked:** Help me understand and build a Flask application with user registration, login, password hashing, CSRF protection, and secure document downloads.
- **What the AI suggested:** Flask routes, password hashing, session-based authentication, CSRF token validation, and checking document ownership before allowing downloads.
- **What I verified:** I ran the application and tested registration, login, document upload, and download. I also reviewed the document download route to understand how it checks the logged-in user's ownership.
- **What I learned:** Hiding a download link in the interface is not enough. The server must verify authorization for every download request.
- **Commit:** Add the actual Git commit URL after checking the relevant commit in my GitHub repository.

## Entry 2 — 23 October 2026: Testing document ownership and authorization

- **What I asked:** Help me test whether one registered user can download another user's private document.
- **What the AI suggested:** Test the download route while logged in as a different user and verify that the server checks document ownership.
- **What I tested:** I logged in with a second account and attempted to open the download URL for a document belonging to another account.
- **Actual result:** The application returned `404 Not Found` for the tested unauthorized download attempt.
- **What I learned:** Authorization must be checked on the server for each document request. A document ID or download URL must not grant access by itself.
- **Commit:** Add the actual Git commit URL if a relevant commit exists. Do not invent a commit link.


## Entry 3 — Audit trail and activity recording

- **What I asked:** Help me record document activity in TrustVault so that important actions can be traced.
- **What the AI suggested:** Store audit events in a database table with fields for the user, document, action, details, and timestamp.
- **What I implemented:** TrustVault records audit entries for document uploads and downloads in the `audit_logs` table.
- **What I verified:** I reviewed the upload and download routes to confirm that they call the audit logging function.
- **Current limitation:** The application does not yet provide a user-facing page to view audit logs. I have not completed a full audit-log security test.
- **What I learned:** Recording an event in a database is different from providing a secure, reviewable audit trail.
- **Commit:** Add the actual relevant Git commit URL if one exists. Do not invent a commit link.


## Entry 4 — File upload validation and size limits

- **What I asked:** Help me restrict uploaded documents to allowed file extensions and limit upload size.
- **What the AI suggested:** Check the filename extension against an allowlist and configure Flask's maximum request size.
- **What I tested:** I tested uploading an unsupported `.exe` file and a file larger than the configured 5 MB request limit.
- **Actual results:** The unsupported file was rejected with a 400 response, and the oversized request was rejected with a 413 response.
- **What I learned:** File extension checks and request-size limits are useful safeguards, but extension checks alone do not prove that a file's contents are safe.
- **Current limitation:** Actual file-content validation has not been implemented or verified.
- **Commit:** Add the actual relevant Git commit URL if one exists. Do not invent a commit link.

## Entry 5 — Deployment and configuration

- **What I asked:** Help me prepare my Flask application for deployment on Render.
- **What the AI suggested:** Add Gunicorn as the production application server, configure the start command, and set environment variables for deployment.
- **What I implemented:** I added Gunicorn to `requirements.txt`, configured the Render start command as `gunicorn app:app`, and configured a `SECRET_KEY` environment variable and secure session cookies.
- **What I verified:** The Render deployment started successfully, and the application's home page returned an HTTP 200 response.
- **What I learned:** A successful deployment does not by itself prove that the application is secure or that uploaded files and database records persist across restarts.
- **Current limitation:** Persistent storage and production security hardening still need review.
- **Commit:** Add the actual relevant Git commit URL if one exists. Do not invent a commit link.