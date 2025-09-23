-- SKIN-TWIN Supplier Research Database Schema
-- Optimized for hypergraph dynamics and supplier intelligence

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Suppliers table - Core supplier information
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_code VARCHAR(20) UNIQUE NOT NULL, -- e.g., NAT0001, MEG0001
    name VARCHAR(255) NOT NULL,
    website_url TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    country VARCHAR(100) DEFAULT 'South Africa',
    supplier_type VARCHAR(100), -- e.g., 'Distributor', 'Manufacturer', 'Importer'
    specializations TEXT[], -- Array of specialization areas
    certifications TEXT[], -- Array of certifications (ISO, Ecocert, etc.)
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, under_review
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ingredients table - Raw materials and active ingredients
CREATE TABLE ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., R1901001
    name VARCHAR(255) NOT NULL,
    inci_name VARCHAR(255), -- International Nomenclature of Cosmetic Ingredients
    cas_number VARCHAR(50), -- Chemical Abstracts Service number
    category VARCHAR(100), -- e.g., 'Emulsifier', 'Active', 'Preservative'
    function_description TEXT,
    natural_origin BOOLEAN DEFAULT FALSE,
    organic_certified BOOLEAN DEFAULT FALSE,
    regulatory_status VARCHAR(100), -- e.g., 'Approved', 'Restricted', 'Banned'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Supplier-Ingredient relationships (hypergraph edges)
CREATE TABLE supplier_ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    ingredient_id UUID REFERENCES ingredients(id) ON DELETE CASCADE,
    availability_status VARCHAR(50) NOT NULL, -- 'in_stock', 'out_of_stock', 'discontinued', 'contact_for_availability'
    pricing_model VARCHAR(50), -- 'fixed', 'tiered', 'quote_based', 'contract'
    base_price DECIMAL(10,2), -- Base price per unit
    currency VARCHAR(10) DEFAULT 'ZAR',
    unit_of_measure VARCHAR(50), -- 'kg', 'g', 'L', 'mL'
    minimum_order_quantity INTEGER,
    lead_time_days INTEGER,
    last_price_update TIMESTAMP WITH TIME ZONE,
    supplier_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(supplier_id, ingredient_id)
);

-- Price history for tracking market dynamics
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_ingredient_id UUID REFERENCES supplier_ingredients(id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'ZAR',
    effective_date TIMESTAMP WITH TIME ZONE NOT NULL,
    price_type VARCHAR(50), -- 'list_price', 'contract_price', 'spot_price'
    volume_tier VARCHAR(50), -- 'small', 'medium', 'large', 'bulk'
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Supplier status monitoring
CREATE TABLE supplier_monitoring (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    check_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    website_status VARCHAR(50), -- 'online', 'offline', 'error'
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    availability_changes JSONB, -- Track what changed since last check
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market intelligence and trends
CREATE TABLE market_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_id UUID REFERENCES ingredients(id) ON DELETE CASCADE,
    intelligence_type VARCHAR(100), -- 'price_trend', 'supply_shortage', 'new_supplier', 'regulatory_change'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    impact_level VARCHAR(50), -- 'low', 'medium', 'high', 'critical'
    source VARCHAR(255),
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    effective_date TIMESTAMP WITH TIME ZONE,
    expiry_date TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hypergraph nodes for complex relationship modeling
CREATE TABLE hypergraph_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id VARCHAR(50) UNIQUE NOT NULL, -- Original node ID from CSV
    label VARCHAR(255) NOT NULL,
    node_type VARCHAR(50), -- 'supplier', 'ingredient', 'category', 'region'
    modularity_class INTEGER,
    properties JSONB, -- Flexible storage for node properties
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hypergraph edges for complex relationships
CREATE TABLE hypergraph_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    edge_id VARCHAR(50),
    source_node_id VARCHAR(50) REFERENCES hypergraph_nodes(node_id),
    target_node_id VARCHAR(50) REFERENCES hypergraph_nodes(node_id),
    edge_type VARCHAR(50), -- 'supplies', 'competes_with', 'substitutes', 'requires'
    weight DECIMAL(10,4),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Supply chain risk assessments
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_id UUID REFERENCES ingredients(id) ON DELETE CASCADE,
    risk_type VARCHAR(100), -- 'single_source', 'geographic_concentration', 'price_volatility'
    risk_level VARCHAR(50), -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    mitigation_strategies TEXT[],
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    assessor VARCHAR(255),
    next_review_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX idx_suppliers_name ON suppliers USING gin(name gin_trgm_ops);
CREATE INDEX idx_ingredients_code ON ingredients(ingredient_code);
CREATE INDEX idx_ingredients_name ON ingredients USING gin(name gin_trgm_ops);
CREATE INDEX idx_supplier_ingredients_availability ON supplier_ingredients(availability_status);
CREATE INDEX idx_price_history_date ON price_history(effective_date DESC);
CREATE INDEX idx_supplier_monitoring_timestamp ON supplier_monitoring(check_timestamp DESC);
CREATE INDEX idx_market_intelligence_type ON market_intelligence(intelligence_type);
CREATE INDEX idx_hypergraph_nodes_type ON hypergraph_nodes(node_type);
CREATE INDEX idx_hypergraph_edges_type ON hypergraph_edges(edge_type);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ingredients_updated_at BEFORE UPDATE ON ingredients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_supplier_ingredients_updated_at BEFORE UPDATE ON supplier_ingredients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hypergraph_nodes_updated_at BEFORE UPDATE ON hypergraph_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hypergraph_edges_updated_at BEFORE UPDATE ON hypergraph_edges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW supplier_summary AS
SELECT 
    s.supplier_code,
    s.name,
    s.supplier_type,
    COUNT(si.ingredient_id) as ingredient_count,
    COUNT(CASE WHEN si.availability_status = 'in_stock' THEN 1 END) as available_ingredients,
    AVG(si.base_price) as avg_price,
    MAX(si.updated_at) as last_updated
FROM suppliers s
LEFT JOIN supplier_ingredients si ON s.id = si.supplier_id
GROUP BY s.id, s.supplier_code, s.name, s.supplier_type;

CREATE VIEW ingredient_availability AS
SELECT 
    i.ingredient_code,
    i.name,
    i.category,
    COUNT(si.supplier_id) as supplier_count,
    COUNT(CASE WHEN si.availability_status = 'in_stock' THEN 1 END) as available_suppliers,
    MIN(si.base_price) as min_price,
    MAX(si.base_price) as max_price,
    AVG(si.base_price) as avg_price
FROM ingredients i
LEFT JOIN supplier_ingredients si ON i.id = si.ingredient_id
GROUP BY i.id, i.ingredient_code, i.name, i.category;

CREATE VIEW supply_chain_risks AS
SELECT 
    i.ingredient_code,
    i.name,
    COUNT(si.supplier_id) as supplier_count,
    CASE 
        WHEN COUNT(si.supplier_id) = 0 THEN 'No Suppliers'
        WHEN COUNT(si.supplier_id) = 1 THEN 'Single Source Risk'
        WHEN COUNT(si.supplier_id) <= 3 THEN 'Limited Sources'
        ELSE 'Multiple Sources'
    END as risk_category,
    STRING_AGG(s.name, ', ') as suppliers
FROM ingredients i
LEFT JOIN supplier_ingredients si ON i.id = si.ingredient_id
LEFT JOIN suppliers s ON si.supplier_id = s.id
GROUP BY i.id, i.ingredient_code, i.name;

-- Comments for documentation
COMMENT ON TABLE suppliers IS 'Core supplier information and capabilities';
COMMENT ON TABLE ingredients IS 'Raw materials and active ingredients catalog';
COMMENT ON TABLE supplier_ingredients IS 'Supplier-ingredient relationships with pricing and availability';
COMMENT ON TABLE price_history IS 'Historical pricing data for market trend analysis';
COMMENT ON TABLE supplier_monitoring IS 'Automated monitoring of supplier website status';
COMMENT ON TABLE market_intelligence IS 'Market trends and intelligence gathering';
COMMENT ON TABLE hypergraph_nodes IS 'Nodes in the supply chain hypergraph';
COMMENT ON TABLE hypergraph_edges IS 'Edges representing relationships in the hypergraph';
COMMENT ON TABLE risk_assessments IS 'Supply chain risk analysis and mitigation strategies';
