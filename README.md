# Open Business Sale Classification

An open source classification reference for businesses for sale, providing shared business activities, optional characteristics and stable identifiers for interoperability between platforms.

**Draft open source classification initiative (`0.5.0-draft.1`).** No portal or industry-body endorsement is claimed.

The visual explorer starts at [index.html](index.html). Browse activities, read definitions and try a classification. See [local running instructions](viewer/README.md) and [GitHub Pages deployment steps](docs/github-pages.md).

## Classification principles

- **Category necessity:** Add a category only when an existing activity, or a combination of up to three activities, cannot reasonably describe the business.
- **Buyer-focused classification:** Optimise for buyers searching for businesses, not brokers advertising them.

These principles guide activities, definitions, aliases and Business Characteristics. See the [contribution criteria](CONTRIBUTING.md#category-proposals).

## Use the catalogue

Download [categories.json](taxonomy/categories.json) for 196 activities, nine optional Business Characteristics, definitions and search aliases in 20 browsing groups. Editable sources are [categories.csv](taxonomy/categories.csv) and [aliases.csv](taxonomy/aliases.csv).

Use each record's stable `id` and `kind`:

- **Activities: 1 to 3.** Describe what the business actually does. Three is a maximum, not a target.
- **Characteristics: 0 to 3, independently.** Optional operating or sale metadata; they do not consume activity selections or replace an activity.

Select only relevant entries supported by the business details. Providers may support all, some or none of the characteristics. See the [selection rules](taxonomy/README.md).

This example selects Cafes and Coffee Shops + Bakery, with Franchise + Under Management metadata:

```json
{
  "catalogueId": "urn:uuid:1747a70b-79ad-4fb1-92e0-ed19b20ce53d",
  "version": "0.5.0-draft.1",
  "activities": ["c0053", "c0051"],
  "characteristics": ["c0260", "c0267"]
}
```

## Exchange classifications

An upload provider can map its own categories to shared IDs; each receiving portal can map those IDs to its own categories. Both keep their names, groups and internal codes. Receiver-maintained mappings can serve multiple upload providers and may remain private.

Shared IDs do not establish a working integration. Sender and receiver must agree on format, catalogue version and classification behaviour. Existing APIs, XML feeds and portal-specific mappings can continue; no new protocol, paid software, hosted service or adopter registration is required. See the [interoperability and integration guide](docs/integration.md).

Optional local tools:

```text
python tools/lookup.py --search "pizza shop"
python tools/lookup.py --activities c0053 c0051 --characteristics c0260 c0267
```

Validation checks classification only; search suggests candidates without selecting one.

[Contribute](CONTRIBUTING.md), read the [review questions](docs/review-notes.md), or see [optional adoption records](ADOPTION.md). Licensed under [Apache 2.0](LICENSE); see [licensing](LICENSING.md).
