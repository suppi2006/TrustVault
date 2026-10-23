# TrustVault — Threat Model

## 1. Assets to Protect
- User accounts and password hashes
- Private uploaded documents
- User sessions and CSRF tokens
- Document ownership information
- Audit log records

## 2. Threats and Mitigations

| Threat | Mitigation | Remaining Risk |
|---|---|---|
| Another user tries to download a private document | The download route checks document ownership on the server | Sharing permissions are not implemented |
| Attacker uploads an unsupported file | File extensions are restricted | File content and MIME type are not fully validated |
| Attacker uploads a very large file | Upload size is limited to 5 MB | Other resource-exhaustion attacks may still be possible |
| Passwords are exposed from the database | Passwords are stored as hashes | Database and server access still need protection |
| Cross-site request forgery | CSRF tokens are checked on supported form submissions | All state-changing routes must be reviewed |
| Session compromise | HTTP-only cookies and SameSite settings are configured | Production cookie and secret-key settings need review |
| User activity cannot be investigated easily | Upload and download events are recorded in audit logs | A user-facing audit log viewer is not implemented |
| Uploaded files disappear after deployment restart | Current deployment uses local file/database storage | Persistent storage needs to be configured |

## 3. Security Tests Performed
- Registered and logged in with test accounts.
- Tested uploading and downloading a document.
- Tested access to another user's document; the request returned HTTP 404.
- Tested an unsupported `.exe` upload; the request returned HTTP 400.
- Tested a file larger than 5 MB; the request returned HTTP 413.

## 4. Known Limitations
- Role-based access and document-sharing workflows are not implemented.
- File content validation and malware scanning are not implemented.
- Login rate limiting and account lockout are not implemented.
- Audit events are recorded, but there is no audit log viewer.
- Production secret-key configuration and persistent storage require review.

## 5. Next Improvements
- Configure a strong secret key through environment variables.
- Review secure cookie settings for production HTTPS.
- Add file-content validation and additional security tests.
- Configure persistent storage for uploaded files and the database.
- Expand audit logging and add controlled access to audit records.