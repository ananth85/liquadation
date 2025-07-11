import pandas as pd
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentTask
import logging
from pathlib import Path

class CSVIngestAgent(BaseAgent):
    """Agent responsible for ingesting and processing CSV data for batch liquidation document generation"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("CSVIngestAgent", logger)
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        
    def get_capabilities(self) -> List[str]:
        return [
            "parse_csv",
            "validate_csv_structure", 
            "process_batch_data",
            "enrich_csv_data"
        ]
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process CSV ingestion tasks"""
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "parse_csv":
            return await self.parse_csv(input_data.get("file_path"))
        elif task_type == "validate_csv_structure":
            return await self.validate_csv_structure(input_data.get("data"))
        elif task_type == "process_batch_data":
            return await self.process_batch_data(input_data.get("data"))
        elif task_type == "enrich_csv_data":
            return await self.enrich_csv_data(input_data.get("data"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def parse_csv(self, file_path: str) -> Dict[str, Any]:
        """Parse CSV file and return structured data"""
        if not file_path:
            raise ValueError("File path is required")
            
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported: {self.supported_formats}")
        
        try:
            # Read file based on extension
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            # Clean data
            cleaned_records = []
            for record in records:
                cleaned = {}
                for key, value in record.items():
                    # Clean column names and handle NaN values
                    clean_key = str(key).strip().lower().replace(' ', '_')
                    cleaned[clean_key] = None if pd.isna(value) else str(value).strip()
                cleaned_records.append(cleaned)
            
            self.logger.info(f"Successfully parsed {len(cleaned_records)} records from {file_path}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "record_count": len(cleaned_records),
                "records": cleaned_records,
                "columns": list(cleaned_records[0].keys()) if cleaned_records else []
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing CSV file {file_path}: {e}")
            raise
    
    async def validate_csv_structure(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate CSV data structure and required fields"""
        if not data:
            return {"valid": False, "errors": ["No data provided"]}
        
        errors = []
        warnings = []
        
        # Required fields mapping (CSV column -> internal field)
        field_mappings = {
            'customer_name': ['customer_name', 'name', 'client_name'],
            'company_name': ['company_name', 'entity_name', 'business_name'],
            'abn': ['abn', 'abn_number'],
            'acn': ['acn', 'acn_number'],
            'email': ['email', 'email_address'],
            'date': ['date', 'liquidation_date', 'closure_date']
        }
        
        # Check for required fields
        sample_record = data[0]
        available_fields = set(sample_record.keys())
        
        mapped_fields = {}
        for internal_field, possible_names in field_mappings.items():
            found = None
            for name in possible_names:
                if name in available_fields:
                    found = name
                    break
            mapped_fields[internal_field] = found
        
        # Validate required fields
        if not mapped_fields['company_name']:
            errors.append("Company name field is required (company_name, entity_name, or business_name)")
        
        # Warnings for missing optional fields
        if not mapped_fields['abn']:
            warnings.append("ABN field not found - will generate synthetic ABN")
        if not mapped_fields['email']:
            warnings.append("Email field not found - will generate synthetic email")
        if not mapped_fields['date']:
            warnings.append("Date field not found - will use current date")
        
        # Validate data quality
        for i, record in enumerate(data):
            if mapped_fields['company_name'] and not record.get(mapped_fields['company_name']):
                errors.append(f"Row {i+1}: Company name is empty")
            
            if mapped_fields['abn'] and record.get(mapped_fields['abn']):
                abn = ''.join(filter(str.isdigit, record[mapped_fields['abn']]))
                if len(abn) != 11:
                    warnings.append(f"Row {i+1}: ABN '{record[mapped_fields['abn']]}' may be invalid (not 11 digits)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "field_mappings": mapped_fields,
            "processed_records": len(data)
        }
    
    async def process_batch_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process batch CSV data and standardize field names"""
        if not data:
            raise ValueError("No data to process")
        
        # First validate the structure
        validation = await self.validate_csv_structure(data)
        if not validation["valid"]:
            raise ValueError(f"CSV validation failed: {'; '.join(validation['errors'])}")
        
        field_mappings = validation["field_mappings"]
        processed_records = []
        
        for i, record in enumerate(data):
            try:
                processed = await self._standardize_record(record, field_mappings)
                processed_records.append(processed)
            except Exception as e:
                self.logger.warning(f"Error processing record {i+1}: {e}")
                continue
        
        self.logger.info(f"Successfully processed {len(processed_records)} out of {len(data)} records")
        
        return {
            "success": True,
            "original_count": len(data),
            "processed_count": len(processed_records),
            "records": processed_records,
            "validation": validation
        }
    
    async def _standardize_record(self, record: Dict[str, Any], field_mappings: Dict[str, str]) -> Dict[str, Any]:
        """Standardize a single record to consistent field names"""
        from faker import Faker
        from datetime import datetime
        fake = Faker('en_AU')
        
        standardized = {}
        
        # Map known fields
        for internal_field, csv_field in field_mappings.items():
            if csv_field and record.get(csv_field):
                standardized[internal_field] = record[csv_field]
        
        # Generate missing required fields
        if 'company_name' not in standardized:
            raise ValueError("Company name is required")
        
        if 'customer_name' not in standardized:
            standardized['customer_name'] = fake.name()
        
        if 'abn' not in standardized:
            standardized['abn'] = str(fake.random_int(min=10000000000, max=99999999999))
        
        if 'acn' not in standardized:
            # Generate ACN from ABN
            abn = standardized['abn']
            acn_digits = abn[1:10] if len(abn) >= 10 else f"{fake.random_int(100000000, 999999999)}"
            standardized['acn'] = f"{acn_digits[:3]} {acn_digits[3:6]} {acn_digits[6:9]}"
        
        if 'email' not in standardized:
            domain = standardized['company_name'].lower().replace(' ', '').replace('pty', '').replace('ltd', '')[:10]
            standardized['email'] = f"info@{domain}.com.au"
        
        if 'date' not in standardized:
            standardized['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Add additional synthetic fields
        standardized.update({
            'directors': [fake.name() for _ in range(fake.random_int(1, 3))],
            'liquidator_name': fake.name(),
            'phone': fake.phone_number(),
            'address': {
                'street': fake.street_address(),
                'suburb': fake.city(),
                'state': fake.random_element(["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]),
                'postcode': fake.postcode()
            },
            'liquidation_type': fake.random_element([
                "Creditors' Voluntary Liquidation",
                "Members' Voluntary Liquidation", 
                "Court Ordered Liquidation"
            ]),
            'reason_for_liquidation': fake.random_element([
                "Financial difficulties and inability to pay debts",
                "Strategic business restructuring",
                "Completion of business purpose",
                "Insolvency and cash flow issues",
                "Director resolution to wind up operations"
            ])
        })
        
        # Copy any additional fields from original record
        for key, value in record.items():
            if key not in field_mappings.values() and value:
                standardized[key] = value
        
        return standardized
    
    async def enrich_csv_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enrich CSV data with additional synthetic details"""
        enriched_records = []
        
        for record in data:
            enriched = record.copy()
            
            # Add liquidation-specific fields if missing
            if 'liquidation_reason_detailed' not in enriched:
                enriched['liquidation_reason_detailed'] = self._generate_detailed_liquidation_reason(record)
            
            if 'creditors' not in enriched:
                enriched['creditors'] = self._generate_creditors_list()
            
            if 'assets_estimate' not in enriched:
                enriched['assets_estimate'] = f"${fake.random_int(10000, 2000000):,}"
            
            if 'debts_estimate' not in enriched:
                enriched['debts_estimate'] = f"${fake.random_int(50000, 5000000):,}"
            
            enriched_records.append(enriched)
        
        return {
            "success": True,
            "enriched_records": enriched_records,
            "enriched_count": len(enriched_records)
        }
    
    def _generate_detailed_liquidation_reason(self, record: Dict[str, Any]) -> str:
        """Generate detailed liquidation reason based on company data"""
        from faker import Faker
        fake = Faker()
        
        reasons = [
            f"The company has experienced significant financial difficulties over the past {fake.random_int(6, 24)} months, resulting in an inability to meet its debt obligations as they fall due.",
            f"Following a comprehensive review of the company's financial position, the directors have determined that the company is insolvent and unable to continue trading.",
            f"The company has been affected by market conditions and decreased demand for its services, leading to unsustainable operating losses.",
            f"Due to the loss of a major client representing {fake.random_int(40, 80)}% of revenue, the company can no longer maintain viable operations.",
            f"The company has accumulated significant debts and despite various restructuring attempts, is unable to return to profitability."
        ]
        
        return fake.random_element(reasons)
    
    def _generate_creditors_list(self) -> List[Dict[str, Any]]:
        """Generate realistic creditors list"""
        from faker import Faker
        fake = Faker('en_AU')
        
        common_creditors = [
            {"name": "Australian Taxation Office", "amount": f"${fake.random_int(50000, 500000):,}", "type": "Government"},
            {"name": "Westpac Banking Corporation", "amount": f"${fake.random_int(100000, 1000000):,}", "type": "Financial"},
            {"name": "Commonwealth Bank", "amount": f"${fake.random_int(50000, 800000):,}", "type": "Financial"},
            {"name": "Trade Creditors", "amount": f"${fake.random_int(20000, 200000):,}", "type": "Trade"},
            {"name": "Employee Entitlements", "amount": f"${fake.random_int(10000, 150000):,}", "type": "Employment"}
        ]
        
        # Return 2-4 random creditors
        return fake.random_elements(common_creditors, length=fake.random_int(2, 4), unique=True) 