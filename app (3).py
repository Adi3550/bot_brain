import heapq
import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for the entire app

# Graph from your assignment's map
graph = {
    'Main Gate': {'Admin Block': 160},
    'Admin Block': {'Main Gate': 160, 'Library': 60, 'Connecting Point': 60},
    'Library': {'Admin Block': 60},
    'Connecting Point': {'Admin Block': 60, 'Academic Block A': 60, 'Academic Block C': 60, 'Academic Block B': 60},
    'Academic Block A': {'Connecting Point': 60},
    'Academic Block C': {'Connecting Point': 60},
    'Academic Block B': {'Connecting Point': 60, 'Foodcourt': 180},
    'Foodcourt': {'Academic Block B': 180, 'Hostel': 70, 'Sports Arena': 220},
    'Hostel': {'Foodcourt': 70, 'Laundry': 220, 'Volleyball Court': 500},
    'Laundry': {'Hostel': 220},
    'Sports Arena': {'Foodcourt': 220, 'Cricket Ground': 410},
    'Cricket Ground': {'Sports Arena': 410},
    'Volleyball Court': {'Hostel': 500}
}

# Coordinates for A* heuristic and Leaflet map
coordinates = {
    'Main Gate': (0, 0),
    'Admin Block': (0, -160),
    'Library': (60, -160),
    'Connecting Point': (0, -220),
    'Academic Block A': (-60, -220),
    'Academic Block C': (60, -220),
    'Academic Block B': (0, -280),
    'Foodcourt': (0, -460),
    'Hostel': (-70, -460),
    'Laundry': (-290, -460),
    'Sports Arena': (220, -460),
    'Cricket Ground': (630, -460),
    'Volleyball Court': (-70, -960)
}

# Building info
building_info = {
    'Library': {'type': 'Academic', 'hours': '8 AM - 10 PM', 'services': 'Study halls, books, computers'},
    'Admin Block': {'type': 'Admin', 'hours': '9 AM - 5 PM', 'services': 'Admissions, fees, admin support'},
    'Hostel': {'type': 'Residential', 'hours': '24/7', 'services': 'Rooms, WiFi, security, common areas'},
    'Foodcourt': {'type': 'Service', 'hours': '7 AM - 10 PM', 'services': 'Meals, snacks, dining'},
    'Sports Arena': {'type': 'Sports', 'hours': '6 AM - 8 PM', 'services': 'Gym, fields, equipment'},
    'Academic Block A': {'type': 'Academic', 'hours': '8 AM - 6 PM', 'services': 'Classrooms, labs'},
    'Academic Block B': {'type': 'Academic', 'hours': '8 AM - 6 PM', 'services': 'Classrooms, labs'},
    'Academic Block C': {'type': 'Academic', 'hours': '8 AM - 6 PM', 'services': 'Classrooms, labs'},
    'Main Gate': {'type': 'Entry', 'hours': '24/7', 'services': 'Security check'},
    'Laundry': {'type': 'Service', 'hours': '8 AM - 8 PM', 'services': 'Washing machines'},
    'Volleyball Court': {'type': 'Sports', 'hours': '6 AM - 8 PM', 'services': 'Court access'},
    'Cricket Ground': {'type': 'Sports', 'hours': '6 AM - 8 PM', 'services': 'Field access'},
    'Connecting Point': {'type': 'Junction', 'hours': 'N/A', 'services': 'Pathway intersection'}
}

# Heuristic: Euclidean distance
def heuristic(a, b):
    (x1, y1) = coordinates[a]
    (x2, y2) = coordinates[b]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Reconstruct path
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

# BFS
def bfs(start, goal):
    queue = [start]
    came_from = {start: None}
    visited = {start}
    explored_count = 1
    steps = [f"BFS Checking: {start}"]
    while queue:
        current = queue.pop(0)
        if current == goal:
            break
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                came_from[neighbor] = current
                explored_count += 1
                steps.append(f"BFS Checking: {neighbor}")
    path = reconstruct_path(came_from, goal) if goal in visited else None
    return path, explored_count, steps

# DFS
def dfs(start, goal):
    stack = [start]
    came_from = {start: None}
    visited = set()
    explored_count = 0
    steps = []
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        explored_count += 1
        steps.append(f"DFS Checking: {current}")
        if current == goal:
            break
        for neighbor in reversed(list(graph.get(current, []))):
            if neighbor not in visited:
                stack.append(neighbor)
                came_from[neighbor] = current
    path = reconstruct_path(came_from, goal) if goal in visited else None
    return path, explored_count, steps

# UCS
def ucs(start, goal):
    frontier = []  # (cost, node)
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = 1
    steps = [f"UCS Checking: {start} (cost: 0)"]
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
                steps.append(f"UCS Checking: {neighbor} (cost: {new_cost})")
    path = reconstruct_path(came_from, goal) if goal in came_from else None
    total_distance = cost_so_far.get(goal, 0)
    return path, explored, steps, total_distance

# A*
def a_star(start, goal):
    frontier = []  # (priority, cost, node)
    heapq.heappush(frontier, (0 + heuristic(start, goal), 0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = 1
    steps = [f"A* Checking: {start} (cost: 0, heuristic: {heuristic(start, goal):.2f})"]
    while frontier:
        _, current_cost, current = heapq.heappop(frontier)
        if current == goal:
            break
        for neighbor, cost in graph.get(current, {}).items():
            new_cost = current_cost + cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, new_cost, neighbor))
                came_from[neighbor] = current
                explored += 1
                steps.append(f"A* Checking: {neighbor} (cost: {new_cost}, heuristic: {heuristic(neighbor, goal):.2f})")
    path = reconstruct_path(came_from, goal) if goal in came_from else None
    total_distance = cost_so_far.get(goal, 0)
    return path, explored, steps, total_distance

# Calculate total distance
def calculate_distance(path):
    if not path or len(path) < 2:
        return 0
    dist = 0
    for i in range(len(path) - 1):
        if path[i] in graph and path[i + 1] in graph[path[i]]:
            dist += graph[path[i]][path[i + 1]]
    return dist

# Calculate walking time
def calculate_walking_time(distance):
    speed = 1.4  # meters per second
    time_seconds = distance / speed
    return round(time_seconds / 60, 2)

# API Endpoints
@app.route('/find_path', methods=['GET'])
def find_path():
    start = request.args.get('start')
    goal = request.args.get('goal')
    algo = request.args.get('algo').upper()
    if start not in graph or goal not in graph:
        return jsonify({"error": "Invalid locations."}), 400
    if algo == 'BFS':
        path, explored, steps = bfs(start, goal)
        dist = calculate_distance(path)
    elif algo == 'DFS':
        path, explored, steps = dfs(start, goal)
        dist = calculate_distance(path)
    elif algo == 'UCS':
        path, explored, steps, dist = ucs(start, goal)
    elif algo == 'A*':
        path, explored, steps, dist = a_star(start, goal)
    else:
        return jsonify({"error": "Invalid algorithm."}), 400
    if path:
        return jsonify({
            "path": path,
            "distance": dist,
            "walking_time": calculate_walking_time(dist),
            "nodes_explored": explored,
            "steps": steps
        })
    else:
        return jsonify({"error": "No path found."}), 404

@app.route('/building_info', methods=['GET'])
def get_building_info():
    building = request.args.get('building')
    info = building_info.get(building, None)
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "No info available."}), 404

@app.route('/compare_algorithms', methods=['GET'])
def get_compare_algorithms():
    pairs = [
        ('Hostel', 'Library'),
        ('Main Gate', 'Admin Block'),
        ('Academic Block A', 'Sports Arena')
    ]
    results = []
    for start, goal in pairs:
        bfs_path, bfs_expl, _ = bfs(start, goal)
        dfs_path, dfs_expl, _ = dfs(start, goal)
        ucs_path, ucs_expl, _, ucs_cost = ucs(start, goal)
        a_path, a_expl, _, a_cost = a_star(start, goal)
        results.append({
            'Pair': f"{start} to {goal}",
            'BFS Nodes': bfs_expl,
            'DFS Nodes': dfs_expl,
            'UCS Nodes': ucs_expl,
            'A* Nodes': a_expl,
            'Shortest Path (UCS/A*)': ucs_cost
        })
    return jsonify(results)

@app.route('/locations', methods=['GET'])
def get_locations():
    return jsonify(sorted(graph.keys()))

if __name__ == '__main__':
    app.run(debug=True, port=5000)