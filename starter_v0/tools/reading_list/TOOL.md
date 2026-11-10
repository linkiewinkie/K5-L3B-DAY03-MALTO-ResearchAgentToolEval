---
name: reading_list
track: core
kind: local_knowledge
requires_env: []
inputs: [action, url, title, note, confirmed]
outputs: [status, entry, entries, count]
side_effect: local_file_write
---
# reading_list

Saves articles the user wants to read later in a local JSON file (`reading_list.json`, or the path
in `READING_LIST_PATH`). Actions: `add`, `list`, `remove`, `clear`. Duplicate URLs are detected
after normalisation. `clear` deletes everything, so it only runs with `confirmed=true`.
