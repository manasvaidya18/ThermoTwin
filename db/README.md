# Database

SQLite file `db/thermotwin.db`, created automatically on first start (it is not committed). It is portable to PostgreSQL
with minor type changes.

| Table | Written by | Contents |
|---|---|---|
| `facilities` | seed | PHCs and hospitals |
| `fridges` | seed | fridge id, facility, label, class (ILR / DOMESTIC) |
| `fridge_stock` | seed | vaccines in each fridge, in display order |
| `vaccines` | seed | freeze sensitivity per vaccine (used for vaccine-aware alerts) |
| `readings` | telemetry-service | 10-minute logger readings per fridge and source |
| `alert_events` | alerts-service | every Guardian tier change |

```bash
python db/init_db.py            # create or update
python db/init_db.py --reset    # start fresh (deletes the file)
```

Files: `schema.sql` (tables), `seed/01_vaccines.sql`, `seed/02_pune_demo.sql`, `init_db.py`.
