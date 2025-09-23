#!/usr/bin/env python3
"""
SKIN-TWIN Data Migration Script

Migrates data from CSV files to Supabase and Neon databases.
Handles the transformation from flat CSV structure to normalized relational schema.

Usage:
    python migrate_data.py --database supabase|neon [--dry-run]
"""

import os
import sys
import csv
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import argparse
import logging
from typing import Dict, List, Optional
import uuid

# Database connection imports
try:
    from supabase import create_client, Client
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Install with: pip install supabase psycopg2-binary pandas")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataMigrator:
    """Handles migration of CSV data to normalized database schema."""
    
    def __init__(self, database_type: str, dry_run: bool = False):
        self.database_type = database_type
        self.dry_run = dry_run
        self.data_dir = Path("../data")
        self.db_connection = None
        self.supabase_client = None
        
        # Initialize database connection
        self._init_database_connection()
        
        # Data containers
        self.suppliers = {}
        self.ingredients = {}
        self.supplier_ingredients = []
        self.hypergraph_nodes = []
        self.hypergraph_edges = []
    
    def _init_database_connection(self):
        """Initialize database connection based on type."""
        if self.database_type == 'supabase':
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")
            self.supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Connected to Supabase")
            
        elif self.database_type == 'neon':
            # Use Neon MCP server for database operations
            logger.info("Using Neon MCP server for database operations")
        else:
            raise ValueError("Database type must be 'supabase' or 'neon'")
    
    def load_csv_data(self):
        """Load and parse CSV data files."""
        logger.info("Loading CSV data files...")
        
        # Load RSNodes_updated.csv
        nodes_file = self.data_dir / "RSNodes_updated.csv"
        if nodes_file.exists():
            with open(nodes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._process_node_row(row)
        
        # Load RSEdges.csv
        edges_file = self.data_dir / "RSEdges.csv"
        if edges_file.exists():
            with open(edges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._process_edge_row(row)
        
        logger.info(f"Loaded {len(self.suppliers)} suppliers, {len(self.ingredients)} ingredients")
    
    def _process_node_row(self, row: Dict):
        """Process a single node row from RSNodes_updated.csv."""
        node_id = row['Id']
        label = row['Label']
        
        # Determine if this is a supplier or ingredient based on ID pattern
        if any(node_id.startswith(prefix) for prefix in ['NAT', 'MEG', 'CRO', 'BOT', 'AEC', 'AKU', 'CAR', 'CHE', '06A']):
            # This is a supplier
            supplier_data = {
                'supplier_code': node_id,
                'name': label,
                'website_url': row.get('supplier_url', ''),
                'availability_status': row.get('availability', ''),
                'pricing_estimate': row.get('pricing_estimate', ''),
                'notes': row.get('notes', ''),
                'modularity_class': int(row.get('modularity_class', 0)) if row.get('modularity_class') else None
            }
            self.suppliers[node_id] = supplier_data
        else:
            # This is an ingredient
            ingredient_data = {
                'ingredient_code': node_id,
                'name': label,
                'modularity_class': int(row.get('modularity_class', 0)) if row.get('modularity_class') else None
            }
            self.ingredients[node_id] = ingredient_data
        
        # Add to hypergraph nodes
        hypergraph_node = {
            'node_id': node_id,
            'label': label,
            'node_type': 'supplier' if node_id in self.suppliers else 'ingredient',
            'modularity_class': int(row.get('modularity_class', 0)) if row.get('modularity_class') else None,
            'properties': {k: v for k, v in row.items() if v and k not in ['Id', 'Label', 'modularity_class']}
        }
        self.hypergraph_nodes.append(hypergraph_node)
    
    def _process_edge_row(self, row: Dict):
        """Process a single edge row from RSEdges.csv."""
        edge_data = {
            'edge_id': row.get('Id', ''),
            'source_node_id': row.get('Source', ''),
            'target_node_id': row.get('Target', ''),
            'edge_type': row.get('Type', 'supplies'),
            'weight': float(row.get('Weight', 1.0)) if row.get('Weight') else 1.0,
            'properties': {k: v for k, v in row.items() if v and k not in ['Id', 'Source', 'Target', 'Type', 'Weight']}
        }
        self.hypergraph_edges.append(edge_data)
        
        # Create supplier-ingredient relationships
        source_id = row.get('Source', '')
        target_id = row.get('Target', '')
        
        if source_id in self.suppliers and target_id in self.ingredients:
            supplier_ingredient = {
                'supplier_code': source_id,
                'ingredient_code': target_id,
                'availability_status': self.suppliers[source_id].get('availability_status', 'unknown'),
                'pricing_model': 'quote_based' if 'contact' in self.suppliers[source_id].get('pricing_estimate', '').lower() else 'fixed',
                'supplier_notes': self.suppliers[source_id].get('notes', '')
            }
            self.supplier_ingredients.append(supplier_ingredient)
    
    def migrate_to_supabase(self):
        """Migrate data to Supabase database."""
        logger.info("Migrating data to Supabase...")
        
        if self.dry_run:
            logger.info("DRY RUN: Would migrate to Supabase")
            return
        
        try:
            # Insert suppliers
            for supplier_code, supplier_data in self.suppliers.items():
                supplier_record = {
                    'supplier_code': supplier_code,
                    'name': supplier_data['name'],
                    'website_url': supplier_data.get('website_url') or None,
                    'supplier_type': self._determine_supplier_type(supplier_data),
                    'status': 'active'
                }
                
                result = self.supabase_client.table('suppliers').upsert(supplier_record).execute()
                logger.debug(f"Inserted supplier: {supplier_code}")
            
            # Insert ingredients
            for ingredient_code, ingredient_data in self.ingredients.items():
                ingredient_record = {
                    'ingredient_code': ingredient_code,
                    'name': ingredient_data['name'],
                    'category': self._determine_ingredient_category(ingredient_data['name'])
                }
                
                result = self.supabase_client.table('ingredients').upsert(ingredient_record).execute()
                logger.debug(f"Inserted ingredient: {ingredient_code}")
            
            # Insert hypergraph nodes
            for node in self.hypergraph_nodes:
                result = self.supabase_client.table('hypergraph_nodes').upsert(node).execute()
            
            # Insert hypergraph edges
            for edge in self.hypergraph_edges:
                result = self.supabase_client.table('hypergraph_edges').upsert(edge).execute()
            
            logger.info("Successfully migrated data to Supabase")
            
        except Exception as e:
            logger.error(f"Error migrating to Supabase: {e}")
            raise
    
    def migrate_to_neon(self):
        """Migrate data to Neon database using MCP server."""
        logger.info("Migrating data to Neon via MCP server...")
        
        if self.dry_run:
            logger.info("DRY RUN: Would migrate to Neon")
            return
        
        # This would use the Neon MCP server for database operations
        # Implementation depends on the specific MCP server setup
        logger.info("Neon migration via MCP server - implementation needed")
    
    def _determine_supplier_type(self, supplier_data: Dict) -> str:
        """Determine supplier type based on available data."""
        notes = supplier_data.get('notes', '').lower()
        name = supplier_data.get('name', '').lower()
        
        if 'distributor' in notes or 'distributor' in name:
            return 'Distributor'
        elif 'manufacturer' in notes or 'manufacturer' in name:
            return 'Manufacturer'
        elif 'importer' in notes or 'importer' in name:
            return 'Importer'
        else:
            return 'Supplier'
    
    def _determine_ingredient_category(self, ingredient_name: str) -> str:
        """Determine ingredient category based on name patterns."""
        name_lower = ingredient_name.lower()
        
        if any(term in name_lower for term in ['emulsifier', 'emuls']):
            return 'Emulsifier'
        elif any(term in name_lower for term in ['preservative', 'preserv']):
            return 'Preservative'
        elif any(term in name_lower for term in ['extract', 'oil', 'butter']):
            return 'Active Ingredient'
        elif any(term in name_lower for term in ['acid', 'salt']):
            return 'Chemical'
        else:
            return 'Other'
    
    def generate_migration_report(self) -> Dict:
        """Generate a report of the migration process."""
        return {
            'timestamp': datetime.now().isoformat(),
            'database_type': self.database_type,
            'dry_run': self.dry_run,
            'suppliers_count': len(self.suppliers),
            'ingredients_count': len(self.ingredients),
            'relationships_count': len(self.supplier_ingredients),
            'hypergraph_nodes_count': len(self.hypergraph_nodes),
            'hypergraph_edges_count': len(self.hypergraph_edges)
        }

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Migrate SKIN-TWIN data to database')
    parser.add_argument('--database', choices=['supabase', 'neon'], required=True,
                       help='Target database type')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without making changes')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize migrator
        migrator = DataMigrator(args.database, args.dry_run)
        
        # Load CSV data
        migrator.load_csv_data()
        
        # Perform migration
        if args.database == 'supabase':
            migrator.migrate_to_supabase()
        elif args.database == 'neon':
            migrator.migrate_to_neon()
        
        # Generate report
        report = migrator.generate_migration_report()
        
        print(f"\nMigration Report:")
        print(f"Database: {report['database_type']}")
        print(f"Suppliers: {report['suppliers_count']}")
        print(f"Ingredients: {report['ingredients_count']}")
        print(f"Relationships: {report['relationships_count']}")
        print(f"Hypergraph Nodes: {report['hypergraph_nodes_count']}")
        print(f"Hypergraph Edges: {report['hypergraph_edges_count']}")
        
        if args.dry_run:
            print("\n(Dry run - no changes made)")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
