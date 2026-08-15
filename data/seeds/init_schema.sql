-- ============================================================
-- BATMAN DATABASE SCHEMA v1.0
-- PostgreSQL 16 + PostGIS 3.4
-- Classification: UNCLASSIFIED - Research/Academic
-- ============================================================

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── ENUMS ─────────────────────────────────────────────────────────────────────

CREATE TYPE mission_type_enum AS ENUM (
    'COUNTER_INFILTRATION',
    'COUNTER_TERRORISM',
    'COUNTER_INSURGENCY',
    'CONVOY_PROTECTION',
    'HIGH_ALTITUDE_LOGISTICS',
    'HADR',
    'HOSTAGE_RESCUE',
    'BORDER_SURVEILLANCE',
    'CRITICAL_INFRA_SECURITY'
);

CREATE TYPE mission_status_enum AS ENUM (
    'PLANNING',
    'APPROVED',
    'EXECUTING',
    'COMPLETE',
    'ABORTED'
);

CREATE TYPE readiness_enum AS ENUM (
    'GREEN',
    'AMBER',
    'RED',
    'BLACK'
);

CREATE TYPE coa_status_enum AS ENUM (
    'DRAFT',
    'SIMULATED',
    'PRESENTED',
    'APPROVED',
    'REJECTED',
    'EXECUTED'
);

CREATE TYPE audit_event_enum AS ENUM (
    'COA_PRESENTED',
    'COA_APPROVED',
    'COA_REJECTED',
    'COA_MODIFIED',
    'PLAN_OVERRIDE',
    'REPLAN_TRIGGERED',
    'MISSION_STARTED',
    'MISSION_COMPLETED',
    'MISSION_ABORTED',
    'THREAT_DETECTED',
    'COMMANDER_LOGIN',
    'COMMANDER_LOGOUT'
);

CREATE TYPE constraint_type_enum AS ENUM (
    'HARD',
    'SOFT'
);

CREATE TYPE objective_type_enum AS ENUM (
    'SECURE',
    'NEUTRALIZE',
    'RESCUE',
    'SURVEY',
    'ESCORT',
    'BLOCK',
    'OBSERVE',
    'SUPPLY'
);

CREATE TYPE threat_category_enum AS ENUM (
    'INFILTRATION',
    'UAV_RECON',
    'DRONE_SWARM',
    'LOITERING_MUNITION',
    'EW_JAMMING',
    'GPS_DENIAL',
    'CYBER_INCIDENT',
    'IED',
    'AMBUSH',
    'EXTREME_WEATHER',
    'ROUTE_DENIAL',
    'HOSTAGE_SITUATION'
);

-- ── USERS (managed by Keycloak; mirror for FK refs) ───────────────────────────

CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keycloak_id UUID UNIQUE NOT NULL,
    username    VARCHAR(100) UNIQUE NOT NULL,
    rank        VARCHAR(50),
    role        VARCHAR(50),
    unit_id     UUID,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    last_login  TIMESTAMPTZ
);

-- ── MISSIONS ──────────────────────────────────────────────────────────────────

CREATE TABLE missions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_code     VARCHAR(50) UNIQUE NOT NULL,
    mission_type     mission_type_enum NOT NULL,
    status           mission_status_enum NOT NULL DEFAULT 'PLANNING',
    classification   VARCHAR(20) NOT NULL DEFAULT 'UNCLASSIFIED',
    created_by       UUID REFERENCES users(id),
    approved_by      UUID REFERENCES users(id),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW(),
    h_hour           TIMESTAMPTZ,
    aor              GEOMETRY(POLYGON, 4326),    -- Area of Responsibility
    mission_params   JSONB NOT NULL DEFAULT '{}',
    constraint_ids   UUID[],
    roe_profile      JSONB DEFAULT '{}',         -- Rules of Engagement
    weather_forecast JSONB DEFAULT '{}'
);

-- ── OBJECTIVES ────────────────────────────────────────────────────────────────

CREATE TABLE objectives (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID REFERENCES missions(id) ON DELETE CASCADE,
    obj_type        objective_type_enum NOT NULL,
    priority        INTEGER CHECK (priority BETWEEN 1 AND 5),
    target_location GEOMETRY(POINT, 4326),
    target_area     GEOMETRY(POLYGON, 4326),
    deadline        TIMESTAMPTZ,
    status          VARCHAR(20) DEFAULT 'PENDING',
    description     TEXT,
    success_criteria JSONB DEFAULT '[]'
);

-- ── CONSTRAINTS ───────────────────────────────────────────────────────────────

CREATE TABLE mission_constraints (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id  UUID REFERENCES missions(id) ON DELETE CASCADE,
    con_type    constraint_type_enum NOT NULL,
    category    VARCHAR(50) NOT NULL,
    predicate   JSONB NOT NULL,          -- serialized logical expression
    penalty     FLOAT DEFAULT 0.0,       -- for soft constraints
    violated    BOOLEAN DEFAULT FALSE,
    description TEXT
);

-- ── UNITS ─────────────────────────────────────────────────────────────────────

CREATE TABLE units (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_code        VARCHAR(50) UNIQUE NOT NULL,
    unit_name        VARCHAR(100),
    unit_type        VARCHAR(50) NOT NULL,
    parent_unit_id   UUID REFERENCES units(id),
    current_position GEOMETRY(POINT, 4326),
    status           readiness_enum DEFAULT 'GREEN',
    capabilities     TEXT[],
    fuel_level       FLOAT CHECK (fuel_level BETWEEN 0 AND 1) DEFAULT 1.0,
    ammo_state       JSONB DEFAULT '{}',
    personnel_count  INTEGER DEFAULT 0,
    vehicle_count    INTEGER DEFAULT 0,
    comms_status     VARCHAR(20) DEFAULT 'NOMINAL',
    last_updated     TIMESTAMPTZ DEFAULT NOW(),
    metadata         JSONB DEFAULT '{}'
);

-- ── UNIT MISSION ASSIGNMENTS ──────────────────────────────────────────────────

CREATE TABLE unit_mission_assignments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id  UUID REFERENCES missions(id) ON DELETE CASCADE,
    unit_id     UUID REFERENCES units(id),
    role        VARCHAR(50),
    assigned_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── COURSES OF ACTION ─────────────────────────────────────────────────────────

CREATE TABLE courses_of_action (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id     UUID REFERENCES missions(id) ON DELETE CASCADE,
    coa_number     INTEGER,
    name           VARCHAR(100),
    style          VARCHAR(20) CHECK (style IN ('BOLD', 'BALANCED', 'CAUTIOUS')),
    status         coa_status_enum DEFAULT 'DRAFT',
    plan_graph     JSONB,          -- HTN plan as JSON task graph
    resource_plan  JSONB,          -- resource allocations
    timeline       JSONB,          -- phase timings
    route_geom     GEOMETRY(MULTILINESTRING, 4326), -- planned routes
    utility_score  FLOAT,
    explanation    JSONB,          -- ExplanationObject
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    modified_by    UUID REFERENCES users(id),
    modified_at    TIMESTAMPTZ
);

-- ── SIMULATION RESULTS ────────────────────────────────────────────────────────

CREATE TABLE simulation_results (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coa_id             UUID REFERENCES courses_of_action(id) ON DELETE CASCADE,
    run_count          INTEGER NOT NULL DEFAULT 500,
    success_rate       FLOAT CHECK (success_rate BETWEEN 0 AND 1),
    mean_casualties    FLOAT,
    std_casualties     FLOAT,
    timeline_p05       INTERVAL,
    timeline_p50       INTERVAL,
    timeline_p95       INTERVAL,
    roe_violation_rate FLOAT,
    fuel_consumed_mean FLOAT,
    failure_modes      JSONB DEFAULT '[]',  -- [{mode, probability}]
    sensitivity        JSONB DEFAULT '{}',  -- Sobol indices
    event_log_sample   JSONB DEFAULT '[]',  -- sample run events
    computed_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ── THREAT ASSESSMENTS ────────────────────────────────────────────────────────

CREATE TABLE threat_assessments (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id       UUID REFERENCES missions(id) ON DELETE CASCADE,
    threat_type      threat_category_enum NOT NULL,
    probability      FLOAT CHECK (probability BETWEEN 0 AND 1),
    confidence       FLOAT CHECK (confidence BETWEEN 0 AND 1),
    risk_score       FLOAT CHECK (risk_score BETWEEN 0 AND 10),
    location         GEOMETRY(POINT, 4326),
    uncertainty_m    FLOAT DEFAULT 500,     -- uncertainty radius in metres
    evidence         JSONB DEFAULT '{}',
    bayesian_params  JSONB DEFAULT '{}',    -- prior, likelihood, posterior
    countermeasures  JSONB DEFAULT '[]',
    assessed_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── DECISION AUDIT (Append-only, Immutable) ───────────────────────────────────

CREATE TABLE decision_audit (
    id                BIGSERIAL PRIMARY KEY,
    event_type        audit_event_enum NOT NULL,
    mission_id        UUID,
    coa_id            UUID,
    actor_id          UUID REFERENCES users(id),
    actor_role        VARCHAR(50),
    timestamp         TIMESTAMPTZ DEFAULT NOW(),
    ai_recommendation JSONB DEFAULT '{}',
    human_decision    JSONB DEFAULT '{}',
    delta             JSONB DEFAULT '{}',    -- what was changed
    rationale         TEXT,
    session_id        UUID,
    checksum          BYTEA                  -- SHA-256(prev_checksum || row_data)
);

-- Prevent updates/deletes on audit log
CREATE RULE no_update_audit AS ON UPDATE TO decision_audit DO INSTEAD NOTHING;
CREATE RULE no_delete_audit AS ON DELETE TO decision_audit DO INSTEAD NOTHING;

-- ── MISSION MEMORY (Case-Based Reasoning index) ───────────────────────────────

CREATE TABLE mission_cases (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id       UUID REFERENCES missions(id),
    mission_type     mission_type_enum NOT NULL,
    terrain_profile  JSONB DEFAULT '{}',
    threat_profile   JSONB DEFAULT '{}',
    resource_profile JSONB DEFAULT '{}',
    season           VARCHAR(20),
    coa_applied      JSONB,
    commander_mods   JSONB DEFAULT '[]',
    outcome          VARCHAR(20),          -- SUCCESS / PARTIAL / FAILURE
    actual_metrics   JSONB DEFAULT '{}',
    predicted_metrics JSONB DEFAULT '{}',
    prediction_error FLOAT,
    lessons_learned  TEXT[],
    failure_modes    JSONB DEFAULT '[]',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ── ALERTS ────────────────────────────────────────────────────────────────────

CREATE TABLE alerts (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id   UUID REFERENCES missions(id),
    alert_type   VARCHAR(50) NOT NULL,
    severity     VARCHAR(20) NOT NULL,  -- INFO / WARNING / CRITICAL
    title        VARCHAR(200),
    message      TEXT,
    data         JSONB DEFAULT '{}',
    acknowledged BOOLEAN DEFAULT FALSE,
    ack_by       UUID REFERENCES users(id),
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ── SPATIAL INDEXES ───────────────────────────────────────────────────────────

CREATE INDEX idx_units_position        ON units               USING GIST(current_position);
CREATE INDEX idx_missions_aor          ON missions            USING GIST(aor);
CREATE INDEX idx_threats_location      ON threat_assessments  USING GIST(location);
CREATE INDEX idx_objectives_loc        ON objectives          USING GIST(target_location);
CREATE INDEX idx_coa_routes            ON courses_of_action   USING GIST(route_geom);

-- ── REGULAR INDEXES ───────────────────────────────────────────────────────────

CREATE INDEX idx_missions_status       ON missions            (status);
CREATE INDEX idx_missions_type         ON missions            (mission_type);
CREATE INDEX idx_coa_mission           ON courses_of_action   (mission_id);
CREATE INDEX idx_coa_status            ON courses_of_action   (status);
CREATE INDEX idx_threats_mission       ON threat_assessments  (mission_id);
CREATE INDEX idx_audit_mission         ON decision_audit      (mission_id);
CREATE INDEX idx_audit_timestamp       ON decision_audit      (timestamp DESC);
CREATE INDEX idx_alerts_mission        ON alerts              (mission_id);
CREATE INDEX idx_cases_type            ON mission_cases       (mission_type);

-- ── SEED: DEFAULT KEYCLOAK SYSTEM USER ────────────────────────────────────────

INSERT INTO users (keycloak_id, username, rank, role)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'batman_system',
    'SYSTEM',
    'SYSTEM_ADMIN'
);

-- ── COMMENTS ──────────────────────────────────────────────────────────────────

COMMENT ON TABLE missions             IS 'Core mission records with geospatial AOR';
COMMENT ON TABLE courses_of_action    IS 'AI-generated and commander-modified COAs';
COMMENT ON TABLE simulation_results   IS 'Monte Carlo war-game statistics per COA';
COMMENT ON TABLE threat_assessments   IS 'Bayesian threat probability estimates';
COMMENT ON TABLE decision_audit       IS 'Immutable append-only command decision log';
COMMENT ON TABLE mission_cases        IS 'Case-Based Reasoning mission memory store';
COMMENT ON COLUMN decision_audit.checksum IS 'SHA-256(prev_row_checksum || current_row_data) — tamper-evident chain';
