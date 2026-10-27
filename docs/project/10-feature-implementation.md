# 10 · Feature implementation and acceptance

| Feature | Implementation | Acceptance evidence |
|---|---|---|
| Expanded data | 5,000 fictional rows, 8 subjects, 10 cohorts; manifest and seeded generator | Unique IDs, row count, value ranges and dynamic averages checked |
| CSV analysis | Three base subjects plus up to 9 additional score columns | Original regression and expanded-data tests |
| Public exploration | Dropdowns, reset, chart values, histogram, search, pagination | Real-data and eight-subject dashboard tests |
| Accounts | Django session login/logout and password change | Login, logout, redirect and password-hash tests |
| Private records | Owner foreign key checked in querysets | Cross-user read/write/delete denied |
| Score entry | Subject choice and integer 0–100 validation | Form/API and database constraint tests |
| API access | Sessions plus scoped read-only bearer tokens | CSRF, expiry, revocation and overposting tests |
| Abuse controls | Rate buckets, body/page/search bounds | 429, 413 and input-bound tests |
| Integration | Read-only agents and MCP stdio tools | Actual HTTP API and MCP handshake/tool-call test |

## Data expansion policy
The original file is preserved unchanged. New fictional scores are not attached to its real-looking rows. Synthetic background labels are sampled independently from synthetic ability; the data must not support claims about demographic groups or educational outcomes. A single mean is an exploration aid, not an educational decision rule.

## Further work
Dataset provenance, institutional roles and student-account mapping, attendance/term models, hosted deployment, MFA, mobile automation and calibrated statistical analysis need separate requirements and tests. They are not represented as completed features.
