# Data Schema

Tables:
- users(id, username, password_hash, role, active)
- streams(id, name, rtsp_url, created_at)
- violation_events(id, type, score, plate_text, plate_conf, speed_kph, evidence_path, evidence_plate_path, meta, created_at)
