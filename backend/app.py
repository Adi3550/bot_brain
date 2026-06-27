import os
import math
import heapq
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import random

load_dotenv()

# Point Flask to the frontend folder to serve HTML/CSS
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# Unified Graph
graph = {
    "Main Gate": {"Admin Block": 160},
    "Admin Block": {"Main Gate": 160, "Library": 60, "Student Center": 60},
    "Library": {"Admin Block": 60},
    "Student Center": {"Admin Block": 60, "Academic Block A": 60, "Academic Block B": 60, "Academic Block C": 60},
    "Academic Block A": {"Student Center": 60},
    "Academic Block C": {"Student Center": 60},
    "Academic Block B": {"Student Center": 60, "Canteen": 180},
    "Canteen": {"Academic Block B": 180, "Main Hostel": 70, "Sports Complex": 220},
    "Main Hostel": {"Canteen": 70, "Medical Center": 220, "Auditorium": 500},
    "Medical Center": {"Main Hostel": 220},
    "Sports Complex": {"Canteen": 220},
    "Auditorium": {"Main Hostel": 500}
}

base_lat = 13.2246
base_lng = 77.7578
coordinates = {
    "Main Gate": (base_lat, base_lng),
    "Admin Block": (base_lat - 0.00160, base_lng),
    "Library": (base_lat - 0.00160, base_lng + 0.00060),
    "Student Center": (base_lat - 0.00220, base_lng),
    "Academic Block A": (base_lat - 0.00220, base_lng - 0.00060),
    "Academic Block C": (base_lat - 0.00220, base_lng + 0.00060),
    "Academic Block B": (base_lat - 0.00280, base_lng),
    "Canteen": (base_lat - 0.00460, base_lng),
    "Main Hostel": (base_lat - 0.00460, base_lng - 0.00070),
    "Medical Center": (base_lat - 0.00460, base_lng - 0.00290),
    "Sports Complex": (base_lat - 0.00460, base_lng + 0.00220),
    "Auditorium": (base_lat - 0.00960, base_lng - 0.00070)
}

building_info = {
    "Library": {"type": "Academic", "hours": "8 AM - 10 PM", "services": "Books, study rooms"},
    "Admin Block": {"type": "Admin", "hours": "9 AM - 5 PM", "services": "Office work"},
    "Main Hostel": {"type": "Residential", "hours": "24/7", "services": "Rooms"},
    "Canteen": {"type": "Service", "hours": "7 AM - 10 PM", "services": "Food"},
    "Sports Complex": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Sports"},
    "Academic Block A": {"type": "Academic", "hours": "8 AM - 6 PM", "services": "Classes"},
    "Academic Block B": {"type": "Academic", "hours": "8 AM - 6 PM", "services": "Classes"},
    "Academic Block C": {"type": "Academic", "hours": "8 AM - 6 PM", "services": "Classes"},
    "Main Gate": {"type": "Entry", "hours": "24/7", "services": "Security"},
    "Medical Center": {"type": "Service", "hours": "24/7", "services": "Health"},
    "Auditorium": {"type": "Academic", "hours": "8 AM - 10 PM", "services": "Events"},
    "Student Center": {"type": "Service", "hours": "8 AM - 8 PM", "services": "Activities"}
}

def calculate_heuristic(start, goal):
    x1, y1 = coordinates[start]
    x2, y2 = coordinates[goal]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 100000  # scaled roughly to meters for heuristic

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from and came_from[current]:
        current = came_from[current]
        path.append(current)
    return path[::-1]

def bfs(start, goal):
    queue = [start]
    came_from = {start: None}
    visited = {start}
    explored = 1
    while queue:
        current = queue.pop(0)
        if current == goal:
            break
        for neighbor in graph.get(current, {}):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                came_from[neighbor] = current
                explored += 1
    return reconstruct_path(came_from, goal) if goal in visited else None, explored

def dfs(start, goal):
    stack = [start]
    came_from = {start: None}
    visited = set()
    explored = 0
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        explored += 1
        if current == goal:
            break
        for neighbor in reversed(list(graph.get(current, {}).keys())):
            if neighbor not in visited:
                stack.append(neighbor)
                came_from[neighbor] = current
    return reconstruct_path(came_from, goal) if goal in visited else None, explored

def ucs(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = 1
    while frontier:
        current_cost, current = heapq.heappop(frontier)
        if current == goal:
            break
        for neighbor, cost in graph.get(current, {}).items():
            new_cost = current_cost + cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(frontier, (new_cost, neighbor))
                came_from[neighbor] = current
                explored += 1
    return reconstruct_path(came_from, goal) if goal in came_from else None, explored, cost_so_far.get(goal, 0)

def a_star(start, goal):
    frontier = []
    heapq.heappush(frontier, (0 + calculate_heuristic(start, goal), 0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = 1
    while frontier:
        _, current_cost, current = heapq.heappop(frontier)
        if current == goal:
            break
        for neighbor, cost in graph.get(current, {}).items():
            new_cost = current_cost + cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + calculate_heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, new_cost, neighbor))
                came_from[neighbor] = current
                explored += 1
    return reconstruct_path(came_from, goal) if goal in came_from else None, explored, cost_so_far.get(goal, 0)

def calculate_distance(path):
    if not path or len(path) < 2: return 0
    return sum(graph[path[i]][path[i+1]] for i in range(len(path)-1))

@app.route('/locations', methods=['GET'])
def get_locations():
    return jsonify({
        "nodes": list(graph.keys()),
        "coordinates": coordinates,
        "building_info": building_info
    })

@app.route('/events', methods=['GET'])
def get_events():
    events_mock = {
        "Library": "Guest lecture at 4 PM in Hall A.",
        "Sports Complex": "Inter-college basketball match ongoing.",
        "Auditorium": "Tech Symposium 2026 Registration open.",
        "Canteen": "Special menu: 20% off all beverages today!"
    }
    return jsonify(events_mock)

@app.route('/find_path', methods=['GET'])
def find_path():
    start = request.args.get('start')
    goal = request.args.get('goal')
    algo = request.args.get('algo', 'A*').upper()
    
    if start not in graph or goal not in graph:
        return jsonify({"error": "Invalid start or goal location."}), 400
        
    if algo == 'BFS':
        path, explored = bfs(start, goal)
        dist = calculate_distance(path)
    elif algo == 'DFS':
        path, explored = dfs(start, goal)
        dist = calculate_distance(path)
    elif algo == 'UCS':
        path, explored, dist = ucs(start, goal)
    elif algo == 'A*':
        path, explored, dist = a_star(start, goal)
    else:
        return jsonify({"error": "Invalid algorithm."}), 400

    if not path:
        return jsonify({"error": "No path found."}), 404
        
    # Generate turn-by-turn directions
    directions = []
    for i in range(len(path) - 1):
        d = graph[path[i]][path[i+1]]
        directions.append(f"Walk {d}m to {path[i+1]}")
        
    return jsonify({
        "path": path,
        "distance": dist,
        "nodes_explored": explored,
        "walking_time": round(dist / 1.4 / 60, 2), # 1.4 m/s walking speed -> mins
        "directions": directions
    })

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get("message", "")
    
    if not model:
        return jsonify({"reply": "AI Chatbot is currently unavailable (Missing GEMINI_API_KEY). But I can tell you we have a beautiful campus!"})
    
    prompt = f"""
    You are BotBrain, the official AI navigator for our campus. Be friendly, concise, and helpful.
    Here is the campus information:
    Buildings: {', '.join(locations for locations in graph.keys())}.
    Building Details: {building_info}
    Events Today: Library (Lecture at 4 PM), Sports Complex (Basketball match), Auditorium (Tech Symposium), Canteen (20% off beverages).
    
    User message: {message}
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text.strip()})
    except Exception as e:
        return jsonify({"reply": f"Sorry, my AI brain encountered an error: {str(e)}"}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
