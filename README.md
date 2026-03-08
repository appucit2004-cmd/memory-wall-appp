# Digital Memory Wall

A modern, private digital memory diary web application where people can submit heartfelt messages about you. Only the admin can view submissions.

## Features

- **Loading Page** - Animated intro when website opens
- **Landing Page** - Beautiful gradient design with glassmorphism
- **Memory Submission** - Name, photo upload, message (min 2000 words)
- **Admin Login** - Secure access to view memories
- **Admin Dashboard** - View, search, and delete memories
- **Private** - Visitors cannot see other people's submissions

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python Flask
- **Database**: SQLite

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Visit: **http://127.0.0.1:5000**

The app will show the loading screen first, then redirect to the landing page.

## Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Project Structure

```
memory-wall-app/
├── app.py              # Flask backend
├── database.db         # SQLite database (created on first run)
├── requirements.txt
├── README.md
├── static/
│   ├── style.css       # All styles
│   ├── script.js       # Frontend JavaScript
│   └── uploads/        # Uploaded photos
└── templates/
    ├── loading.html    # Loading screen
    ├── index.html      # Landing page
    ├── submit.html     # Memory submission form
    ├── login.html      # Admin login
    └── dashboard.html  # Admin memory wall
```

## Routes

| Route | Description |
|-------|-------------|
| `/` | Redirects to loading page |
| `/loading` | Animated loading screen |
| `/home` | Landing page |
| `/submit` | Submit memory form |
| `/admin-login` | Admin login |
| `/dashboard` | Private memory wall (admin only) |
| `/delete-memory/<id>` | Delete memory (admin only) |
| `/logout` | Admin logout |

## Database Schema

**Table: memories**

| Column | Type |
|--------|------|
| id | INTEGER (Primary Key) |
| name | TEXT |
| photo | TEXT (file path) |
| message | TEXT |
| created_at | TIMESTAMP |

## Security Notes

- Change admin credentials in production (use environment variables)
- Consider using a stronger `secret_key` for sessions
- For production: use HTTPS, proper authentication, and a production WSGI server (e.g., Gunicorn)
