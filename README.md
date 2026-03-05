# Delivery Tracker

Delivery Tracker is a Flask + SQLite web app for managing local delivery operations. It helps you create deliveries, assign drivers, update statuses, and monitor recent activity through notifications.

## Features

- Create and view deliveries
- Assign deliveries to drivers
- Update delivery status (`Pending`, `Out for Delivery`, `Delivered`, `Failed`)
- Manage drivers
- Notification feed for key actions
- SQLite database with starter seed data

## Tech Stack

- Python 3
- Flask
- SQLite
- Jinja2 templates

## Project Structure

- `app.py`: Main Flask application and routes
- `schema.sql`: Database schema and seed inserts
- `delivery.db`: SQLite database file
- `templates/`: HTML templates
- `static/`: Static assets (CSS/JS)
- `requirements.txt`: Python dependencies

## Setup

1. Clone the repository:

```bash
git clone https://github.com/ninavevinay/Delivery_Tracker.git
cd Delivery_Tracker
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
python app.py
```

The app runs at: `http://127.0.0.1:5000`

If `delivery.db` does not exist, it is initialized automatically on first run.

## Initialize Database Manually (Optional)

```bash
flask --app app.py init-db
```

## Main Routes

- `GET /` - Dashboard with deliveries and notifications
- `GET, POST /deliveries/new` - Create a delivery
- `GET /deliveries/<delivery_id>` - Delivery details
- `POST /deliveries/<delivery_id>/status` - Update status
- `POST /notifications/read` - Mark notifications as read
- `GET /drivers` - List drivers
- `POST /drivers/new` - Add a new driver

## Notes

- Default Flask secret key is development-only. Set `SECRET_KEY` in environment for production.
- Uses SQLite (`delivery.db`) for local persistence.

## License

This project is for learning and demo purposes.
