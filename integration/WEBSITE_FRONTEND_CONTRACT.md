# Website Frontend → Backend Contract

## Current public website role

The website remains public and static-first:

```txt
/diamonds/  public catalog surface
/score/     gateway to Analyzer
/workspace/ professional access page
/index/     public market index shell
```

## What frontend may store

Allowed in localStorage:

```txt
favorite stone IDs
compare list IDs
UI preferences
non-sensitive filters
```

Not allowed in localStorage:

```txt
access tokens
refresh tokens
passwords
admin flag
payment status
B2B prices
client names
private reports
```

## Frontend access check flow

```txt
1. User opens /workspace/
2. Frontend calls GET /auth/me if token exists
3. Frontend calls POST /access/check with resource=workspace
4. Backend responds allowed=true/false
5. Frontend shows correct public/private UI
```

## Diamonds → Analyzer flow

Current frontend URL handoff:

```txt
https://kurgin-analyzer...streamlit.app/?source=kurgin-diamonds&stone=KRD-...
```

Future backend-supported flow:

```txt
1. User selects stone in /diamonds/
2. Website calls POST /reports or POST /score/calculate if access allowed
3. Analyzer opens with report_id or stone_id
```

## Public score rule

The website can display precomputed score values from `diamonds-data.json` or public API.
It must not calculate protected formula logic in public JS.
