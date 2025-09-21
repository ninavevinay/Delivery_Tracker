import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'delivery.db')

DRIVERS = [
	(1, 'Ayush Sharma', '785524441'),
	(2, 'Vikas Kumar', '7852255562'),
	(3, 'Vijay Kumar', '7452639654'),
]

DELIVERIES = [
	(1, '1', 'Vinay Ninave', 'Mahal Nagpur', 'Pending', None, 1),
	(2, '2', 'Aaliya Ali', 'Wadi Higana', 'Out for Delivery', None, 2),
	(3, '3', 'Piyush Lomte', 'Friend Colony', 'Delivered', None, 3),
]

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()
now = datetime.utcnow().isoformat()

# Upsert drivers
for did, name, phone in DRIVERS:
	cur.execute(
		"""
		INSERT INTO drivers(id, name, phone) VALUES(?, ?, ?)
		ON CONFLICT(id) DO UPDATE SET name=excluded.name, phone=excluded.phone
		""",
		(did, name, phone)
	)

# Upsert deliveries
for did, order_no, customer, address, status, eta, driver_id in DELIVERIES:
	cur.execute(
		"""
		INSERT INTO deliveries(id, order_number, customer_name, address, status, estimated_delivery, updated_at, driver_id)
		VALUES(?, ?, ?, ?, ?, ?, ?, ?)
		ON CONFLICT(id) DO UPDATE SET
			order_number=excluded.order_number,
			customer_name=excluded.customer_name,
			address=excluded.address,
			status=excluded.status,
			estimated_delivery=excluded.estimated_delivery,
			updated_at=excluded.updated_at,
			driver_id=excluded.driver_id
		""",
		(did, order_no, customer, address, status, eta, now, driver_id)
	)

conn.commit()
conn.close()
print('Seed data added/updated successfully.')
