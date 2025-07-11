"""
Australian Liquidation Document Templates
Professional templates for liquidation proceedings
"""

from typing import Dict, Any, List
from datetime import datetime


class LiquidationTemplates:
    """Collection of Australian liquidation document templates"""
    
    @staticmethod
    def liquidation_resolution(context: Dict[str, Any]) -> str:
        """Template for liquidation resolution"""
        org_name = context.get('organization', '[COMPANY NAME]')
        date = datetime.now().strftime('%d %B %Y')
        
        return f"""
# RESOLUTION FOR VOLUNTARY LIQUIDATION

## {org_name}
### ACN: [TO BE COMPLETED]
### ABN: [TO BE COMPLETED]

**Date:** {date}

---

## SPECIAL RESOLUTION

WHEREAS the Company has resolved to wind up voluntarily pursuant to Section 491 of the Corporations Act 2001 (Cth);

AND WHEREAS it is necessary to appoint a liquidator to conduct the winding up of the Company;

NOW THEREFORE IT IS RESOLVED:

1. **Winding Up Resolution**
   That the Company be wound up voluntarily pursuant to Section 491 of the Corporations Act 2001 (Cth).

2. **Appointment of Liquidator**
   That [LIQUIDATOR NAME], registered liquidator (Registration No. [NUMBER]), be and is hereby appointed as liquidator of the Company for the purposes of winding up its affairs and distributing its property.

3. **Powers of Liquidator**
   That the liquidator be and is hereby authorized to:
   - Realize the assets of the Company
   - Pay the debts and liabilities of the Company
   - Distribute any surplus among the members according to their rights
   - Execute all necessary documents for the winding up

4. **Compliance**
   That the liquidator is authorized to take all steps necessary to ensure compliance with the Corporations Act 2001 (Cth) and all other applicable laws.

5. **Effective Date**
   This resolution takes effect immediately upon passing.

---

**CERTIFICATION**

We, the undersigned directors of {org_name}, certify that this resolution was passed by special resolution of the members of the Company in accordance with the Corporations Act 2001 (Cth).

**Director Signatures:**

_________________________________
[DIRECTOR NAME]
Director
Date: __________________

_________________________________
[DIRECTOR NAME] 
Director
Date: __________________

---

**Legal Note:** This document has been prepared in accordance with Australian liquidation laws and the Corporations Act 2001 (Cth). Professional legal advice should be sought before execution.
        """.strip()
    
    @staticmethod
    def creditor_notification(context: Dict[str, Any]) -> str:
        """Template for creditor notification"""
        org_name = context.get('organization', '[COMPANY NAME]')
        date = datetime.now().strftime('%d %B %Y')
        
        return f"""
# NOTICE TO CREDITORS

## {org_name}
### (In Liquidation)
### ACN: [TO BE COMPLETED]

**Date:** {date}

---

## NOTICE OF APPOINTMENT OF LIQUIDATOR

**TO ALL CREDITORS OF {org_name.upper()}**

**NOTICE IS HEREBY GIVEN** that pursuant to Section 497 of the Corporations Act 2001 (Cth):

### 1. LIQUIDATION COMMENCED
The Company resolved to wind up voluntarily on [DATE] and [LIQUIDATOR NAME] was appointed as liquidator of the Company.

### 2. CREDITOR OBLIGATIONS
All creditors of the Company are required to:

- **Submit Proof of Debt:** Lodge formal proof of debt with the liquidator within [TIME PERIOD] of this notice
- **Provide Documentation:** Include all supporting documentation for claims
- **Update Contact Details:** Ensure current contact information is provided

### 3. ASSET REALIZATION
The liquidator will proceed to:
- Realize the assets of the Company
- Investigate the Company's affairs
- Pay creditors according to statutory priorities
- Distribute any surplus to members

### 4. MEETING OF CREDITORS
A meeting of creditors will be held:

**Date:** [TO BE ADVISED]
**Time:** [TO BE ADVISED]  
**Location:** [TO BE ADVISED]

Further details will be provided in due course.

### 5. CONTACT INFORMATION
All correspondence should be directed to:

**Liquidator:** [LIQUIDATOR NAME]
**Address:** [LIQUIDATOR ADDRESS]
**Phone:** [PHONE NUMBER]
**Email:** [EMAIL ADDRESS]

### 6. STATUTORY INFORMATION
- **Date of Resolution:** [DATE]
- **Date of Appointment:** [DATE]
- **Liquidator Registration:** [NUMBER]

---

**IMPORTANT:** Creditors who fail to lodge proof of debt within the specified time may not be entitled to participate in any distribution.

This notice is issued pursuant to Section 497 of the Corporations Act 2001 (Cth).

**Liquidator:** [LIQUIDATOR NAME]
**Date:** {date}

---

**Legal Disclaimer:** This notice is issued in accordance with Australian liquidation procedures. Creditors should seek independent legal advice regarding their rights and obligations.
        """.strip()
    
    @staticmethod
    def liquidator_appointment_notice(context: Dict[str, Any]) -> str:
        """Template for liquidator appointment notice"""
        org_name = context.get('organization', '[COMPANY NAME]')
        date = datetime.now().strftime('%d %B %Y')
        
        return f"""
# NOTICE OF APPOINTMENT OF LIQUIDATOR

## {org_name}
### ACN: [TO BE COMPLETED]
### ABN: [TO BE COMPLETED]

**Date of Appointment:** {date}

---

## OFFICIAL NOTIFICATION

**NOTICE IS HEREBY GIVEN** pursuant to Section 499 of the Corporations Act 2001 (Cth) that:

### 1. APPOINTMENT DETAILS
- **Company:** {org_name}
- **Liquidator:** [LIQUIDATOR NAME]
- **Registration Number:** [LIQUIDATOR REGISTRATION]
- **Date of Appointment:** {date}
- **Type of Liquidation:** Voluntary Liquidation

### 2. LIQUIDATOR DECLARATION
I, [LIQUIDATOR NAME], a registered liquidator under the Corporations Act 2001 (Cth), hereby accept the appointment as liquidator of {org_name}.

### 3. QUALIFICATIONS
- Registered Liquidator Number: [NUMBER]
- Professional Body: [PROFESSIONAL BODY]
- Insurance Details: [INSURANCE INFORMATION]

### 4. LIQUIDATION PROCESS
The liquidation will proceed in accordance with:
- Corporations Act 2001 (Cth)
- Corporations Regulations 2001
- ASIC Regulatory Guidelines
- Australian Restructuring Insolvency & Turnaround Association (ARITA) Code of Professional Practice

### 5. IMMEDIATE ACTIONS
As liquidator, I will immediately:
- Take control of the Company's assets
- Investigate the Company's affairs
- Realize assets for the benefit of creditors
- Ensure compliance with all statutory obligations

### 6. CREDITOR RIGHTS
Creditors have the right to:
- Lodge proof of debt
- Attend creditors' meetings
- Request information about the liquidation
- Challenge the liquidator's remuneration

### 7. CONTACT INFORMATION
**Liquidator:** [LIQUIDATOR NAME]
**Firm:** [FIRM NAME]
**Address:** [BUSINESS ADDRESS]
**Phone:** [PHONE NUMBER]
**Email:** [EMAIL ADDRESS]
**Website:** [WEBSITE]

### 8. NEXT STEPS
- Creditor meeting to be called within [TIMEFRAME]
- Asset valuation and realization to commence
- Investigation of Company affairs
- Preparation of statutory reports

---

**EXECUTED** this {date.split()[0]} day of {date.split()[1]} {date.split()[2]}

**Liquidator Signature:**

_________________________________
[LIQUIDATOR NAME]
Registered Liquidator
Registration No: [NUMBER]

---

**Statutory Compliance:** This notice satisfies the requirements of Section 499 of the Corporations Act 2001 (Cth) and has been prepared in accordance with ASIC guidelines.
        """.strip()
    
    @staticmethod
    def director_statement(context: Dict[str, Any]) -> str:
        """Template for director statement in liquidation"""
        org_name = context.get('organization', '[COMPANY NAME]')
        date = datetime.now().strftime('%d %B %Y')
        
        return f"""
# DIRECTOR'S STATEMENT AS TO AFFAIRS

## {org_name}
### ACN: [TO BE COMPLETED]

**Date:** {date}

---

## STATEMENT PURSUANT TO SECTION 497 OF THE CORPORATIONS ACT 2001 (CTH)

### 1. COMPANY DETAILS
- **Company Name:** {org_name}
- **ACN:** [TO BE COMPLETED]
- **ABN:** [TO BE COMPLETED]
- **Registered Office:** [ADDRESS]
- **Principal Place of Business:** [ADDRESS]

### 2. DIRECTOR DECLARATION
I, [DIRECTOR NAME], director of the above-named company, make the following statement as to the affairs of the company as at {date}:

### 3. COMPANY AFFAIRS

#### 3.1 Financial Position
- **Total Assets (Estimated Realizable Value):** $[AMOUNT]
- **Total Liabilities:** $[AMOUNT]
- **Estimated Surplus/(Deficiency):** $[AMOUNT]

#### 3.2 Reason for Liquidation
The company resolved to wind up for the following reasons:
- [REASON 1]
- [REASON 2]
- [REASON 3]

#### 3.3 Asset Summary
**Real Property:** $[AMOUNT]
**Plant & Equipment:** $[AMOUNT]
**Motor Vehicles:** $[AMOUNT]
**Stock:** $[AMOUNT]
**Debtors:** $[AMOUNT]
**Cash at Bank:** $[AMOUNT]
**Other Assets:** $[AMOUNT]

**TOTAL ASSETS:** $[AMOUNT]

#### 3.4 Liability Summary
**Secured Creditors:** $[AMOUNT]
**Preferential Creditors:** $[AMOUNT]
**Unsecured Creditors:** $[AMOUNT]
**Contingent Liabilities:** $[AMOUNT]

**TOTAL LIABILITIES:** $[AMOUNT]

### 4. CREDITOR INFORMATION
The major creditors of the company are:
1. [CREDITOR NAME] - $[AMOUNT]
2. [CREDITOR NAME] - $[AMOUNT]
3. [CREDITOR NAME] - $[AMOUNT]

### 5. EMPLOYEE INFORMATION
- **Number of Employees:** [NUMBER]
- **Employee Entitlements:** $[AMOUNT]
- **Superannuation Obligations:** $[AMOUNT]

### 6. DIRECTOR CERTIFICATION
I certify that:
- This statement is true and complete to the best of my knowledge
- All company books and records have been made available
- There are no undisclosed liabilities known to me
- The company has not traded while insolvent

### 7. BOOKS AND RECORDS
The company's books and records are located at:
**Address:** [LOCATION]
**Contact:** [CONTACT PERSON]

---

**DIRECTOR SIGNATURE:**

_________________________________
[DIRECTOR NAME]
Director
Date: __________________

**WITNESS:**

_________________________________
[WITNESS NAME]
Signature
Date: __________________

---

**Legal Note:** This statement is made pursuant to Section 497 of the Corporations Act 2001 (Cth). Providing false or misleading information is a criminal offense.
        """.strip()
    
    @staticmethod
    def asset_realization_notice(context: Dict[str, Any]) -> str:
        """Template for asset realization notice"""
        org_name = context.get('organization', '[COMPANY NAME]')
        date = datetime.now().strftime('%d %B %Y')
        
        return f"""
# NOTICE OF ASSET REALIZATION

## {org_name}
### (In Liquidation)
### ACN: [TO BE COMPLETED]

**Date:** {date}

---

## NOTICE TO CREDITORS AND STAKEHOLDERS

**NOTICE IS HEREBY GIVEN** that the liquidator of {org_name} will proceed with the realization of company assets.

### 1. ASSET REALIZATION PROCESS
The following assets will be offered for sale:

#### 1.1 Real Property
- **Property 1:** [DESCRIPTION] - Estimated Value: $[AMOUNT]
- **Property 2:** [DESCRIPTION] - Estimated Value: $[AMOUNT]

#### 1.2 Plant & Equipment
- **Equipment Category 1:** [DESCRIPTION] - Estimated Value: $[AMOUNT]
- **Equipment Category 2:** [DESCRIPTION] - Estimated Value: $[AMOUNT]

#### 1.3 Motor Vehicles
- **Vehicle 1:** [DESCRIPTION] - Estimated Value: $[AMOUNT]
- **Vehicle 2:** [DESCRIPTION] - Estimated Value: $[AMOUNT]

#### 1.4 Stock & Inventory
- **Stock Category 1:** [DESCRIPTION] - Estimated Value: $[AMOUNT]
- **Stock Category 2:** [DESCRIPTION] - Estimated Value: $[AMOUNT]

### 2. SALE PROCESS
Assets will be sold by:
- **Public Auction:** [DATE AND LOCATION]
- **Private Treaty:** By negotiation with liquidator
- **Tender Process:** For specified assets

### 3. VIEWING ARRANGEMENTS
Asset inspections can be arranged by contacting:
**Contact:** [CONTACT PERSON]
**Phone:** [PHONE NUMBER]
**Email:** [EMAIL ADDRESS]

### 4. SALE CONDITIONS
- All sales are subject to liquidator approval
- Assets sold "as is, where is"
- Payment terms: [PAYMENT TERMS]
- Settlement: [SETTLEMENT TERMS]

### 5. CREDITOR INTERESTS
Creditors with security interests should contact the liquidator immediately to:
- Verify security registrations
- Negotiate asset releases
- Discuss payment arrangements

### 6. DISTRIBUTION PRIORITY
Proceeds will be distributed in accordance with:
1. Liquidator's costs and expenses
2. Secured creditor claims
3. Preferential creditor claims
4. Unsecured creditor claims
5. Member distributions (if any surplus)

### 7. IMPORTANT DATES
- **Asset Inspection Period:** [DATES]
- **Tender Submissions:** [DATE]
- **Auction Date:** [DATE]
- **Settlement Date:** [DATE]

### 8. LIQUIDATOR CONTACT
**Liquidator:** [LIQUIDATOR NAME]
**Firm:** [FIRM NAME]
**Address:** [ADDRESS]
**Phone:** [PHONE NUMBER]
**Email:** [EMAIL ADDRESS]

---

**ISSUED** by [LIQUIDATOR NAME], Liquidator of {org_name}

**Date:** {date}

---

**Legal Compliance:** This notice is issued in accordance with the Corporations Act 2001 (Cth) and ASIC regulatory requirements for asset realization in liquidation proceedings.
        """.strip()


def get_template_by_type(document_type: str) -> callable:
    """Get template function by document type"""
    templates = {
        'liquidation resolution': LiquidationTemplates.liquidation_resolution,
        'creditor notification': LiquidationTemplates.creditor_notification,
        'liquidator appointment notice': LiquidationTemplates.liquidator_appointment_notice,
        'liquidator appointment': LiquidationTemplates.liquidator_appointment_notice,
        'director statement': LiquidationTemplates.director_statement,
        'asset realization notice': LiquidationTemplates.asset_realization_notice,
        'asset realization': LiquidationTemplates.asset_realization_notice,
    }
    
    # Try exact match first
    if document_type.lower() in templates:
        return templates[document_type.lower()]
    
    # Try partial match
    for template_name, template_func in templates.items():
        if any(word in document_type.lower() for word in template_name.split()):
            return template_func
    
    # Default to liquidation resolution
    return LiquidationTemplates.liquidation_resolution 