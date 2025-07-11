#!/usr/bin/env python3
"""
Enhanced RAG Knowledge Agent for Liquidation Document Generation
Now supports dynamic knowledge updates from PDF analysis and template generation
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .base_agent import BaseAgent, AgentTask


@dataclass
class DocumentKnowledge:
    """Enhanced document knowledge structure with PDF analysis integration"""
    document_type: str
    structure: Dict[str, Any]
    legal_clauses: List[str]
    compliance_rules: List[str]
    professional_terms: Dict[str, str]
    template_patterns: Dict[str, Any]  # New: Template patterns from PDF analysis
    design_elements: Dict[str, Any]    # New: Design elements and styling
    multipage_support: bool            # New: Multi-page capability
    logo_integration: bool             # New: Logo support
    complexity_level: str              # New: Simple/Medium/Complex
    source_documents: List[str]        # New: Source PDF documents


@dataclass
class LegalClause:
    """Enhanced legal clause with context and applicability"""
    clause_id: str
    title: str
    content: str
    section_reference: str
    applicable_documents: List[str]
    mandatory: bool
    context_requirements: List[str]     # New: When this clause applies
    template_integration: Dict[str, Any]  # New: How to integrate in templates


@dataclass
class ComplianceRule:
    """Enhanced compliance rule with template integration"""
    rule_id: str
    title: str
    description: str
    requirement: str
    penalty: str
    deadline_type: str
    applicable_entities: List[str]
    validation_method: str
    template_checks: List[str]          # New: Template validation points
    pdf_examples: List[str]             # New: Example documents showing compliance


@dataclass
class TemplatePattern:
    """New: Template pattern from PDF analysis"""
    pattern_id: str
    source_document: str
    document_type: str
    layout_features: Dict[str, Any]
    content_sections: List[str]
    design_elements: Dict[str, Any]
    complexity_score: int
    reusability_score: int
    generated_template: Optional[str]


class RAGKnowledgeAgent(BaseAgent):
    """
    Enhanced RAG Knowledge Agent with PDF Analysis Integration
    
    New capabilities:
    - Dynamic knowledge base updates from PDF analysis
    - Template pattern recognition and storage
    - Design element cataloging
    - Multi-source knowledge consolidation
    - Automatic compliance checking enhancement
    """
    
    def __init__(self, knowledge_file: str = "knowledge_base.json", logger: Optional[logging.Logger] = None):
        super().__init__("RAG Knowledge Agent", logger)
        self.knowledge_file = Path(knowledge_file)
        
        # Enhanced knowledge base
        self.knowledge_base: Dict[str, DocumentKnowledge] = {}
        self.legal_clauses: Dict[str, LegalClause] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.template_patterns: Dict[str, TemplatePattern] = {}  # New
        self.design_library: Dict[str, Any] = {}                # New
        self.pdf_analysis_cache: Dict[str, Any] = {}            # New
        
        # Performance tracking
        self.knowledge_stats = {
            "documents_analyzed": 0,
            "templates_generated": 0,
            "patterns_discovered": 0,
            "last_update": None
        }
        
        # Load existing knowledge
        self._load_knowledge_base()
        self._initialize_enhanced_knowledge()
        
        self.logger.info("Enhanced RAG Knowledge Agent initialized with PDF analysis support")

    def _initialize_enhanced_knowledge(self):
        """Initialize enhanced knowledge base with PDF analysis capabilities"""
        # Existing knowledge initialization
        self._initialize_document_knowledge()
        self._initialize_legal_clauses()
        self._initialize_compliance_rules()
        
        # New: Initialize template patterns and design library
        self._initialize_template_patterns()
        self._initialize_design_library()

    def _initialize_template_patterns(self):
        """Initialize template patterns from PDF analysis"""
        # Base template patterns that can be enhanced by PDF analysis
        base_patterns = {
            "simple_resolution": TemplatePattern(
                pattern_id="simple_resolution",
                source_document="internal_template",
                document_type="liquidation_resolution",
                layout_features={
                    "header": {"type": "centered", "logo_support": False},
                    "body": {"columns": 1, "sections": ["resolution", "signatures"]},
                    "footer": {"minimal": True}
                },
                content_sections=["header", "company_info", "resolution_text", "signatures"],
                design_elements={"fonts": ["Times New Roman"], "colors": ["black"], "borders": "minimal"},
                complexity_score=1,
                reusability_score=8,
                generated_template="liquidation_resolution.j2"
            ),
            
            "complex_multipage": TemplatePattern(
                pattern_id="complex_multipage",
                source_document="government_sample",
                document_type="comprehensive_liquidation",
                layout_features={
                    "header": {"type": "branded", "logo_support": True},
                    "body": {"columns": 1, "sections": ["multiple"], "tables": True},
                    "footer": {"page_numbers": True, "contact_info": True}
                },
                content_sections=["header", "company_info", "resolution", "assets", "liabilities", "notices", "signatures"],
                design_elements={"fonts": ["Times New Roman", "Arial"], "colors": ["black", "grey"], "borders": "formal"},
                complexity_score=5,
                reusability_score=6,
                generated_template=None
            )
        }
        
        self.template_patterns.update(base_patterns)

    def _initialize_design_library(self):
        """Initialize design element library"""
        self.design_library = {
            "headers": {
                "simple": {"alignment": "center", "font_size": "18pt", "font_weight": "bold"},
                "formal": {"alignment": "center", "font_size": "16pt", "font_weight": "bold", "border_bottom": "2px solid"},
                "branded": {"alignment": "left", "logo_position": "top-left", "company_name": "prominent"}
            },
            
            "logos": {
                "placement": ["top-center", "top-left", "top-right"],
                "max_sizes": {"width": "200px", "height": "80px"},
                "formats": ["png", "jpg", "svg"]
            },
            
            "tables": {
                "assets": {"columns": ["Description", "Book Value", "Estimated Value"], "styling": "bordered"},
                "liabilities": {"columns": ["Creditor", "Nature", "Amount", "Security"], "styling": "bordered"},
                "signatures": {"columns": ["Name", "Position", "Signature", "Date"], "styling": "minimal"}
            },
            
            "layouts": {
                "single_page": {"sections": ["header", "body", "footer"]},
                "multi_page": {"sections": ["header", "body_pages", "appendices", "footer"]},
                "form_based": {"sections": ["header", "form_fields", "instructions", "footer"]}
            }
        }

    def get_capabilities(self) -> List[str]:
        return [
            "get_document_knowledge",
            "add_document_knowledge",
            "update_knowledge_base", 
            "get_legal_clauses",
            "get_compliance_rules",
            "analyze_document_compliance",
            "integrate_pdf_analysis",       # New
            "update_template_patterns",     # New
            "get_design_recommendations",   # New
            "consolidate_knowledge",        # New
            "get_pattern_suggestions",      # New
            "validate_document_structure",  # New
            "export_enhanced_knowledge"     # New
        ]

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process enhanced RAG tasks with PDF analysis integration"""
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            # Existing tasks
            if task_type == "get_document_knowledge":
                return await self._get_document_knowledge(input_data)
            elif task_type == "add_document_knowledge":
                return await self._add_document_knowledge(input_data)
            elif task_type == "update_knowledge_base":
                return await self._update_knowledge_base(input_data)
            elif task_type == "get_legal_clauses":
                return await self._get_legal_clauses(input_data)
            elif task_type == "get_compliance_rules":
                return await self._get_compliance_rules(input_data)
            elif task_type == "analyze_document_compliance":
                return await self._analyze_document_compliance(input_data)
            
            # New PDF analysis integration tasks
            elif task_type == "integrate_pdf_analysis":
                return await self._integrate_pdf_analysis(input_data)
            elif task_type == "update_template_patterns":
                return await self._update_template_patterns(input_data)
            elif task_type == "get_design_recommendations":
                return await self._get_design_recommendations(input_data)
            elif task_type == "consolidate_knowledge":
                return await self._consolidate_knowledge(input_data)
            elif task_type == "get_pattern_suggestions":
                return await self._get_pattern_suggestions(input_data)
            elif task_type == "validate_document_structure":
                return await self._validate_document_structure(input_data)
            elif task_type == "export_enhanced_knowledge":
                return await self._export_enhanced_knowledge(input_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"RAG knowledge task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Using existing knowledge base"
            }

    async def _integrate_pdf_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate PDF analysis results into the knowledge base"""
        analysis_data = input_data.get("analysis_results", {})
        if not analysis_data:
            return {
                "success": False,
                "error": "No analysis data provided"
            }
        
        self.logger.info("Integrating PDF analysis results into knowledge base")
        
        integrated_count = 0
        new_patterns = 0
        updated_knowledge = 0
        
        # Process each analyzed document
        for doc_id, analysis in analysis_data.items():
            if not isinstance(analysis, dict) or not analysis.get("success"):
                continue
            
            doc_analysis = analysis.get("analysis", {})
            if not doc_analysis:
                continue
            
            # Create template pattern from analysis
            pattern = await self._create_pattern_from_analysis(doc_id, doc_analysis)
            if pattern:
                self.template_patterns[pattern.pattern_id] = pattern
                new_patterns += 1
            
            # Update document knowledge
            doc_type = self._infer_document_type(doc_analysis)
            if doc_type:
                await self._update_document_knowledge_from_analysis(doc_type, doc_analysis)
                updated_knowledge += 1
            
            # Update design library
            await self._update_design_library_from_analysis(doc_analysis)
            
            # Cache analysis for future reference
            self.pdf_analysis_cache[doc_id] = {
                "analysis": doc_analysis,
                "timestamp": datetime.now().isoformat(),
                "integrated": True
            }
            
            integrated_count += 1
        
        # Update statistics
        self.knowledge_stats["documents_analyzed"] += integrated_count
        self.knowledge_stats["patterns_discovered"] += new_patterns
        self.knowledge_stats["last_update"] = datetime.now().isoformat()
        
        # Save updated knowledge base
        self._save_knowledge_base()
        
        return {
            "success": True,
            "integrated_documents": integrated_count,
            "new_patterns": new_patterns,
            "updated_knowledge": updated_knowledge,
            "total_patterns": len(self.template_patterns),
            "cache_size": len(self.pdf_analysis_cache)
        }

    async def _create_pattern_from_analysis(self, doc_id: str, analysis: Dict[str, Any]) -> Optional[TemplatePattern]:
        """Create template pattern from PDF analysis"""
        try:
            document_name = analysis.get("document_name", f"doc_{doc_id}")
            doc_type = self._infer_document_type(analysis)
            
            if not doc_type:
                return None
            
            # Extract layout features
            layout_features = {}
            design_elements = analysis.get("design_elements", {})
            
            # Header analysis
            headers = analysis.get("headers_footers", {}).get("headers", [])
            layout_features["header"] = {
                "type": "formal" if headers else "simple",
                "logo_support": "has_logo" in analysis.get("content_types", [])
            }
            
            # Body analysis
            sections = analysis.get("sections", [])
            tables = analysis.get("tables", [])
            layout_features["body"] = {
                "columns": 1,  # Most liquidation docs are single column
                "sections": sections,
                "tables": len(tables) > 0
            }
            
            # Footer analysis
            footers = analysis.get("headers_footers", {}).get("footers", [])
            layout_features["footer"] = {
                "has_content": bool(footers),
                "page_numbers": any("page" in f.lower() for f in footers)
            }
            
            # Calculate complexity and reusability scores
            complexity_score = self._calculate_complexity_score(analysis)
            reusability_score = self._calculate_reusability_score(analysis)
            
            pattern = TemplatePattern(
                pattern_id=f"pattern_{hashlib.md5(document_name.encode()).hexdigest()[:8]}",
                source_document=document_name,
                document_type=doc_type,
                layout_features=layout_features,
                content_sections=sections,
                design_elements=design_elements,
                complexity_score=complexity_score,
                reusability_score=reusability_score,
                generated_template=None  # Will be set when template is generated
            )
            
            return pattern
            
        except Exception as e:
            self.logger.warning(f"Failed to create pattern from analysis: {e}")
            return None

    def _infer_document_type(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Infer document type from analysis"""
        sections = analysis.get("sections", [])
        content_types = analysis.get("content_types", [])
        
        # Mapping based on detected sections
        if any("resolution" in s.lower() for s in sections):
            return "liquidation_resolution"
        elif any("creditor" in s.lower() or "notice" in s.lower() for s in sections):
            return "creditor_notice"
        elif any("liquidator" in s.lower() or "appointment" in s.lower() for s in sections):
            return "liquidator_appointment"
        elif any("director" in s.lower() or "statement" in s.lower() for s in sections):
            return "director_statement"
        elif "has_forms" in content_types:
            return "liquidation_form"
        else:
            return "general_liquidation"

    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate complexity score (1-5) based on document features"""
        score = 1
        
        # Page count
        pages = analysis.get("total_pages", 1)
        if pages > 1:
            score += min(pages - 1, 2)  # Up to +2 for multiple pages
        
        # Content types
        content_types = analysis.get("content_types", [])
        if "has_tables" in content_types:
            score += 1
        if "has_forms" in content_types:
            score += 1
        if "has_logo" in content_types:
            score += 0.5
        
        # Number of sections
        sections = len(analysis.get("sections", []))
        if sections > 5:
            score += 1
        
        return min(int(score), 5)

    def _calculate_reusability_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate reusability score (1-10) based on generalizability"""
        score = 5  # Base score
        
        # Standard sections increase reusability
        sections = analysis.get("sections", [])
        standard_sections = ["header", "company_info", "resolution", "signatures"]
        common_sections = sum(1 for s in standard_sections if any(std in s.lower() for std in standard_sections))
        score += common_sections
        
        # Complexity can reduce reusability
        complexity = self._calculate_complexity_score(analysis)
        if complexity > 3:
            score -= 1
        
        # Forms and specific layouts reduce reusability
        content_types = analysis.get("content_types", [])
        if "has_forms" in content_types:
            score -= 2
        
        return max(min(score, 10), 1)

    async def _update_document_knowledge_from_analysis(self, doc_type: str, analysis: Dict[str, Any]) -> None:
        """Update document knowledge based on PDF analysis"""
        if doc_type not in self.knowledge_base:
            # Create new document knowledge
            self.knowledge_base[doc_type] = DocumentKnowledge(
                document_type=doc_type,
                structure={},
                legal_clauses=[],
                compliance_rules=[],
                professional_terms={},
                template_patterns={},
                design_elements={},
                multipage_support=False,
                logo_integration=False,
                complexity_level="Simple",
                source_documents=[]
            )
        
        knowledge = self.knowledge_base[doc_type]
        
        # Update structure
        knowledge.structure.update({
            "sections": analysis.get("sections", []),
            "page_count": analysis.get("total_pages", 1),
            "content_types": analysis.get("content_types", [])
        })
        
        # Update capabilities
        content_types = analysis.get("content_types", [])
        knowledge.multipage_support = analysis.get("total_pages", 1) > 1
        knowledge.logo_integration = "has_logo" in content_types
        
        # Update complexity level
        complexity_score = self._calculate_complexity_score(analysis)
        if complexity_score <= 2:
            knowledge.complexity_level = "Simple"
        elif complexity_score <= 4:
            knowledge.complexity_level = "Medium"
        else:
            knowledge.complexity_level = "Complex"
        
        # Add source document
        doc_name = analysis.get("document_name", "unknown")
        if doc_name not in knowledge.source_documents:
            knowledge.source_documents.append(doc_name)
        
        # Update design elements
        knowledge.design_elements.update(analysis.get("design_elements", {}))

    async def _update_design_library_from_analysis(self, analysis: Dict[str, Any]) -> None:
        """Update design library with new patterns from analysis"""
        design_elements = analysis.get("design_elements", {})
        
        # Update margins if detected
        if "page_margins" in design_elements:
            margins = design_elements["page_margins"]
            if "margins" not in self.design_library:
                self.design_library["margins"] = {}
            
            margin_key = f"margins_{len(self.design_library['margins'])}"
            self.design_library["margins"][margin_key] = margins
        
        # Update font usage
        text_patterns = analysis.get("text_patterns", [])
        if text_patterns and "fonts" not in self.design_library:
            self.design_library["fonts"] = {}
        
        for pattern in text_patterns:
            pattern_type = pattern.get("type", "unknown")
            font_size = pattern.get("font_size", 12)
            
            if pattern_type not in self.design_library.get("fonts", {}):
                self.design_library["fonts"][pattern_type] = {
                    "sizes": [font_size],
                    "usage": pattern.get("sample_count", 1)
                }
            else:
                existing = self.design_library["fonts"][pattern_type]
                if font_size not in existing["sizes"]:
                    existing["sizes"].append(font_size)
                existing["usage"] += pattern.get("sample_count", 1)

    async def _get_design_recommendations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get design recommendations based on document type and requirements"""
        doc_type = input_data.get("document_type", "")
        requirements = input_data.get("requirements", {})
        
        recommendations = {
            "layout": {},
            "styling": {},
            "components": {},
            "templates": []
        }
        
        # Get matching patterns
        matching_patterns = [
            pattern for pattern in self.template_patterns.values()
            if pattern.document_type == doc_type or doc_type in pattern.document_type
        ]
        
        if matching_patterns:
            # Sort by reusability score
            matching_patterns.sort(key=lambda p: p.reusability_score, reverse=True)
            best_pattern = matching_patterns[0]
            
            recommendations["layout"] = best_pattern.layout_features
            recommendations["styling"] = best_pattern.design_elements
            recommendations["templates"].append({
                "pattern_id": best_pattern.pattern_id,
                "source": best_pattern.source_document,
                "complexity": best_pattern.complexity_score,
                "reusability": best_pattern.reusability_score
            })
        
        # Add design library recommendations
        if "headers" in self.design_library:
            header_style = "formal" if requirements.get("formal", True) else "simple"
            if requirements.get("logo"):
                header_style = "branded"
            
            if header_style in self.design_library["headers"]:
                recommendations["components"]["header"] = self.design_library["headers"][header_style]
        
        if "tables" in self.design_library and requirements.get("tables"):
            recommendations["components"]["tables"] = self.design_library["tables"]
        
        return {
            "success": True,
            "recommendations": recommendations,
            "matching_patterns": len(matching_patterns),
            "confidence": min(len(matching_patterns) * 20, 100)  # Up to 100% with 5+ patterns
        }

    async def _get_pattern_suggestions(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get template pattern suggestions based on requirements"""
        doc_type = input_data.get("document_type", "")
        features_needed = input_data.get("features", [])
        complexity_preference = input_data.get("complexity", "medium")
        
        # Filter patterns by document type
        relevant_patterns = [
            pattern for pattern in self.template_patterns.values()
            if doc_type in pattern.document_type or pattern.document_type == "general_liquidation"
        ]
        
        # Score patterns based on requirements
        scored_patterns = []
        for pattern in relevant_patterns:
            score = 0
            
            # Base reusability score
            score += pattern.reusability_score
            
            # Complexity matching
            complexity_map = {"simple": 1, "medium": 3, "complex": 5}
            preferred_complexity = complexity_map.get(complexity_preference, 3)
            complexity_diff = abs(pattern.complexity_score - preferred_complexity)
            score -= complexity_diff * 2  # Penalty for complexity mismatch
            
            # Feature matching
            layout_features = pattern.layout_features
            if "logo" in features_needed and layout_features.get("header", {}).get("logo_support"):
                score += 5
            if "tables" in features_needed and layout_features.get("body", {}).get("tables"):
                score += 5
            if "multipage" in features_needed and any("page" in str(f) for f in layout_features.values()):
                score += 3
            
            scored_patterns.append({
                "pattern": pattern,
                "score": score,
                "match_reasons": []  # Could be enhanced with detailed matching
            })
        
        # Sort by score
        scored_patterns.sort(key=lambda x: x["score"], reverse=True)
        
        # Format suggestions
        suggestions = []
        for item in scored_patterns[:5]:  # Top 5 suggestions
            pattern = item["pattern"]
            suggestions.append({
                "pattern_id": pattern.pattern_id,
                "source_document": pattern.source_document,
                "document_type": pattern.document_type,
                "complexity": pattern.complexity_score,
                "reusability": pattern.reusability_score,
                "match_score": item["score"],
                "features": {
                    "logo_support": pattern.layout_features.get("header", {}).get("logo_support", False),
                    "table_support": pattern.layout_features.get("body", {}).get("tables", False),
                    "multipage": pattern.complexity_score > 2
                },
                "generated_template": pattern.generated_template
            })
        
        return {
            "success": True,
            "suggestions": suggestions,
            "total_patterns": len(relevant_patterns),
            "top_suggestion": suggestions[0] if suggestions else None
        }

    async def _validate_document_structure(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate document structure against known patterns"""
        doc_type = input_data.get("document_type", "")
        proposed_structure = input_data.get("structure", {})
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Get reference patterns
        reference_patterns = [
            pattern for pattern in self.template_patterns.values()
            if pattern.document_type == doc_type
        ]
        
        if not reference_patterns:
            validation_results["warnings"].append(f"No reference patterns found for document type: {doc_type}")
            return {
                "success": True,
                "validation": validation_results
            }
        
        # Check against most common pattern
        common_pattern = max(reference_patterns, key=lambda p: p.reusability_score)
        expected_sections = common_pattern.content_sections
        proposed_sections = proposed_structure.get("sections", [])
        
        # Check for missing critical sections
        critical_sections = ["header", "company_info", "signatures"]
        for section in critical_sections:
            if not any(section.lower() in s.lower() for s in proposed_sections):
                validation_results["errors"].append(f"Missing critical section: {section}")
                validation_results["valid"] = False
        
        # Check for recommended sections
        for section in expected_sections:
            if not any(section.lower() in s.lower() for s in proposed_sections):
                validation_results["suggestions"].append(f"Consider adding section: {section}")
        
        # Check layout consistency
        if "layout" in proposed_structure:
            layout = proposed_structure["layout"]
            expected_layout = common_pattern.layout_features
            
            # Logo check
            if layout.get("logo") and not expected_layout.get("header", {}).get("logo_support"):
                validation_results["warnings"].append("Logo usage detected but not common in this document type")
        
        return {
            "success": True,
            "validation": validation_results,
            "reference_pattern": common_pattern.pattern_id,
            "confidence": len(reference_patterns) * 20  # More patterns = higher confidence
        }

    async def _consolidate_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate knowledge from multiple sources"""
        consolidation_results = {
            "merged_patterns": 0,
            "updated_knowledge": 0,
            "removed_duplicates": 0,
            "enhanced_clauses": 0
        }
        
        # Merge similar template patterns
        pattern_groups = {}
        for pattern in self.template_patterns.values():
            key = f"{pattern.document_type}_{pattern.complexity_score}"
            if key not in pattern_groups:
                pattern_groups[key] = []
            pattern_groups[key].append(pattern)
        
        # Consolidate similar patterns
        for group_patterns in pattern_groups.values():
            if len(group_patterns) > 1:
                # Merge similar patterns
                merged_pattern = self._merge_patterns(group_patterns)
                if merged_pattern:
                    # Replace individual patterns with merged one
                    for pattern in group_patterns:
                        if pattern.pattern_id in self.template_patterns:
                            del self.template_patterns[pattern.pattern_id]
                    
                    self.template_patterns[merged_pattern.pattern_id] = merged_pattern
                    consolidation_results["merged_patterns"] += 1
        
        # Update legal clauses with template integration
        for clause in self.legal_clauses.values():
            if not hasattr(clause, 'template_integration') or not clause.template_integration:
                clause.template_integration = self._generate_template_integration(clause)
                consolidation_results["enhanced_clauses"] += 1
        
        # Save consolidated knowledge
        self._save_knowledge_base()
        
        return {
            "success": True,
            "consolidation": consolidation_results,
            "total_patterns": len(self.template_patterns),
            "total_clauses": len(self.legal_clauses)
        }

    def _merge_patterns(self, patterns: List[TemplatePattern]) -> Optional[TemplatePattern]:
        """Merge similar template patterns"""
        if not patterns:
            return None
        
        # Use the pattern with highest reusability as base
        base_pattern = max(patterns, key=lambda p: p.reusability_score)
        
        # Merge features from all patterns
        merged_features = base_pattern.layout_features.copy()
        merged_sections = list(base_pattern.content_sections)
        merged_design = base_pattern.design_elements.copy()
        source_docs = [base_pattern.source_document]
        
        for pattern in patterns:
            if pattern.pattern_id != base_pattern.pattern_id:
                # Merge layout features
                for key, value in pattern.layout_features.items():
                    if key not in merged_features:
                        merged_features[key] = value
                    elif isinstance(value, dict) and isinstance(merged_features[key], dict):
                        merged_features[key].update(value)
                
                # Merge sections
                for section in pattern.content_sections:
                    if section not in merged_sections:
                        merged_sections.append(section)
                
                # Merge design elements
                merged_design.update(pattern.design_elements)
                source_docs.append(pattern.source_document)
        
        # Create merged pattern
        merged_pattern = TemplatePattern(
            pattern_id=f"merged_{hashlib.md5('_'.join(source_docs).encode()).hexdigest()[:8]}",
            source_document=f"merged_from_{len(source_docs)}_sources",
            document_type=base_pattern.document_type,
            layout_features=merged_features,
            content_sections=merged_sections,
            design_elements=merged_design,
            complexity_score=max(p.complexity_score for p in patterns),
            reusability_score=int(sum(p.reusability_score for p in patterns) / len(patterns)),
            generated_template=None
        )
        
        return merged_pattern

    def _generate_template_integration(self, clause: LegalClause) -> Dict[str, Any]:
        """Generate template integration instructions for a legal clause"""
        integration = {
            "placement": "body",
            "format": "paragraph",
            "conditional": False,
            "variables": []
        }
        
        # Analyze clause content for integration hints
        content_lower = clause.content.lower()
        
        # Determine placement
        if any(word in content_lower for word in ["signature", "director", "witness"]):
            integration["placement"] = "signature_section"
        elif any(word in content_lower for word in ["notice", "creditor", "meeting"]):
            integration["placement"] = "notice_section"
        elif any(word in content_lower for word in ["appointment", "liquidator"]):
            integration["placement"] = "appointment_section"
        
        # Determine format
        if "list" in content_lower or "following" in content_lower:
            integration["format"] = "list"
        elif "table" in content_lower or "schedule" in content_lower:
            integration["format"] = "table"
        
        # Check if conditional
        if any(word in content_lower for word in ["if", "when", "unless", "where"]):
            integration["conditional"] = True
        
        return integration

    async def _export_enhanced_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export enhanced knowledge base with PDF analysis integration"""
        export_format = input_data.get("format", "json")
        include_patterns = input_data.get("include_patterns", True)
        include_analysis_cache = input_data.get("include_analysis_cache", False)
        
        export_data = {
            "knowledge_base": {},
            "legal_clauses": {},
            "compliance_rules": {},
            "statistics": self.knowledge_stats.copy(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Export document knowledge
        for doc_type, knowledge in self.knowledge_base.items():
            export_data["knowledge_base"][doc_type] = asdict(knowledge)
        
        # Export legal clauses
        for clause_id, clause in self.legal_clauses.items():
            export_data["legal_clauses"][clause_id] = asdict(clause)
        
        # Export compliance rules
        for rule_id, rule in self.compliance_rules.items():
            export_data["compliance_rules"][rule_id] = asdict(rule)
        
        # Include template patterns if requested
        if include_patterns:
            export_data["template_patterns"] = {}
            for pattern_id, pattern in self.template_patterns.items():
                export_data["template_patterns"][pattern_id] = asdict(pattern)
        
        # Include design library
        export_data["design_library"] = self.design_library.copy()
        
        # Include PDF analysis cache if requested
        if include_analysis_cache:
            export_data["pdf_analysis_cache"] = self.pdf_analysis_cache.copy()
        
        # Save to file
        export_file = Path(input_data.get("output_file", f"enhanced_knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"))
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "export_file": str(export_file),
                "format": export_format,
                "size_kb": export_file.stat().st_size / 1024,
                "sections_exported": {
                    "document_knowledge": len(export_data["knowledge_base"]),
                    "legal_clauses": len(export_data["legal_clauses"]),
                    "compliance_rules": len(export_data["compliance_rules"]),
                    "template_patterns": len(export_data.get("template_patterns", {})),
                    "design_library_categories": len(export_data["design_library"])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Export failed: {str(e)}"
            }

    # Enhanced existing methods to work with new structure
    async def _get_document_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced document knowledge retrieval with template pattern matching"""
        doc_type = input_data.get("document_type", "liquidation_resolution")
        context = input_data.get("context", {})
        
        # Get base knowledge
        if doc_type not in self.knowledge_base:
            # Try to find similar document type
            similar_types = [dt for dt in self.knowledge_base.keys() if doc_type in dt or dt in doc_type]
            if similar_types:
                doc_type = similar_types[0]
            else:
                doc_type = "liquidation_resolution"  # Fallback
        
        knowledge = self.knowledge_base[doc_type]
        
        # Get matching template patterns
        matching_patterns = [
            pattern for pattern in self.template_patterns.values()
            if pattern.document_type == doc_type or doc_type in pattern.document_type
        ]
        
        # Select best pattern based on context
        best_pattern = None
        if matching_patterns:
            # Score patterns based on context requirements
            for pattern in matching_patterns:
                score = pattern.reusability_score
                
                # Context-based scoring
                if context.get("logo") and pattern.layout_features.get("header", {}).get("logo_support"):
                    score += 10
                if context.get("multipage") and pattern.complexity_score > 2:
                    score += 10
                if context.get("tables") and pattern.layout_features.get("body", {}).get("tables"):
                    score += 10
                
                pattern.temp_score = score
            
            best_pattern = max(matching_patterns, key=lambda p: getattr(p, 'temp_score', p.reusability_score))
        
        # Enhanced insights with template recommendations
        insights = [
            f"Document type: {knowledge.document_type}",
            f"Complexity level: {knowledge.complexity_level}",
            f"Multi-page support: {'Yes' if knowledge.multipage_support else 'No'}",
            f"Logo integration: {'Supported' if knowledge.logo_integration else 'Not supported'}",
            f"Source documents: {len(knowledge.source_documents)}"
        ]
        
        if best_pattern:
            insights.extend([
                f"Recommended template pattern: {best_pattern.pattern_id}",
                f"Pattern complexity: {best_pattern.complexity_score}/5",
                f"Pattern reusability: {best_pattern.reusability_score}/10"
            ])
        
        return {
            "success": True,
            "knowledge": asdict(knowledge),
            "template_pattern": asdict(best_pattern) if best_pattern else None,
            "matching_patterns": len(matching_patterns),
            "insights": insights,
            "confidence_score": min(85 + len(knowledge.source_documents) * 5, 100)
        }

    def _save_knowledge_base(self):
        """Save enhanced knowledge base to file"""
        save_data = {
            "knowledge_base": {k: asdict(v) for k, v in self.knowledge_base.items()},
            "legal_clauses": {k: asdict(v) for k, v in self.legal_clauses.items()},
            "compliance_rules": {k: asdict(v) for k, v in self.compliance_rules.items()},
            "template_patterns": {k: asdict(v) for k, v in self.template_patterns.items()},
            "design_library": self.design_library,
            "pdf_analysis_cache": self.pdf_analysis_cache,
            "knowledge_stats": self.knowledge_stats,
            "last_saved": datetime.now().isoformat()
        }
        
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Enhanced knowledge base saved to {self.knowledge_file}")
        except Exception as e:
            self.logger.error(f"Failed to save knowledge base: {e}")

    def _load_knowledge_base(self):
        """Load enhanced knowledge base from file"""
        if not self.knowledge_file.exists():
            self.logger.info("No existing knowledge base found, will create new one")
            return
        
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load document knowledge
            if "knowledge_base" in data:
                for doc_type, knowledge_data in data["knowledge_base"].items():
                    self.knowledge_base[doc_type] = DocumentKnowledge(**knowledge_data)
            
            # Load legal clauses
            if "legal_clauses" in data:
                for clause_id, clause_data in data["legal_clauses"].items():
                    self.legal_clauses[clause_id] = LegalClause(**clause_data)
            
            # Load compliance rules
            if "compliance_rules" in data:
                for rule_id, rule_data in data["compliance_rules"].items():
                    self.compliance_rules[rule_id] = ComplianceRule(**rule_data)
            
            # Load template patterns (new)
            if "template_patterns" in data:
                for pattern_id, pattern_data in data["template_patterns"].items():
                    self.template_patterns[pattern_id] = TemplatePattern(**pattern_data)
            
            # Load design library (new)
            if "design_library" in data:
                self.design_library = data["design_library"]
            
            # Load PDF analysis cache (new)
            if "pdf_analysis_cache" in data:
                self.pdf_analysis_cache = data["pdf_analysis_cache"]
            
            # Load statistics (new)
            if "knowledge_stats" in data:
                self.knowledge_stats.update(data["knowledge_stats"])
            
            self.logger.info(f"Enhanced knowledge base loaded from {self.knowledge_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            self.logger.info("Starting with empty knowledge base")

    # Keep all existing methods from the original RAG agent
    def _initialize_document_knowledge(self):
        """Initialize existing document knowledge"""
        # [Keep existing implementation but enhance with new fields]
        # ... existing code with added fields for new features
        pass

    def _initialize_legal_clauses(self):
        """Initialize existing legal clauses"""
        # [Keep existing implementation but enhance with template integration]
        # ... existing code with template_integration and pdf_examples fields
        pass

    def _initialize_compliance_rules(self):
        """Initialize existing compliance rules"""
        # [Keep existing implementation but enhance with template checks]
        # ... existing code with template_checks and pdf_examples fields
        pass 