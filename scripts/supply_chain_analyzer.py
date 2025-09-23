#!/usr/bin/env python3
"""
SKIN-TWIN Supply Chain Analysis Tool

Implements automated analysis to support strategic recommendations:
- 4.1: Diversify Supplier Base
- 4.2: Strengthen Supplier Relationships  
- 4.3: Enhance Pricing Transparency
- 4.4: Leverage Local and International Suppliers

Usage:
    python supply_chain_analyzer.py [--analysis-type all|diversification|relationships|pricing|sourcing]
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
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupplyChainAnalyzer:
    """Implements supply chain analysis to support strategic recommendations."""
    
    def __init__(self, data_dir="../data", reports_dir="../reports"):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        
        # Data containers
        self.suppliers = {}
        self.ingredients = {}
        self.supply_relationships = []
        self.edges_data = []
        
        self.load_data()
    
    def load_data(self):
        """Load data from CSV files."""
        logger.info("Loading supply chain data...")
        
        # Load nodes data
        nodes_file = self.data_dir / "RSNodes_updated.csv"
        if nodes_file.exists():
            with open(nodes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    node_id = row['Id']
                    
                    # Determine if supplier or ingredient based on ID patterns
                    # R-codes are ingredients, everything else that's not clearly an ingredient should be a supplier
                    if node_id.startswith('R') and len(node_id) > 5:
                        # This is an ingredient
                        self.ingredients[node_id] = {
                            'id': node_id,
                            'name': row['Label'],
                            'suppliers': []  # Will be populated from edges
                        }
                    else:
                        # This is a supplier
                        self.suppliers[node_id] = {
                            'id': node_id,
                            'name': row['Label'],
                            'availability': row.get('availability', 'Unknown'),
                            'pricing': row.get('pricing_estimate', 'Unknown'),
                            'url': row.get('supplier_url', ''),
                            'notes': row.get('notes', ''),
                            'status': row.get('website_status', 'unknown')
                        }
        
        # Load edges data to establish supply relationships
        edges_file = self.data_dir / "RSEdges.csv"
        if edges_file.exists():
            with open(edges_file, 'r', encoding='utf-8') as f:
                # The edges file is tab-separated, not comma-separated
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    source = row.get('Source', '')
                    target = row.get('Target', '')
                    
                    # In this data, ingredients (R codes) point to suppliers
                    if source in self.ingredients and target in self.suppliers:
                        self.supply_relationships.append({
                            'supplier_id': target,
                            'ingredient_id': source,
                            'supplier_name': self.suppliers[target]['name'],
                            'ingredient_name': self.ingredients[source]['name']
                        })
                        self.ingredients[source]['suppliers'].append(target)
                        
                    self.edges_data.append(row)
        
        logger.info(f"Loaded {len(self.suppliers)} suppliers and {len(self.ingredients)} ingredients")
    
    def analyze_supplier_diversification(self) -> Dict:
        """Analyze supplier diversification risks (Strategic Recommendation 4.1)."""
        logger.info("Analyzing supplier diversification opportunities...")
        
        # Identify single-sourced ingredients
        single_sourced = []
        limited_sourced = []
        well_diversified = []
        
        for ingredient_id, ingredient_data in self.ingredients.items():
            supplier_count = len(ingredient_data['suppliers'])
            
            if supplier_count == 0:
                # No suppliers identified
                pass
            elif supplier_count == 1:
                single_sourced.append({
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient_data['name'],
                    'supplier_id': ingredient_data['suppliers'][0],
                    'supplier_name': self.suppliers[ingredient_data['suppliers'][0]]['name'],
                    'risk_level': 'CRITICAL'
                })
            elif supplier_count <= 2:
                limited_sourced.append({
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient_data['name'],
                    'supplier_count': supplier_count,
                    'suppliers': [self.suppliers[s]['name'] for s in ingredient_data['suppliers']],
                    'risk_level': 'HIGH'
                })
            else:
                well_diversified.append({
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient_data['name'],
                    'supplier_count': supplier_count,
                    'risk_level': 'LOW'
                })
        
        # Generate recommendations for alternative suppliers
        alternative_recommendations = []
        for item in single_sourced[:10]:  # Top 10 most critical
            recommendations = self._suggest_alternative_suppliers(item['ingredient_name'])
            alternative_recommendations.append({
                'ingredient': item['ingredient_name'],
                'current_supplier': item['supplier_name'],
                'suggested_alternatives': recommendations
            })
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_ingredients': len(self.ingredients),
                'single_sourced_count': len(single_sourced),
                'limited_sourced_count': len(limited_sourced),
                'well_diversified_count': len(well_diversified),
                'diversification_percentage': round((len(well_diversified) / len(self.ingredients)) * 100, 1) if self.ingredients else 0
            },
            'critical_risks': single_sourced,
            'high_risks': limited_sourced,
            'alternative_recommendations': alternative_recommendations,
            'action_plan': {
                'immediate_priority': len(single_sourced),
                'medium_priority': len(limited_sourced),
                'recommendation': "Focus on identifying alternative suppliers for the {} single-sourced ingredients".format(len(single_sourced))
            }
        }
        
        return analysis
    
    def analyze_supplier_relationships(self) -> Dict:
        """Analyze supplier relationship opportunities (Strategic Recommendation 4.2)."""
        logger.info("Analyzing supplier relationship strengthening opportunities...")
        
        # Identify key suppliers by portfolio size
        supplier_portfolios = defaultdict(list)
        for rel in self.supply_relationships:
            supplier_portfolios[rel['supplier_id']].append(rel['ingredient_id'])
        
        # Rank suppliers by strategic importance
        strategic_suppliers = []
        for supplier_id, ingredients in supplier_portfolios.items():
            supplier_data = self.suppliers[supplier_id]
            strategic_suppliers.append({
                'supplier_id': supplier_id,
                'supplier_name': supplier_data['name'],
                'ingredient_count': len(ingredients),
                'market_share_pct': round((len(ingredients) / len(self.ingredients)) * 100, 1) if self.ingredients else 0,
                'relationship_strength': self._assess_relationship_strength(supplier_data),
                'contact_info_complete': bool(supplier_data.get('url') and supplier_data['url'] != 'Unknown'),
                'website_status': supplier_data.get('status', 'unknown'),
                'specialization': self._determine_specialization(supplier_data['name'], supplier_data['notes'])
            })
        
        # Sort by ingredient count (market share)
        strategic_suppliers.sort(key=lambda x: x['ingredient_count'], reverse=True)
        
        # Generate relationship strengthening recommendations
        top_suppliers = strategic_suppliers[:5]
        recommendations = []
        for supplier in top_suppliers:
            rec = {
                'supplier': supplier['supplier_name'],
                'priority': 'HIGH' if supplier['ingredient_count'] > 10 else 'MEDIUM',
                'actions': []
            }
            
            if not supplier['contact_info_complete']:
                rec['actions'].append('Establish direct contact and gather complete contact information')
            
            if supplier['website_status'] == 'offline':
                rec['actions'].append('Verify supplier status and update contact information')
            
            if supplier['relationship_strength'] == 'WEAK':
                rec['actions'].append('Schedule relationship building meetings and establish partnership agreements')
            
            rec['actions'].append('Negotiate volume-based pricing and early access to new products')
            rec['actions'].append('Establish regular communication schedule and technical support channels')
            
            recommendations.append(rec)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'strategic_suppliers': strategic_suppliers,
            'top_partnerships': top_suppliers,
            'relationship_recommendations': recommendations,
            'summary': {
                'total_suppliers': len(self.suppliers),
                'active_relationships': len([s for s in strategic_suppliers if s['website_status'] == 'online']),
                'top_5_market_share': sum(s['ingredient_count'] for s in top_suppliers)
            }
        }
        
        return analysis
    
    def analyze_pricing_transparency(self) -> Dict:
        """Analyze pricing transparency opportunities (Strategic Recommendation 4.3)."""
        logger.info("Analyzing pricing transparency enhancement opportunities...")
        
        # Categorize suppliers by pricing transparency
        transparent_pricing = []
        quote_based = []
        no_pricing_info = []
        
        for supplier_id, supplier_data in self.suppliers.items():
            pricing = supplier_data['pricing'].lower()
            ingredient_count = len([r for r in self.supply_relationships if r['supplier_id'] == supplier_id])
            
            supplier_info = {
                'supplier_id': supplier_id,
                'supplier_name': supplier_data['name'],
                'pricing_info': supplier_data['pricing'],
                'ingredient_count': ingredient_count,
                'url': supplier_data['url']
            }
            
            if 'r' in pricing and '.' in pricing:  # Contains currency amounts
                transparent_pricing.append(supplier_info)
            elif 'contact' in pricing or 'quote' in pricing:
                quote_based.append(supplier_info)
            else:
                no_pricing_info.append(supplier_info)
        
        # Generate pricing transparency improvement plan
        transparency_actions = []
        
        # For quote-based suppliers, recommend systematic quote requests
        high_priority_quotes = [s for s in quote_based if s['ingredient_count'] > 5]
        for supplier in high_priority_quotes[:10]:
            transparency_actions.append({
                'supplier': supplier['supplier_name'],
                'action': 'Request comprehensive pricing list for all {} ingredients'.format(supplier['ingredient_count']),
                'priority': 'HIGH',
                'expected_outcome': 'Establish baseline pricing for comparison and negotiation'
            })
        
        # Recommend implementing competitive bidding
        ingredients_for_bidding = []
        for ingredient_id, ingredient_data in self.ingredients.items():
            if len(ingredient_data['suppliers']) > 1:
                supplier_names = [self.suppliers[s]['name'] for s in ingredient_data['suppliers']]
                ingredients_for_bidding.append({
                    'ingredient': ingredient_data['name'],
                    'supplier_count': len(ingredient_data['suppliers']),
                    'suppliers': supplier_names
                })
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'pricing_categories': {
                'transparent_pricing': transparent_pricing,
                'quote_based': quote_based,
                'no_pricing_info': no_pricing_info
            },
            'transparency_metrics': {
                'transparent_suppliers': len(transparent_pricing),
                'quote_based_suppliers': len(quote_based),
                'transparency_percentage': round((len(transparent_pricing) / len(self.suppliers)) * 100, 1) if self.suppliers else 0
            },
            'improvement_actions': transparency_actions,
            'competitive_bidding_opportunities': ingredients_for_bidding[:15],  # Top 15 opportunities
            'recommendations': {
                'immediate': 'Request quotes from top {} suppliers for systematic price comparison'.format(len(high_priority_quotes)),
                'systematic': 'Implement quarterly pricing surveys for all major ingredients',
                'competitive': 'Establish competitive bidding process for {} multi-sourced ingredients'.format(len(ingredients_for_bidding))
            }
        }
        
        return analysis
    
    def analyze_sourcing_strategy(self) -> Dict:
        """Analyze local vs international sourcing strategy (Strategic Recommendation 4.4)."""
        logger.info("Analyzing local vs international sourcing strategy...")
        
        # Classify suppliers by origin
        local_suppliers = []
        international_suppliers = []
        acquired_suppliers = []
        
        for supplier_id, supplier_data in self.suppliers.items():
            supplier_info = {
                'supplier_id': supplier_id,
                'supplier_name': supplier_data['name'],
                'ingredient_count': len([r for r in self.supply_relationships if r['supplier_id'] == supplier_id]),
                'notes': supplier_data['notes'],
                'url': supplier_data['url']
            }
            
            # Classify based on URL domain and notes
            url = supplier_data['url'].lower()
            notes = supplier_data['notes'].lower()
            
            if any(domain in url for domain in ['.co.za', 'south africa']) or 'south africa' in notes:
                if any(term in notes for term in ['brenntag', 'azelis', 'acquired']):
                    acquired_suppliers.append({**supplier_info, 'acquisition_company': self._extract_acquisition_info(notes)})
                else:
                    local_suppliers.append(supplier_info)
            elif any(domain in url for domain in ['.com', '.co.uk', '.fr']) and 'south africa' not in notes:
                international_suppliers.append(supplier_info)
            else:
                local_suppliers.append(supplier_info)  # Default to local if unclear
        
        # Analyze market concentration
        local_market_share = sum(s['ingredient_count'] for s in local_suppliers)
        international_market_share = sum(s['ingredient_count'] for s in international_suppliers)
        acquired_market_share = sum(s['ingredient_count'] for s in acquired_suppliers)
        
        total_relationships = len(self.supply_relationships)
        # Handle case where no relationships are found
        if total_relationships == 0:
            total_relationships = 1  # Prevent division by zero
        
        # Generate sourcing recommendations
        sourcing_recommendations = []
        
        # If too locally concentrated
        if local_market_share / total_relationships > 0.8:
            sourcing_recommendations.append({
                'recommendation': 'Increase international supplier diversity',
                'rationale': 'Over-reliance on local suppliers creates geographic risk',
                'action': 'Identify 3-5 international suppliers for critical ingredients',
                'priority': 'HIGH'
            })
        
        # Leverage acquired companies
        if acquired_suppliers:
            sourcing_recommendations.append({
                'recommendation': 'Leverage global networks of acquired local suppliers',
                'rationale': 'Acquisitions by Brenntag and Azelis provide access to international supply chains',
                'action': 'Explore international ingredient options through local acquired distributors',
                'priority': 'MEDIUM'
            })
        
        # International expansion opportunities
        top_international = sorted(international_suppliers, key=lambda x: x['ingredient_count'], reverse=True)[:3]
        if top_international:
            sourcing_recommendations.append({
                'recommendation': 'Strengthen relationships with top international suppliers',
                'rationale': 'International suppliers provide access to innovative ingredients and competitive pricing',
                'action': f"Focus on partnerships with {', '.join(s['supplier_name'] for s in top_international)}",
                'priority': 'MEDIUM'
            })
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'supplier_classification': {
                'local_suppliers': local_suppliers,
                'international_suppliers': international_suppliers,
                'acquired_suppliers': acquired_suppliers
            },
            'market_distribution': {
                'local_market_share_pct': round((local_market_share / total_relationships) * 100, 1) if total_relationships else 0,
                'international_market_share_pct': round((international_market_share / total_relationships) * 100, 1) if total_relationships else 0,
                'acquired_market_share_pct': round((acquired_market_share / total_relationships) * 100, 1) if total_relationships else 0
            },
            'strategic_recommendations': sourcing_recommendations,
            'geographic_risk_assessment': {
                'concentration_risk': 'HIGH' if local_market_share / total_relationships > 0.8 else 'MEDIUM',
                'diversification_opportunity': len(international_suppliers),
                'acquisition_leverage': len(acquired_suppliers)
            }
        }
        
        return analysis
    
    def _suggest_alternative_suppliers(self, ingredient_name: str) -> List[str]:
        """Suggest alternative suppliers based on ingredient type and existing network."""
        # This is a simplified suggestion algorithm
        # In reality, this would use more sophisticated matching based on ingredient categories
        
        ingredient_lower = ingredient_name.lower()
        suggestions = []
        
        # Suggest based on ingredient type patterns
        if any(term in ingredient_lower for term in ['extract', 'phytenlene', 'cosmelene']):
            suggestions.extend(['Natchem CC (Greentech portfolio)', 'Botanichem', 'Materia Medica'])
        
        if any(term in ingredient_lower for term in ['emulsifier', 'emuls']):
            suggestions.extend(['Croda Chemicals', 'AECI Specialty Chemicals', 'Savannah Fine Chemicals'])
        
        if any(term in ingredient_lower for term in ['oil', 'butter']):
            suggestions.extend(['Clive Teubes CC', 'Botanichem', 'A&E Connock'])
        
        # Remove duplicates and limit suggestions
        return list(set(suggestions))[:3]
    
    def _assess_relationship_strength(self, supplier_data: Dict) -> str:
        """Assess the strength of current supplier relationship."""
        if supplier_data.get('status') == 'online' and supplier_data.get('url'):
            return 'STRONG'
        elif supplier_data.get('url') and supplier_data['url'] != 'Unknown':
            return 'MODERATE'
        else:
            return 'WEAK'
    
    def _determine_specialization(self, name: str, notes: str) -> str:
        """Determine supplier specialization based on name and notes."""
        text = (name + ' ' + notes).lower()
        
        if any(term in text for term in ['greentech', 'botanical', 'natural']):
            return 'Botanical Actives'
        elif any(term in text for term in ['silab', 'biotechnology']):
            return 'Biotech Ingredients'
        elif any(term in text for term in ['croda', 'emulsifier', 'biotech']):
            return 'Advanced Chemicals'
        elif any(term in text for term in ['fragrance', 'essential oil']):
            return 'Fragrances & Oils'
        else:
            return 'General Ingredients'
    
    def _extract_acquisition_info(self, notes: str) -> str:
        """Extract acquisition company information from notes."""
        notes_lower = notes.lower()
        if 'brenntag' in notes_lower:
            return 'Brenntag'
        elif 'azelis' in notes_lower:
            return 'Azelis'
        else:
            return 'Unknown'
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive analysis report for all strategic recommendations."""
        logger.info("Generating comprehensive supply chain analysis report...")
        
        diversification = self.analyze_supplier_diversification()
        relationships = self.analyze_supplier_relationships()
        pricing = self.analyze_pricing_transparency()
        sourcing = self.analyze_sourcing_strategy()
        
        comprehensive_report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'Comprehensive Supply Chain Analysis',
                'strategic_focus': 'Implementation of Strategic Recommendations 4.1-4.4'
            },
            'executive_summary': {
                'total_suppliers': len(self.suppliers),
                'total_ingredients': len(self.ingredients),
                'supply_relationships': len(self.supply_relationships),
                'critical_risks': diversification['summary']['single_sourced_count'],
                'transparency_level': pricing['transparency_metrics']['transparency_percentage'],
                'local_dependency': sourcing['market_distribution']['local_market_share_pct']
            },
            'strategic_analyses': {
                '4.1_supplier_diversification': diversification,
                '4.2_supplier_relationships': relationships,
                '4.3_pricing_transparency': pricing,
                '4.4_sourcing_strategy': sourcing
            },
            'implementation_roadmap': {
                'immediate_actions': [
                    f"Address {diversification['summary']['single_sourced_count']} single-sourced ingredients",
                    f"Request pricing from {len(pricing['pricing_categories']['quote_based'])} quote-based suppliers",
                    f"Strengthen relationships with top {len(relationships['top_partnerships'])} strategic suppliers"
                ],
                'medium_term_goals': [
                    "Implement systematic pricing comparison process",
                    "Establish backup suppliers for critical ingredients",
                    "Leverage international networks through acquired suppliers"
                ],
                'long_term_objectives': [
                    "Achieve 80% supplier diversification for all ingredients",
                    "Establish transparent pricing for 90% of supplier network",
                    "Balance local/international sourcing for optimal risk management"
                ]
            }
        }
        
        return comprehensive_report
    
    def save_analysis_report(self, analysis_data: Dict, report_type: str):
        """Save analysis report to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"supply_chain_analysis_{report_type}_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis report saved to {report_file}")
        return report_file

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Analyze SKIN-TWIN supply chain for strategic recommendations')
    parser.add_argument('--analysis-type', 
                       choices=['all', 'diversification', 'relationships', 'pricing', 'sourcing'],
                       default='all',
                       help='Type of analysis to perform')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize analyzer
        analyzer = SupplyChainAnalyzer()
        
        # Perform selected analysis
        if args.analysis_type == 'all':
            report = analyzer.generate_comprehensive_report()
            print("\n=== COMPREHENSIVE SUPPLY CHAIN ANALYSIS ===")
            print(f"Total Suppliers: {report['executive_summary']['total_suppliers']}")
            print(f"Total Ingredients: {report['executive_summary']['total_ingredients']}")
            print(f"Critical Single-Source Risks: {report['executive_summary']['critical_risks']}")
            print(f"Pricing Transparency: {report['executive_summary']['transparency_level']}%")
            print(f"Local Market Dependency: {report['executive_summary']['local_dependency']}%")
            
            analyzer.save_analysis_report(report, 'comprehensive')
        
        elif args.analysis_type == 'diversification':
            analysis = analyzer.analyze_supplier_diversification()
            print(f"\n=== SUPPLIER DIVERSIFICATION ANALYSIS ===")
            print(f"Single-sourced ingredients: {analysis['summary']['single_sourced_count']}")
            print(f"Limited-sourced ingredients: {analysis['summary']['limited_sourced_count']}")
            print(f"Diversification percentage: {analysis['summary']['diversification_percentage']}%")
            
            analyzer.save_analysis_report(analysis, 'diversification')
        
        elif args.analysis_type == 'relationships':
            analysis = analyzer.analyze_supplier_relationships()
            print(f"\n=== SUPPLIER RELATIONSHIPS ANALYSIS ===")
            print(f"Total suppliers: {analysis['summary']['total_suppliers']}")
            print(f"Active relationships: {analysis['summary']['active_relationships']}")
            print(f"Top 5 suppliers market share: {analysis['summary']['top_5_market_share']} ingredients")
            
            analyzer.save_analysis_report(analysis, 'relationships')
        
        elif args.analysis_type == 'pricing':
            analysis = analyzer.analyze_pricing_transparency()
            print(f"\n=== PRICING TRANSPARENCY ANALYSIS ===")
            print(f"Transparent pricing: {analysis['transparency_metrics']['transparent_suppliers']} suppliers")
            print(f"Quote-based pricing: {analysis['transparency_metrics']['quote_based_suppliers']} suppliers")
            print(f"Transparency percentage: {analysis['transparency_metrics']['transparency_percentage']}%")
            
            analyzer.save_analysis_report(analysis, 'pricing')
        
        elif args.analysis_type == 'sourcing':
            analysis = analyzer.analyze_sourcing_strategy()
            print(f"\n=== SOURCING STRATEGY ANALYSIS ===")
            print(f"Local market share: {analysis['market_distribution']['local_market_share_pct']}%")
            print(f"International market share: {analysis['market_distribution']['international_market_share_pct']}%")
            print(f"Acquired suppliers: {len(analysis['supplier_classification']['acquired_suppliers'])}")
            
            analyzer.save_analysis_report(analysis, 'sourcing')
        
        print(f"\nAnalysis complete. Report saved to reports directory.")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()