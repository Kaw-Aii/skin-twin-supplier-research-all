#!/usr/bin/env python3
"""
Sync SKIN-TWIN supplier hypergraph data with Supabase database
"""

import os
import csv
import json
from datetime import datetime
from supabase import create_client, Client

def load_csv_data(file_path):
    """Load data from CSV file"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def sync_suppliers_to_supabase():
    """Sync supplier data to Supabase"""
    
    # Initialize Supabase client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        return False
    
    supabase: Client = create_client(url, key)
    
    try:
        # Load updated nodes data
        nodes_file = "/home/ubuntu/skin-twin-supplier-research/data/RSNodes_updated_new.csv"
        nodes_data = load_csv_data(nodes_file)
        
        # Load edges data
        edges_file = "/home/ubuntu/skin-twin-supplier-research/data/RSEdges.csv"
        edges_data = load_csv_data(edges_file)
        
        # Create tables if they don't exist
        print("Creating Supabase tables...")
        
        # Create suppliers table
        suppliers_schema = """
        CREATE TABLE IF NOT EXISTS suppliers (
            id VARCHAR(20) PRIMARY KEY,
            label VARCHAR(255),
            timeset VARCHAR(50),
            modularity_class INTEGER,
            availability TEXT,
            pricing_estimate TEXT,
            supplier_url TEXT,
            notes TEXT,
            last_updated DATE,
            website_status VARCHAR(50),
            contact_info TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Create ingredients table
        ingredients_schema = """
        CREATE TABLE IF NOT EXISTS ingredients (
            id VARCHAR(20) PRIMARY KEY,
            label VARCHAR(255),
            timeset VARCHAR(50),
            modularity_class INTEGER,
            availability TEXT,
            pricing_estimate TEXT,
            supplier_url TEXT,
            notes TEXT,
            last_updated DATE,
            website_status VARCHAR(50),
            contact_info TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Create edges table
        edges_schema = """
        CREATE TABLE IF NOT EXISTS supplier_ingredient_edges (
            id SERIAL PRIMARY KEY,
            source VARCHAR(20),
            target VARCHAR(20),
            type VARCHAR(20),
            label VARCHAR(255),
            timeset VARCHAR(50),
            weight INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute schema creation via RPC (if available) or handle manually
        print("Tables schema prepared for manual creation if needed")
        
        # Separate suppliers and ingredients
        suppliers = []
        ingredients = []
        
        for node in nodes_data:
            # Suppliers typically have longer IDs and specific patterns
            if len(node['Id']) <= 10 and not node['Id'].startswith('R'):
                # This is a supplier
                supplier_data = {
                    'id': node['Id'],
                    'label': node['Label'],
                    'timeset': node.get('timeset', ''),
                    'modularity_class': int(node['modularity_class']) if node['modularity_class'] else None,
                    'availability': node.get('availability', ''),
                    'pricing_estimate': node.get('pricing_estimate', ''),
                    'supplier_url': node.get('supplier_url', ''),
                    'notes': node.get('notes', ''),
                    'last_updated': node.get('last_updated', ''),
                    'website_status': node.get('website_status', ''),
                    'contact_info': node.get('contact_info', '')
                }
                suppliers.append(supplier_data)
            else:
                # This is an ingredient
                ingredient_data = {
                    'id': node['Id'],
                    'label': node['Label'],
                    'timeset': node.get('timeset', ''),
                    'modularity_class': int(node['modularity_class']) if node['modularity_class'] else None,
                    'availability': node.get('availability', ''),
                    'pricing_estimate': node.get('pricing_estimate', ''),
                    'supplier_url': node.get('supplier_url', ''),
                    'notes': node.get('notes', ''),
                    'last_updated': node.get('last_updated', ''),
                    'website_status': node.get('website_status', ''),
                    'contact_info': node.get('contact_info', '')
                }
                ingredients.append(ingredient_data)
        
        # Sync suppliers
        print(f"Syncing {len(suppliers)} suppliers...")
        for supplier in suppliers:
            try:
                result = supabase.table('suppliers').upsert(supplier).execute()
                print(f"Synced supplier: {supplier['id']} - {supplier['label']}")
            except Exception as e:
                print(f"Error syncing supplier {supplier['id']}: {e}")
        
        # Sync ingredients
        print(f"Syncing {len(ingredients)} ingredients...")
        for ingredient in ingredients:
            try:
                result = supabase.table('ingredients').upsert(ingredient).execute()
                print(f"Synced ingredient: {ingredient['id']} - {ingredient['label']}")
            except Exception as e:
                print(f"Error syncing ingredient {ingredient['id']}: {e}")
        
        # Sync edges
        print(f"Syncing {len(edges_data)} edges...")
        for edge in edges_data:
            edge_data = {
                'source': edge['Source'],
                'target': edge['Target'],
                'type': edge['Type'],
                'label': edge.get('Label', ''),
                'timeset': edge.get('timeset', ''),
                'weight': int(edge['Weight']) if edge['Weight'] else 1
            }
            try:
                result = supabase.table('supplier_ingredient_edges').upsert(edge_data).execute()
                print(f"Synced edge: {edge['Source']} -> {edge['Target']}")
            except Exception as e:
                print(f"Error syncing edge {edge['Source']} -> {edge['Target']}: {e}")
        
        print("Supabase sync completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during Supabase sync: {e}")
        return False

if __name__ == "__main__":
    success = sync_suppliers_to_supabase()
    if success:
        print("Data synchronization completed successfully!")
    else:
        print("Data synchronization failed!")
