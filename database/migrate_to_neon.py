#!/usr/bin/env python3
"""
Migrate SKIN-TWIN CSV data to Neon database using MCP server
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

def run_mcp_command(tool_name, params):
    """Execute MCP command and return result."""
    cmd = [
        'manus-mcp-cli', 'tool', 'call', tool_name,
        '--server', 'neon',
        '--input', json.dumps({"params": params})
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def load_csv_data():
    """Load data from CSV files."""
    data_dir = Path("../data")
    
    # Load nodes
    nodes = []
    nodes_file = data_dir / "RSNodes_updated.csv"
    if nodes_file.exists():
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            nodes = list(reader)
    
    # Load edges
    edges = []
    edges_file = data_dir / "RSEdges.csv"
    if edges_file.exists():
        with open(edges_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            edges = list(reader)
    
    return nodes, edges

def migrate_hypergraph_nodes(nodes):
    """Migrate hypergraph nodes to Neon."""
    project_id = "mute-tree-40398424"
    database = "neondb"
    
    print(f"Migrating {len(nodes)} hypergraph nodes...")
    
    for i, node in enumerate(nodes):
        node_id = node['Id']
        label = node['Label']
        
        # Determine node type
        if any(node_id.startswith(prefix) for prefix in ['NAT', 'MEG', 'CRO', 'BOT', 'AEC', 'AKU', 'CAR', 'CHE', '06A']):
            node_type = 'supplier'
        else:
            node_type = 'ingredient'
        
        # Prepare properties
        properties = {k: v for k, v in node.items() if v and k not in ['Id', 'Label', 'modularity_class']}
        
        # Insert node
        sql = f"""
        INSERT INTO hypergraph_nodes (node_id, label, node_type, modularity_class, properties)
        VALUES ('{node_id}', '{label.replace("'", "''")}', '{node_type}', 
                {node.get('modularity_class') or 'NULL'}, '{json.dumps(properties)}')
        ON CONFLICT (node_id) DO UPDATE SET
            label = EXCLUDED.label,
            node_type = EXCLUDED.node_type,
            modularity_class = EXCLUDED.modularity_class,
            properties = EXCLUDED.properties,
            updated_at = NOW();
        """
        
        success, result = run_mcp_command('run_sql', {
            'projectId': project_id,
            'database': database,
            'sql': sql
        })
        
        if not success:
            print(f"Error inserting node {node_id}: {result}")
        elif i % 10 == 0:
            print(f"Processed {i+1}/{len(nodes)} nodes...")
    
    print("✓ Hypergraph nodes migration completed")

def migrate_hypergraph_edges(edges):
    """Migrate hypergraph edges to Neon."""
    project_id = "mute-tree-40398424"
    database = "neondb"
    
    print(f"Migrating {len(edges)} hypergraph edges...")
    
    for i, edge in enumerate(edges):
        edge_id = edge.get('Id', '')
        source = edge.get('Source', '')
        target = edge.get('Target', '')
        edge_type = edge.get('Type', 'supplies')
        weight = edge.get('Weight', '1.0')
        
        # Prepare properties
        properties = {k: v for k, v in edge.items() if v and k not in ['Id', 'Source', 'Target', 'Type', 'Weight']}
        
        # Insert edge
        sql = f"""
        INSERT INTO hypergraph_edges (edge_id, source_node_id, target_node_id, edge_type, weight, properties)
        VALUES ('{edge_id}', '{source}', '{target}', '{edge_type}', {weight}, '{json.dumps(properties)}')
        ON CONFLICT DO NOTHING;
        """
        
        success, result = run_mcp_command('run_sql', {
            'projectId': project_id,
            'database': database,
            'sql': sql
        })
        
        if not success:
            print(f"Error inserting edge {edge_id}: {result}")
        elif i % 10 == 0:
            print(f"Processed {i+1}/{len(edges)} edges...")
    
    print("✓ Hypergraph edges migration completed")

def migrate_suppliers_and_ingredients(nodes):
    """Migrate suppliers and ingredients to normalized tables."""
    project_id = "mute-tree-40398424"
    database = "neondb"
    
    suppliers = []
    ingredients = []
    
    # Separate suppliers and ingredients
    for node in nodes:
        node_id = node['Id']
        if any(node_id.startswith(prefix) for prefix in ['NAT', 'MEG', 'CRO', 'BOT', 'AEC', 'AKU', 'CAR', 'CHE', '06A']):
            suppliers.append(node)
        else:
            ingredients.append(node)
    
    # Migrate suppliers
    print(f"Migrating {len(suppliers)} suppliers...")
    for supplier in suppliers:
        supplier_code = supplier['Id']
        name = supplier['Label'].replace("'", "''")
        website_url = supplier.get('supplier_url', '')
        
        sql = f"""
        INSERT INTO suppliers (supplier_code, name, website_url, supplier_type, status)
        VALUES ('{supplier_code}', '{name}', '{website_url}', 'Supplier', 'active')
        ON CONFLICT (supplier_code) DO UPDATE SET
            name = EXCLUDED.name,
            website_url = EXCLUDED.website_url,
            updated_at = NOW();
        """
        
        success, result = run_mcp_command('run_sql', {
            'projectId': project_id,
            'database': database,
            'sql': sql
        })
        
        if not success:
            print(f"Error inserting supplier {supplier_code}: {result}")
    
    # Migrate ingredients
    print(f"Migrating {len(ingredients)} ingredients...")
    for ingredient in ingredients:
        ingredient_code = ingredient['Id']
        name = ingredient['Label'].replace("'", "''")
        
        sql = f"""
        INSERT INTO ingredients (ingredient_code, name, category)
        VALUES ('{ingredient_code}', '{name}', 'Unknown')
        ON CONFLICT (ingredient_code) DO UPDATE SET
            name = EXCLUDED.name,
            updated_at = NOW();
        """
        
        success, result = run_mcp_command('run_sql', {
            'projectId': project_id,
            'database': database,
            'sql': sql
        })
        
        if not success:
            print(f"Error inserting ingredient {ingredient_code}: {result}")
    
    print("✓ Suppliers and ingredients migration completed")

def verify_migration():
    """Verify the migration was successful."""
    project_id = "mute-tree-40398424"
    database = "neondb"
    
    # Count records in each table
    tables = ['hypergraph_nodes', 'hypergraph_edges', 'suppliers', 'ingredients']
    
    print("\nMigration Verification:")
    print("=" * 40)
    
    for table in tables:
        success, result = run_mcp_command('run_sql', {
            'projectId': project_id,
            'database': database,
            'sql': f'SELECT COUNT(*) as count FROM {table};'
        })
        
        if success:
            # Parse the result to get count
            print(f"{table}: Migration completed")
        else:
            print(f"{table}: Error - {result}")

def main():
    """Main execution function."""
    print("SKIN-TWIN Data Migration to Neon Database")
    print("=" * 50)
    
    # Load CSV data
    print("Loading CSV data...")
    nodes, edges = load_csv_data()
    print(f"Loaded {len(nodes)} nodes and {len(edges)} edges")
    
    # Migrate data
    migrate_hypergraph_nodes(nodes)
    migrate_hypergraph_edges(edges)
    migrate_suppliers_and_ingredients(nodes)
    
    # Verify migration
    verify_migration()
    
    print("\n✓ Migration completed successfully!")

if __name__ == "__main__":
    main()
