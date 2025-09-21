import os
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, flash

DATABASE = os.path.join(os.path.dirname(__file__), 'delivery.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change')


# --------------------
# Database connections
# --------------------

def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(DATABASE)
		g.db.row_factory = sqlite3.Row
	return g.db


@app.teardown_appcontext
def close_db(exception):
	db = g.pop('db', None)
	if db is not None:
		db.close()


def init_db():
	with app.app_context():
		db = get_db()
		with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
			db.executescript(f.read())
		db.commit()


# --------------------
# Utilities
# --------------------

def create_notification(db, message):
	"""Insert a notification message into the notifications table."""
	db.execute(
		"INSERT INTO notifications(message, created_at, is_read) VALUES (?, ?, 0)",
		(message, datetime.utcnow().isoformat())
	)
	db.commit()


# --------------------
# Routes
# --------------------

@app.route('/')
def index():
	db = get_db()
	deliveries = db.execute(
		"""
		SELECT d.id, d.order_number, d.customer_name, d.address, d.status,
		       d.estimated_delivery, d.updated_at,
		       COALESCE(dr.name, '') AS driver_name
		FROM deliveries d
		LEFT JOIN drivers dr ON d.driver_id = dr.id
		ORDER BY d.updated_at DESC
		"""
	).fetchall()
	notifications = db.execute(
		"SELECT id, message, created_at, is_read FROM notifications ORDER BY created_at DESC LIMIT 10"
	).fetchall()
	return render_template('index.html', deliveries=deliveries, notifications=notifications)


@app.route('/deliveries/new', methods=['GET', 'POST'])
def create_delivery():
	db = get_db()
	if request.method == 'POST':
		order_number = request.form.get('order_number', '').strip()
		customer_name = request.form.get('customer_name', '').strip()
		address = request.form.get('address', '').strip()
		estimated_delivery = request.form.get('estimated_delivery', '').strip()
		driver_id = request.form.get('driver_id') or None

		if not order_number or not customer_name or not address:
			flash('Order number, customer name, and address are required.', 'error')
			return redirect(url_for('create_delivery'))

		db.execute(
			"""
			INSERT INTO deliveries(order_number, customer_name, address, status, estimated_delivery, updated_at, driver_id)
			VALUES(?, ?, ?, 'Pending', ?, ?, ?)
			""",
			(order_number, customer_name, address, estimated_delivery or None, datetime.utcnow().isoformat(), driver_id)
		)
		db.commit()
		create_notification(db, f"New delivery created: {order_number}")
		flash('Delivery created.', 'success')
		return redirect(url_for('index'))
	
	drivers = db.execute("SELECT id, name FROM drivers ORDER BY name").fetchall()
	return render_template('create_delivery.html', drivers=drivers)


@app.route('/deliveries/<int:delivery_id>')
def delivery_detail(delivery_id: int):
	db = get_db()
	delivery = db.execute(
		"""
		SELECT d.*, COALESCE(dr.name, '') AS driver_name
		FROM deliveries d
		LEFT JOIN drivers dr ON d.driver_id = dr.id
		WHERE d.id = ?
		""",
		(delivery_id,)
	).fetchone()
	if not delivery:
		flash('Delivery not found.', 'error')
		return redirect(url_for('index'))
	return render_template('delivery_detail.html', delivery=delivery)


@app.route('/deliveries/<int:delivery_id>/status', methods=['POST'])
def update_status(delivery_id: int):
	db = get_db()
	new_status = request.form.get('status', '').strip()
	valid_statuses = {'Pending', 'Out for Delivery', 'Delivered', 'Failed'}
	if new_status not in valid_statuses:
		flash('Invalid status.', 'error')
		return redirect(url_for('delivery_detail', delivery_id=delivery_id))

	res = db.execute("SELECT order_number, status FROM deliveries WHERE id = ?", (delivery_id,)).fetchone()
	if not res:
		flash('Delivery not found.', 'error')
		return redirect(url_for('index'))

	db.execute(
		"UPDATE deliveries SET status = ?, updated_at = ? WHERE id = ?",
		(new_status, datetime.utcnow().isoformat(), delivery_id)
	)
	db.commit()
	create_notification(db, f"Delivery {res['order_number']} status updated to {new_status}")
	flash('Status updated.', 'success')
	return redirect(url_for('delivery_detail', delivery_id=delivery_id))


@app.route('/notifications/read', methods=['POST'])
def mark_notifications_read():
	db = get_db()
	db.execute("UPDATE notifications SET is_read = 1 WHERE is_read = 0")
	db.commit()
	flash('Notifications marked as read.', 'success')
	return redirect(url_for('index'))
    

# --------------------
# Drivers section
# --------------------

@app.route('/drivers', methods=['GET'])
def drivers_list():
	db = get_db()
	drivers = db.execute("SELECT id, name, phone FROM drivers ORDER BY name").fetchall()
	return render_template('drivers.html', drivers=drivers)


@app.route('/drivers/new', methods=['POST'])
def drivers_create():
	db = get_db()
	name = request.form.get('name', '').strip()
	phone = request.form.get('phone', '').strip()
	if not name:
		flash('Driver name is required.', 'error')
		return redirect(url_for('drivers_list'))
	db.execute("INSERT INTO drivers(name, phone) VALUES(?, ?)", (name, phone or None))
	db.commit()
	create_notification(db, f"New driver added: {name}")
	flash('Driver added.', 'success')
	return redirect(url_for('drivers_list'))


# --------------------
# CLI helpers
# --------------------

@app.cli.command('init-db')
def init_db_command():
	"""Initialize the database tables."""
	init_db()
	print('Initialized the database.')


if __name__ == '__main__':
	if not os.path.exists(DATABASE):
		init_db()
	app.run(host='0.0.0.0', port=5000, debug=True)