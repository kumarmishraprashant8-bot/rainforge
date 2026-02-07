# 🌧️ Rain Forge Deployment Guide

This guide will help you deploy the "Rain Forge" application for your hackathon demo. We will deploy the **Frontend to Vercel** and the **Backend to Render**.

## Prerequisites

1.  **GitHub Account**: You need to push this code to a GitHub repository.
2.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
3.  **Render Account**: Sign up at [render.com](https://render.com).

---

## Step 1: Push to GitHub

If you haven't already, push this code to a new GitHub repository.

```bash
git init
git add .
git commit -m "Initial commit for deployment"
# Create a repo on GitHub, then run:
git remote add origin https://github.com/YOUR_USERNAME/rain-forge-demo.git
git push -u origin main
```

---

## Step 2: Deploy Backend (Render)

1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Blueprints**.
3.  Connect your GitHub repository.
4.  Render will detect the `render.yaml` file in the root.
5.  Click **Apply**. Render will automatically create the Database and the Backend Service.
6.  **Wait for deployment**: It might take a few minutes.
7.  **Copy the Backend URL**: Once done, you will see a URL like `https://rainforge-backend.onrender.com`. Copy this!

---

## Step 3: Deploy Frontend (Vercel)

1.  Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  **Configure Project**:
    *   **Framework Preset**: Vite
    *   **Root Directory**: Click `Edit` and select `frontend`. **(Important!)**
    *   **Environment Variables**:
        *   Name: `VITE_API_URL`
        *   Value: Paste your Render Backend URL (e.g., `https://rainforge-backend.onrender.com`) **without the trailing slash**.
5.  Click **Deploy**.

---

## Step 4: Final Connection

1.  Once the Frontend is deployed, Vercel will give you a domain (e.g., `https://rain-forge-demo.vercel.app`).
2.  Go back to **Render Dashboard** -> **rainforge-backend** -> **Environment**.
3.  Edit the `ALLOWED_ORIGINS` variable. Add your Vercel URL to the list (comma-separated).
    *   Example: `https://rain-forge-demo.vercel.app`
4.  **Save Changes** (Render will redeploy).

---

## ✅ Deployment Complete!

Visit your Vercel URL. Your app should now be live and connected to the backend!

### Troubleshooting

*   **Global install errors**: Render's free tier spins down after inactivity. The first request might take 50 seconds.
*   **CORS errors**: Make sure your Vercel URL is exactly matched in the Backend `ALLOWED_ORIGINS`.
