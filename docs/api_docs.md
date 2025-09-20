# API

POST /inference/frame multipart form with `file`; optional query: pixel_per_meter,fps,signal_state,stop_line_y. Returns violations, plate, evidence and challan status.

GET /events?page=1&page_size=20 — Paginated events.

POST /issue-fine — Mock e-challan trigger. Body: { violations, plate, evidence }.
