#!/usr/bin/env python3
"""
Populate Neon database with SKIN-TWIN supplier hypergraph data
"""

import csv
import psycopg2
from datetime import datetime

def load_csv_data(file_path):
    """Load data from CSV file"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def populate_neon_database():
    """Populate Neon database with supplier and ingredient data"""
    
    # Connection string for Neon database
    conn_string = "postgresql://neondb_owner:npg_ZI4cLyCwUzB5@ep-dawn-smoke-adevyrp3-pooler.c-2.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
    
    try:
        # Connect to database
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        print("Connected to Neon database successfully!")
        
        # Load updated nodes data
        nodes_file = "/home/ubuntu/skin-twin-supplier-research/data/RSNodes_updated_new.csv"
        nodes_data = load_csv_data(nodes_file)
        
        # Load edges data
        edges_file = "/home/ubuntu/skin-twin-supplier-research/data/RSEdges.csv"
        edges_data = load_csv_data(edges_file)
        
        # Separate suppliers and ingredients
        suppliers = []
        ingredients = []
        
        for node in nodes_data:
            # Suppliers typically have shorter IDs and don't start with 'R'
            if len(node['Id']) <= 10 and not node['Id'].startswith('R'):
                suppliers.append(node)
            else:
                ingredients.append(node)
        
        # Insert suppliers
        print(f"Inserting {len(suppliers)} suppliers...")
        for supplier in suppliers:
            insert_sql = """
            INSERT INTO suppliers (id, label, timeset, modularity_class, availability, 
                                 pricing_estimate, supplier_url, notes, last_updated, 
                                 website_status, contact_info)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                label = EXCLUDED.label,
                availability = EXCLUDED.availability,
                pricing_estimate = EXCLUDED.pricing_estimate,
                supplier_url = EXCLUDED.supplier_url,
                notes = EXCLUDED.notes,
                last_updated = EXCLUDED.last_updated,
                website_status = EXCLUDED.website_status,
                contact_info = EXCLUDED.contact_info
            """
            
            last_updated = supplier.get('last_updated', '')
            if last_updated == '2025-09-23':
                last_updated_date = '2025-09-23'
            else:
                last_updated_date = None
            
            cur.execute(insert_sql, (
                supplier['Id'],
                supplier['Label'],
                supplier.get('timeset', ''),
                int(supplier['modularity_class']) if supplier['modularity_class'] else None,
                supplier.get('availability', ''),
                supplier.get('pricing_estimate', ''),
                supplier.get('supplier_url', ''),
                supplier.get('notes', ''),
                last_updated_date,
                supplier.get('website_status', ''),
                supplier.get('contact_info', '')
            ))
            print(f"Inserted/Updated supplier: {supplier['Id']} - {supplier['Label']}")
        
        # Insert ingredients
        print(f"Inserting {len(ingredients)} ingredients...")
        for ingredient in ingredients:
            insert_sql = """
            INSERT INTO ingredients (id, label, timeset, modularity_class, availability, 
                                   pricing_estimate, supplier_url, notes, last_updated, 
                                   website_status, contact_info)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                label = EXCLUDED.label,
                availability = EXCLUDED.availability,
                pricing_estimate = EXCLUDED.pricing_estimate,
                supplier_url = EXCLUDED.supplier_url,
                notes = EXCLUDED.notes,
                last_updated = EXCLUDED.last_updated,
                website_status = EXCLUDED.website_status,
                contact_info = EXCLUDED.contact_info
            """
            
            last_updated = ingredient.get('last_updated', '')
            if last_updated == '2025-09-23':
                last_updated_date = '2025-09-23'
            else:
                last_updated_date = None
            
            cur.execute(insert_sql, (
                ingredient['Id'],
                ingredient['Label'],
                ingredient.get('timeset', ''),
                int(ingredient['modularity_class']) if ingredient['modularity_class'] else None,
                ingredient.get('availability', ''),
                ingredient.get('pricing_estimate', ''),
                ingredient.get('supplier_url', ''),
                ingredient.get('notes', ''),
                last_updated_date,
                ingredient.get('website_status', ''),
                ingredient.get('contact_info', '')
            ))
            print(f"Inserted/Updated ingredient: {ingredient['Id']} - {ingredient['Label']}")
        
        # Insert edges
        print(f"Inserting {len(edges_data)} edges...")
        for edge in edges_data:
            insert_sql = """
            INSERT INTO supplier_ingredient_edges (source, target, type, label, timeset, weight)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """
            
            cur.execute(insert_sql, (
                edge['Source'],
                edge['Target'],
                edge['Type'],
                edge.get('Label', ''),
                edge.get('timeset', ''),
                int(edge['Weight']) if edge['Weight'] else 1
            ))
            print(f"Inserted edge: {edge['Source']} -> {edge['Target']}")
        
        # Commit changes
        conn.commit()
        print("All data committed successfully!")
        
        # Get summary statistics
        cur.execute("SELECT COUNT(*) FROM suppliers")
        supplier_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM ingredients")
        ingredient_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM supplier_ingredient_edges")
        edge_count = cur.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"- Suppliers: {supplier_count}")
        print(f"- Ingredients: {ingredient_count}")
        print(f"- Edges: {edge_count}")
        
        # Close connection
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error during database population: {e}")
        return False

if __name__ == "__main__":
    success = populate_neon_database()
    if success:
        print("Neon database population completed successfully!")
    else:
        print("Neon database population failed!")
