# Cloud-Based Online File Storage System (Google Drive Clone)

A scalable web-based cloud storage application built with Python Flask and SQLite, modeled after modern services like Google Drive. It supports secure authentication, file uploads, metadata management, public shareable links, and AWS S3-compatible cloud storage architecture.

## 🚀 Live Demo
- **Public URL:** [http://13.235.76.168:8080](http://13.235.76.168:8080)
- **Deployment Platform:** AWS EC2 (Ubuntu Linux)

---

## 🛠 Tech Stack
- **Backend:** Python, Flask, Gunicorn
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Cloud & Deployment:** AWS EC2, AWS S3 / Boto3 integration, Linux systemd daemon

---

## ✨ Features
- **User Authentication:** Password hashing using Werkzeug and secure session tracking.
- **File Management:** Upload, download, and delete files with unique UUID keys to prevent name collisions.
- **Metadata Tracking:** Records file size, MIME content type, upload timestamp, and ownership in a relational database.
- **Public Sharing:** Generates secure, tokenized public links allowing external users to download shared files directly.
- **Production Server:** Configured as an automated systemd background service via Gunicorn on port 8080.

---

## 💻 Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/raheem-cloud/cloud-drive-app.git](https://github.com/raheem-cloud/cloud-drive-app.git)
   cd cloud-drive-app