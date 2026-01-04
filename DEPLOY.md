# 🚀 Deploy to Render

## Prerequisites
- GitHub account with this repo pushed
- [Render account](https://render.com) (free tier available)
- API keys ready: `GOOGLE_API_KEY`, `SONAR_API_KEY`

---

## Quick Deploy (Blueprint)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **New** → **Blueprint**
   - Connect your GitHub repo
   - Select the repo with `render.yaml`
   - Click **Apply**

3. **Set Environment Variables**
   
   After deployment starts, go to each service and add:
   
   | Variable | Service | Required |
   |----------|---------|----------|
   | `GOOGLE_API_KEY` | Backend | ✅ Yes |
   | `SONAR_API_KEY` | Backend | ✅ Yes |
   | `TWILIO_ACCOUNT_SID` | Backend | Optional |
   | `TWILIO_AUTH_TOKEN` | Backend | Optional |
   | `TWILIO_WHATSAPP_NUMBER` | Backend | Optional |

4. **Wait for Build** (~5-10 minutes for first deploy)

5. **Access Your App**
   - Backend: `https://health-chatbot-backend.onrender.com/health`
   - Frontend: `https://health-chatbot-frontend.onrender.com`

---

## Manual Deploy (Alternative)

### Backend Service
1. New → Web Service → Connect repo
2. **Name**: `health-chatbot-backend`
3. **Build Command**: `pip install -r backend/requirements-render.txt`
4. **Start Command**: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
5. Add environment variables

### Frontend Service
1. New → Web Service → Connect repo
2. **Name**: `health-chatbot-frontend`
3. **Build Command**: `pip install -r frontend/requirements-render.txt`
4. **Start Command**: `cd frontend && streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add `API_URL` = your backend URL (e.g., `https://health-chatbot-backend.onrender.com`)

---

## Notes

> ⚠️ **Free Tier Limitation**: Services spin down after 15 min of inactivity. First request after idle may take 30-60 seconds.

> 💡 **Tip**: To keep services active, use [UptimeRobot](https://uptimerobot.com) to ping your `/health` endpoint every 14 minutes.
