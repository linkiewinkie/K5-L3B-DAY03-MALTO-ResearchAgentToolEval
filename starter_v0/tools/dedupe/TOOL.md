---
name: dedupe
track: core
kind: local_formatter
requires_env: []
inputs: [items, key, limit]
outputs: [items, input_count, item_count, skipped]
side_effect: false
---
# dedupe

Removes duplicate items (same normalised URL or title) from results already collected
by lookup/social_search. It does not fetch data.
