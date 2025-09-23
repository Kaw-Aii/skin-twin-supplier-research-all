-- SKIN-TWIN Supplier Research Database Schema for Neon
-- Simplified version for initial setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    website_url TEXT,
    supplier_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ingredients table
CREATE TABLE IF NOT EXISTS ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Supplier-Ingredient relationships
CREATE TABLE IF NOT EXISTS supplier_ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    ingredient_id UUID REFERENCES ingredients(id) ON DELETE CASCADE,
    availability_status VARCHAR(50) NOT NULL,
    pricing_model VARCHAR(50),
    base_price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'ZAR',
    supplier_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(supplier_id, ingredient_id)
);

-- Hypergraph nodes
CREATE TABLE IF NOT EXISTS hypergraph_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id VARCHAR(50) UNIQUE NOT NULL,
    label VARCHAR(255) NOT NULL,
    node_type VARCHAR(50),
    modularity_class INTEGER,
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hypergraph edges
CREATE TABLE IF NOT EXISTS hypergraph_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    edge_id VARCHAR(50),
    source_node_id VARCHAR(50) REFERENCES hypergraph_nodes(node_id),
    target_node_id VARCHAR(50) REFERENCES hypergraph_nodes(node_id),
    edge_type VARCHAR(50),
    weight DECIMAL(10,4),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX IF NOT EXISTS idx_ingredients_code ON ingredients(ingredient_code);
CREATE INDEX IF NOT EXISTS idx_hypergraph_nodes_type ON hypergraph_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_hypergraph_edges_type ON hypergraph_edges(edge_type);
