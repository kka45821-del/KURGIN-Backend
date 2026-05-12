# Environment Variables

No real secrets are included in this package.

## Required

```env
APP_ENV=development
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost:5432/kurgin
JWT_SECRET=replace_with_strong_secret
JWT_ACCESS_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=30
CORS_ALLOWED_ORIGINS=https://kurgin-website.vercel.app,https://cvdrap.ru
PASSWORD_HASH_ALGORITHM=argon2id
```

## Formula API

```env
FORMULA_MODE=local
FORMULA_API_URL=
FORMULA_API_KEY=
```

`FORMULA_API_KEY` must never be exposed in frontend JavaScript.

## Payments

```env
PAYMENT_PROVIDER=placeholder
PAYMENT_WEBHOOK_SECRET=replace_with_provider_secret
PAYMENT_SUCCESS_URL=https://cvdrap.ru/profile/
PAYMENT_CANCEL_URL=https://cvdrap.ru/score/
```

## Object Storage

```env
OBJECT_STORAGE_ENDPOINT=
OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_ACCESS_KEY=
OBJECT_STORAGE_SECRET_KEY=
```

Storage keys must not be committed to GitHub.
