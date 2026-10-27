# Documentation project instructions

This repository contains Tavi’s public partner integration documentation, hosted by Mintlify. Pages use MDX with YAML frontmatter; configuration is in `docs.json`; diagrams are SVG assets in `images/`.

## Writing

- Write concise instructions for new readers, in active voice.
- Use generic partner terminology and sentence case headings.
- Tavi contacts customers directly for routine questions and visit coordination. Phone is required; email is optional.
- The partner application maintains key work-order activity through webhooks.
- Aim for an agreed rate card; record approval for additional scope or spending.
- Keep the short, flexible billing summary on the overview.
- Avoid revision commentary, repeated implementation disclaimers and contrasts with earlier versions.
- Do not publish a live API base URL or enable interactive API calls until partner access is ready.

## Checks and publishing

Run `npx --yes mint validate` and `npx --yes mint broken-links`. Inspect affected pages and diagrams in a browser. Pushing to `main` publishes the site; verify the deployment and live pages before reporting completion.
