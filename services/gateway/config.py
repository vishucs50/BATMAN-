"""
Gateway Settings — loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import list


class Settings(BaseSettings):
    # Service identity
    SERVICE_NAME: str = "batman-gateway"
    SERVICE_VERSION: str = "2.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://batman:batman_dev_secret@localhost:5432/batman"

    # Redis
    REDIS_URL: str = "redis://:batman_redis_secret@localhost:6379/0"

    # Kafka
    KAFKA_BOOTSTRAP: str = "localhost:9092"

    # Keycloak / Auth
    KEYCLOAK_URL: str = "http://localhost:8443"
    KEYCLOAK_REALM: str = "batman"
    KEYCLOAK_CLIENT_ID: str = "batman-gateway"
    KEYCLOAK_CLIENT_SECRET: str = "batman-gateway-secret-dev"
    JWT_ALGORITHM: str = "RS256"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1", "batman-gateway"]

    # Service URLs (internal)
    MISSION_SVC_URL: str = "http://batman-mission-svc:8001"
    PLANNING_SVC_URL: str = "http://batman-planning-svc:8002"
    WARGAME_SVC_URL: str = "http://batman-wargame-svc:8003"
    THREAT_SVC_URL: str = "http://batman-threat-svc:8004"
    LOGISTICS_SVC_URL: str = "http://batman-logistics-svc:8005"
    KG_SVC_URL: str = "http://batman-kg-svc:8006"
    GIS_SVC_URL: str = "http://batman-gis-svc:8007"
    AUDIT_SVC_URL: str = "http://batman-audit-svc:8011"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
