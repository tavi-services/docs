"""Build the published API reference spec from Tavi's backend OpenAPI snapshot.

Usage:
    python3 scripts/build_openapi.py <path-to-monorepo>/backend/openapi.json

Keeps only the client API routes a client API key reaches (mirrors
`CLIENT_API_KEY_ROUTES` in the backend's `app/auth.py`), the schemas they
reference, and the API key security scheme. Operation descriptions are
dropped (they are written for Tavi engineers); the guide pages carry the
prose. Writes `api-reference/openapi.json`.
"""

import json
import sys
from pathlib import Path

# (path, method) pairs published in the reference, with the sidebar group and
# the summary shown under it. Keep in step with CLIENT_API_KEY_ROUTES (spend is
# left out of the work-order docs on purpose).
ROUTES: dict[tuple[str, str], tuple[str, str]] = {
    ("/api/v1/jobs/client/", "post"): ("Work orders", "Create a work order"),
    ("/api/v1/jobs/client", "get"): ("Work orders", "List work orders"),
    ("/api/v1/jobs/client/{job_id}", "get"): ("Work orders", "Get a work order"),
    ("/api/v1/jobs/client/{job_id}/options/{letter}/approve", "post"): (
        "Work orders",
        "Approve an option",
    ),
    ("/api/v1/attachments/upload/job/{job_id}", "post"): (
        "Photos and files",
        "Upload a photo or file",
    ),
    ("/api/v1/locations/client/", "post"): ("Sites", "Create a site"),
    ("/api/v1/locations/", "get"): ("Sites", "List sites"),
    ("/api/v1/trades/", "get"): ("Trades", "List trades"),
}

# Query parameters only Tavi staff may send; partners never need them.
STAFF_ONLY_PARAMS = {"org_id", "organization_id"}

# Request fields used only by Tavi's own apps.
INTERNAL_FIELDS = {"ai_chat_tool_use_id"}

# Response fields the backend withholds from API key callers (always null for
# them), so the reference leaves them out.
WITHHELD_FIELDS = {("ClientJobDetailResponse", "pipeline")}

# Public descriptions for the schemas a partner reads. The backend's own
# schema docstrings are written for Tavi engineers, so every schema not listed
# here is published without a description.
SCHEMA_DESCRIPTIONS = {
    "ClientJobCreateRequest": "A new work order.",
    "ClientSiteContactCreateRequest": "The person at the site Tavi coordinates the visit with.",
    "ClientJobResponse": "A work order as it appears in a list.",
    "ClientJobDetailResponse": (
        "A work order with its sourcing progress, quotes, visits and sign-off evidence. "
        "Subcontractor identities are never included; Tavi is the contracted provider."
    ),
    "ClientEscalationContactCreateRequest": (
        "Who Tavi escalates to when the site contact can't decide, such as a facility manager."
    ),
    "ClientOptionApproveRequest": (
        "The option's terms as you read them: pre_tax_amount, tax_amount and scope_of_work "
        "from the option. Tavi refuses the approval if any of them changed since."
    ),
    "ClientOptionApproveResponse": "The approved option and when it was approved.",
    "ClientOptionSummary": "One anonymized provider option and its quote, once published.",
    "ClientAwardedOption": "The option that was awarded, with its price and payment schedule.",
    "ClientJobVisitReadResponse": (
        "A site visit or work visit, with arrival and departure times, who signed off, "
        "and sign-off photos."
    ),
    "ClientLocationCreate": "A new site. Tavi geocodes the address.",
    "LocationResponse": "A site.",
    "LocationSummary": "The site a work order is at.",
    "FileResponse": "A stored photo or file. download_url works without an API key for at least 30 days.",
    "JobStatus": (
        "DRAFT: received, Tavi is reviewing it. ACTIVE: Tavi is sourcing, scheduling or doing "
        "the work. SETTLEMENT: work done, payment processing. COMPLETED: closed. "
        "CANCELLED: cancelled."
    ),
}

# Public descriptions for parameters and fields whose backend text describes
# Tavi's own apps.
PARAM_DESCRIPTIONS = {
    "scope": (
        "'assigned' (default): work orders at sites your account is on the team for. "
        "'all': every work order in your organization."
    ),
    "location_id": "Only work orders at this site.",
    "asset_id": "Only work orders about this piece of equipment.",
    "status": "Only work orders in this status.",
}
FIELD_DESCRIPTIONS = {
    ("FileResponse", "download_url"): (
        "Link to the file's content. Works without an API key and stays valid for "
        "at least 30 days; read the work order again for a fresh link."
    ),
}


def collect_refs(node: object, found: set[str]) -> None:
    """Add every `#/components/schemas/<name>` referenced under `node`."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            found.add(ref.rsplit("/", 1)[1])
        for value in node.values():
            collect_refs(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_refs(value, found)


def main() -> None:
    """Filter the snapshot named on the command line into the published spec."""
    source = json.loads(Path(sys.argv[1]).read_text())
    paths: dict[str, dict] = {}
    for (path, method), (tag, summary) in ROUTES.items():
        operation = dict(source["paths"][path][method])
        operation["summary"] = summary
        operation["tags"] = [tag]
        operation.pop("description", None)
        operation["parameters"] = [
            p
            for p in operation.get("parameters", [])
            if p.get("name") not in STAFF_ONLY_PARAMS
            and p.get("in") != "header"  # the key goes in the security scheme
        ]
        for param in operation["parameters"]:
            if param["name"] in PARAM_DESCRIPTIONS:
                param["description"] = PARAM_DESCRIPTIONS[param["name"]]
        operation["security"] = [{"ApiKey": []}]
        paths.setdefault(path, {})[method] = operation

    # Pull in referenced schemas until the set stops growing. Withheld fields
    # go first, so a schema only they reference isn't published.
    schemas = source["components"]["schemas"]
    for schema_name, field in WITHHELD_FIELDS:
        schemas[schema_name].get("properties", {}).pop(field, None)
        if field in schemas[schema_name].get("required", []):
            schemas[schema_name]["required"].remove(field)
    needed: set[str] = set()
    collect_refs(paths, needed)
    while True:
        before = len(needed)
        for name in list(needed):
            collect_refs(schemas[name], needed)
        if len(needed) == before:
            break
    published = {}
    for name in sorted(needed):
        schema = json.loads(json.dumps(schemas[name]))
        for field in INTERNAL_FIELDS:
            schema.get("properties", {}).pop(field, None)
        schema.pop("description", None)
        if name == "JobStatus":
            # Tavi's internal parking state; the client API reports it as ACTIVE.
            schema["enum"] = [v for v in schema["enum"] if v != "INACTIVE"]
        if name in SCHEMA_DESCRIPTIONS:
            schema["description"] = SCHEMA_DESCRIPTIONS[name]
        for (schema_name, field), text in FIELD_DESCRIPTIONS.items():
            if schema_name == name and field in schema.get("properties", {}):
                schema["properties"][field]["description"] = text
        published[name] = schema

    spec = {
        "openapi": source["openapi"],
        "info": {"title": "Tavi Client API", "version": "1.0"},
        # Same hosts as quickstart.mdx: prod, then the demo backend the sandbox key runs on.
        "servers": [
            {"url": "https://api.trytavi.com", "description": "Production"},
            {"url": "https://api.demo.trytavi.com", "description": "Sandbox"},
        ],
        # Sidebar groups in ROUTES order.
        "tags": [{"name": tag} for tag in dict.fromkeys(t for t, _ in ROUTES.values())],
        "paths": paths,
        "components": {
            "schemas": published,
            "securitySchemes": {
                "ApiKey": {"type": "apiKey", "in": "header", "name": "X-Tavi-API-Key"}
            },
        },
    }
    out = Path(__file__).resolve().parent.parent / "api-reference" / "openapi.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"Wrote {out} ({len(paths)} paths, {len(published)} schemas)")


if __name__ == "__main__":
    main()
