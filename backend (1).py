# BotBrain 

# List of campus locations (12 buildings as required)
locations = [
    "Academic Block A", "Academic Block B", "Academic Block C",
    "Admin Block", "Auditorium", "Canteen",
    "Library", "Main Gate", "Main Hostel",
    "Medical Center", "Sports Complex", "Student Center"
]

# Simple graph with distances in meters 
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

# Coordinates for A* heuristic 
coordinates = {
    "Main Gate": (0, 0),
    "Admin Block": (0, -160),
    "Library": (60, -160),
    "Student Center": (0, -220),
    "Academic Block A": (-60, -220),
    "Academic Block C": (60, -220),
    "Academic Block B": (0, -280),
    "Canteen": (0, -460),
    "Main Hostel": (-70, -460),
    "Medical Center": (-290, -460),
    "Sports Complex": (220, -460),
    "Auditorium": (-70, -960)
}

# Building details 
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

# Helper function to calculate straight-line distance (for A* heuristic)
def calculate_heuristic(start, goal):
    x1, y1 = coordinates[start]
    x2, y2 = coordinates[goal]
    # Using the Pythagorean theorem (learned in math class!)
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance

# Helper function to get the path from start to goal
def get_path(came_from, goal):
    path = [goal]
    current = goal
    while current in came_from and came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()  # Flip the path to start from the beginning
    return path

# BFS - Breadth-First Search (explores level by level like a wave)
def bfs(start, goal):
    # Use a queue to visit places one level at a time
    queue = [start]
    # Keep track of where we came from
    came_from = {start: None}
    # Mark visited places
    visited = {start}
    # Count how many places we check
    explored_count = 1
    # Store steps for showing work
    steps = [f"BFS Checking: {start}"]
    
    while queue:
        current = queue.pop(0)  # Take the first place from the queue
        if current == goal:
            break  # We found the goal!
        for neighbor in graph.get(current, []):  # Get all connected places
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)  # Add to queue to check next
                came_from[neighbor] = current  # Remember where we came from
                explored_count += 1
                steps.append(f"BFS Checking: {neighbor}")
    path = get_path(came_from, goal) if goal in visited else None
    return path, explored_count, steps

# DFS - Depth-First Search (goes deep before backtracking)
def dfs(start, goal):
    # Use a stack to go deep into one path
    stack = [start]
    # Keep track of where we came from
    came_from = {start: None}
    # Mark visited places
    visited = set()
    # Count how many places we check
    explored_count = 0
    # Store steps for showing work
    steps = []
    
    while stack:
        current = stack.pop()  # Take the last place from the stack
        if current in visited:
            continue  # Skip if already visited
        visited.add(current)
        explored_count += 1
        steps.append(f"DFS Checking: {current}")
        if current == goal:
            break  # We found the goal!
        for neighbor in reversed(list(graph.get(current, []))):  # Check in reverse for depth
            if neighbor not in visited:
                stack.append(neighbor)  # Add to stack to go deeper
                came_from[neighbor] = current  # Remember where we came from
    path = get_path(came_from, goal) if goal in visited else None
    return path, explored_count, steps

# UCS - Uniform Cost Search (finds cheapest path first)
def ucs(start, goal):
    # Use a priority queue to pick the cheapest path
    from queue import PriorityQueue
    pq = PriorityQueue()
    pq.put((0, start))  # (cost, place)
    # Keep track of where we came from
    came_from = {start: None}
    # Track total cost to each place
    cost_so_far = {start: 0}
    # Count how many places we check
    explored_count = 1
    # Store steps for showing work
    steps = [f"UCS Checking: {start} (cost: 0)"]
    
    while not pq.empty():
        current_cost, current = pq.get()  # Get the cheapest path
        if current == goal:
            break  # We found the goal!
        for neighbor, distance in graph.get(current, {}).items():
            new_cost = current_cost + distance  # Add the distance to get new cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                pq.put((new_cost, neighbor))  # Add to queue with new cost
                came_from[neighbor] = current  # Remember where we came from
                explored_count += 1
                steps.append(f"UCS Checking: {neighbor} (cost: {new_cost})")
    path = get_path(came_from, goal) if goal in cost_so_far else None
    total_distance = cost_so_far.get(goal, 0)
    return path, explored_count, steps, total_distance

# A* - A* Search (uses heuristic to find path faster)
def a_star(start, goal):
    # Use a priority queue with heuristic
    from queue import PriorityQueue
    pq = PriorityQueue()
    pq.put((calculate_heuristic(start, goal), 0, start))  # (priority, cost, place)
    # Keep track of where we came from
    came_from = {start: None}
    # Track total cost to each place
    cost_so_far = {start: 0}
    # Count how many places we check
    explored_count = 1
    # Store steps for showing work
    steps = [f"A* Checking: {start} (cost: 0, heuristic: {calculate_heuristic(start, goal):.2f})"]
    
    while not pq.empty():
        _, current_cost, current = pq.get()  # Get the best priority
        if current == goal:
            break  # We found the goal!
        for neighbor, distance in graph.get(current, {}).items():
            new_cost = current_cost + distance  # Add the distance
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + calculate_heuristic(neighbor, goal)  # Add heuristic
                pq.put((priority, new_cost, neighbor))  # Add to queue
                came_from[neighbor] = current  # Remember where we came from
                explored_count += 1
                steps.append(f"A* Checking: {neighbor} (cost: {new_cost}, heuristic: {calculate_heuristic(neighbor, goal):.2f})")
    path = get_path(came_from, goal) if goal in cost_so_far else None
    total_distance = cost_so_far.get(goal, 0)
    return path, explored_count, steps, total_distance

# Calculate total distance of a path
def calculate_distance(path):
    if not path or len(path) < 2:
        return 0
    total = 0
    for i in range(len(path) - 1):
        if path[i] in graph and path[i + 1] in graph[path[i]]:
            total += graph[path[i]][path[i + 1]]
    return total

# Calculate walking time in minutes
def calculate_walking_time(distance):
    speed = 1.4  # meters per second (walking speed)
    time_seconds = distance / speed
    return round(time_seconds / 60, 2)  # Convert to minutes

# Compare all algorithms for a pair
def compare_algorithms(start, goal):
    print(f"\nComparing algorithms for {start} to {goal}:")
    print("| Algorithm | Nodes Checked | Distance (m) |")
    print("|-----------|---------------|--------------|")
    algorithms = {"BFS": bfs, "DFS": dfs, "UCS": ucs, "A*": a_star}
    results = {}
    for algo_name, algo_func in algorithms.items():
        if algo_name in ["BFS", "DFS"]:
            path, explored, steps = algo_func(start, goal)
            dist = calculate_distance(path) if path else 0
        else:
            path, explored, steps, dist = algo_func(start, goal)
        results[algo_name] = {"explored": explored, "distance": dist}
        print(f"| {algo_name:<9} | {explored:<13} | {dist:<12} |")
    print("\nNote: UCS and A* give the shortest path. BFS and DFS might not.")

# Main program to let user choose
def main():
    print("Welcome to BotBrain - My First Campus Navigator!")
    while True:
        print("\nWhat do you want to do?")
        print("1. Find a Path")
        print("2. Learn About a Building")
        print("3. See Algorithm Comparison")
        print("4. Quit")
        try:
            choice = int(input("Enter a number (1-4): "))
        except ValueError:
            print("Oops! Please enter a number.")
            continue
        
        if choice == 4:
            print("Thanks for using BotBrain! Goodbye!")
            break
        elif choice == 1:
            print("\nPick your starting place:")
            for i, place in enumerate(locations, 1):
                print(f"{i}. {place}")
            try:
                start_num = int(input("Enter number: ")) - 1
                start = locations[start_num]
            except (ValueError, IndexError):
                print("Wrong number! Try again.")
                continue
            
            print("\nPick your ending place:")
            for i, place in enumerate(locations, 1):
                print(f"{i}. {place}")
            try:
                end_num = int(input("Enter number: ")) - 1
                end = locations[end_num]
            except (ValueError, IndexError):
                print("Wrong number! Try again.")
                continue
            
            print("\nPick an algorithm:")
            print("1. BFS (Breadth-First Search)")
            print("2. DFS (Depth-First Search)")
            print("3. UCS (Uniform Cost Search)")
            print("4. A* (A-Star Search)")
            try:
                algo_num = int(input("Enter number: "))
                algo_map = {1: "BFS", 2: "DFS", 3: "UCS", 4: "A*"}
                algo = algo_map[algo_num]
            except (ValueError, KeyError):
                print("Wrong choice! Try 1-4.")
                continue
            
            # Run the chosen algorithm
            if algo == "BFS":
                path, explored, steps = bfs(start, end)
                distance = calculate_distance(path) if path else 0
            elif algo == "DFS":
                path, explored, steps = dfs(start, end)
                distance = calculate_distance(path) if path else 0
            elif algo == "UCS":
                path, explored, steps, distance = ucs(start, end)
            elif algo == "A*":
                path, explored, steps, distance = a_star(start, end)
            
            print("\nHow I checked the path:")
            for step in steps:
                print(step)
            if path and None not in path:
                print(f"\nPath: {' -> '.join(path)}")
                print(f"Total Distance: {distance} meters")
                print(f"Walking Time: {calculate_walking_time(distance)} minutes")
                print(f"Places Checked: {explored}")
                info = building_info.get(end, {})
                print(f"\n{end} Details: Type={info.get('type', 'Unknown')}, Hours={info.get('hours', 'Unknown')}, Services={info.get('services', 'Unknown')}")
                compare_algorithms(start, end)
            else:
                print(f"\nSorry, no path from {start} to {end}. Maybe the map is incomplete!")
        elif choice == 2:
            print("\nPick a building to learn about:")
            for i, place in enumerate(locations, 1):
                print(f"{i}. {place}")
            try:
                num = int(input("Enter number: ")) - 1
                building = locations[num]
                info = building_info.get(building, {})
                print(f"\n{building}: Type={info.get('type', 'Unknown')}, Hours={info.get('hours', 'Unknown')}, Services={info.get('services', 'Unknown')}")
            except (ValueError, IndexError):
                print("Wrong number! Try again.")
        elif choice == 3:
            compare_algorithms("Main Gate", "Library")
            compare_algorithms("Student Center", "Canteen")
            compare_algorithms("Main Hostel", "Sports Complex")
        else:
            print("Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()