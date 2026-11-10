---
name: extract_links
track: core
kind: local_formatter
requires_env: []
inputs: [text, unique]
outputs: [links, count, total_found]
side_effect: false
---
# extract_links

Extracts every http(s) URL from text the user provided and returns the list plus the count.
It does not open the links; use fetch to read one.
