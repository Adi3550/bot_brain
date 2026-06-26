# BotBrain - Campus Navigator 🗺️🤖

BotBrain is an intelligent, modern web application designed to help students and visitors navigate a campus efficiently. It calculates the shortest paths between buildings using various algorithms and features an AI-powered assistant (via Google Gemini) that can answer questions about building hours, services, and live events.

## Features ✨
- **Pathfinding Engine:** Compare shortest paths using **A***, **UCS**, **BFS**, and **DFS**.
- **Interactive Map:** Modern dark-themed Leaflet.js map with animated turn-by-turn route drawing.
- **AI Chatbot:** Integrated with Google Gemini Flash to answer campus-related queries intelligently.
- **Data Visualization:** Real-time Chart.js bar graphs comparing algorithm efficiency (Nodes Explored).
- **Responsive UI:** Built with Tailwind CSS for seamless desktop and mobile experiences.

## Tech Stack 🛠️
- **Frontend:** HTML5, Tailwind CSS, Leaflet.js, Chart.js
- **Backend:** Python, Flask, Flask-CORS, Gunicorn
- **AI Integration:** Google Generative AI (Gemini 1.5 Flash)

## Setup & Local Development 🚀

### 1. Backend Setup
1. Open a terminal in the `backend/` directory.
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your Environment Variables:
   - Copy `.env.example` to `.env`
   - Add your Google AI Studio API key: `GEMINI_API_KEY=your_key_here`
5. Run the server:
   ```bash
   python app.py
   ```
   *(The server will run on `http://127.0.0.1:5000`)*

### 2. Frontend Setup
1. Open the `frontend/` directory.
2. Simply double-click `index.html` to open it in your browser!
3. Ensure the backend is running so the frontend can fetch locations and paths.

## Deployment 🌍

### Deploying the Backend on Render
1. Create a new **Web Service** on Render.
2. Point it to this repository.
3. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. **Environment Variables:** Add `GEMINI_API_KEY` to Render's environment variables.
5. Once deployed, update the `API_BASE` variable in `frontend/index.html` with your new Render URL.

### Deploying the Frontend on GitHub Pages
1. Go to your GitHub repository Settings > Pages.
2. Select the `main` branch and `/` root folder, then click Save.
3. Your frontend will be live in minutes!

---
*All original assignment documentation has been preserved in the `docs/` folder.*