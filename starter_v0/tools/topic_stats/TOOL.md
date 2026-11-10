---
name: topic_stats
track: core
kind: local_formatter
requires_env: []
inputs: [items, top_n, min_articles, topics]
outputs: [mode, total_articles, topics, skipped]
side_effect: false
---
# topic_stats

Finds the most mentioned topics across articles already collected. Auto mode counts keywords
(one vote per article) and keeps those in at least `min_articles` articles; custom mode counts
the topics the user names. Each topic reports article count, share, representative sources and an
example title. Topic labels are accent-folded lower-case. It does not fetch data.
