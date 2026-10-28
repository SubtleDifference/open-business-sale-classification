# Interoperability and integration

Open Business Sale Classification is a common reference between systems with different internal categories. A shared ID carries the meaning of the originating classification; each receiver decides how to represent it internally. Neither party must adopt the other's names, groups or internal codes.

## Sender to receiver

An upload provider or CRM can adopt shared activity IDs directly, or map its own categories to them while retaining its user-facing terminology. Where agreed, it includes the shared IDs when exchanging listings.

Each advertising portal can maintain its own shared-ID-to-local-category mapping. It keeps its browsing structure, internal IDs and acceptance rules. A receiver-maintained mapping can serve multiple supporting upload providers, reducing the need for each sender to recreate the portal's full classification structure.

For the shared activity `c0053 = Cafes and Coffee Shops`:

| System | Representation |
| --- | --- |
| Sender | Maps its own cafe classification to shared ID c0053. |
| Portal A | Maps c0053 to its existing Cafes category. |
| Portal B | Maps c0053 to its Food and Hospitality / Cafes classification. |
| Portal C | Maps c0053 to its own internal category code. |

These are conceptual examples, not verified mappings for real portals. A shared ID must never be assumed to equal a portal's internal ID or substituted for an expected portal code without agreement.

## Mapping rules

- Keep shared-ID meanings stable. Local labels and browsing groups may differ.
- Many shared activities can map to one broader local category.
- Mapping a broad shared activity to a narrower local category may require further business details. Preserve ambiguity or seek clarification; do not silently choose an arbitrary destination.
- Record the catalogue identity/version used by a mapping, and make the version available through the agreed exchange or configuration.
- Receiver-specific validation governs acceptance and local representation; it does not redefine a shared ID.
- Mappings are implementation-specific and may remain private. A portal is not obliged to publish them.

## Optional characteristics

A listing requires 1 to 3 activities and may independently have 0 to 3 characteristics. Characteristics provide operating or sale information for search and filtering without increasing industry-activity selections.

For example, Cafes and Coffee Shops (`c0053`) can carry Franchise (`c0260`) and Under Management (`c0267`). A portal maps the activity to its cafe category and may expose the characteristics as separate filters.

A receiver may support all, some or none of the characteristics. Unsupported characteristics can be ignored without invalidating an otherwise valid activity classification. Do not turn them into industry categories or create combined activities such as Franchise Cafes.

## Agree the exchange

Shared IDs alone do not establish compatibility. Sender and receiver must agree on the exchanged format, supported catalogue version, activity mapping, characteristic support and validation behaviour.

The catalogue supplies definitions and stable identifiers, not a transport protocol. Existing APIs, XML feeds and other protocols can continue. If both parties support exchanging shared IDs, use them as agreed; otherwise existing portal-specific mappings and formats remain valid. No new feed specification, hosted API or integration service is required.

## Read one file

Use a local copy of [categories.json](../taxonomy/categories.json). It includes catalogue identity/version metadata and `groups[].categories[]`. Each record has `id`, `name`, `kind`, editorial `status`, `description` and embedded `aliases` with contextual notes. Use `kind` to distinguish activities from optional characteristics.

From the repository root:

```python
import json
from pathlib import Path

catalogue = json.loads(Path("taxonomy/categories.json").read_text(encoding="utf-8"))
by_id = {c["id"]: c for g in catalogue["groups"] for c in g["categories"]}
takeaway = by_id["c0064"]
print(takeaway["name"])
print([a["alias"] for a in takeaway["aliases"]])
```

CSV consumers can read [categories.csv](../taxonomy/categories.csv) and join [aliases.csv](../taxonomy/aliases.csv) on `category_id`. CSV files are editable sources; JSON is generated.

## Validate or search locally

```text
python tools/lookup.py --activities c0053 c0051 --characteristics c0260 c0267
python tools/lookup.py --search "pizza shop"
```

Omit `--characteristics` where unused. Validation rejects duplicate, unknown/retired or wrong-kind IDs. It never infers activities from characteristics. Results include `catalogueId`, `version`, `valid`, `activities`, `characteristics` and `issues`. Exit status is 0 for valid selections, 1 for invalid selections with JSON preserved, and 2 for usage/file errors.

Search returns candidates and contextual `matchedAliases`. Exact matches exclude less precise partial matches; legitimate ambiguous matches remain choices. Neither local validation nor a search result establishes receiver acceptance.
