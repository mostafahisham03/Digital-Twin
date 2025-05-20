import xml.etree.ElementTree as ET
import json

def convert_netxml_to_json(xml_path, json_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    nodes = []
    edges = []

    # Extract junctions (nodes)
    for junction in root.findall('junction'):
        junction_type = junction.get('type')
        if junction_type == 'internal':
            continue  # skip helper/internal nodes
        node_id = junction.get('id')
        x = float(junction.get('x'))
        y = float(junction.get('y'))
        nodes.append({
            'id': node_id,
            'position': {'x': x, 'y': 0.0, 'z': y}
        })

    # Extract edges
    for edge in root.findall('edge'):
        edge_id = edge.get('id')
        from_node = edge.get('from')
        to_node = edge.get('to')

        if not from_node or not to_node:
            continue  # skip internal or pedestrian edges

        lanes = []
        for i, lane in enumerate(edge.findall('lane')):
            lane_id = lane.get('id')
            shape = []
            shape_str = lane.get('shape')
            if shape_str:
                for point in shape_str.strip().split():
                    x, y = map(float, point.split(','))
                    shape.append({'x': x, 'y': 0.0, 'z': y})

            lanes.append({
                'id': lane_id,
                'index': i,
                'width': float(lane.get('width', 3.2)),
                'shape': shape
            })

        edges.append({
            'id': edge_id,
            'from': from_node,
            'to': to_node,
            'lanes': lanes
        })

    output = {
        'nodes': nodes,
        'edges': edges
    }

    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)

# Usage
convert_netxml_to_json('sumotestmap.net.xml', 'sumomap.json')
