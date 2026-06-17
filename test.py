"""
BotBrain - Student Campus Navigator
Chanakya University
Author: Your Name
"""

from collections import deque
import heapq, math

# ---------------------------
# Backend: Campus Graph
# ---------------------------
GRAPH = {
    "Main Gate": {"Admin": 180},
    "Admin": {"Main Gate": 180, "Connecting Point": 80, "Library": 80},
    "Library": {"Admin": 80},
    "Connecting Point": {"Admin": 80, "AC Block A": 60, "AC Block C": 60, "AC Block B": 60},
    "AC Block A": {"Connecting Point": 60},
    "AC Block C": {"Connecting Point": 60},
    "AC Block B": {"Connecting Point": 60, "Laundry": 260, "Food Court": 200},
    "Laundry": {"AC Block B": 260, "Food Court": 80, "Hostel": 260},
    "Food Court": {"AC Block B": 200, "Laundry": 80, "Sports Arena": 280},
    "Hostel": {"Laundry": 260},
    "Sports Arena": {"Food Court": 280, "Volleyball Court": 500, "Cricket Ground": 485},
    "Volleyball Court": {"Sports Arena": 500},
    "Cricket Ground": {"Sports Arena": 485}
}

# Coordinates for heuristic (for A*)
COORDS = {
    "Main Gate": (0, 0),
    "Admin": (0, 180),
    "Library": (80, 180),
    "Connecting Point": (0, 100),
    "AC Block A": (-60, 100),
    "AC Block C": (60, 100),
    "AC Block B": (0, 40),
    "Laundry": (-100, 20),
    "Food Court": (0, 0),
    "Hostel": (-160, 0),
    "Sports Arena": (0, -280),
    "Volleyball Court": (-50, -330),
    "Cricket Ground": (50, -330)
}

# ---------------------------
# Backend: Helper Functions
# ---------------------------
def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return None
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    return path[::-1]

def path_distance(path, graph):
    if not path: return float('inf')
    dist = 0
    for i in range(len(path)-1):
        dist += graph[path[i]][path[i+1]]
    return dist

def walking_time(distance, speed=1.4):
    return round(distance / speed, 2)

# ---------------------------
# Backend: Search Algorithms
# ---------------------------
def bfs(start, goal, graph):
    queue = deque([start])
    came_from = {start: None}
    visited = set([start])
    nodes = 0
    while queue:
        current = queue.popleft()
        nodes += 1
        if current == goal:
            break
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
    return reconstruct_path(came_from, start, goal), nodes

def dfs(start, goal, graph):
    stack = [start]
    came_from = {start: None}
    visited = set()
    nodes = 0
    while stack:
        current = stack.pop()
        if current in visited: continue
        visited.add(current)
        nodes += 1
        if current == goal:
            break
        for neighbor in reversed(list(graph[current])):
            if neighbor not in visited:
                came_from[neighbor] = current
                stack.append(neighbor)
    return reconstruct_path(came_from, start, goal), nodes

def ucs(start, goal, graph):
    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodes = 0
    while pq:
        current_cost, current = heapq.heappop(pq)
        nodes += 1
        if current == goal:
            break
        for neighbor, weight in graph[current].items():
            new_cost = current_cost + weight
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(pq, (new_cost, neighbor))
    return reconstruct_path(came_from, start, goal), nodes

def heuristic(a, b, coords=COORDS):
    (x1, y1), (x2, y2) = coords[a], coords[b]
    return math.hypot(x2 - x1, y2 - y1)

def astar(start, goal, graph, coords=COORDS):
    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodes = 0
    while pq:
        _, current = heapq.heappop(pq)
        nodes += 1
        if current == goal:
            break
        for neighbor, weight in graph[current].items():
            new_cost = cost_so_far[current] + weight
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal, coords)
                came_from[neighbor] = current
                heapq.heappush(pq, (priority, neighbor))
    return reconstruct_path(came_from, start, goal), nodes

# ---------------------------
# Frontend: Menu Interface
# ---------------------------
def main():
    print("===== BotBrain Campus Navigator =====")
    print("Available locations:")
    for place in GRAPH.keys():
        print(" -", place)

    start = input("\nEnter START location: ").strip()
    goal = input("Enter DESTINATION location: ").strip()

    if start not in GRAPH or goal not in GRAPH:
        print("Invalid locations. Please try again.")
        return

    print("\nChoose Algorithm:")
    print("1. BFS")
    print("2. DFS")
    print("3. UCS")
    print("4. A* Search")

    choice = input("Enter choice (1-4): ")

    if choice == "1":
        path, nodes = bfs(start, goal, GRAPH)
    elif choice == "2":
        path, nodes = dfs(start, goal, GRAPH)
    elif choice == "3":
        path, nodes = ucs(start, goal, GRAPH)
    elif choice == "4":
        path, nodes = astar(start, goal, GRAPH, COORDS)
    else:
        print("Invalid choice!")
        return

    if path:
        dist = path_distance(path, GRAPH)
        time = walking_time(dist)
        print("\n===== Navigation Result =====")
        print("Path:", " -> ".join(path))
        print("Total Distance:", dist, "meters")
        print("Estimated Walking Time:", time, "seconds")
        print("Nodes Explored:", nodes)
    else:
        print("No path found!")

if _name_ == "_main_":
    main()