"""
Ce script génère une visualisation graphique interactive de l'arbre de décision défini dans decision_tree.yaml.
Il utilise la bibliothèque NetworkX et Pyvis pour créer une visualisation HTML interactive.
"""

import yaml
import os
import re
import json

def load_decision_tree(decision_tree):
    """Charge l'arbre de décision depuis le fichier YAML."""
    with open(decision_tree, 'r') as file:
        tree_data = yaml.safe_load(file)
    return tree_data

def extract_condition(condition_text):
    """Extrait une condition plus lisible pour l'affichage."""
    if not condition_text:
        return ""
    
    # Nettoyer et formater la condition
    condition = condition_text.replace("==", "=")
    
    return condition

def create_node_id(text):
    """Crée un identifiant unique pour chaque nœud basé sur son texte."""
    # Remplacer les caractères non alphanumériques par des underscores
    node_id = re.sub(r'[^a-zA-Z0-9]', '_', text)
    # S'assurer que l'ID commence par une lettre
    if not node_id[0].isalpha():
        node_id = 'n' + node_id
    return node_id

def visualize_decision_tree(decision_tree):
    """Génère uniquement une visualisation HTML interactive de l'arbre de décision."""
    try:
        import networkx as nx
        from pyvis.network import Network
        
        # Charger l'arbre de décision
        tree_data = load_decision_tree(decision_tree)
        
        # Créer un graphe NetworkX
        G = nx.DiGraph()
        
        # Créer un nœud racine explicite
        root_node_id = "root_node"
        G.add_node(root_node_id, 
                   label="Type de données", 
                   title="Point de départ de l'arbre de décision",
                   color="#FFD700",  # Or
                   shape="ellipse",
                   font={"size": 16, "bold": True})
        
        # Fonction récursive pour ajouter des nœuds et des arêtes
        def add_nodes_edges(data, parent_id=None, edge_label=None, node_counter=None):
            if node_counter is None:
                node_counter = {'count': 0}
            
            if isinstance(data, dict):
                if 'if' in data:
                    # Nœud de décision
                    condition = extract_condition(data['if'])
                    node_id = f"decision_{node_counter['count']}"
                    node_counter['count'] += 1
                    
                    # Ajouter le nœud avec des informations détaillées
                    G.add_node(node_id, 
                               label=condition, 
                               title=f"Condition: {condition}",
                               color="#D2E5FF",  # Bleu clair
                               shape="diamond",
                               font={"size": 14})
                    
                    # Connecter au parent
                    if parent_id:
                        # Ne pas ajouter d'étiquette aux arêtes
                        G.add_edge(parent_id, node_id, 
                                  arrows="to")
                    
                    # Traiter les enfants
                    if 'then' in data:
                        add_nodes_edges(data['then'], node_id, None, node_counter)
                    if 'else' in data:
                        add_nodes_edges(data['else'], node_id, None, node_counter)
                
                elif 'leaf_id' in data:
                    # Nœud feuille
                    leaf_id = str(data['leaf_id'])
                    cell_title = data.get('cell_title', 'Action')
                    args = data.get('arguments', [])
                    
                    node_id = f"leaf_{leaf_id}"
                    label = f"{cell_title}\n(ID: {leaf_id})"
                    
                    # Créer un contenu détaillé pour l'infobulle
                    tooltip = f"<div style='max-width:300px'><h3>{cell_title}</h3>"
                    tooltip += f"<p><b>ID:</b> {leaf_id}</p>"
                    if args:
                        tooltip += f"<p><b>Arguments:</b> {', '.join(args)}</p>"
                    tooltip += "</div>"
                    
                    # Ajouter le nœud
                    G.add_node(node_id, 
                               label=label, 
                               title=tooltip,
                               color="#C5E8B7",  # Vert clair
                               shape="box",
                               font={"size": 14, "bold": True})
                    
                    # Connecter au parent
                    if parent_id:
                        # Ne pas ajouter d'étiquette aux arêtes
                        G.add_edge(parent_id, node_id, 
                                  arrows="to")
                
                elif 'actions' in data:
                    # Liste d'actions
                    for action in data['actions']:
                        # Ne pas passer d'étiquette pour les arêtes
                        add_nodes_edges(action, parent_id, None, node_counter)
                
                else:
                    # Autres types de nœuds
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            add_nodes_edges(value, parent_id, None, node_counter)
            
            elif isinstance(data, list):
                # Liste de nœuds
                for item in data:
                    add_nodes_edges(item, parent_id, edge_label, node_counter)
        
        # Trouver la clé principale dans le fichier YAML
        main_key = None
        for key in tree_data:
            if key.startswith('decision_tree'):
                main_key = key
                break
        
        if main_key and main_key in tree_data and isinstance(tree_data[main_key], list):
            top_level_nodes = []
            for i, item in enumerate(tree_data[main_key]):
                if 'if' in item:
                    # Créer un nœud pour chaque condition principale
                    condition = extract_condition(item['if'])
                    node_id = f"top_level_{i}"
                    
                    G.add_node(node_id, 
                              label=condition, 
                              title=f"Condition principale: {condition}",
                              color="#D2E5FF",  # Bleu clair
                              shape="diamond",
                              font={"size": 14})
                    
                    # Connecter ce nœud au nœud racine
                    G.add_edge(root_node_id, node_id, 
                              arrows="to")
                    
                    # Traiter les enfants de ce nœud
                    if 'then' in item:
                        add_nodes_edges(item['then'], node_id, None, {'count': 100 + i*100})
                    if 'else' in item:
                        add_nodes_edges(item['else'], node_id, None, {'count': 100 + i*100 + 50})
        else:
            # Fallback au cas où la structure n'est pas comme attendu
            print(f"Structure non reconnue dans le fichier YAML : {', '.join(tree_data.keys())}")
            if main_key:
                add_nodes_edges(tree_data[main_key])
            else:
                add_nodes_edges(tree_data)
        
        # Créer un fichier HTML directement sans passer par pyvis.save_graph
        output_file = 'decision_tree_interactive.html'
        
        # Extraire les nœuds et les arêtes du graphe NetworkX
        nodes_data = []
        for node, attrs in G.nodes(data=True):
            node_data = {"id": node, "label": attrs.get("label", node)}
            # Ajouter les autres attributs s'ils existent
            if "title" in attrs:
                node_data["title"] = attrs["title"]
            if "color" in attrs:
                node_data["color"] = attrs["color"]
            if "shape" in attrs:
                node_data["shape"] = attrs["shape"]
            if "font" in attrs:
                node_data["font"] = attrs["font"]
            nodes_data.append(node_data)
        
        edges_data = []
        for source, target, attrs in G.edges(data=True):
            edge_data = {"from": source, "to": target}
            # Ajouter les autres attributs s'ils existent
            if "title" in attrs:
                edge_data["title"] = attrs["title"]
            if "label" in attrs:
                edge_data["label"] = attrs["label"]
            if "font" in attrs:
                edge_data["font"] = attrs["font"]
            if "arrows" in attrs:
                edge_data["arrows"] = attrs["arrows"]
            edges_data.append(edge_data)
        
        # Configuration du visualiseur
        options = {
            "nodes": {
                "font": {"size": 16},
                "margin": 10
            },
            "edges": {
                "color": {"inherit": True},
                "smooth": {"enabled": True, "type": "cubicBezier"},
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
        
        # Générer le HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Visualisation de l'arbre de décision</title>
    <!-- Intégrer vis.js depuis CDN -->
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
    <h1>Visualisation de l'arbre de décision</h1>
    <div class="info">
        <p><strong>Instructions :</strong> Vous pouvez faire un zoom avant/arrière avec la molette de la souris, déplacer le graphe en maintenant le clic gauche, et voir des détails en survolant les nœuds.</p>
    </div>

    <div id="mynetwork"></div>

    <script type="text/javascript">
        // Créer un réseau vis.js
        var container = document.getElementById('mynetwork');
        
        // Données pour le réseau
        var data = {{
            nodes: new vis.DataSet({json.dumps(nodes_data)}),
            edges: new vis.DataSet({json.dumps(edges_data)})
        }};
        
        // Options pour le réseau
        var options = {json.dumps(options)};
        
        // Initialiser le réseau
        var network = new vis.Network(container, data, options);
        
        // Zoom sur le graphe
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
        
        # Écrire le fichier HTML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Visualisation HTML interactive générée : {output_file}")
        
        # Ouvrir le fichier HTML
        try:
            if os.name == 'nt':  # Windows
                os.system(f'start {output_file}')
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open {output_file}')
        except:
            print("Impossible d'ouvrir automatiquement le fichier HTML. Veuillez l'ouvrir manuellement.")
        
        return True
    
    except Exception as e:
        print(f"Erreur lors de la génération de la visualisation HTML : {str(e)}")
        return False

if __name__ == "__main__":
    print("Génération de la visualisation interactive de l'arbre de décision...")
    visualize_decision_tree(decision_tree = 'decision_tree_preprocessing.yaml')
    visualize_decision_tree(decision_tree = 'decision_tree_modelling.yaml')