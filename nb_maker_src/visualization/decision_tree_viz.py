"""
Module for visualizing decision trees using NetworkX and Pyvis.
"""

import yaml
import os
import re
import json
from typing import Dict, Any, List, Optional

def load_decision_tree(decision_tree: str) -> Dict[str, Any]:
    """Load the decision tree from a YAML file."""
    with open(decision_tree, 'r') as file:
        tree_data = yaml.safe_load(file)
    return tree_data

def extract_condition(condition_text: str) -> str:
    """Extract a more readable condition for display."""
    if not condition_text:
        return ""
    return condition_text.replace("==", "=")

def create_node_id(text: str) -> str:
    """Create a unique identifier for each node based on its text."""
    node_id = re.sub(r'[^a-zA-Z0-9]', '_', text)
    if not node_id[0].isalpha():
        node_id = 'n' + node_id
    return node_id

def visualize_decision_tree(decision_tree: str) -> bool:
    """Generate an interactive HTML visualization of the decision tree."""
    try:
        import networkx as nx
        from pyvis.network import Network
        
        # Load the decision tree
        tree_data = load_decision_tree(decision_tree)
        
        # Create a NetworkX graph
        G = nx.DiGraph()
        
        # Create root node
        root_node_id = "root_node"
        G.add_node(root_node_id, 
                   label="Data Type", 
                   title="Starting point of the decision tree",
                   color="#FFD700",  # Gold
                   shape="ellipse",
                   font={"size": 16, "bold": True})
        
        def add_nodes_edges(data: Any, parent_id: Optional[str] = None, 
                          edge_label: Optional[str] = None, 
                          node_counter: Optional[Dict[str, int]] = None) -> None:
            if node_counter is None:
                node_counter = {'count': 0}
            
            if isinstance(data, dict):
                if 'if' in data:
                    # Decision node
                    condition = extract_condition(data['if'])
                    node_id = f"decision_{node_counter['count']}"
                    node_counter['count'] += 1
                    
                    G.add_node(node_id, 
                               label=condition, 
                               title=f"Condition: {condition}",
                               color="#D2E5FF",  # Light blue
                               shape="diamond",
                               font={"size": 14})
                    
                    if parent_id:
                        G.add_edge(parent_id, node_id, arrows="to")
                    
                    if 'then' in data:
                        add_nodes_edges(data['then'], node_id, None, node_counter)
                    if 'else' in data:
                        add_nodes_edges(data['else'], node_id, None, node_counter)
                
                elif 'leaf_id' in data:
                    # Leaf node
                    leaf_id = str(data['leaf_id'])
                    cell_title = data.get('cell_title', 'Action')
                    args = data.get('arguments', [])
                    
                    node_id = f"leaf_{leaf_id}"
                    label = f"{cell_title}\n(ID: {leaf_id})"
                    
                    tooltip = f"<div style='max-width:300px'><h3>{cell_title}</h3>"
                    tooltip += f"<p><b>ID:</b> {leaf_id}</p>"
                    if args:
                        tooltip += f"<p><b>Arguments:</b> {', '.join(args)}</p>"
                    tooltip += "</div>"
                    
                    G.add_node(node_id, 
                               label=label, 
                               title=tooltip,
                               color="#C5E8B7",  # Light green
                               shape="box",
                               font={"size": 14, "bold": True})
                    
                    if parent_id:
                        G.add_edge(parent_id, node_id, arrows="to")
                
                elif 'actions' in data:
                    for action in data['actions']:
                        add_nodes_edges(action, parent_id, None, node_counter)
                
                else:
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            add_nodes_edges(value, parent_id, None, node_counter)
            
            elif isinstance(data, list):
                for item in data:
                    add_nodes_edges(item, parent_id, edge_label, node_counter)
        
        # Find main key in YAML
        main_key = None
        for key in tree_data:
            if key.startswith('decision_tree'):
                main_key = key
                break
        
        if main_key and main_key in tree_data and isinstance(tree_data[main_key], list):
            for i, item in enumerate(tree_data[main_key]):
                if 'if' in item:
                    condition = extract_condition(item['if'])
                    node_id = f"top_level_{i}"
                    
                    G.add_node(node_id, 
                              label=condition, 
                              title=f"Main condition: {condition}",
                              color="#D2E5FF",
                              shape="diamond",
                              font={"size": 14})
                    
                    G.add_edge(root_node_id, node_id, arrows="to")
                    
                    if 'then' in item:
                        add_nodes_edges(item['then'], node_id, None, {'count': 100 + i*100})
                    if 'else' in item:
                        add_nodes_edges(item['else'], node_id, None, {'count': 100 + i*100 + 50})
        else:
            print(f"Unrecognized structure in YAML file: {', '.join(tree_data.keys())}")
            if main_key:
                add_nodes_edges(tree_data[main_key])
            else:
                add_nodes_edges(tree_data)
        
        # Create HTML file
        base_name = os.path.splitext(os.path.basename(decision_tree))[0]
        output_file = f'decision_tree_{base_name}.html'
        
        # Extract nodes and edges
        nodes_data = []
        for node, attrs in G.nodes(data=True):
            node_data = {"id": node, "label": attrs.get("label", node)}
            for attr in ["title", "color", "shape", "font"]:
                if attr in attrs:
                    node_data[attr] = attrs[attr]
            nodes_data.append(node_data)
        
        edges_data = []
        for source, target, attrs in G.edges(data=True):
            edge_data = {"from": source, "to": target}
            for attr in ["title", "label", "font", "arrows"]:
                if attr in attrs:
                    edge_data[attr] = attrs[attr]
            edges_data.append(edge_data)
        
        # Visualizer configuration
        options = {
            "nodes": {
                "font": {"size": 16},
                "margin": 10
            },
            "edges": {
                "color": {"inherit": True},
                "smooth": {"enabled": True, "type": "straightCross"},
                "arrows": {"to": {"enabled": True, "scaleFactor": 1}}
            },
            "physics": {
                "enabled": True,
                "hierarchicalRepulsion": {
                    "centralGravity": 0.0,
                    "springLength": 120,
                    "springConstant": 0.01,
                    "nodeDistance": 250
                },
                "minVelocity": 0.75,
                "solver": "hierarchicalRepulsion"
            },
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD",
                    "sortMethod": "directed",
                    "levelSeparation": 180,
                    "nodeSpacing": 200,
                    "treeSpacing": 200
                }
            },
            "interaction": {
                "navigationButtons": True,
                "keyboard": True
            }
        }
        
        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Decision Tree Visualization</title>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/dist/vis-network.min.css" rel="stylesheet" type="text/css" />
    <style type="text/css">
        #mynetwork {{
            width: 100%;
            height: 800px;
            border: 1px solid lightgray;
            background-color: #f9f9f9;
        }}
        .vis-tooltip {{
            position: absolute;
            visibility: hidden;
            padding: 5px;
            white-space: nowrap;
            font-family: verdana;
            font-size: 14px;
            color: #000000;
            background-color: #f5f4ed;
            -moz-border-radius: 3px;
            -webkit-border-radius: 3px;
            border-radius: 3px;
            border: 1px solid #808074;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            word-break: break-word;
        }}
        h1 {{
            font-family: Arial, sans-serif;
            color: #333;
            text-align: center;
        }}
        .info {{
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <h1>Decision Tree Visualization</h1>
    <div class="info">
        <p><strong>Instructions:</strong> You can zoom in/out with the mouse wheel, move the graph by holding the left click, and see details by hovering over nodes.</p>
    </div>

    <div id="mynetwork"></div>

    <script type="text/javascript">
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: new vis.DataSet({json.dumps(nodes_data)}),
            edges: new vis.DataSet({json.dumps(edges_data)})
        }};
        var options = {json.dumps(options)};
        var network = new vis.Network(container, data, options);
        
        network.once('afterDrawing', function() {{
            network.fit({{
                animation: {{
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }}
            }});
        }});
    </script>
</body>
</html>
"""
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Interactive HTML visualization generated: {output_file}")
        
        # Open HTML file
        try:
            if os.name == 'nt':  # Windows
                os.system(f'start {output_file}')
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open {output_file}')
        except:
            print("Unable to automatically open the HTML file. Please open it manually.")
        
        return True
    
    except Exception as e:
        print(f"Error generating HTML visualization: {str(e)}")
        return False

if __name__ == "__main__":
    print("Generating interactive visualization of the decision tree...")
    visualize_decision_tree('src/trees/decision_tree_preprocessing.yaml')
    visualize_decision_tree('src/trees/decision_tree_modelling.yaml') 