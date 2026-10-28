# Contributing and maintenance

Contributions to Open Business Sale Classification are welcome from portals, brokers, CRM developers and upload providers through issues or pull requests, without commercial obligations. Identify any source or reuse restrictions.

## Editorial principles

- **Category necessity:** Add a category only when an existing activity, or a combination of up to three activities, cannot reasonably describe the business.
- **Buyer-focused classification:** Optimise for buyers searching for businesses, not brokers advertising them.

Apply both principles to activities, definitions, aliases and Business Characteristics. Keep the catalogue concise; buyer discovery takes precedence over advertising reach.

## Category proposals

Explain:

1. Which existing activities and definitions were considered.
2. Why those activities, individually or in combinations of up to three, are insufficient.
3. Why a search alias would not solve the terminology or discovery problem.
4. Whether an existing Business Characteristic addresses the distinction.
5. How the proposed activity would improve buyer search and discovery.

A new activity must be genuinely distinct, meaningfully different from existing activities, useful for buyer discovery and clear enough for different providers to classify comparable businesses consistently. It must be difficult to represent adequately through existing activities, combinations or aliases.

Do not add an activity merely because a business is unusual or niche, a broker wants more exposure, several existing activities are combined, an operating model is already covered by characteristics, a marketing term is popular, or one portal uses that terminology. Do not introduce narrow subcategories just to distinguish business types.

A niche can qualify when the activity is genuinely different and has meaningful buyer search intent. Frequency alone neither qualifies nor disqualifies it.

Use aliases where terminology differs but the underlying activity remains the same. Do not use aliases to disguise genuinely different activities. An ambiguous search phrase can offer several candidates with contextual notes, without claiming they are the same activity. Definition, alias and characteristic proposals should explain their buyer-search benefit and why existing wording or metadata is insufficient. Do not create combined activities such as Franchise Cafes or Cafes Under Management.

## Maintenance and decisions

Subtle Difference is the original author and maintainer, responsible for reviewing and merging changes. Apply the same criteria to every contributor and record acceptance or rejection reasons against the criteria above.

Preserve the [selection rules](taxonomy/README.md): 1 to 3 activities and independently 0 to 3 optional characteristics. Preserve IDs for unchanged meanings; changed meanings need new IDs. Record removed IDs in the retirement ledger. Report scope questions before making substantial changes.

Keep documentation provider-neutral and promotion outside the catalogue. Reserve provider names for [confirmed adoption records](ADOPTION.md), using the same criteria for everyone.

## Checks

Edit CSV sources, increment the catalogue version when data or selection constraints change, then regenerate and check JSON. Documentation clarifications alone do not require a catalogue version change. Python 3.10+ and its standard library are sufficient:

```text
python tools/catalogue.py
python tools/catalogue.py --check
python -m unittest discover -s tests
```

Contributions use Apache 2.0. Submit only material you have authority to contribute, with no private client data or restricted third-party material. Contributors retain ownership; no copyright assignment is required. See [licensing](LICENSING.md).
