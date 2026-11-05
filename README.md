# ✨ Social Media Caption Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An AI-powered full-stack web application to generate creative social media captions and hashtags using Google Gemini AI.**

[Live Demo](#) · [Features](#-features) · [Installation](#-installation) · [API Docs](#-api-endpoints)

</div>

---

## 📸 Screenshots

> Landing Page · Dashboard · Caption Generator · Hashtag Tool

*(Add your screenshots here after running the app)*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Caption Generator** | Generate 3 unique captions per request via Google Gemini 1.5 Flash |
| #️⃣ **Hashtag Generator** | Popular / Niche / General hashtag categories |
| 📌 **My Captions** | Save, search, filter, inline-edit, and delete captions |
| ❤️ **Favorites** | Heart and collect your best captions |
| 🕐 **Caption History** | Full history with search, filter and export |
| 👤 **Authentication** | Register, login, logout with bcrypt hashed passwords |
| 🌙 **Dark / Light Mode** | Persistent theme stored in localStorage |
| 📊 **Dashboard Stats** | Animated counters + Chart.js platform breakdown |
| 📥 **Export** | Download captions and hashtags as `.txt` files |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |
| 🛡️ **Secure** | Hashed passwords, session management, parameterized queries |
| 🎭 **Demo Mode** | Works without an API key — clearly labeled sample captions |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+, Flask 3.0, Blueprints |
| **Database** | SQLite (auto-initialized, no setup needed) |
| **AI** | Google Gemini 1.5 Flash API |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Charts** | Chart.js 4.4 |
| **Icons** | Bootstrap Icons 1.11 |
| **Auth** | bcrypt password hashing |
| **Config** | python-dotenv |
| **Deploy** | gunicorn + Render / Railway / PythonAnywhere |

---

## 📁 Project Structure

```
social-media-caption-assistant/
├── app.py                      # Flask application factory
├── config.py                   # Configuration from .env
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── Procfile                    # gunicorn for deployment
│
├── database/
│   └── db.py                   # SQLite schema & connection helper
│
├── services/
│   ├── ai_service.py           # Gemini API + demo mode fallback
│   └── caption_service.py      # Caption CRUD, favorites, stats
│
├── routes/
│   ├── auth.py                 # Register / Login / Logout
│   ├── captions.py             # Caption & Hashtag API endpoints
│   └── dashboard.py            # Dashboard, profile, settings
│
├── templates/                  # 14 Jinja2 HTML templates
│   ├── index.html              # Landing page
│   ├── dashboard_base.html     # Sidebar layout
│   ├── dashboard.html          # Main dashboard
│   ├── generate.html           # Caption generator
│   ├── captions.html           # My Captions
│   ├── hashtags.html           # Hashtag generator
│   ├── history.html            # Caption history
│   ├── favorites.html          # Favorites
│   ├── profile.html            # User profile
│   ├── settings.html           # Settings
│   ├── login.html              # Login
│   ├── register.html           # Register
│   └── forgot_password.html    # Forgot password
│
└── static/
    ├── css/style.css           # Full SaaS design system (dark/light mode)
    ├── js/app.js               # All frontend logic
    └── manifest.json           # PWA manifest
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/social-media-caption-assistant.git
cd social-media-caption-assistant
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set your values:

```env
SECRET_KEY=your-very-secret-key-change-this
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_PATH=database/caption_assistant.db
FLASK_DEBUG=True
```

### 5. Run the Application

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000** 🎉

> The SQLite database creates itself automatically — no setup needed.

---

## 🤖 AI Setup (Google Gemini)

The app works in **Demo Mode** without an API key (sample captions are shown and clearly labeled).

To enable **real AI generation**:

1. Visit **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Add it to your `.env`:
   ```
   GEMINI_API_KEY=AIzaSy...your-key
   ```
5. Restart the server

> The free tier allows **15 requests/minute** and **1 million tokens/day** — more than enough.

---

## 🌐 Pages & Routes

| Page | URL | Access |
|------|-----|--------|
| Landing | `/` | Public |
| Register | `/register` | Public |
| Login | `/login` | Public |
| Forgot Password | `/forgot-password` | Public |
| Dashboard | `/dashboard` | 🔒 Login required |
| Generate Caption | `/generate` | 🔒 Login required |
| My Captions | `/my-captions` | 🔒 Login required |
| Hashtag Generator | `/hashtags` | 🔒 Login required |
| Caption History | `/history` | 🔒 Login required |
| Favorites | `/favorites` | 🔒 Login required |
| Profile | `/profile` | 🔒 Login required |
| Settings | `/settings` | 🔒 Login required |

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/generate` | Generate 3 captions | ✅ |
| POST | `/api/hashtags` | Generate hashtags | ✅ |
| GET | `/api/captions` | List captions (filterable) | ✅ |
| PUT | `/api/captions/<id>` | Update / save caption | ✅ |
| DELETE | `/api/captions/<id>` | Delete caption | ✅ |
| POST | `/api/favorites` | Toggle favorite | ✅ |
| GET | `/api/favorites` | List favorites | ✅ |
| GET | `/api/stats` | Dashboard statistics | ✅ |
| POST | `/api/profile` | Update profile | ✅ |

### Example Request — Generate Captions

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "sunset hike in the mountains",
    "platform": "Instagram",
    "category": "Travel",
    "tone": "Inspirational",
    "length": "medium"
  }'
```

### Example Response

```json
{
  "captions": [
    {
      "id": 1,
      "text": "Every peak conquered is a fear left behind...",
      "hashtags": "#travel #hiking #mountains #adventure",
      "char_count": 182
    }
  ],
  "is_demo": false,
  "platform": "Instagram"
}
```

---

## 🗄️ Database Schema

```sql
-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Captions
CREATE TABLE captions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    category TEXT NOT NULL,
    tone TEXT NOT NULL,
    topic TEXT NOT NULL,
    caption_text TEXT NOT NULL,
    hashtags TEXT,
    caption_length TEXT DEFAULT 'medium',
    is_saved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Favorites
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    caption_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (caption_id) REFERENCES captions(id) ON DELETE CASCADE,
    UNIQUE(user_id, caption_id)
);
```

---

## 🔐 Security

| Feature | Implementation |
|---------|----------------|
| Password Hashing | `bcrypt.hashpw()` with auto salt |
| Session Management | Flask server-side sessions |
| SQL Injection | Parameterized queries only |
| API Key Protection | Stored in `.env`, never sent to frontend |
| Auth Guard | `@login_required` decorator on all protected routes |
| Input Validation | Server-side on all endpoints |

---

## 🚀 Deployment

### Render (Free — Recommended)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add **Environment Variables:**
   - `SECRET_KEY` → any random string
   - `GEMINI_API_KEY` → your Gemini key
6. Click **Deploy**

### Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
2. Add env vars in Railway dashboard
3. Done — Railway auto-detects Flask

### PythonAnywhere (Free)

1. Upload project files via Files tab
2. Create a Web App → Manual Config → Python 3.10
3. Set WSGI file to point to `app.py`
4. Add environment variables

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add: your feature description'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 👨‍💻 Author

Built as a full-stack college project demonstrating:
- Python Flask + Blueprints architecture
- Google Gemini AI integration
- SQLite database with proper relationships
- Professional SaaS UI design
- Dark/Light mode
- RESTful API design

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ using Python Flask + Google Gemini AI

</div>
