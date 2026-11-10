---
name: rank
track: core
kind: local_formatter
requires_env: []
inputs: [items, by, order, limit]
outputs: [items, input_count, item_count, unranked, skipped]
side_effect: false
---
# rank

Sorts items already collected by lookup/social_search by score, date or title and can keep
only the top N. Items missing the sort field are kept after the ranked ones. It does not fetch data.
