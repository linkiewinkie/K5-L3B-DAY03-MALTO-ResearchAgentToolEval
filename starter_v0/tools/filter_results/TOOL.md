---
name: filter_results
track: core
kind: local_formatter
requires_env: []
inputs: [items, sources, days]
outputs: [items, input_count, item_count, removed_by_source, removed_by_date, removed_undated, skipped]
side_effect: false
---
# filter_results

Filters items already collected by lookup/social_search: keep only the wanted sources
(matched on the `source` field or the url domain, case-insensitive) and/or only items
published within the last N days. Items without a parsable date are dropped when `days` is set.
It does not fetch data.
