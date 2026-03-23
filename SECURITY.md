# GTS Logistics – Security Policy

## 1. Introduction

This Security Policy defines the security requirements and operational controls for the GTS Logistics Platform, covering backend services, frontend applications, AI modules, and infrastructure.
All contributors, developers, and operators must comply with this policy.

2. Reporting Security Vulnerabilities

We strongly encourage responsible disclosure.

Primary contact: <security@gabanilogistics.com>

Acknowledgment: within 72 hours

Fix coordination: within 7–14 days depending on severity

Do not disclose vulnerabilities publicly until an official advisory or patch is released.

3. Secrets & Credential Management
Prohibited

Committing secrets, tokens, DB passwords, API keys, or OAuth credentials to Git.

Storing secrets inside source code, JS bundles, or frontend builds.

Required

Use environment variables via:

.env (local)

.env.production (deployment)

.env.example (template only)

.env files must always be included in .gitignore

Use secret rotation every 90 days or immediately upon suspected breach.

Production credentials must be stored in a secure vault (e.g., Render Secrets, AWS Secrets Manager).

4. Dependency Security
Automated Monitoring

Enable and enforce:

Dependabot for Python (pip) & Node (npm)

GitHub Advanced Security features:

Dependabot Alerts

Secret Scanning

Code Scanning (CodeQL)

Pull Request Requirements

Every PR must:

Pass CI linting (black, flake8, eslint)

Pass unit tests

Pass:

pip-audit
npm audit --production

Contain no new high-severity CVEs in dependencies.

5. Authentication & Authorization
JWT Token Requirements

Short-lived JWT access tokens

Default: 15–30 minutes

Refresh tokens: 7–30 days

Include:

sub → user ID

role → RBAC role

kid → Key ID (for rotation)

exp → expiration timestamp

Key Rotation

Maintain a JWKS structure with multiple active keys.

Rotate signing keys every 90–180 days.

Hashing

Passwords must only use:

pbkdf2_sha256 (current DB standard)
or

bcrypt for new accounts
Configured via CryptContext.

RBAC Roles

Defined roles:

admin — full operational access

broker — freight & loadboard operations

ops — dispatch & field operations

customer — limited portal access

Enforced via backend dependency:

Depends(require_roles(["admin", "ops"]))

6. API Security

All REST endpoints must require authentication except explicitly public routes.

CORS must be restricted to approved domains.

Rate limiting is enabled:

100 requests / minute per IP

Sensitive operations must require:

Fresh access token

Valid role

Optional 2FA for admin endpoints

Headers

Always return:

X-Frame-Options: DENY

X-Content-Type-Options: nosniff

Strict-Transport-Security: max-age=63072000

Content-Security-Policy (backend and frontend)

7. Data Protection
Encryption

All traffic must use HTTPS/TLS 1.2+

PostgreSQL connections must use:

sslmode=require

Passwords are never logged.

PII Handling

Minimize Personally Identifiable Information (PII)

Delete or anonymize user data upon request

Logs must not contain sensitive data

8. Logging & Monitoring

Logs must:

Be centralized (Render Logs / Cloud Logs)

Never include passwords or secrets

Monitor for:

Failed login attempts

JWT invalidation

Suspicious API usage patterns

9. Secure Development Lifecycle (SDLC)
Every new feature must include:

Threat modeling (STRIDE)

Security review

Automated tests (unit + integration)

Code review by at least one senior developer

Static Code Analysis

Mandatory CodeQL scan per PR

Dependency Locking

Backend: use requirements.txt with exact pinned versions

Frontend: use package-lock.json or pnpm-lock.yaml

10. Deployment Guidelines
Production Deployment Rules

Direct SSH access prohibited

Only automated CI/CD deploys allowed

.env.production variables configured in Render dashboard

Database credentials must never appear in logs

Backup Policy

Daily automated PostgreSQL backup retention: 7–30 days

Verify restore capability monthly

11. AI Security Considerations

For OpenAI + internal AI bots:

Disable AI in production unless OPENAI_API_KEY is configured

Enable request auditing for:

Finances

Load posting

Shipment data

Never allow direct SQL execution from bots

Validate and sanitize all AI outputs before use

12. Incident Response

If a breach is suspected:

Revoke compromised tokens & rotate secrets

Lock admin accounts temporarily

Review audit logs for root-cause analysis

Notify affected stakeholders within 48 hours

Patch and redeploy fixed version

13. Revision

This policy must be reviewed every 6 months

Updates require approval by:

CTO (Technical Lead)

Security Lead
