import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    with get_conn() as conn, conn.cursor() as cur:
        # Create the schema
        cur.execute("""
            -- add pgcrypto extension for generating random uuids
            CREATE EXTENSION IF NOT EXISTS pgcrypto;

            CREATE TABLE IF NOT EXISTS hotel_rooms (
                id SERIAL PRIMARY KEY,
                room_number INT NOT NULL,
                type VARCHAR DEFAULT 'standard',
                price INT NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS hotel_guests (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR NOT NULL,
                lastname VARCHAR NOT NULL,
                address VARCHAR,
                created_at TIMESTAMP DEFAULT now()
            );
            ALTER TABLE hotel_guests ADD COLUMN IF NOT EXISTS api_key UUID DEFAULT gen_random_uuid();
            -- encode(gen_random_bytes(32), 'hex');
            UPDATE hotel_guests SET api_key = gen_random_uuid() WHERE api_key IS NULL;


            CREATE TABLE IF NOT EXISTS hotel_bookings (
                id SERIAL PRIMARY KEY,
                guest_id INT REFERENCES hotel_guests(id),
                -- same results as above
                room_id INT,
                FOREIGN KEY (room_id) REFERENCES hotel_rooms(id),
                datefrom DATE DEFAULT CURRENT_DATE,
                dateto DATE DEFAULT (CURRENT_DATE + INTERVAL '1 day'),
                addinfo VARCHAR,
                created_at TIMESTAMP DEFAULT now(),
                stars INT
            );

            -- add columns
            -- ALTER TABLE rooms ADD COLUMN IF NOT EXISTS room_type VARCHAR;

            -- create a view
            CREATE OR REPLACE VIEW bookings_view AS
                SELECT
                    g.firstname,
                    b.room_id,
                    r.room_number,
                    b.datefrom,
                    (b.dateto - b.datefrom) AS stays,
                    (r.price * (b.dateto - b.datefrom)) AS gross_price,
                    CASE
                        WHEN dateto - datefrom >= 7 THEN (r.price * (b.dateto - b.datefrom) * 0.8)
                        ELSE (r.price * (b.dateto - b.datefrom))
                    END AS total_price,
                    b.addinfo,
                    b.stars,
                    b.id,
                    b.guest_id
                FROM hotel_guests AS g
                INNER JOIN hotel_bookings AS b
                    ON g.id = b.guest_id
                INNER JOIN hotel_rooms AS r
                    ON r.id = b.room_id
        """)