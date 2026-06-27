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
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    model = None

# Unified Graph
graph = {
    "Main Gate": {"Admin Block": 320},
    "Admin Block": {"Main Gate": 320, "Library": 10, "Auditorium": 10, "Academic Block B": 300, "Academic Block C": 370, "Academic Block D": 400},
    "Library": {"Admin Block": 10},
    "Auditorium": {"Admin Block": 10},
    "Academic Block B": {"Admin Block": 300},
    "Academic Block C": {"Admin Block": 370, "Canteen": 120, "Main Hostel": 200},
    "Academic Block D": {"Admin Block": 400},
    "Canteen": {"Academic Block C": 120, "Medical Center": 10, "Main Hostel": 170, "Sports Ground": 510},
    "Medical Center": {"Canteen": 10},
    "Main Hostel": {"Canteen": 170, "Academic Block C": 200},
    "Sports Ground": {"Canteen": 510}
}

coordinates = {
    "Main Gate": (13.221371, 77.755112),
    "Admin Block": (13.222201, 77.755277),
    "Library": (13.221823, 77.755435),
    "Auditorium": (13.222017, 77.755388),
    "Academic Block B": (13.223147, 77.754911),
    "Academic Block C": (13.223345, 77.755969),
    "Academic Block D": (13.222556, 77.756232),
    "Canteen": (13.224877, 77.757148),
    "Medical Center": (13.224494, 77.757009),
    "Main Hostel": (13.224525, 77.758944),
    "Sports Ground": (13.228847, 77.757402)
}

building_info = {
    "Main Gate": {"type": "Entry", "hours": "24/7", "services": "Security, Campus Map"},
    "Admin Block": {"type": "Admin", "hours": "9 AM - 5 PM", "services": "Admissions, Finance, Offices"},
    "Library": {"type": "Academic", "hours": "8 AM - 10 PM", "services": "Books, Study Rooms, Computers"},
    "Auditorium": {"type": "Academic", "hours": "Event Based", "services": "Events, Seminars, Workshops"},
    "Academic Block B": {"type": "Academic", "hours": "Under Construction", "services": "Future Classrooms"},
    "Academic Block C": {"type": "Academic", "hours": "8 AM - 6 PM", "services": "Classrooms, Labs, Faculty Cabins"},
    "Academic Block D": {"type": "Academic", "hours": "Under Construction", "services": "Future Classrooms"},
    "Main Hostel": {"type": "Residential", "hours": "24/7", "services": "Accommodation, Common Room"},
    "Canteen": {"type": "Service", "hours": "7 AM - 9 PM", "services": "Food Court, Beverages, Snacks"},
    "Medical Center": {"type": "Service", "hours": "24/7", "services": "First Aid, Doctor on Call, Pharmacy"},
    "Sports Ground": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Cricket Pitch, Running Track, Pavilion"}
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
        "Sports Ground": "Inter-college cricket match ongoing.",
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
    Events Today: Library (Lecture at 4 PM), Sports Ground (Cricket match), Auditorium (Tech Symposium), Canteen (20% off beverages).
    
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
