# Architecture

React/Vite calls the FastAPI REST API through a centralized Axios client. FastAPI routers use SQLAlchemy PostgreSQL persistence and JWT ownership checks. The threat, chatbot, route and notification boundaries are deliberately replaceable local baselines.
