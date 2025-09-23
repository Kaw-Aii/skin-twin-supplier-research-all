#!/usr/bin/env python3
"""Debug script to check supplier/ingredient classification"""

import csv
from pathlib import Path

data_dir = Path("../data")
nodes_file = data_dir / "RSNodes_updated.csv"

suppliers = {}
ingredients = {}

with open(nodes_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        node_id = row['Id']
        
        # Current classification logic
        if any(node_id.startswith(prefix) for prefix in ['NAT', 'MEG', 'CRO', 'BOT', 'AEC', 'AKU', 'CAR', 'CHE', '06A', 'CLI', 'COS', 'EXS', 'MAT', 'MER', 'MIL', 'ORC', 'SAV', 'IMC', 'PRO', 'VAN']):
            suppliers[node_id] = row['Label']
        else:
            ingredients[node_id] = row['Label']

print(f"Suppliers found: {len(suppliers)}")
for k, v in list(suppliers.items())[:10]:
    print(f"  {k}: {v}")

print(f"\nIngredients found: {len(ingredients)}")  
for k, v in list(ingredients.items())[:10]:
    print(f"  {k}: {v}")

# Check some specific patterns
print(f"\nR-codes: {len([k for k in ingredients.keys() if k.startswith('R')])}")
print(f"Three letter codes: {len([k for k in suppliers.keys() if len(k) <= 7])}")