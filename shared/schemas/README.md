# Shared contracts

JSON Schemas for the data passed between the parts of ThermoTwin:

| File | Between |
|---|---|
| `reading_ingest.schema.json` | devices (ESP32, eVIN feed) -> backend `POST /api/readings` |
| `scored_reading.schema.json` | prediction engine `POST /score` -> backend |
| `fridge_summary.schema.json` | backend `/api/fridges` -> frontend |
