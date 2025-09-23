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

## Key Findings Summary

### Major Suppliers Identified
- **Natchem CC**: 16 ingredients (18% market share) - Exclusive Greentech distributor
- **Meganede CC**: 15 ingredients (16% market share) - Silab distributor  
- **Croda Chemicals**: 7 premium biotech ingredients with local Centre of Excellence
- **Botanichem**: 2 ingredients with transparent online pricing (R352-R10,318 range)
- **AECI Specialty Chemicals**: Diversified chemical company with sustainability focus
- **Carst & Walker**: Substantial importer and distributor, part of Hobart Enterprises group

### Critical Supply Chain Insights
- **Coverage**: 25 ingredients analyzed (27% of total 91-ingredient portfolio)
- **Single-sourcing Risk**: 100% of ingredients have only one identified supplier
- **Pricing Transparency Gap**: Only Botanichem provides direct online pricing
- **Geographic Concentration**: All suppliers based in South Africa
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

- **Last Updated**: September 22, 2025
- **Coverage**: 25/91 ingredients (27%)
- **Verification**: Direct supplier website research
- **Accuracy**: Contact information verified through official sources

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
