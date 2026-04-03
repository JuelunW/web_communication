import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    with get_conn() as conn, conn.cursor() as cur:
        # Create the schema
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hotel_rooms (
                id SERIAL PRIMARY KEY,
                room_number INT NOT NULL,
                type VARCHAR DEFAULT 'standard',
                price NUMRIC NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS hotel_guests (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR NOT NULL,
                lastname VARCHAR NOT NULL,
                address VARCHAR,
                created_at TIMESTAMP DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS hotel_bookings (
                id SERIAL PRIMARY KEY,
                guest_id INT,
                FOREIGN KEY (guest_id) REFERENCES hotel_guests(id),
                room_id INT,
                FOREIGN KEY (room_id) REFERENCES hotel_rooms(id),
                datefrom DATE NOT NULL,
                dateto DATE DEFAULT (CURRENT_DATE + INTERVAL '1 day'),
                addinfo VARCHAR,
                created_at TIMESTAMP DEFAULT now()
            );



            -- add columns
            -- ALTER TABLE rooms ADD COLUMN IF NOT EXISTS room_type VARCHAR;
        """)