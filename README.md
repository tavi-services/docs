# Tavi Client API documentation

Client API documentation hosted by Mintlify.

- Public site: https://tavi-services-limited.mintlify.site/
- Dashboard: https://app.mintlify.com/tavi-services-limited/tavi-services-limited/publishes/overview
- Source: MDX pages, SVG diagrams in `images/`, configuration in `docs.json`, and a generated API reference in `api-reference/openapi.json`.

## Preview and validate

Run these commands from this repository:

```sh
npx --yes mint dev --port 10418
npx --yes mint validate
npx --yes mint broken-links
```

## Rebuild the API reference

```sh
python3 scripts/build_openapi.py <monorepo>/backend/openapi.json
```

## Publish

Push documentation changes to `main`. Check the dashboard for the connected branch build. If no build appears, click **Manual update** on the Publishes overview. Confirm a successful publish and check the public pages after each update.
