# Contributing

## Add / Fix Data

- Open an issue with a link or screenshot to the `!process` message(s) you want included.
- If you have a Discord CSV export folder, attach it or share the folder name/path you used.

## Run Locally

- Update `public/data/intern_data.json` by merging new export folders:
  - `python scripts/merge_imports.py /path/to/export_dir`
- Regenerate the README:
  - `python scripts/generate_readme.py`

