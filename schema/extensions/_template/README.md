# Extension template

An extension adds fields for one domain (soil, biodiversity, climate, ...) without touching the
core record. Use one when a field is useful for a group of records and does not fit an existing
field. If it would be useful for almost every record, propose it for the core instead.

1. Copy this folder to `schema/extensions/<name>/<version>/` (e.g. `soil/0.1.0/`).
2. In `schema.json`, replace `EXAMPLE` with `<name>` in the `$id`, the title and the property key.
   Every field of the extension lives under that single key.
3. Add a valid and an invalid record under `tests/fixtures/` and run `pytest`.
4. Records that use it declare it and add the block:

```yaml
extensions: [soil@0.1.0]
soil:
  depth: 0-30 cm
```

A block whose extension is not declared, or an extension that does not exist, makes the record
invalid. A new version goes in a new folder; records keep the version they declare until migrated.
