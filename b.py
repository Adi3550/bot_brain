from flask import Flask, jsonify, request
import math

app = Flask(__name__)

# List of campus locations
locations = [
    "Main Gate", "Admin Block", "Cafe", "Library", "Auditorium",
    "Academic Block B", "Food Court", "Laundry", "Faculty Hostel",
    "Hostel", "Sports Complex", "Football Ground", "Cricket Ground",
    "Basketball Court", "Volleyball Court", "Tennis Court"
]

# Graph with distances in meters (estimated based on coordinates)
graph = {
    "Main Gate": {"Admin Block": 100, "Cafe": 120},
    "Admin Block": {"Main Gate": 100, "Library": 50, "Auditorium": 60},
    "Cafe": {"Main Gate": 120, "Admin Block": 80},
    "Library": {"Admin Block": 50, "Auditorium": 70},
    "Auditorium": {"Admin Block": 60, "Library": 70, "Academic Block B": 150},
    "Academic Block B": {"Auditorium": 150, "Food Court": 200},
    "Food Court": {"Academic Block B": 200, "Laundry": 50, "Faculty Hostel": 70, "Hostel": 300},
    "Laundry": {"Food Court": 50, "Faculty Hostel": 40},
    "Faculty Hostel": {"Food Court": 70, "Laundry": 40, "Hostel": 250},
    "Hostel": {"Food Court": 300, "Faculty Hostel": 250, "Sports Complex": 500},
    "Sports Complex": {"Hostel": 500, "Football Ground": 100, "Cricket Ground": 150, "Basketball Court": 200, "Volleyball Court": 250, "Tennis Court": 220},
    "Football Ground": {"Sports Complex": 100},
    "Cricket Ground": {"Sports Complex": 150},
    "Basketball Court": {"Sports Complex": 200},
    "Volleyball Court": {"Sports Complex": 250},
    "Tennis Court": {"Sports Complex": 220}
}

# Coordinates for A* heuristic (latitude, longitude from frontend)
coordinates = {
    "Main Gate": (13.2213517, 77.7551040),
    "Admin Block": (13.2221039, 77.7551951),
    "Cafe": (13.2222655, 77.7551286),
    "Library": (13.2220964, 77.7554430),
    "Auditorium": (13.2222219, 77.7552483),
    "Academic Block B": (13.2232977, 77.7559360),
    "Food Court": (13.2248993, 77.7571096),
    "Laundry": (13.2245360, 77.7571372),
    "Faculty Hostel": (13.2236718, 77.7571935),
    "Hostel": (13.2244538, 77.7591013),
    "Sports Complex": (13.2281226, 77.7577549),
    "Football Ground": (13.2280384, 77.7563453),
    "Cricket Ground": (13.2284361, 77.7575469),
    "Basketball Court": (13.2287872, 77.7581721),
    "Volleyball Court": (13.2286880, 77.7585798),
    "Tennis Court": (13.2284498, 77.7583519)
}

# Building details
building_info = {
    "Main Gate": {"type": "Entry", "hours": "24/7", "services": "Security"},
    "Admin Block": {"type": "Admin", "hours": "9 AM - 5 PM", "services": "Office work"},
    "Cafe": {"type": "Service", "hours": "8 AM - 8 PM", "services": "Snacks, drinks"},
    "Library": {"type": "Academic", "hours": "8 AM - 10 PM", "services": "Books, study rooms"},
    "Auditorium": {"type": "Academic", "hours": "8 AM - 10 PM", "services": "Events"},
    "Academic Block B": {"type": "Academic", "hours": "8 AM - 6 PM", "services": "Classes"},
    "Food Court": {"type": "Service", "hours": "7 AM - 10 PM", "services": "Food"},
    "Laundry": {"type": "Service", "hours": "8 AM - 8 PM", "services": "Washing"},
    "Faculty Hostel": {"type": "Residential", "hours": "24/7", "services": "Rooms"},
    "Hostel": {"type": "Residential", "hours": "24/7", "services": "Rooms, WiFi"},
    "Sports Complex": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Fields, gym"},
    "Football Ground": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Field access"},
    "Cricket Ground": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Field access"},
    "Basketball Court": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Court access"},
    "Volleyball Court": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Court access"},
    "Tennis Court": {"type": "Sports", "hours": "6 AM - 8 PM", "services": "Court access"}
}

# Heuristic: Haversine distance (approximate for simplicity)
def calculate_heuristic(start, goal):
    from math import radians, sin, cos, sqrt, atan2
    lat1, lon1 = map(radians, coordinates[start])
    lat2, lon2 = map(radians, coordinates[goal])
    R = 6371000  # Earth radius in meters
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Reconstruct path
def get_path(came_from, goal):
    path = [goal]
    current = goal
    while current in came_from and came_from[current] is not None:
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
    path = get_path(came_from, goal) if goal in visited else None
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
    path = get_path(came_from, goal) if goal in visited else None
    return path, explored_count, steps

# UCS
def ucs(start, goal):
    from queue import PriorityQueue
    pq = PriorityQueue()
    pq.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored_count = 1
    steps = [f"UCS Checking: {start} (cost: 0)"]
    while not pq.empty():
        current_cost, current = pq.get()
        if current == goal:
            break
        for neighbor, distance in graph.get(current, {}).items():
            new_cost = current_cost + distance
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                pq.put((new_cost, neighbor))
                came_from[neighbor] = current
                explored_count += 1
                steps.append(f"UCS Checking: {neighbor} (cost: {new_cost})")
    path = get_path(came_from, goal) if goal in cost_so_far else None
    total_distance = cost_so_far.get(goal, 0)
    return path, explored_count, steps, total_distance

# A*
def a_star(start, goal):
    from queue import PriorityQueue
    pq = PriorityQueue()
    pq.put((calculate_heuristic(start, goal), 0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored_count = 1
    steps = [f"A* Checking: {start} (cost: 0, heuristic: {calculate_heuristic(start, goal):.2f})"]
    while not pq.empty():
        _, current_cost, current = pq.get()
        if current == goal:
            break
        for neighbor, distance in graph.get(current, {}).items():
            new_cost = current_cost + distance
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + calculate_heuristic(neighbor, goal)
                pq.put((priority, new_cost, neighbor))
                came_from[neighbor] = current
                explored_count += 1
                steps.append(f"A* Checking: {neighbor} (cost: {new_cost}, heuristic: {calculate_heuristic(neighbor, goal):.2f})")
    path = get_path(came_from, goal) if goal in cost_so_far else None
    total_distance = cost_so_far.get(goal, 0)
    return path, explored_count, steps, total_distance

# Calculate total distance
def calculate_distance(path):
    if not path or len(path) < 2:
        return 0
    total = 0
    for i in range(len(path) - 1):
        if path[i] in graph and path[i + 1] in graph[path[i]]:
            total += graph[path[i]][path[i + 1]]
    return total

# Calculate walking time
def calculate_walking_time(distance):
    speed = 1.4  # meters per second
    time_seconds = distance / speed
    return round(time_seconds / 60, 2)

# API Endpoints
@app.route('/locations', methods=['GET'])
def get_locations():
    return jsonify(sorted(locations))

@app.route('/find_path', methods=['GET'])
def find_path():
    start = request.args.get('start')
    goal = request.args.get('goal')
    algo = request.args.get('algo', 'A*').upper()  # Default to A* if not specified
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)