# Migration notes (schema 1 -> v0.1)

50 records, 70 notes. Things a person should look at; they do not make a record incomplete. Missing minimum fields are in minimum_gaps.md.

| Record | Field | Note |
|---|---|---|
| MFL-2026-001 | `data` | download field mixes links and text, text not migrated: 'For MFLL: Internal\nOverall dataset' |
| MFL-2026-001 | `source_updated` | schema-1 last_updated '2024-2025' is not a date: not migrated |
| MFL-2026-002 | `source_updated` | schema-1 last_updated '2024-2025' is not a date: not migrated |
| MFL-2026-003 | `license` | old value 'Other (specify in notes)' is a placeholder with no licence terms |
| MFL-2026-004 | `license` | old value 'Other (specify in notes)' is a placeholder with no licence terms |
| MFL-2026-005 | `license` | old value 'Other (specify in notes)' is a placeholder with no licence terms |
| MFL-2026-006 | `data` | download field mixes links and text, text not migrated: 'Internal (Available on request' |
| MFL-2026-006 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-007 | `data` | download field mixes links and text, text not migrated: 'Internal (Available on request' |
| MFL-2026-007 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-011 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-012 | `data` | 3 links in one field: check names and which is primary |
| MFL-2026-012 | `license` | old value 'Other (specify in notes)' is a placeholder with no licence terms |
| MFL-2026-014 | `data` | schema-1 data_type 'Mixed': access points marked kind mixed; describe or split them |
| MFL-2026-014 | `temporal` | period 'Static' has no year: kept as text only |
| MFL-2026-018 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-019 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-021 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-026 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-029 | `data` | schema-1 data_type 'Mixed': access points marked kind mixed; describe or split them |
| MFL-2026-035 | `data` | download text without a URL on a public record: 'Internal Available on request' |
| MFL-2026-036 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-037 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-038 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-044 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-045 | `data` | download field mixes links and text, text not migrated: 'HarvestChoice, International Food Policy Research Institute (IFPRI); University of Minnesota, 2017, "CELL5M: A Multidisciplinary Geospatial Database for Africa South of the Sahara", , Harvard Dataverse, V5' |
| MFL-2026-045 | `license` | old value 'Other (specify in notes)' is a placeholder with no licence terms |
| MFL-2026-048 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-050 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-050 | `temporal` | period 'present' has no year: kept as text only |
| MFL-2026-051 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-051 | `temporal` | period 'present' has no year: kept as text only |
| MFL-2026-052 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-052 | `temporal` | period 'present' has no year: kept as text only |
| MFL-2026-053 | `data` | schema-1 data_type 'Mixed': access points marked kind mixed; describe or split them |
| MFL-2026-053 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-053 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-053 | `resource_type` | set to dataset as in schema 1; the title suggests a document: confirm |
| MFL-2026-054 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-054 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-054 | `temporal` | period 'present' has no year: kept as text only |
| MFL-2026-055 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-055 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-056 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-056 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-057 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-057 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-058 | `license` | old value 'Other (specify in notes)' is a placeholder with no licence terms |
| MFL-2026-064 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-067 | `data` | 2 links in one field: check names and which is primary |
| MFL-2026-067 | `data` | download field mixes links and text, text not migrated: 'CHIRPS data ( ). ERA5 AgERA5 v2.0' |
| MFL-2026-068 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-069 | `mosaic.landscapes` | schema-1 value 'NATIONAL' is not a living landscape: left out |
| MFL-2026-070 | `mosaic.landscapes` | schema-1 value 'GLOBAL' is not a living landscape: left out |
| MFL-2026-070 | `resource_type` | set to dataset as in schema 1; the title suggests a document: confirm |
| MFL-2026-071 | `mosaic.landscapes` | schema-1 value 'GLOBAL' is not a living landscape: left out |
| MFL-2026-072 | `temporal` | period 'Current boundaries' has no year: kept as text only |
| MFL-2026-073 | `temporal` | period 'Current' has no year: kept as text only |
| MFL-2026-074 | `temporal` | period 'Current' has no year: kept as text only |
| MFL-2026-085 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-086 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-087 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-088 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-089 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-090 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-091 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-092 | `license` | the licence text describes access, not licence terms: confirm the terms with the owner |
| MFL-2026-106 | `data` | schema-1 data_type 'Mixed': access points marked kind mixed; describe or split them |
| MFL-2026-106 | `temporal` | period 'Static' has no year: kept as text only |
| MFL-2026-108 | `temporal` | period 'Static' has no year: kept as text only |
