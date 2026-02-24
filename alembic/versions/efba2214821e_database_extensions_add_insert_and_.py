"""Database extensions: add insert and select sql functions

Revision ID: efba2214821e
Revises: f1b0fb5ef51e
Create Date: 2026-02-22 18:01:25.030836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efba2214821e'
down_revision = 'f1b0fb5ef51e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION get_measurements_by_tags(
        tags JSONB,
        start_time TIMESTAMPTZ DEFAULT NULL,
        end_time TIMESTAMPTZ DEFAULT NULL,
        window_size INTERVAL DEFAULT '1 hour'::interval
    )
    RETURNS TABLE (
        "timestamp" TIMESTAMPTZ,
        name VARCHAR(500),
        value DOUBLE PRECISION
    ) 
    LANGUAGE plpgsql 
    STABLE
    AS $$
    DECLARE
        v_start TIMESTAMPTZ;
        v_end TIMESTAMPTZ;
    BEGIN
        -- Find the absolute minimum time
        IF start_time IS NULL THEN
            SELECT min(m.timestamp)
            INTO v_start
            FROM measurements m
            JOIN series_catalog sc ON m.series_id = sc.id
            WHERE sc.tags::jsonb @> get_measurements_by_tags.tags;
        ELSE
            v_start := start_time;
        END IF;
    
        -- Find the absolute maximum time
        IF end_time IS NULL THEN
            SELECT max(m.timestamp)
            INTO v_end
            FROM measurements m
                    JOIN series_catalog sc ON m.series_id = sc.id
            WHERE sc.tags::jsonb @> get_measurements_by_tags.tags;
        ELSE
            v_end := end_time;
        END IF;
        
        -- If there are no measurements for the given tags, return an empty result
        IF v_start IS NULL OR v_end IS NULL THEN
            RETURN;
        END IF;
    
        -- Use time_bucket_gapfill to get buckets even if there are no measurements, and dynamic aggregation based on the aggregation_method in series_catalog
        RETURN QUERY
        SELECT time_bucket_gapfill(window_size, m.timestamp, v_start, v_end) AS "timestamp",
            sc.name::VARCHAR(500) AS name,
            locf(
                CASE
                    WHEN sc.aggregation_method = 'sum' THEN sum(m.value)
                    WHEN sc.aggregation_method = 'max' THEN max(m.value)
                    WHEN sc.aggregation_method = 'min' THEN min(m.value)
                    WHEN sc.aggregation_method = 'last' THEN last (m.value, m.timestamp)
                    ELSE avg (m.value)
                END
            )::DOUBLE PRECISION AS value
       FROM measurements m
       JOIN series_catalog sc ON m.series_id = sc.id
       WHERE sc.tags::jsonb @> get_measurements_by_tags.tags
            AND m.timestamp >= v_start
            AND m.timestamp <= v_end
       GROUP BY 1, 2, sc.aggregation_method
       ORDER BY 1, 2;
       END;
    $$;
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION get_categorical_by_tags(
        tags JSONB,
        start_time TIMESTAMPTZ DEFAULT NULL,
        end_time TIMESTAMPTZ DEFAULT NULL,
        window_size INTERVAL DEFAULT '1 hour'::interval
    )
    RETURNS TABLE (
        "timestamp" TIMESTAMPTZ,
        name VARCHAR(500),
        state TEXT,
        value INTEGER
    ) 
    LANGUAGE plpgsql 
    STABLE
    AS $$
    DECLARE
        v_start TIMESTAMPTZ;
        v_end TIMESTAMPTZ;
    BEGIN
        -- Find the absolute minimum time
        IF start_time IS NULL THEN
            SELECT min(m.timestamp)
            INTO v_start
            FROM categorical_measurements cm
            JOIN series_catalog sc ON m.series_id = sc.id
            WHERE sc.tags::jsonb @> get_categorical_by_tags.tags;
        ELSE
            v_start := start_time;
        END IF;
    
        -- Find the absolute maximum time
        IF end_time IS NULL THEN
            SELECT max(m.timestamp)
            INTO v_end
            FROM categorical_measurements cm
                    JOIN series_catalog sc ON cm.series_id = sc.id
            WHERE sc.tags::jsonb @> get_categorical_by_tags.tags;
        ELSE
            v_end := end_time;
        END IF;
        
        -- If there are no measurements for the given tags, return an empty result
        IF v_start IS NULL OR v_end IS NULL THEN
            RETURN;
        END IF;
    
        -- Use time_bucket_gapfill to get buckets even if there are no measurements, and dynamic aggregation based on the aggregation_method in series_catalog
        RETURN QUERY
        WITH grouped_data AS (
            SELECT 
                time_bucket_gapfill(window_size, cm.timestamp, v_start, v_end) AS bucket,
                cm.series_id,
                locf(first(cm.value, cm.timestamp)) AS last_val
            FROM categorical_measurements cm
            JOIN categories_catalog cc ON cm.series_id = cc.id
            WHERE cc.tags::jsonb @> get_categorical_by_tags.tags
              AND cm.timestamp >= v_start AND cm.timestamp <= v_end
            GROUP BY 1, 2
        )
        -- Add a join to categories_catalog to get the name and state mapping, and use the last_val to get the state text
        SELECT 
            gd.bucket AS "timestamp",
            cc.name::VARCHAR(500),
            -- Jsonb ->> operator returns null if the key does not exist, so we use COALESCE to return 'Unknown' in that case
            COALESCE(cc.state_mapping::jsonb ->> gd.last_val::text, 'Unknown (' || gd.last_val || ')') AS state_text,
            gd.last_val AS value
        FROM grouped_data gd
        JOIN categories_catalog cc ON gd.series_id = cc.id
        ORDER BY 1, 2;
        END;
    $$;
    """)


def downgrade() -> None:
    op.execute("""
        DROP FUNCTION IF EXISTS get_measurements_by_tags(JSONB, TIMESTAMPTZ, TIMESTAMPTZ, INTERVAL);
    """)
    op.execute("""
        DROP FUNCTION IF EXISTS get_categorical_by_tags(JSONB, TIMESTAMPTZ, TIMESTAMPTZ, INTERVAL);
    """)