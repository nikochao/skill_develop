# TimeEdit selectors

- Student entry: `https://www.schema.uu.se/`
- Student landing page: `/uu/web/wr_student/`
- Schedule search: `/uu/web/wr_student/ri1Q4.html`
- Search type: `select[name="fancytypeselector"]`
- Course search input: `input[name="fftext"]`
- Search result container: `#objectsearchresult`
- Search candidates: `#objectsearchresult .searchObject`
- Show schedule button text: `Visa schema`

SSO returns to `/uu/web` after authentication, so navigate to the schedule
search path again after login completes.
