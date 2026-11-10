---
name: summarize_stats
track: core
kind: local_formatter
requires_env: []
inputs: [items, top_sources]
outputs: [total_items, source_count, sources, oldest, newest, span_days, undated, skipped]
side_effect: false
---
# summarize_stats

Computes an overview of items already collected: total count, count per source, and the date
range from oldest to newest. Items without a parsable date are counted in `undated`. It does not fetch data.
