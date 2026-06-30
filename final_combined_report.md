# BotBrain - Campus Navigator: Final Combined Report

## 📖 Project Overview
BotBrain is an intelligent, interactive campus navigation system that combines advanced graph pathfinding algorithms with a generative AI assistant. It provides users with turn-by-turn directions across campus and answers queries about building services, hours, and events.

## 🛠️ Technology Stack

### Frontend Architecture
- **Core:** HTML5, Vanilla JavaScript (ES6+), CSS3
- **Styling Framework:** Tailwind CSS (via CDN)
  - Used for rapid prototyping, responsive design, and modern aesthetic utilities.
- **Mapping Library:** Leaflet.js
  - Utilized for rendering the interactive map, custom markers, and dynamic polyline drawing for routes.
  - Configured with Google Maps Satellite Hybrid tiles for highly detailed, real-world imagery.
- **Data Visualization:** Chart.js
  - Used to dynamically render bar charts comparing the efficiency (nodes explored) of different pathfinding algorithms.
- **UI/UX Design Language:** Glassmorphism
  - Heavy use of `backdrop-blur`, semi-transparent deep backgrounds, and gradient typography to create a premium, full-screen immersive overlay.

### Backend Architecture
- **Language:** Python 3.10+
- **Web Framework:** Flask (along with `flask-cors` for origin management)
- **Production Server:** Gunicorn (WSGI server configured for Render deployment)
- **AI Integration:** Google Generative AI SDK (`google-generativeai==0.8.6`)
  - Powered by the `gemini-pro` model for natural language processing.
- **Data Structures:** NetworkX (or custom graph dictionaries)
  - Used to model the campus as a mathematical graph (nodes = buildings, edges = walkways with distances).

## 🚀 Key Features & What Was Accomplished

### 1. Interactive Full-Screen Campus Map
- Mapped 11 precise campus locations (e.g., Main Gate, Library, Auditorium, Academic Blocks, Hostels) using exact GPS coordinates.
- Replaced standard map views with a highly detailed Google Maps Satellite layout.
- Added interactive map markers with custom Emojis and popups displaying building hours, services, and dynamic events.

### 2. Multi-Algorithm Pathfinding Engine
- Developed and exposed an API that calculates the optimal route between any two campus locations.
- **Implemented Algorithms:**
  - **A* (A-Star):** Heuristic-based optimal routing.
  - **Uniform Cost Search (UCS):** Distance-based optimal routing.
  - **Breadth-First Search (BFS) & Depth-First Search (DFS):** Unweighted graph traversal.
- Features turn-by-turn directions and calculates total distance alongside estimated walking times.
- Added a visual path animation that literally "draws" the route on the map using CSS `stroke-dasharray`.

### 3. Smart AI Chatbot Assistant
- Integrated Google's Gemini AI to answer questions contextually based on injected campus data.
- **Offline Rule-Based Fallback:** Implemented a robust, zero-dependency offline backup brain. If the API key fails or rate-limits, the system instantly catches the error and falls back to an internal pattern-matching engine that guarantees 100% uptime for core queries (library hours, food locations, events).

### 4. "Apple Vision Pro" Style Responsive UI
- Completely overhauled the interface to feature a massive, 100% screen-width background map.
- Built floating, frosted-glass control panels for the Pathfinding inputs and Chatbot.
- Designed a flawless mobile and tablet layout where the interactive map stays securely locked to the top of the screen, while the control panels remain perfectly scrollable underneath.

## 📦 Deployment
- **Platform:** Render.com
- **CI/CD:** Connected directly to GitHub main branch.
- Configured explicit `requirements.txt` pinning to ensure robust server builds and prevent dependency mismatches across environments.
