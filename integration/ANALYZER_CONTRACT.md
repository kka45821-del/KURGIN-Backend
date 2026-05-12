# Analyzer ↔ Backend Contract

## Current Analyzer role

Analyzer is the professional analytical app.
It can remain Streamlit during MVP.

## Future backend calls

Analyzer should use:

```txt
POST /auth/login
GET /auth/me
POST /access/check
POST /score/calculate
POST /reports
GET /reports
POST /payments/checkout
```

## Query parameters from Website

Analyzer may receive:

```txt
source=kurgin-diamonds
stone=KRD-100287
sku=KRD-100287
shape=Круг
carat=1.01
color=F
clarity=VS2
score=77
report=LG6123456789
lab=IGI
```

Analyzer must treat these as **untrusted client input**.
If exact data matters, Analyzer must fetch authoritative stone data from backend by SKU/report.

## Report persistence

When saving a report:

```json
{
  "report_level": "detailed",
  "payload": {
    "input": {},
    "result": {},
    "stone_ref": "KRD-100287"
  }
}
```

Backend decides whether the user may save the requested report level.
