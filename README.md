# Tavi Partner API documentation

Partner integration documentation hosted by Mintlify.

- Public site: https://tavi-services-limited.mintlify.site/
- Dashboard: https://app.mintlify.com/tavi-services-limited/tavi-services-limited/publishes/overview
- Source: six MDX pages, five SVG diagrams in `images/`, configuration in `docs.json`.

## Preview and validate

Run these commands from this repository:

```sh
npx --yes mint dev --port 10418
npx --yes mint validate
npx --yes mint broken-links
```

## Publish

Push documentation changes to `main`. Check the dashboard for the connected branch build. If no build appears, click **Manual update** on the Publishes overview. Confirm a successful publish and check the public pages after each update.

## Editorial conventions

Use generic partner terminology. Tavi contacts customers directly for routine questions and scheduling. Phone is required; email is optional. The partner receives key work-order updates through webhooks. Pricing aims for an agreed rate card, with approval for additional scope or spending. Keep the billing summary on the overview.

The API reference describes the integration contract under discussion. Do not add a live API host or interactive requests until partner access is ready.
