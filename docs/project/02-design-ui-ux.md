# 02 · Design and UI/UX

## Information architecture
The public root is a clearly labelled synthetic demonstration. A prominent workspace link leads to login and then the private record list. The private area links back to the demo and to password change; logout is a POST form. Administration is a separate superuser-only route.

## Screen specification
- Demo: explanatory synthetic-data notice; five dropdowns and reset; count, average, pass rate and top subject; group averages with sample sizes; subject averages; score histogram; searchable table with all discovered subject columns.
- Login: labelled username/password fields, CSRF field, generic invalid-credentials response and an explicit note that accounts are provisioned locally.
- Workspace: pseudonymous code/cohort form; validation errors adjacent to fields; twenty-five records per page; score-edit links.
- Score editor: existing subject scores, subject dropdown and whole-number score field constrained to 0–100.

## Interaction and accessibility
Dropdowns affect the whole demo; search affects the table only. Reset clears both. Empty results show an explanation; failed CSV loading shows an alert. Search and grouping have accessible labels. Charts have adjacent numeric values; data can also be inspected in tables. Small screens stack summary cards and scroll wide tables horizontally. Keyboard focus uses browser-native controls.

## Boundaries and follow-up
The private workspace never substitutes demo data when authorization fails. No real names or contact fields are requested. Existing chart bars need inline numeric styling under the CSP; scripts do not allow inline execution. A full assistive-technology audit and mobile-browser automation remain follow-up work; no WCAG conformance certification is claimed.
