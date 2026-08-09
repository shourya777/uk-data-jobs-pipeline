# Notes: matching companies to the UK sponsor register

These are real lessons from an earlier prototype of this idea, kept here so
you don't repeat the same mistakes when you implement `int_postings_sponsor_matched.sql`.

## The naive approach doesn't work

First instinct: normalize both the job posting's company name and the
register's `Organisation Name` (lowercase, strip "Ltd"/"Limited"/"PLC"/etc.),
then do a substring or token match. This produces confident-looking but
wrong matches, for example:

| Job posting company | Naive match picked | Why it's wrong |
|---|---|---|
| Zego | "Azego TS Ltd" | Substring match on "zego" inside "Azego" — different company entirely |
| Sky | "Sky Supermarket" | Single generic token match — should be "Sky UK Limited" |
| Sainsbury's | "The Sainsbury Laboratory" | Wrong entity — a genetics research institute, not the supermarket |
| Transform | "Transform Housing & Support" | Coincidental word overlap, unrelated housing charity |
| Oxford Group International | "Oxford Analytica" | Single-token ("oxford") match on an unrelated company |

The register has 140,000+ entries, so with a database that large, almost
any short or common company name will have *some* substring overlap with
something. Precision matters more than recall here — an incorrect "yes,
this company sponsors visas" claim is worse than a missed true positive.

## What actually worked

1. **Multi-token matching, not substring matching.** Split both names into
   tokens, strip a stopword list (ltd, limited, plc, group, holdings,
   international, uk, technologies, solutions, consulting, global...),
   and require *all* significant tokens from the job posting's company
   name to appear as whole tokens in a register entry — not as a raw
   substring.

2. **Verify single-token matches manually or with a second signal**, e.g.
   town/city plausibility. "LEGO Company Ltd" in the register lists
   Slough, Berkshire — which is genuinely LEGO's UK office location — so
   that match could be trusted. A single generic word matching against an
   entry in an implausible location/industry is a red flag, not a match.

3. **When ambiguous, exclude rather than guess.** For company names not
   directly identifiable (e.g. "N Consulting Global", "Intelstack",
   "Response Informatics" — none had an unambiguous register entry), the
   right move is to leave them out of `is_verified_sponsor = true` rather
   than force a low-confidence match.

4. **Group/subsidiary structures need a manual map.** Elsevier, LexisNexis
   Risk Solutions, and Cirium are all trading names under the RELX group;
   none appear standalone in the register, but "RELX (UK) Limited" does.
   A hardcoded lookup table for known parent/subsidiary relationships beats
   trying to infer this algorithmically.

## Implementation suggestion

Keep a small `seeds/known_sponsor_matches.csv` seed (starter version
included in this repo) with columns `company_name_raw, sponsor_entity,
category`, curated by hand as you go. Use it as the first lookup in
`int_postings_sponsor_matched.sql`; only fall through to the fuzzy
token-matching macro for names not already in the seed. This mirrors how
the matching was actually done in practice — a growing curated map plus a
conservative fallback, not a fully automated fuzzy-match pipeline.
