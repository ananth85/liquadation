"""
Professional AI Agent System - Test Suite
========================================

This package contains comprehensive tests for the Professional AI Agent System,
including document generation diversity tests, PDF quality validation, and
system integration tests.

Test Modules:
- test_diverse_docs.py: Tests for diverse document generation with different law firms and templates
- test_professional_pdf.py: Professional PDF generation quality tests
- test_system.py: System integration and configuration tests

Usage:
    Run diversity test: python tests/test_diverse_docs.py
    Run PDF quality test: python tests/test_professional_pdf.py
    Run system test: python tests/test_system.py
    
    # Or run from project root:
    python -m tests.test_diverse_docs
    python -m tests.test_professional_pdf
    python -m tests.test_system

Test Categories:
    🏛️  Document Diversity: Verifies different law firms, templates, and document structures
    📄 PDF Quality: Tests professional PDF generation capabilities  
    ⚙️  System Integration: Validates system configuration and components
"""

__version__ = "1.0.0"
__author__ = "AI Agent Development Team"

# Test module imports
from . import test_diverse_docs
from . import test_professional_pdf
from . import test_system

__all__ = ['test_diverse_docs', 'test_professional_pdf', 'test_system'] 