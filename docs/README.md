# CropCare 🌱

An advanced AI-powered precision agriculture web platform designed for farmers, agricultural scientists, and administrators. Built with **FastAPI**, **SQLAlchemy**, **Groq AI**, **Cloudinary**, and modern responsive web design.

---

## Architecture Overview

- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy ORM
- **Frontend**: Responsive HTML5, Vanilla CSS, Tailwind CSS, JavaScript
- **Database**: Neon PostgreSQL (Serverless Cloud PostgreSQL with SQLAlchemy connection pooling)

- **AI Engine**: Groq API (Llama 3 / Vision analysis for Crop Recommendations, Disease Diagnosis, and Land Lease Strategic Assessments)
- **PDF Report Engine**: ReportLab 5.0 (Automated, downloadable Land Lease Estimation reports)
- **Persistent File Storage**: Cloudinary (Profiles & Diagnosis images)
- **Weather Integration**: Open-Meteo Geocoding & Historical/Forecast APIs


---

## Quick Start (Local Development)

1. **Clone & Create Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   copy .env.example .env
   ```

4. **Run Development Server**:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Production Deployment

CropCare is configured for high-performance production deployment across **Vercel** (Static CDN frontend) and **Railway** (Containerized FastAPI backend + MySQL).

Please see [DEPLOYMENT.md](./DEPLOYMENT.md) for full step-by-step production setup instructions.
