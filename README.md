# Open Business Sale Classification (OBSC)

Open Business Sale Classification is an open source reference for classifying businesses for sale. It helps buyers discover relevant businesses and supports consistent data exchange between platforms.

**Current catalogue: draft `0.5.0-draft.1`.** Adoption is voluntary; no formal industry endorsement or established adoption is claimed.

## Explore the catalogue

**[Open the catalogue explorer](https://subtledifference.github.io/open-business-sale-classification/)**

Browse 196 business activities, explore nine optional Business Characteristics, search names and aliases, read definitions, and try creating an example classification with shared IDs.

## Use OBSC in your platform

- [Canonical JSON catalogue](taxonomy/categories.json) — activities, characteristics, definitions, embedded aliases and version metadata.
- [Category CSV](taxonomy/categories.csv) and [alias CSV](taxonomy/aliases.csv) — editable sources.
- [Interoperability and integration guide](docs/integration.md) — mapping, exchange examples and lookup tools.

Upload providers can adopt shared IDs or map existing categories to them. Advertising portals can map those IDs to their own categories. Neither needs to replace its existing names, codes or category structures.

Shared IDs do not establish a working integration: sender and receiver agree on supported formats, catalogue versions and mapping behaviour. Existing feeds and APIs can continue; no software purchase or hosted service is required.

## Contribute

Feedback and contributions are welcome from brokers, portals, industry organisations and software providers. Read the [contribution guidelines](CONTRIBUTING.md) and [draft review questions](docs/review-notes.md).

Subtle Difference is the original author and maintainer. Contributions are assessed using the same provider-neutral criteria.

## Classification principles

- **Category necessity:** Add a category only when an existing activity, or a combination of up to three activities, cannot reasonably describe the business.
- **Buyer discovery:** Optimise classification for buyers finding relevant businesses, not additional advertising exposure.

Select **1 to 3 business activities** describing what the business does, plus **0 to 3 optional Business Characteristics** describing how it operates or is offered for sale. The limits are independent: characteristics do not consume activity selections or replace an activity. Three is a maximum, not a target; select only entries supported by the business details.

Providers may support all, some or none of the characteristics. See the [full selection rules](taxonomy/README.md).

This example selects Cafes and Coffee Shops + Bakery, with Franchise + Under Management:

```json
{
  "catalogueId": "urn:uuid:1747a70b-79ad-4fb1-92e0-ed19b20ce53d",
  "version": "0.5.0-draft.1",
  "activities": ["c0053", "c0051"],
  "characteristics": ["c0260", "c0267"]
}
```

## Licensing

Licensed under [Apache 2.0](LICENSE), with attribution in [NOTICE](NOTICE). See the [licensing summary](LICENSING.md). No portal or industry-body endorsement is claimed.
