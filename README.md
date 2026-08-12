# CropCare 🌱

An advanced AI-powered precision agriculture web platform designed for farmers, agricultural scientists, and administrators. Built with **FastAPI**, **SQLAlchemy**, **Groq AI**, **Cloudinary**, and modern responsive web design.

---

## 📁 Architecture & Directory Structure

For full architectural details and comprehensive explanations of every directory and file in the codebase, please see:
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [docs/README.md](docs/README.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🚀 Quick Start (Local Development)

### One-Click Launch (Windows)
Double-click `start.bat` (or run `.\start.bat` in terminal) to launch the backend server, health checks, and browser UI automatically. To stop all background processes, run `.\stop.bat`.

### Manual Startup
1. **Activate Virtual Environment**:
   ```bash
   .\venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your database and API credentials.

4. **Launch Server**:
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
   Open `http://127.0.0.1:8000` in your browser.
