"""
Enhanced Configuration management for the Professional AI Agent system
Reads from .env file for comprehensive configuration management
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_bool(value: str, default: bool = False) -> bool:
    """Convert string environment variable to boolean"""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('true', '1', 'yes', 'on')

def get_list(value: str, delimiter: str = ',') -> List[str]:
    """Convert string environment variable to list"""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]

class Config:
    """Enhanced configuration class for the Professional AI Agent system"""
    
    def __init__(self):
        # =============================================================================
        # API KEYS AND AUTHENTICATION
        # =============================================================================
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
        self.openai_api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4.1')
        self.openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
        
        # Internal LLM Configuration (fallback when OpenAI not available)
        self.internal_llm_enabled = get_bool(os.getenv('INTERNAL_LLM_ENABLED', 'true'))
        self.internal_llm_api_base = os.getenv('INTERNAL_LLM_API_BASE', 'http://localhost:8000/v1')
        self.internal_llm_api_key = os.getenv('INTERNAL_LLM_API_KEY', 'your_internal_llm_key_here')
        self.internal_llm_model = os.getenv('INTERNAL_LLM_MODEL', 'llama2-70b-chat')
        self.internal_llm_max_tokens = int(os.getenv('INTERNAL_LLM_MAX_TOKENS', '4000'))
        self.internal_llm_temperature = float(os.getenv('INTERNAL_LLM_TEMPERATURE', '0.3'))
        self.internal_llm_timeout = int(os.getenv('INTERNAL_LLM_TIMEOUT', '60'))
        
        # LLM Fallback Configuration
        self.auto_fallback_enabled = get_bool(os.getenv('AUTO_FALLBACK_ENABLED', 'true'))
        self.fallback_retry_attempts = int(os.getenv('FALLBACK_RETRY_ATTEMPTS', '2'))
        self.primary_llm_provider = os.getenv('PRIMARY_LLM_PROVIDER', 'openai')  # 'openai' or 'internal'
        
        # Search API Configuration
        self.serpapi_api_key = os.getenv('SERPAPI_API_KEY', 'your_serpapi_key_here')
        self.duckduckgo_enabled = get_bool(os.getenv('DUCKDUCKGO_ENABLED', 'true'))
        self.wikipedia_enabled = get_bool(os.getenv('WIKIPEDIA_ENABLED', 'true'))
        
        # =============================================================================
        # AGENT CONFIGURATION
        # =============================================================================
        
        # Agent Identity
        self.agent_name = os.getenv('AGENT_NAME', 'Professional Legal AI Agent')
        self.agent_version = os.getenv('AGENT_VERSION', '2.0.0')
        self.agent_description = os.getenv('AGENT_DESCRIPTION', 'Federal Court Quality Document Generation System')
        
        # System Behavior
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
        self.memory_cleanup_enabled = get_bool(os.getenv('MEMORY_CLEANUP_ENABLED', 'true'))
        
        # =============================================================================
        # DOCUMENT GENERATION CONFIGURATION
        # =============================================================================
        
        # PDF Generation Settings
        self.pdf_output_dir = Path(os.getenv('PDF_OUTPUT_DIR', 'output'))
        self.pdf_page_size = os.getenv('PDF_PAGE_SIZE', 'A4')
        self.pdf_font_family = os.getenv('PDF_FONT_FAMILY', 'Helvetica')
        self.pdf_font_size_body = int(os.getenv('PDF_FONT_SIZE_BODY', '10'))
        self.pdf_font_size_heading = int(os.getenv('PDF_FONT_SIZE_HEADING', '12'))
        self.pdf_font_size_title = int(os.getenv('PDF_FONT_SIZE_TITLE', '14'))
        self.pdf_margin_top = int(os.getenv('PDF_MARGIN_TOP', '25'))
        self.pdf_margin_bottom = int(os.getenv('PDF_MARGIN_BOTTOM', '25'))
        self.pdf_margin_left = int(os.getenv('PDF_MARGIN_LEFT', '25'))
        self.pdf_margin_right = int(os.getenv('PDF_MARGIN_RIGHT', '25'))
        
        # Document Quality
        self.generate_fallback_text = get_bool(os.getenv('GENERATE_FALLBACK_TEXT', 'true'))
        self.include_financial_schedules = get_bool(os.getenv('INCLUDE_FINANCIAL_SCHEDULES', 'true'))
        self.include_legal_clauses = get_bool(os.getenv('INCLUDE_LEGAL_CLAUSES', 'true'))
        self.include_asset_analysis = get_bool(os.getenv('INCLUDE_ASSET_ANALYSIS', 'true'))
        self.include_liability_analysis = get_bool(os.getenv('INCLUDE_LIABILITY_ANALYSIS', 'true'))
        
        # =============================================================================
        # LEGAL AND COMPLIANCE CONFIGURATION
        # =============================================================================
        
        # Australian Legal Framework
        self.corporations_act_year = int(os.getenv('CORPORATIONS_ACT_YEAR', '2001'))
        self.jurisdiction = os.getenv('JURISDICTION', 'Australia')
        self.court_type = os.getenv('COURT_TYPE', 'Federal Court of Australia')
        self.registry = os.getenv('REGISTRY', 'Commercial and Corporations List')
        
        # Liquidation Standards
        self.liquidator_registration_required = get_bool(os.getenv('LIQUIDATOR_REGISTRATION_REQUIRED', 'true'))
        self.asic_compliance_enabled = get_bool(os.getenv('ASIC_COMPLIANCE_ENABLED', 'true'))
        self.creditor_protection_enabled = get_bool(os.getenv('CREDITOR_PROTECTION_ENABLED', 'true'))
        self.employee_entitlement_calculations = get_bool(os.getenv('EMPLOYEE_ENTITLEMENT_CALCULATIONS', 'true'))
        
        # Document Compliance
        self.federal_court_formatting = get_bool(os.getenv('FEDERAL_COURT_FORMATTING', 'true'))
        self.professional_signatures = get_bool(os.getenv('PROFESSIONAL_SIGNATURES', 'true'))
        self.legal_clause_validation = get_bool(os.getenv('LEGAL_CLAUSE_VALIDATION', 'true'))
        self.financial_accuracy_check = get_bool(os.getenv('FINANCIAL_ACCURACY_CHECK', 'true'))
        
        # =============================================================================
        # FINANCIAL CALCULATIONS CONFIGURATION
        # =============================================================================
        
        # Currency and Formatting
        self.currency_symbol = os.getenv('CURRENCY_SYMBOL', 'AUD $')
        self.currency_format = os.getenv('CURRENCY_FORMAT', '{symbol}{amount:,.2f}')
        self.percentage_decimal_places = int(os.getenv('PERCENTAGE_DECIMAL_PLACES', '2'))
        self.financial_rounding = int(os.getenv('FINANCIAL_ROUNDING', '2'))
        
        # Asset Valuation Factors
        self.asset_realization_factors = {
            'cash': float(os.getenv('ASSET_REALIZATION_FACTOR_CASH', '1.00')),
            'debtors': float(os.getenv('ASSET_REALIZATION_FACTOR_DEBTORS', '0.80')),
            'inventory': float(os.getenv('ASSET_REALIZATION_FACTOR_INVENTORY', '0.60')),
            'plant': float(os.getenv('ASSET_REALIZATION_FACTOR_PLANT', '0.40')),
            'property': float(os.getenv('ASSET_REALIZATION_FACTOR_PROPERTY', '0.90')),
            'vehicles': float(os.getenv('ASSET_REALIZATION_FACTOR_VEHICLES', '0.50'))
        }
        
        # Liability Priorities
        self.liability_priorities = {
            'secured_creditors': get_bool(os.getenv('PRIORITY_1_SECURED_CREDITORS', 'true')),
            'liquidator_costs': get_bool(os.getenv('PRIORITY_2_LIQUIDATOR_COSTS', 'true')),
            'employee_entitlements': get_bool(os.getenv('PRIORITY_3_EMPLOYEE_ENTITLEMENTS', 'true')),
            'preferential_creditors': get_bool(os.getenv('PRIORITY_4_PREFERENTIAL_CREDITORS', 'true')),
            'unsecured_creditors': get_bool(os.getenv('PRIORITY_5_UNSECURED_CREDITORS', 'true')),
            'related_party_loans': get_bool(os.getenv('PRIORITY_6_RELATED_PARTY_LOANS', 'true'))
        }
        
        # =============================================================================
        # SEARCH AND RESEARCH CONFIGURATION
        # =============================================================================
        
        # Web Search Configuration
        self.search_max_results = int(os.getenv('SEARCH_MAX_RESULTS', '10'))
        self.search_timeout = int(os.getenv('SEARCH_TIMEOUT', '15'))
        self.search_engines = get_list(os.getenv('SEARCH_ENGINES', 'google,duckduckgo,wikipedia'))
        self.search_relevance_threshold = float(os.getenv('SEARCH_RELEVANCE_THRESHOLD', '0.6'))
        
        # Legal Research
        self.legal_research_enabled = get_bool(os.getenv('LEGAL_RESEARCH_ENABLED', 'true'))
        self.current_law_research = get_bool(os.getenv('CURRENT_LAW_RESEARCH', 'true'))
        self.case_law_integration = get_bool(os.getenv('CASE_LAW_INTEGRATION', 'false'))
        self.regulatory_updates = get_bool(os.getenv('REGULATORY_UPDATES', 'true'))
        
        # Legal Search Queries
        self.legal_search_queries = get_list(os.getenv(
            'LEGAL_SEARCH_QUERIES', 
            'Australian liquidation procedures 2024,ASIC liquidation requirements,Corporations Act liquidation compliance'
        ))
        
        # =============================================================================
        # LOGGING AND MONITORING CONFIGURATION
        # =============================================================================
        
        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'professional_agent.log')
        self.log_max_size = os.getenv('LOG_MAX_SIZE', '10MB')
        self.log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        self.log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console Logging
        self.console_log_enabled = get_bool(os.getenv('CONSOLE_LOG_ENABLED', 'true'))
        self.console_log_level = os.getenv('CONSOLE_LOG_LEVEL', 'INFO')
        self.console_log_color = get_bool(os.getenv('CONSOLE_LOG_COLOR', 'true'))
        
        # Performance Monitoring
        self.performance_monitoring = get_bool(os.getenv('PERFORMANCE_MONITORING', 'true'))
        self.execution_time_tracking = get_bool(os.getenv('EXECUTION_TIME_TRACKING', 'true'))
        self.memory_usage_tracking = get_bool(os.getenv('MEMORY_USAGE_TRACKING', 'true'))
        self.error_tracking = get_bool(os.getenv('ERROR_TRACKING', 'true'))
        
        # =============================================================================
        # SECURITY SETTINGS
        # =============================================================================
        
        # Data Protection
        self.zero_persistent_storage = get_bool(os.getenv('ZERO_PERSISTENT_STORAGE', 'true'))
        self.memory_cleanup_after_use = get_bool(os.getenv('MEMORY_CLEANUP_AFTER_USE', 'true'))
        self.api_key_masking = get_bool(os.getenv('API_KEY_MASKING', 'true'))
        self.sensitive_data_encryption = get_bool(os.getenv('SENSITIVE_DATA_ENCRYPTION', 'false'))
        
        # Network Security
        self.verify_ssl_certificates = get_bool(os.getenv('VERIFY_SSL_CERTIFICATES', 'true'))
        self.connection_timeout = int(os.getenv('CONNECTION_TIMEOUT', '30'))
        self.max_redirects = int(os.getenv('MAX_REDIRECTS', '5'))
        self.user_agent = os.getenv('USER_AGENT', 'Professional-AI-Agent/2.0')
        
        # =============================================================================
        # PROFESSIONAL FEATURES
        # =============================================================================
        
        # Customer Management
        self.customer_profile_generation = get_bool(os.getenv('CUSTOMER_PROFILE_GENERATION', 'true'))
        self.industry_specific_analysis = get_bool(os.getenv('INDUSTRY_SPECIFIC_ANALYSIS', 'true'))
        self.contact_management = get_bool(os.getenv('CONTACT_MANAGEMENT', 'true'))
        self.special_requirements_tracking = get_bool(os.getenv('SPECIAL_REQUIREMENTS_TRACKING', 'true'))
        
        # Document Types
        self.document_types = {
            'professional_affidavit': get_bool(os.getenv('GENERATE_PROFESSIONAL_AFFIDAVIT', 'true')),
            'liquidation_resolution': get_bool(os.getenv('GENERATE_LIQUIDATION_RESOLUTION', 'true')),
            'creditor_notification': get_bool(os.getenv('GENERATE_CREDITOR_NOTIFICATION', 'true')),
            'director_statement': get_bool(os.getenv('GENERATE_DIRECTOR_STATEMENT', 'true')),
            'asset_realization_notice': get_bool(os.getenv('GENERATE_ASSET_REALIZATION_NOTICE', 'true'))
        }
        
        # Quality Assurance
        self.quality_assurance = {
            'federal_court_compliance': get_bool(os.getenv('FEDERAL_COURT_COMPLIANCE_CHECK', 'true')),
            'financial_calculation_validation': get_bool(os.getenv('FINANCIAL_CALCULATION_VALIDATION', 'true')),
            'legal_clause_verification': get_bool(os.getenv('LEGAL_CLAUSE_VERIFICATION', 'true')),
            'professional_formatting_check': get_bool(os.getenv('PROFESSIONAL_FORMATTING_CHECK', 'true'))
        }
        
        # =============================================================================
        # DEVELOPMENT AND TESTING
        # =============================================================================
        
        # Development Mode
        self.development_mode = get_bool(os.getenv('DEVELOPMENT_MODE', 'false'))
        self.debug_mode = get_bool(os.getenv('DEBUG_MODE', 'false'))
        self.test_mode = get_bool(os.getenv('TEST_MODE', 'false'))
        self.mock_api_responses = get_bool(os.getenv('MOCK_API_RESPONSES', 'false'))
        
        # Testing Configuration
        self.test_output_dir = Path(os.getenv('TEST_OUTPUT_DIR', 'test_output'))
        self.test_companies = get_list(os.getenv('TEST_COMPANIES', 'Tech Solutions Pty Ltd,Manufacturing Corp,Retail Enterprises'))
        self.test_generate_sample_data = get_bool(os.getenv('TEST_GENERATE_SAMPLE_DATA', 'true'))
        
        # Demo Configuration
        self.demo_mode = get_bool(os.getenv('DEMO_MODE', 'false'))
        self.demo_organizations = int(os.getenv('DEMO_ORGANIZATIONS', '5'))
        self.demo_documents_per_org = int(os.getenv('DEMO_DOCUMENTS_PER_ORG', '5'))
        self.demo_include_research = get_bool(os.getenv('DEMO_INCLUDE_RESEARCH', 'true'))
        
        # =============================================================================
        # SYSTEM LIMITS
        # =============================================================================
        
        # Processing Limits
        self.max_organizations_per_request = int(os.getenv('MAX_ORGANIZATIONS_PER_REQUEST', '10'))
        self.max_documents_per_organization = int(os.getenv('MAX_DOCUMENTS_PER_ORGANIZATION', '10'))
        self.max_document_size_mb = int(os.getenv('MAX_DOCUMENT_SIZE_MB', '50'))
        self.max_processing_time_minutes = int(os.getenv('MAX_PROCESSING_TIME_MINUTES', '30'))
        
        # Memory Management
        self.max_memory_usage_mb = int(os.getenv('MAX_MEMORY_USAGE_MB', '2048'))
        self.garbage_collection_enabled = get_bool(os.getenv('GARBAGE_COLLECTION_ENABLED', 'true'))
        self.memory_threshold_warning = int(os.getenv('MEMORY_THRESHOLD_WARNING', '1536'))
        self.memory_cleanup_interval = int(os.getenv('MEMORY_CLEANUP_INTERVAL', '300'))
        
        # File Management
        self.max_output_files = int(os.getenv('MAX_OUTPUT_FILES', '1000'))
        self.auto_cleanup_old_files = get_bool(os.getenv('AUTO_CLEANUP_OLD_FILES', 'true'))
        self.file_retention_days = int(os.getenv('FILE_RETENTION_DAYS', '30'))
        self.backup_generated_documents = get_bool(os.getenv('BACKUP_GENERATED_DOCUMENTS', 'false'))
        
        # =============================================================================
        # INITIALIZATION
        # =============================================================================
        
        # Create necessary directories
        self.pdf_output_dir.mkdir(exist_ok=True)
        if self.test_mode:
            self.test_output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Validate configuration
        self._post_init_validation()
    
    def _setup_logging(self):
        """Setup enhanced logging configuration"""
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        handlers = []
        
        # File handler
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(logging.Formatter(self.log_format))
            handlers.append(file_handler)
        
        # Console handler
        if self.console_log_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.log_format))
            console_level = getattr(logging, self.console_log_level.upper(), logging.INFO)
            console_handler.setLevel(console_level)
            handlers.append(console_handler)
        
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )
    
    def _post_init_validation(self):
        """Post-initialization validation and warnings"""
        if self.development_mode:
            logging.warning("Development mode is enabled - some features may behave differently")
        
        if self.debug_mode:
            logging.warning("Debug mode is enabled - additional logging and slower performance expected")
        
        if not self.verify_ssl_certificates:
            logging.warning("SSL certificate verification is disabled - use only in development")
    
    def validate_config(self) -> bool:
        """Validate the configuration for required settings"""
        validation_issues = []
        
        # Check required API keys
        openai_available = self.openai_api_key and not self.openai_api_key.startswith('your_')
        internal_llm_available = (
            self.internal_llm_enabled and 
            self.internal_llm_api_key and 
            not self.internal_llm_api_key.startswith('your_')
        )
        
        if not openai_available and not internal_llm_available:
            validation_issues.append("Either OPENAI_API_KEY or INTERNAL_LLM_API_KEY is required for LLM functionality")
        elif not openai_available:
            logging.info("OpenAI API not configured - will use internal LLM as primary")
        elif not internal_llm_available and self.auto_fallback_enabled:
            logging.warning("Internal LLM not configured - no fallback available if OpenAI fails")
        
        # Check critical settings
        if self.max_organizations_per_request <= 0:
            validation_issues.append("MAX_ORGANIZATIONS_PER_REQUEST must be greater than 0")
        
        if self.max_documents_per_organization <= 0:
            validation_issues.append("MAX_DOCUMENTS_PER_ORGANIZATION must be greater than 0")
        
        # Check directory permissions
        try:
            test_file = self.pdf_output_dir / '.test_write'
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            validation_issues.append(f"Cannot write to PDF output directory: {e}")
        
        # Report validation issues
        if validation_issues:
            for issue in validation_issues:
                logging.warning(f"Configuration validation: {issue}")
            return False
        
        return True
    
    def get_enabled_document_types(self) -> List[str]:
        """Get list of enabled document types"""
        return [doc_type for doc_type, enabled in self.document_types.items() if enabled]
    
    def get_search_engines(self) -> List[str]:
        """Get list of enabled search engines"""
        engines = []
        if 'google' in self.search_engines and self.serpapi_api_key and not self.serpapi_api_key.startswith('your_'):
            engines.append('google')
        if 'duckduckgo' in self.search_engines and self.duckduckgo_enabled:
            engines.append('duckduckgo')
        if 'wikipedia' in self.search_engines and self.wikipedia_enabled:
            engines.append('wikipedia')
        return engines
    
    def format_currency(self, amount: float) -> str:
        """Format currency amount according to configuration"""
        return self.currency_format.format(
            symbol=self.currency_symbol,
            amount=round(amount, self.financial_rounding)
        )
    
    def __str__(self) -> str:
        """Enhanced string representation of the configuration"""
        # Mask sensitive information
        masked_openai_key = self._mask_key(self.openai_api_key)
        masked_internal_llm_key = self._mask_key(self.internal_llm_api_key)
        masked_serpapi_key = self._mask_key(self.serpapi_api_key)
        
        enabled_doc_types = ', '.join(self.get_enabled_document_types())
        enabled_search_engines = ', '.join(self.get_search_engines())
        
        return f"""
Professional AI Agent Configuration v{self.agent_version}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent Details:
  Name: {self.agent_name}
  Version: {self.agent_version}
  Description: {self.agent_description}

API Configuration:
  Primary Provider: {self.primary_llm_provider}
  OpenAI Model: {self.openai_model}
  OpenAI API Key: {masked_openai_key}
  Internal LLM: {'✅' if self.internal_llm_enabled else '❌'}
  Internal LLM Model: {self.internal_llm_model}
  Internal LLM API Key: {masked_internal_llm_key}
  Auto Fallback: {'✅' if self.auto_fallback_enabled else '❌'}
  SerpAPI Key: {masked_serpapi_key}
  Temperature: {self.openai_temperature}

Document Generation:
  PDF Output: {self.pdf_output_dir}
  Page Size: {self.pdf_page_size}
  Font Family: {self.pdf_font_family}
  Enabled Types: {enabled_doc_types}

Legal Framework:
  Jurisdiction: {self.jurisdiction}
  Court Type: {self.court_type}
  Corporations Act: {self.corporations_act_year}
  Federal Court Formatting: {'✅' if self.federal_court_formatting else '❌'}

Financial Settings:
  Currency: {self.currency_symbol}
  Rounding: {self.financial_rounding} decimal places
  Asset Analysis: {'✅' if self.include_asset_analysis else '❌'}
  Liability Analysis: {'✅' if self.include_liability_analysis else '❌'}

Search & Research:
  Enabled Engines: {enabled_search_engines}
  Max Results: {self.search_max_results}
  Legal Research: {'✅' if self.legal_research_enabled else '❌'}

System Settings:
  Log Level: {self.log_level}
  Performance Monitoring: {'✅' if self.performance_monitoring else '❌'}
  Memory Cleanup: {'✅' if self.memory_cleanup_enabled else '❌'}
  Development Mode: {'✅' if self.development_mode else '❌'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
    
    def _mask_key(self, key: str) -> str:
        """Mask API key for display"""
        if not key or key.startswith('your_'):
            return "not_set"
        elif len(key) > 8:
            return f"{key[:8]}{'*' * (len(key) - 12)}{key[-4:]}"
        else:
            return "***masked***" 