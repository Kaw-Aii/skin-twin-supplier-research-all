# SKIN-TWIN Database Infrastructure

This directory contains the database schema, migration scripts, and documentation for the SKIN-TWIN supplier research hypergraph infrastructure.

## Database Architecture

The SKIN-TWIN project uses a dual-database architecture to provide optimal grip on hypergraph dynamics:

### Neon Database (Primary)
- **Project ID**: `mute-tree-40398424`
- **Database**: `neondb`
- **Purpose**: Primary operational database with full hypergraph schema
- **Features**: PostgreSQL 17, serverless scaling, branch-based development

### Supabase Database (Secondary)
- **Purpose**: Real-time features, authentication, and API access
- **Features**: Real-time subscriptions, Row Level Security, auto-generated APIs

## Schema Overview

### Core Tables

#### `hypergraph_nodes`
Central table storing all nodes in the supply chain hypergraph.
- **Records**: 114 nodes (9 suppliers, 105 ingredients)
- **Key Fields**: `node_id`, `label`, `node_type`, `modularity_class`, `properties`
- **Purpose**: Unified storage for all hypergraph entities

#### `hypergraph_edges`
Relationships between nodes in the hypergraph.
- **Purpose**: Supply relationships, dependencies, and network connections
- **Key Fields**: `source_node_id`, `target_node_id`, `edge_type`, `weight`

#### `suppliers`
Normalized supplier information extracted from hypergraph nodes.
- **Records**: 9 major suppliers
- **Key Fields**: `supplier_code`, `name`, `website_url`, `supplier_type`
- **Examples**: Natchem CC, Meganede CC, Croda Chemicals, Botanichem

#### `ingredients`
Normalized ingredient catalog extracted from hypergraph nodes.
- **Records**: 105 ingredients
- **Key Fields**: `ingredient_code`, `name`, `category`
- **Coverage**: Raw materials, active ingredients, emulsifiers, preservatives

### Extended Tables (Future Implementation)

#### `supplier_ingredients`
Many-to-many relationships with pricing and availability data.
- **Purpose**: Track supplier-specific ingredient availability and pricing
- **Key Fields**: `availability_status`, `pricing_model`, `base_price`

#### `price_history`
Historical pricing data for market trend analysis.
- **Purpose**: Track price changes over time for market intelligence
- **Key Fields**: `price`, `effective_date`, `price_type`, `volume_tier`

#### `supplier_monitoring`
Automated monitoring of supplier website status.
- **Purpose**: Track supplier website availability and response times
- **Key Fields**: `website_status`, `response_time_ms`, `availability_changes`

#### `market_intelligence`
Market trends and intelligence gathering.
- **Purpose**: Store market insights, regulatory changes, supply disruptions
- **Key Fields**: `intelligence_type`, `impact_level`, `confidence_score`

#### `risk_assessments`
Supply chain risk analysis and mitigation strategies.
- **Purpose**: Identify and track supply chain vulnerabilities
- **Key Fields**: `risk_type`, `risk_level`, `mitigation_strategies`

## Files in this Directory

### Schema Files
- **`schema.sql`**: Complete database schema with all tables, indexes, and views
- **`neon_schema.sql`**: Simplified schema for initial Neon setup
- **`schema_oneline.sql`**: Generated single-line schema for MCP execution

### Migration Scripts
- **`migrate_data.py`**: Comprehensive migration script for both Supabase and Neon
- **`migrate_to_neon.py`**: Specialized Neon migration using MCP server
- **`requirements.txt`**: Python dependencies for migration scripts

### Documentation
- **`README.md`**: This file - comprehensive database documentation

## Current Database Status

### Migration Results
```
✓ Hypergraph Nodes: 114 records migrated
✓ Hypergraph Edges: 91 relationships migrated  
✓ Suppliers: 9 suppliers identified and catalogued
✓ Ingredients: 105 ingredients catalogued
✓ Schema: All core tables created successfully
```

### Data Distribution
- **Suppliers (9 nodes)**:
  - o6 Agencies (06A0001)
  - A&E Connock (AEC001)
  - AECI Specialty Chemicals (AKU001)
  - Botanichem (BOT0003)
  - Carst & Walker (CAR0002)
  - Croda Chemicals (CRO0001)
  - Meganede CC (MEG0001)
  - Natchem CC (NAT0001)
  - Savannah Fine Chemicals (SAV0001)

- **Ingredients (105 nodes)**: Raw materials covering emulsifiers, active ingredients, preservatives, and specialty chemicals

## Usage Examples

### Connecting to Neon Database

#### Using MCP Server
```bash
# List all tables
manus-mcp-cli tool call get_database_tables --server neon \
  --input '{"params": {"projectId": "mute-tree-40398424", "database": "neondb"}}'

# Query supplier data
manus-mcp-cli tool call run_sql --server neon \
  --input '{"params": {"projectId": "mute-tree-40398424", "database": "neondb", 
  "sql": "SELECT * FROM hypergraph_nodes WHERE node_type = '\''supplier'\''"}}'
```

#### Using Direct Connection
```python
import psycopg2
from manus_mcp_cli import get_connection_string

# Get connection string via MCP
conn_str = get_connection_string("mute-tree-40398424", "neondb")
conn = psycopg2.connect(conn_str)
```

### Common Queries

#### Supplier Analysis
```sql
-- Get all suppliers with their ingredient counts
SELECT 
    hn.node_id,
    hn.label as supplier_name,
    COUNT(he.target_node_id) as ingredient_count
FROM hypergraph_nodes hn
LEFT JOIN hypergraph_edges he ON hn.node_id = he.source_node_id
WHERE hn.node_type = 'supplier'
GROUP BY hn.node_id, hn.label
ORDER BY ingredient_count DESC;
```

#### Supply Chain Risk Assessment
```sql
-- Identify ingredients with single suppliers (high risk)
SELECT 
    target.label as ingredient_name,
    COUNT(DISTINCT source.node_id) as supplier_count,
    STRING_AGG(source.label, ', ') as suppliers
FROM hypergraph_edges he
JOIN hypergraph_nodes source ON he.source_node_id = source.node_id
JOIN hypergraph_nodes target ON he.target_node_id = target.node_id
WHERE source.node_type = 'supplier' AND target.node_type = 'ingredient'
GROUP BY target.node_id, target.label
HAVING COUNT(DISTINCT source.node_id) = 1
ORDER BY target.label;
```

#### Network Analysis
```sql
-- Analyze supplier modularity classes (market segments)
SELECT 
    modularity_class,
    COUNT(*) as supplier_count,
    STRING_AGG(label, ', ') as suppliers
FROM hypergraph_nodes 
WHERE node_type = 'supplier' AND modularity_class IS NOT NULL
GROUP BY modularity_class
ORDER BY supplier_count DESC;
```

## Automation Integration

### Scheduled Updates
The database is automatically updated through:
- **Weekly supplier research**: Updates availability and pricing data
- **Market intelligence gathering**: Tracks industry trends and changes
- **Risk assessment updates**: Monitors supply chain vulnerabilities

### API Integration
- **Supabase APIs**: Auto-generated REST and GraphQL APIs
- **Real-time subscriptions**: Live updates for critical supply chain events
- **Authentication**: Secure access control for sensitive supplier data

## Performance Optimization

### Indexes
- `idx_suppliers_code`: Fast supplier lookups by code
- `idx_ingredients_code`: Fast ingredient lookups by code  
- `idx_hypergraph_nodes_type`: Efficient node type filtering
- `idx_hypergraph_edges_type`: Efficient edge type filtering

### Views (Planned)
- `supplier_summary`: Aggregated supplier statistics
- `ingredient_availability`: Multi-supplier ingredient analysis
- `supply_chain_risks`: Risk assessment dashboard data

## Security Considerations

### Data Protection
- **Supplier Information**: Sensitive contact and pricing data
- **Market Intelligence**: Competitive information requiring access control
- **Personal Data**: Contact information subject to privacy regulations

### Access Control
- **Row Level Security**: Planned implementation in Supabase
- **API Authentication**: Secure access to supplier data
- **Audit Logging**: Track access to sensitive information

## Future Enhancements

### Planned Features
1. **Real-time Price Tracking**: Live pricing updates from supplier APIs
2. **Automated Risk Scoring**: ML-based supply chain risk assessment
3. **Market Trend Analysis**: Predictive analytics for ingredient pricing
4. **Supplier Performance Metrics**: KPI tracking and scorecards
5. **Integration APIs**: Connect with ERP and procurement systems

### Schema Evolution
- **Additional supplier metadata**: Certifications, capabilities, lead times
- **Enhanced ingredient data**: INCI names, CAS numbers, regulatory status
- **Relationship attributes**: Pricing tiers, contract terms, exclusivity
- **Temporal data**: Historical tracking of all changes

## Troubleshooting

### Common Issues
1. **Connection Timeouts**: Use connection pooling for high-frequency queries
2. **Large Result Sets**: Implement pagination for ingredient listings
3. **JSON Queries**: Use proper JSONB operators for properties field
4. **Migration Conflicts**: Check for duplicate node_id values

### Monitoring
- **Database Performance**: Query execution times and resource usage
- **Data Quality**: Validation of supplier and ingredient data
- **Sync Status**: Ensure consistency between Neon and Supabase

---

*Database infrastructure for the SKIN-TWIN hypergraph supplier research platform*
