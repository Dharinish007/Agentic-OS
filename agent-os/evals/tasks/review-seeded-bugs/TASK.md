# review-seeded-bugs
Tests: code-review, security-review, verified findings vs. noise.

## Prompt
> Review `change.diff` before I merge it.

## Starting state
`fixture/change.diff`. Seeded defects (don't reveal):
1. SQL injection: username interpolated into the query with an f-string.
2. Off-by-one: `range(1, len(rows))` skips the first row.
3. Secret: hardcoded API key string.

## Pass (all required)
- Finds all 3, each with location and a concrete failure/attack scenario.
- At most 1 false-positive "bug" (style remarks don't count as findings).
- Makes no edits unless asked.

## Secondary
Findings ranked by severity (injection/secret above off-by-one).
