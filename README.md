# carpool-backend

---

## 🧭 Description

**Carpool Backend** is a backend service for a carpooling platform.  
It enables users to **register**, **book rides**, and **manage trips** efficiently.  
Built using **Python** and **Django REST Framework**, it provides RESTful APIs for user management, ride booking, and more.

---

## ✨ Features

- 🔐 **User Registration and Authentication**
- 🚗 **Ride Booking and Management**
- 🔎 **Search for Available Rides**
- 📜 **View Ride History**
- ⚙️ **Admin Panel for Ride and User Management**

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| Language | Python |
| Framework | Django, Django REST Framework |
| Database | SQLite (can be swapped for PostgreSQL/MySQL) |
| API Docs | Swagger / OpenAPI |
| Authentication | JWT / Token-based |

---

## 📚 API Documentation

Once the server is running, you can view the interactive API documentation at:  
👉 [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/nikhil-sutar/carpool-backend.git
cd carpool-backend
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv .venv
```

### 3️⃣ Activate the Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 4️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 5️⃣ Make Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7️⃣ Run the Server

```bash
python manage.py runserver
```

---

## 🚀 Usage

After starting the server, you can:
- Access the admin panel at: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Explore the API endpoints via Swagger UI
- Start making API requests to manage rides and users

---