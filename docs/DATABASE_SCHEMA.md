# Database schema

Every user-owned table includes `user_id` and is filtered by the authenticated user in its router. UUID string keys, foreign keys, timestamps, unique identity fields and indexes are defined in `backend/app/models/entities.py`.
