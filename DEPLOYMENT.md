# CropCare Production Deployment Guide 🚀

This guide explains how to deploy CropCare securely and reliably in production using **Neon PostgreSQL** (Database), **Railway / Render** (Backend API), and **Vercel** (Edge CDN Frontend + Rewrites).

---

## Part 1: Neon PostgreSQL Setup

1. Log in to [Neon](https://neon.tech/).
2. Create a new PostgreSQL project and copy your connection string.
3. Update `DATABASE_URL` format to use `postgresql+psycopg://`:
   `postgresql+psycopg://username:password@ep-xxxx.neon.tech/neondb?sslmode=require`

### Step 2: Deploy FastAPI Backend Service
1. In your deployment dashboard (Railway / Render), add the following environment variables:
   ```env
   ENVIRONMENT=production
   DEBUG=false
   PORT=8000
   DATABASE_URL=postgresql+psycopg://neondb_owner:password@ep-xxx.neon.tech/neondb?sslmode=require

   SECRET_KEY=<generate-long-random-string>
   JWT_SECRET=<generate-long-random-string>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   WEATHERSTACK_API_KEY=<your-weather-key>
   GROQ_API_KEY=<your-groq-key>
   CHATBOT_ID=<your-chatbase-id>
   CLOUDINARY_CLOUD_NAME=<your-cloudinary-name>
   CLOUDINARY_API_KEY=<your-cloudinary-key>
   CLOUDINARY_API_SECRET=<your-cloudinary-secret>
   ADMIN_EMAIL=admin@cropcare.com
   ADMIN_PASSWORD=<strong-admin-password>
   ```
4. Click **Settings** -> **Networking** -> **Generate Domain** (e.g., `https://cropcare-api.up.railway.app`).

---

## Part 2: Vercel Frontend Deployment

### Step 1: Connect GitHub Repo to Vercel
1. Log in to [Vercel](https://vercel.com/) and click **Add New** -> **Project**.
2. Import the `CropCare` GitHub repository.

### Step 2: Configure Vercel Edge Rewrites
1. Open `vercel.json` in your repository root and ensure the destination URLs point to your Railway API domain generated in Part 1:
   ```json
   {
     "rewrites": [
       { "source": "/auth/:path*", "destination": "https://cropcare-api.up.railway.app/auth/:path*" },
       { "source": "/user/:path*", "destination": "https://cropcare-api.up.railway.app/user/:path*" },
       { "source": "/admin/:path*", "destination": "https://cropcare-api.up.railway.app/admin/:path*" },
       { "source": "/api/:path*", "destination": "https://cropcare-api.up.railway.app/api/:path*" }
     ]
   }
   ```
2. Commit and push `vercel.json` to GitHub. Vercel will automatically deploy.
3. Access your frontend on your Vercel URL (`https://cropcare.vercel.app`).

---

## Part 3: System Health Verification

Once deployed, verify system operations by hitting the automated health check endpoint:
```
GET https://cropcare-api.up.railway.app/api/v1/system/health
```
**Expected Standardized Response**:
```json
{
  "success": true,
  "message": "System health check completed",
  "data": {
    "status": "healthy",
    "database": "connected",
    "environment": "production"
  },
  "errors": null
}
```
