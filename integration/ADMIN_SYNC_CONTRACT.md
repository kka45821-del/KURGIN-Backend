# Admin ↔ Backend Contract

## Admin role

Admin is internal. It should not be publicly linked in the main website navigation.

## Admin-managed entities

```txt
plans
prices
free access users
diamonds catalog
index data
academy content
information content
score coefficients / config references
workspace role approvals
```

## Required protected endpoints

```txt
GET /admin/audit
POST /admin/plans
POST /admin/diamonds/import
PATCH /admin/diamonds/{id}
PATCH /admin/users/{id}/roles
PATCH /admin/users/{id}/plans
POST /admin/index/publish
```

## Audit log rule

Every admin mutation must write to `admin_audit_logs`:

```txt
actor_user_id
action
target_type
target_id
before_payload
after_payload
ip_hash
created_at
```

## Security

Admin role is never granted by frontend state.
It is stored in `user_roles` and checked server-side.
