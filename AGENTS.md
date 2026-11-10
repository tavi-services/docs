# Documentation project instructions

This repository contains Tavi’s public client API documentation, hosted by Mintlify. Pages use MDX with YAML frontmatter; configuration is in `docs.json`; diagrams are SVG assets in `images/`.

## Writing

- Write concise instructions for new readers, in active voice, with sentence case headings.
- Document only what the API does today. Every field, status and error named on a page must exist in the backend (`tavi-services/monorepo`, `backend/openapi.json`).
- Tavi contacts the on-site contact directly by phone and text. Partners follow progress by polling; there are no status callbacks yet.
- Avoid revision commentary and contrasts with earlier versions.
- Do not publish a live API base URL or enable interactive API calls until partner access is ready.

## API reference

`api-reference/openapi.json` is generated. Rebuild it from the backend snapshot after any change to the client routes:

```sh
python3 scripts/build_openapi.py <monorepo>/backend/openapi.json
```

The script's `ROUTES` must match `CLIENT_API_KEY_ROUTES` in the backend's `app/auth.py`.

## Checks and publishing

Run `npx --yes mint validate` and `npx --yes mint broken-links`. Inspect affected pages and diagrams in a browser. Pushing to `main` publishes the site; verify the deployment and live pages before reporting completion.
