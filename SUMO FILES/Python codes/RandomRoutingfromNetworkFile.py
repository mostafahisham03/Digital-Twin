import xml.etree.ElementTree as ET
import random

def parse_edge_variables(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    edge_variables = []
    for edge in root.findall(".//edge"):
        edge_id = edge.get("id")
        from_node = edge.get("from")
        to_node = edge.get("to")

        if edge_id is not None and from_node is not None and to_node is not None:
            edge_variables.append((edge_id, from_node, to_node))

    return edge_variables

def generate_random_route(start_edge_id, destination_edge_id, network_file_path):
    edge_vars = parse_edge_variables(network_file_path)
    
    # Generate a random route
    route = []
    current_edge_id = start_edge_id
    visited_edges = set()

    while current_edge_id != destination_edge_id:
        # Add the current edge to the route
        route.append(current_edge_id)
        visited_edges.add(current_edge_id)

        # Find the current edge in the list
        current_edge = next((edge for edge in edge_vars if edge[0] == current_edge_id), None)

        if current_edge is None:
            print("No route found between the specified edges.")
            break

        # Find next edges that have not been visited
        next_edges = [edge for edge in edge_vars if edge[1] == current_edge[2] and edge[0] not in visited_edges]
        
        if not next_edges:
            # Backtrack to the previous edge
            route.pop()
            if not route:
                print("No route found between the specified edges.")
                break

            current_edge_id = route[-1]
        else:
            # Select a random next edge
            random_edge = random.choice(next_edges)
            current_edge_id = random_edge[0]

    # Add the destination edge to the route if found
    if current_edge_id == destination_edge_id:
        route.append(destination_edge_id)
    
    return route

# Example usage
# start_edge_id = "B1B0"
# destination_edge_id = "C1C0"
# network_file_path = "C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Testing Scenarios/sumotesting.net.xml"

# route = generate_random_route(start_edge_id, destination_edge_id, network_file_path)

# # Print the random route
# print("Random Route:")
# print(route)






def random_next_edge(startEdge,network_file_path):
    edge_vars = parse_edge_variables(network_file_path)
    current_edge = next((edge for edge in edge_vars if edge[0] == startEdge), None)

    next_edges = [edge for edge in edge_vars if edge[1] == current_edge[2]]
    if next_edges is not None:
        random_edge = random.choice(next_edges)[0]
        return random_edge
    else:
        return None
# trial
network_file_path = "C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Testing Scenarios/sumotesting.net.xml"
startEdge= "A0A1"
nextedge=random_next_edge(startEdge, network_file_path)
print(nextedge)
