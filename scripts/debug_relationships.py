#!/usr/bin/env python3
"""Debug script to check relationship loading"""

import csv
from pathlib import Path

data_dir = Path("../data")
nodes_file = data_dir / "RSNodes_updated.csv"
edges_file = data_dir / "RSEdges.csv"

# Load suppliers and ingredients 
suppliers = {}
ingredients = {}

with open(nodes_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        node_id = row['Id']
        if node_id.startswith('R') and len(node_id) > 5:
            ingredients[node_id] = row['Label']
        else:
            suppliers[node_id] = row['Label']

print(f"Loaded {len(suppliers)} suppliers and {len(ingredients)} ingredients")

# Check edges
relationships = []
with open(edges_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        source = row.get('Source', '')
        target = row.get('Target', '')
        
        if i < 5:  # Print first 5 for debugging
            print(f"Edge {i}: {source} -> {target}")
            print(f"  Source in ingredients: {source in ingredients}")
            print(f"  Target in suppliers: {target in suppliers}")
        
        # Check for the relationship pattern we expect
        if source in ingredients and target in suppliers:
            relationships.append((source, target))

print(f"\nFound {len(relationships)} supply relationships")
if relationships:
    print("First 5 relationships:")
    for i, (ing, sup) in enumerate(relationships[:5]):
        print(f"  {ingredients[ing]} <- {suppliers[sup]}")