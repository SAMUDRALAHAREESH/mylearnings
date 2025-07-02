import can
import sqlite3
from datetime import datetime
import logging
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PGN_RPM = 61444        # 0x0CF00400
PGN_ODOMETER = 65217   # 0x18FEC100

WHEEL_DIAMETER = 0.8  

WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER  # approx 2.513 meters

def init_db():
    try:
        conn = sqlite3.connect('j1939_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_data (
                timestamp TEXT,
                pgn INTEGER,
                parameter TEXT,
                value REAL
            )
        ''')
        # Check if an initial odometer reading exists
        cursor.execute("SELECT value FROM vehicle_data WHERE parameter = 'Odometer' ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        if not result:
            # Insert initial odometer reading of 1000 km
            initial_odometer = 1000.0
            cursor.execute('''
                INSERT INTO vehicle_data (timestamp, pgn, parameter, value)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), PGN_ODOMETER, 'Odometer', initial_odometer))
            logging.info(f"Initialized odometer to {initial_odometer} km")
        conn.commit()
        logging.info("Database initialized successfully.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
        raise

def parse_j1939_message(msg, last_rpm_time, last_odometer):
    arbitration_id = msg.arbitration_id
    pgn = (arbitration_id >> 8) & 0x1FFFF
    data = msg.data
    current_time = datetime.now()
    logging.info(f"Received Arbitration ID: {hex(arbitration_id)}, PGN: {hex(pgn)}, Data: {data.hex()} (len={len(data)})")

    if pgn == PGN_RPM and len(data) >= 5:
        rpm_raw = (data[3] << 8) | data[4]
        rpm = rpm_raw * 0.125
        logging.info(f"Parsed RPM: {rpm} rpm from raw: {hex(rpm_raw)}, bytes [4]={hex(data[3])}, [5]={hex(data[4])}")
        
        # Calculate vehicle speed (km/h) from RPM
        speed_kmh = (rpm * WHEEL_CIRCUMFERENCE * 60) / ( 1000)
        logging.info(f"Calculated Speed: {speed_kmh:.2f} km/h from RPM: {rpm}")
        
        # Calculate odometer increment if gear is engaged (RPM > 0)
        odometer_increment = 0.0
        if rpm > 0 and last_rpm_time is not None:
            time_delta = (current_time - last_rpm_time).total_seconds() / 3600.0  # Convert to hours
            odometer_increment = speed_kmh * time_delta
            last_odometer += odometer_increment
            logging.info(f"Odometer incremented by {odometer_increment:.6f} km to {last_odometer:.2f} km")
        
        return pgn, 'RPM', rpm, last_odometer, current_time

    elif pgn == PGN_ODOMETER and len(data) >= 4:
        raw = (data[3] << 24) | (data[2] << 16) | (data[1] << 8) | data[0]
        odometer_km = raw * 0.005
        logging.info(f"Parsed Odometer: {odometer_km} km from raw: {hex(raw)}, bytes [1-4]={list(data[0:4])}")
        return pgn, 'Odometer', odometer_km, last_odometer, last_rpm_time

    logging.warning(f"No valid data parsed for PGN: {hex(pgn)}")
    return pgn, None, None, last_odometer, last_rpm_time

def store_data(conn, timestamp, pgn, parameter, value):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicle_data (timestamp, pgn, parameter, value)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, pgn, parameter, value))
        conn.commit()
        logging.info(f"Stored: {parameter} = {value} (PGN: {hex(pgn)}) at {timestamp}")
    except sqlite3.Error as e:
        logging.error(f"Database insert error: {e}")
        raise

def main():
    conn = None
    bus = None
    last_rpm_time = None
    last_odometer = None
    try:
        conn = init_db()
        # Fetch the latest odometer value
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM vehicle_data WHERE parameter = 'Odometer' ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        last_odometer = result[0] if result else 1000.0
        logging.info(f"Starting with odometer: {last_odometer} km")

        bus = can.interface.Bus(
            channel='vcan0',
            bustype='socketcan',
            can_filters=[
                {"can_id": 0x0CF00400, "can_mask": 0x1FFFFF00},  # RPM
                {"can_id": 0x18FEC100, "can_mask": 0x1FFFFF00}   # Odometer
            ]
        )
        logging.info("CAN bus initialized with filters for RPM and Odometer.")

        while True:
            msg = bus.recv(timeout=1.0)
            if msg is None:
                logging.debug("No message received, waiting...")
                continue

            pgn, parameter, value, last_odometer, last_rpm_time = parse_j1939_message(msg, last_rpm_time, last_odometer)
            if parameter and value is not None:
                timestamp = datetime.now().isoformat()
                store_data(conn, timestamp, pgn, parameter, value)
                # Store updated odometer when processing RPM
                if parameter == 'RPM' and value > 0:
                    store_data(conn, timestamp, PGN_ODOMETER, 'Odometer', last_odometer)
            else:
                logging.warning(f"Skipping storage for PGN {hex(pgn)}: Invalid parameter or value")

    except can.CanError as e:
        logging.error(f"CAN bus error: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")
        if bus:
            bus.shutdown()
            logging.info("CAN bus shutdown.")
        logging.info("Program terminated.")

if __name__ == "__main__":
    main()