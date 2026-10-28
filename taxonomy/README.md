# Category rules

The catalogue contains 196 activities and nine Business Characteristics. Every record has `kind: activity` or `kind: characteristic`; all entries are part of the current draft. The `active` and `proposed` editorial statuses do not imply endorsement or adoption.

## Classification principles

**Category necessity:** Add a category only when an existing activity, or a combination of up to three activities, cannot reasonably describe the business.

**Buyer-focused classification:** Optimise for buyers searching for businesses, not brokers advertising them.

These guide activities, definitions, aliases and characteristics. Different terminology usually calls for an alias; a model already covered by characteristics does not need a combined activity. A genuine new activity must meet the [contribution criteria](../CONTRIBUTING.md#category-proposals).

## Select activities

A listing requires **1 to 3 business activities**. Choose what the business actually does, using the definitions. Three is an absolute maximum, not a recommendation. Avoid broad/specialist duplicates or loosely related activities. Groups help browsing; selections may cross groups.

Examples include Cafes and Coffee Shops + Bakery, or IT Support and Managed Services + Cybersecurity when both are substantial activities.

## Optional Business Characteristics

A listing may also have **0 to 3 characteristics**, independently of its activities. Characteristics are optional metadata, not additional business activities. They cannot supply a missing activity. Providers may implement all, some or none of them. Unsupported characteristics can be ignored by a receiver without invalidating an otherwise valid activity classification; never treat them as industry activities.

| ID | Characteristic | Meaning |
| --- | --- | --- |
| c0260 | Franchise | Operates under a franchise agreement. |
| c0261 | Home Based | Core operation principally based at a residential home. |
| c0262 | Online Operation | Online channels are central to the core business. |
| c0263 | Mobile Operation | Core delivery travels to customers or uses a mobile unit. |
| c0264 | Relocatable | The operating base can move while retaining the core business. |
| c0265 | Business with Property | Ownership of operating property is included in the sale. |
| c0266 | Owner Operated | Owner actively works in day-to-day operations. |
| c0267 | Under Management | Manager runs day-to-day operations; owner primarily oversees. |
| c0268 | Premises Based | Core operation uses dedicated leased or owned premises. |

Use the full definitions and actual business details. Online Operation can combine with Premises Based; using premises does not mean property is included. Owner Operated and Under Management can coexist where responsibilities support both. Home-based, online or mobile operation does not establish Relocatable.

## Aliases and search

Every JSON category includes `aliases: [{"alias": "...", "note": "..."}]`, or `[]` when none apply. [aliases.csv](aliases.csv) is the editable source; the exporter joins it to [categories.csv](categories.csv) by ID.

Aliases are search vocabulary, including alternate names, narrower business terms and contextual phrases. Use them when the underlying activity is unchanged, never to disguise a genuinely different activity. They do not establish equivalence or select a category automatically. An exact ambiguous term such as pizza shop can suggest both Restaurant and Takeaway Food.

Exact IDs take priority; exact names and aliases exclude longer partial matches. Thus online business suggests Online Operation, while online business with premises suggests both Online Operation and Premises Based. Without exact matches, search uses word prefixes, then description/group fallback. Case, Unicode width, HTML entities and punctuation are normalised; short AI/IT-style terms match whole words. Brand search terms imply no appointment or endorsement.

## Stable IDs and files

[categories.json](categories.json) is generated from the category and alias CSVs. Its catalogue identity and version apply to all embedded records. Use `kind`, rather than group position or label text, to distinguish activities and characteristics.

Keep IDs for unchanged meanings, including label corrections or group moves. A changed meaning requires a new ID; never reuse an ID. [retired.csv](retired.csv) is a small non-selectable ID ledger with optional replacement IDs. It prevents reuse, not automatic selection.

Catalogue data and selection-constraint changes require a version change; editorial or integration documentation clarifications alone do not. [Generate and check the export](../CONTRIBUTING.md#checks) after editing the sources.
