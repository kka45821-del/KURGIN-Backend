# KURGIN Backend Security Checklist

## Secrets

- [ ] No API keys in public frontend.
- [ ] No API keys in GitHub commits.
- [ ] Secrets stored only in environment variables or secrets manager.
- [ ] Separate secrets for dev/staging/prod.

## Auth

- [ ] Passwords hashed with Argon2id or bcrypt.
- [ ] Minimum password length enforced.
- [ ] Login rate limiting enabled.
- [ ] Refresh tokens hashed in database.
- [ ] Refresh token cookie is HttpOnly, Secure, SameSite=Lax or Strict.
- [ ] Access token short-lived.
- [ ] Logout revokes refresh session.

## Authorization

- [ ] Role checks performed server-side.
- [ ] Admin endpoints require admin role.
- [ ] Partner prices never sent to public anonymous frontend.
- [ ] Workspace collections scoped by owner_user_id.
- [ ] Reports scoped by owner user or explicit workspace access.

## Payments

- [ ] Payment webhooks verify provider signature.
- [ ] Payment status stored in database, not localStorage.
- [ ] Guest checkout links payment to verified email or claim token.
- [ ] Plan access is derived from payment/user_plan records.

## API

- [ ] CORS restricted to approved origins.
- [ ] HTTPS only.
- [ ] Request body size limits.
- [ ] Input validation on all endpoints.
- [ ] Audit logs for admin changes.
- [ ] Error responses do not leak secrets or stack traces.

## Data

- [ ] Personal data minimization.
- [ ] Client cards are private Workspace data.
- [ ] Object Storage URLs are signed or protected where needed.
- [ ] Backups enabled for production database.

## Formula

- [ ] Formula code not exposed in frontend.
- [ ] Formula API protected with server-side access control.
- [ ] Public catalog shows only precomputed/public score values.
