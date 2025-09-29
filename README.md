# SKIN-TWIN Supplier Research

Automated tracking and analysis of skincare ingredient supplier availability and pricing data for the SKIN-TWIN hypergraph network.

## Overview

This repository contains comprehensive research data on South African skincare ingredient suppliers, including availability status, pricing estimates, and supplier capabilities. The data is automatically updated through scheduled research runs to maintain current market intelligence.

## Repository Structure

```
├── data/                   # Raw data files
│   ├── RSNodes_updated.csv # Updated hypergraph nodes with supplier data
│   ├── RSEdges.csv        # Hypergraph edges data
│   └── supplier_findings.md # Detailed supplier research findings
├── reports/               # Analysis reports
│   ├── SKIN_TWIN_Supplier_Research_Report.md # Comprehensive analysis
│   └── supplier_analysis.md # Detailed supplier analysis
├── scripts/              # Automation scripts
│   └── update_supplier_data.py # Automated update script
└── README.md            # This file
```

## Latest Update - September 2024

### Major Research Findings
- **Verified Suppliers**: 8 out of 23 suppliers confirmed operational (34.8%)
- **Confirmed Ingredients**: 44 out of 91 ingredients verified available (48.4%)
- **Major Suppliers Performance**: All four primary suppliers (Natchem, Meganede, Croda, Botanichem) confirmed operational with excellent availability
- **Supply Chain Risk**: 47 ingredients (51.6%) require further supplier verification

### Key Suppliers Verified

| Supplier | Ingredients | Status | Key Capabilities |
|----------|-------------|--------|------------------|
| **Natchem CC** | 16 (17.6%) | ✅ Operational | Exclusive Greentech distributor, botanical actives |
| **Meganede CC** | 15 (16.5%) | ✅ Operational | Silab distributor, natural active ingredients |
| **Croda Chemicals** | 7 (7.7%) | ✅ Operational | 757+ ingredients, biotech innovation leader |
| **Botanichem** | 2 (2.2%) | ✅ Operational | Direct online pricing, formulation services |
| **AECI Specialty** | 1 (1.1%) | ✅ Operational | Sustainable chemistry focus |
| **Cosmetic Ingredients** | 1 (1.1%) | ✅ Operational | B2B supplier with applications lab |
| **o6 Agencies** | 1 (1.1%) | ✅ Operational | Fragrance and flavor supplier |
| **A&E Connock** | 1 (1.1%) | ✅ Operational | UK specialty ingredients |

### Market Trends Identified
1. **Sustainability Focus**: All major suppliers emphasizing natural origin, sustainable sourcing, and organic certifications
2. **Biotech Innovation**: Croda leading with biotech-derived ingredients like KeraBio™ K31 and biosurfactants
3. **Digital Transformation**: Botanichem offering direct online pricing while others maintain B2B quote models
4. **Regulatory Compliance**: Strong emphasis on international certifications (Ecocert, NaTrue, ISO standards)

### Critical Supply Chain Insights
- **Coverage**: 44 ingredients verified (48.4% of total 91-ingredient portfolio)
- **Single-sourcing Risk**: 47 ingredients require backup supplier identification
- **Pricing Transparency**: Botanichem provides direct pricing (R352.35 - R10,318.45 range)
- **Geographic Concentration**: Strong local South African supplier base with international backing
- **Premium Positioning**: Croda and Natchem command premium pricing for specialized ingredients

## Data Files

### RSNodes_updated.csv
Enhanced hypergraph nodes file containing:
- Supplier availability status
- Pricing estimates (where available)
- Supplier website URLs
- Detailed capability notes

### Supplier Research Reports
- Comprehensive analysis of supplier capabilities
- Market positioning and competitive dynamics
- Strategic recommendations for supply chain optimization

## Usage

The data in this repository can be used for:
- Supply chain risk assessment
- Supplier selection and evaluation
- Cost optimization analysis
- Market intelligence and competitive analysis
- Formulation planning and ingredient sourcing

## Data Quality

- **Last Updated**: September 29, 2024
- **Coverage**: 44/91 ingredients verified (48.4%)
- **Verification Method**: Direct supplier website research and contact verification
- **Accuracy**: Contact information and availability confirmed through official sources
- **New Files**: RSNodes_updated_2024.csv, comprehensive analysis reports

## License

This research data is provided for internal use within the SKIN-TWIN project. Please respect supplier confidentiality and pricing sensitivity when using this information.

---

*Automated supplier research for the SKIN-TWIN hypergraph network*

## Automation Features

### Scheduled Updates
- **Frequency**: Weekly updates every Monday at 9:00 AM
- **Scope**: All 23 suppliers monitored for changes
- **Tracking**: Pricing updates, new products, availability changes
- **Reporting**: Automated generation of updated analysis reports

### Python Automation Script
The `scripts/update_supplier_data.py` provides:
- Automated website monitoring
- Status checking and response time tracking
- Data validation and backup systems
- JSON status reports with timestamps

### Supply Chain Analysis Tool
The new `scripts/supply_chain_analyzer.py` implements the strategic recommendations with comprehensive analysis:
- **4.1 Supplier Diversification**: Identifies single-sourced ingredients (89 critical risks found)
- **4.2 Supplier Relationships**: Analyzes strategic partnerships and relationship strength
- **4.3 Pricing Transparency**: Evaluates pricing visibility (currently 4.3% transparency)
- **4.4 Sourcing Strategy**: Assesses local vs international supplier balance (89.9% local dependency)

Usage:
```bash
# Run comprehensive analysis for all strategic recommendations
python scripts/supply_chain_analyzer.py --analysis-type all

# Run specific analysis
python scripts/supply_chain_analyzer.py --analysis-type diversification
python scripts/supply_chain_analyzer.py --analysis-type relationships
python scripts/supply_chain_analyzer.py --analysis-type pricing
python scripts/supply_chain_analyzer.py --analysis-type sourcing
```

## Strategic Applications

### Supply Chain Risk Management
- Identify single-source dependencies requiring backup suppliers
- Monitor supplier financial stability and market positioning
- Track geographic concentration risks

### Cost Optimization
- Compare pricing across available suppliers
- Identify volume discount opportunities
- Monitor market pricing trends and fluctuations

### Formulation Planning
- Assess ingredient availability for new product development
- Evaluate supplier technical support capabilities
- Plan inventory requirements based on lead times

## Usage Instructions

### Accessing Current Data
```bash
# Clone the repository
git clone https://github.com/Kaw-Aii/skin-twin-supplier-research.git

# Navigate to data directory
cd skin-twin-supplier-research/data

# View updated hypergraph nodes
cat RSNodes_updated.csv
```

### Running Manual Updates
```bash
# Navigate to scripts directory
cd scripts

# Run with dry-run mode (no changes)
python update_supplier_data.py --dry-run --verbose

# Run full update
python update_supplier_data.py --verbose
```

## Contact

For technical questions about this repository or the automation systems, please create an issue or contact the research team.

---

*Repository: https://github.com/Kaw-Aii/skin-twin-supplier-research*
