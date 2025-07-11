import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentTask
import logging

class DataFetchAgent(BaseAgent):
    """Agent responsible for fetching company data from ABN API and other external sources"""
    
    def __init__(self, abn_api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        super().__init__("DataFetchAgent", logger)
        self.abn_api_key = abn_api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_capabilities(self) -> List[str]:
        return [
            "fetch_abn_data",
            "fetch_company_details", 
            "validate_abn",
            "enrich_company_data"
        ]
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process data fetching tasks"""
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "fetch_abn_data":
            return await self.fetch_abn_data(input_data.get("abn"))
        elif task_type == "fetch_company_details":
            return await self.fetch_company_details(input_data.get("company_name"))
        elif task_type == "validate_abn":
            return await self.validate_abn(input_data.get("abn"))
        elif task_type == "enrich_company_data":
            return await self.enrich_company_data(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def fetch_abn_data(self, abn: str) -> Dict[str, Any]:
        """Fetch company data from ABN Lookup API"""
        if not abn:
            raise ValueError("ABN is required")
            
        # Clean ABN (remove spaces, ensure 11 digits)
        clean_abn = ''.join(filter(str.isdigit, abn))
        if len(clean_abn) != 11:
            raise ValueError("ABN must be 11 digits")
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # ABR Business Lookup API
            url = f"https://abr.business.gov.au/json/AbnDetails.aspx"
            params = {
                "abn": clean_abn,
                "guid": self.abn_api_key or "DEMO_KEY",  # Use demo for testing
                "callback": ""
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_abn_response(data, clean_abn)
                else:
                    # Fallback to synthetic data if API fails
                    self.logger.warning(f"ABN API failed, generating synthetic data for {clean_abn}")
                    return self._generate_synthetic_abn_data(clean_abn)
                    
        except Exception as e:
            self.logger.error(f"Error fetching ABN data: {e}")
            # Fallback to synthetic data
            return self._generate_synthetic_abn_data(clean_abn)
    
    def _parse_abn_response(self, data: Dict[str, Any], abn: str) -> Dict[str, Any]:
        """Parse ABN API response into standardized format"""
        try:
            if "Abn" in data and data["Abn"]:
                abn_data = data["Abn"]
                return {
                    "abn": abn,
                    "acn": abn_data.get("Acn", ""),
                    "entity_name": abn_data.get("EntityName", ""),
                    "entity_type": abn_data.get("EntityType", ""),
                    "status": abn_data.get("AbnStatus", "Active"),
                    "address": {
                        "state": abn_data.get("AddressState", ""),
                        "postcode": abn_data.get("AddressPostcode", ""),
                    },
                    "source": "abn_api",
                    "valid": True
                }
            else:
                return self._generate_synthetic_abn_data(abn)
        except Exception as e:
            self.logger.error(f"Error parsing ABN response: {e}")
            return self._generate_synthetic_abn_data(abn)
    
    def _generate_synthetic_abn_data(self, abn: str) -> Dict[str, Any]:
        """Generate synthetic company data when API is unavailable"""
        from faker import Faker
        fake = Faker('en_AU')
        
        # Generate ACN from ABN (simplified)
        acn_digits = abn[1:10]  # Use middle 9 digits
        acn = f"{acn_digits[:3]} {acn_digits[3:6]} {acn_digits[6:9]}"
        
        company_suffixes = ["Pty Ltd", "Limited", "Pty Limited", "Holdings Pty Ltd"]
        
        return {
            "abn": abn,
            "acn": acn,
            "entity_name": f"{fake.company().replace(',', '').replace('.', '')} {fake.random_element(company_suffixes)}",
            "entity_type": "Australian Private Company",
            "status": "Active",
            "address": {
                "state": fake.random_element(["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]),
                "postcode": fake.postcode(),
                "street": fake.street_address(),
                "suburb": fake.city()
            },
            "industry": fake.random_element([
                "Technology Services", "Financial Services", "Retail Trade", 
                "Construction", "Manufacturing", "Professional Services",
                "Healthcare", "Education", "Hospitality", "Transport"
            ]),
            "source": "synthetic",
            "valid": True
        }
    
    async def fetch_company_details(self, company_name: str) -> Dict[str, Any]:
        """Fetch company details by name (fallback to synthetic)"""
        if not company_name:
            raise ValueError("Company name is required")
            
        # In a real implementation, this would search by company name
        # For now, generate synthetic data
        return self._generate_synthetic_company_data(company_name)
    
    def _generate_synthetic_company_data(self, company_name: str) -> Dict[str, Any]:
        """Generate synthetic company data based on company name"""
        from faker import Faker
        fake = Faker('en_AU')
        
        # Generate ABN
        abn = fake.random_int(min=10000000000, max=99999999999)
        
        return {
            "company_name": company_name,
            "abn": str(abn),
            "acn": f"{fake.random_int(100, 999)} {fake.random_int(100, 999)} {fake.random_int(100, 999)}",
            "entity_type": "Australian Private Company",
            "status": "Active",
            "address": {
                "street": fake.street_address(),
                "suburb": fake.city(),
                "state": fake.random_element(["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]),
                "postcode": fake.postcode()
            },
            "directors": [fake.name() for _ in range(fake.random_int(1, 3))],
            "source": "synthetic"
        }
    
    async def validate_abn(self, abn: str) -> Dict[str, Any]:
        """Validate ABN using checksum algorithm"""
        if not abn:
            return {"valid": False, "error": "ABN is required"}
            
        clean_abn = ''.join(filter(str.isdigit, abn))
        if len(clean_abn) != 11:
            return {"valid": False, "error": "ABN must be 11 digits"}
        
        # ABN checksum validation
        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        try:
            # Subtract 1 from first digit
            digits = [int(d) for d in clean_abn]
            digits[0] -= 1
            
            # Calculate checksum
            checksum = sum(digit * weight for digit, weight in zip(digits, weights))
            valid = checksum % 89 == 0
            
            return {
                "valid": valid,
                "abn": clean_abn,
                "formatted_abn": f"{clean_abn[:2]} {clean_abn[2:5]} {clean_abn[5:8]} {clean_abn[8:11]}"
            }
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    async def enrich_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich existing company data with additional details"""
        enriched = company_data.copy()
        
        # Add missing fields with synthetic data
        from faker import Faker
        fake = Faker('en_AU')
        
        if "directors" not in enriched:
            enriched["directors"] = [fake.name() for _ in range(fake.random_int(1, 3))]
            
        if "phone" not in enriched:
            enriched["phone"] = fake.phone_number()
            
        if "email" not in enriched:
            company_name = enriched.get("entity_name", enriched.get("company_name", "company"))
            domain = company_name.lower().replace(" ", "").replace("pty", "").replace("ltd", "")[:10]
            enriched["email"] = f"info@{domain}.com.au"
            
        if "established_date" not in enriched:
            enriched["established_date"] = fake.date_between(start_date='-20y', end_date='-1y').strftime('%Y-%m-%d')
            
        return enriched 