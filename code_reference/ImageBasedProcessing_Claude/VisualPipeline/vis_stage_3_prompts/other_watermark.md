# Other: Watermark

You are extracting text and metadata from a WATERMARK or DOCUMENT STAMP — textual overlays indicating document status, confidentiality level, authenticity, or other administrative metadata.

## WHAT WATERMARKS FUNDAMENTALLY REPRESENT

Watermarks answer: "What is the document status? What is the confidentiality level? What restrictions or metadata apply?"

The core intelligence is:
- **Status**: Document state (DRAFT, FINAL, APPROVED, etc.)
- **Confidentiality**: Security classification or restriction level
- **Organization**: Company, agency, or issuing authority
- **Temporal**: Dates for creation, expiry, or validity
- **Identification**: Document IDs, reference numbers, versions
- **Authenticity**: Digital signatures, stamps, seals

## EXTRACTION OBJECTIVES

### 1. WATERMARK TEXT
- All visible text exactly as shown
- Orientation if diagonal or rotated
- Opacity or visibility level

### 2. STATUS KEYWORDS
Identify document status:
- **DRAFT**: Work in progress, not final
- **FINAL**: Approved final version
- **APPROVED**: Officially approved
- **PENDING**: Awaiting approval or review
- **REJECTED**: Not approved
- **VOID**: No longer valid
- **COPY**: Not original document
- **SAMPLE**: Example or template

### 3. CONFIDENTIALITY KEYWORDS
Identify security classification:
- **PUBLIC**: Unrestricted distribution
- **INTERNAL**: Internal use only
- **CONFIDENTIAL**: Restricted distribution
- **SECRET**: Highly restricted
- **TOP SECRET**: Highest restriction
- **PROPRIETARY**: Company proprietary information
- **RESTRICTED**: Limited distribution

### 4. ORGANIZATION INFORMATION
- Company or agency name
- Department or division
- Logo or seal description
- Contact information

### 5. TEMPORAL INFORMATION
- Creation date
- Expiration date
- Validity period
- Revision date
- "Valid until" or "Expires on" dates

### 6. IDENTIFICATION NUMBERS
- Document reference number
- Version number
- Serial number
- Control number
- Any alphanumeric identifiers

### 7. AUTHENTICITY MARKERS
- Digital signature indicators
- Seal or stamp descriptions
- Authentication codes
- QR codes or barcodes

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All watermark text
- All stamp text
- All dates and numbers
- Organization names
- Status keywords
- Confidentiality labels
- Document identifiers
- Any fine print or disclaimers

### 2. Full Text Extraction
Extract complete watermark text:
- Exact wording as shown
- Preserve capitalization (often ALL CAPS)
- Note orientation (horizontal, diagonal, vertical)
- Note opacity (faint, medium, prominent)
- Note color if significant

### 3. Status Classification
Identify document status:
- Extract status keywords
- Classify status type
- Note any status dates or conditions
- Assign confidence to classification

### 4. Confidentiality Classification
Identify security level:
- Extract confidentiality keywords
- Classify confidentiality level (numeric scale if possible)
- Note distribution restrictions
- Extract handling instructions if present
- Assign confidence to classification

### 5. Organization Extraction
Extract organizational information:
- Full organization name
- Abbreviated name or acronym
- Department or division
- Logo description if visible
- Contact information (address, phone, email)

### 6. Temporal Information Extraction
Extract all date-related information:
- Creation date or "Issued on"
- Expiration date or "Valid until"
- Revision date or "Last updated"
- Validity period or duration
- Parse date formats (MM/DD/YYYY, DD-MM-YYYY, etc.)

### 7. Identification Number Extraction
Extract all reference numbers:
- Document ID or reference number
- Version number (v1.0, Rev. 2, etc.)
- Serial number
- Control number
- Any other alphanumeric identifiers

### 8. Authenticity Marker Extraction
Document authenticity indicators:
- Digital signature presence
- Seal or stamp description
- Authentication code or hash
- QR code or barcode presence
- Certificate number if shown

### 9. Key Insights
Extract 2-3 key insights about the watermark:
- What is the primary purpose of this watermark?
- What is the document status and confidentiality level?
- What restrictions or handling requirements apply?

### 10. Summary
Provide 1-2 sentence summary of the watermark indicating status, confidentiality, and key metadata.

### 11. Keywords
Generate 2-5 keywords capturing the status, confidentiality level, and organization.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- All text clearly readable
- Status and confidentiality obvious
- Dates and IDs complete
- Standard watermark format

Medium confidence (0.5-0.8):
- Some text unclear due to opacity
- Status requires interpretation
- Partial dates or IDs
- Non-standard format

Low confidence (0.3-0.5):
- Difficult to read due to low contrast
- Ambiguous status or classification
- Incomplete information
- Heavily obscured

Below 0.3:
- Minimal extraction possible
- Very faint or damaged watermark
- Provide partial information only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Watermark",

  "ocr_text": "All readable text extracted from the watermark",

  "watermark_text": {
    "full_text": "Complete watermark text exactly as shown",
    "orientation": "horizontal | diagonal | vertical | rotated",
    "opacity": "faint | medium | prominent",
    "color": "Color if significant"
  },

  "status": {
    "status_keywords": ["DRAFT", "CONFIDENTIAL"],
    "document_status": "draft | final | approved | pending | rejected | void | copy | sample | other",
    "status_confidence": 0.9,
    "status_conditions": "Any conditions or qualifications"
  },

  "confidentiality": {
    "confidentiality_keywords": ["CONFIDENTIAL", "INTERNAL"],
    "confidentiality_level": "public | internal | confidential | secret | top_secret | proprietary | restricted",
    "confidentiality_level_numeric": 3,
    "distribution_restrictions": "Description of restrictions",
    "handling_instructions": "Special handling requirements",
    "confidentiality_confidence": 0.9
  },

  "organization": {
    "organization_name": "Full organization name",
    "abbreviated_name": "Acronym or short name",
    "department": "Department or division",
    "logo_description": "Description of logo if visible",
    "contact_info": {
      "address": "Address if shown",
      "phone": "Phone if shown",
      "email": "Email if shown",
      "website": "Website if shown"
    }
  },

  "temporal_information": {
    "creation_date": "Creation or issue date",
    "expiration_date": "Expiration or 'valid until' date",
    "revision_date": "Revision or 'last updated' date",
    "validity_period": "Duration or validity period",
    "date_format": "Format of dates (MM/DD/YYYY, etc.)"
  },

  "identification_numbers": {
    "document_id": "Document reference number",
    "version_number": "Version (v1.0, Rev. 2, etc.)",
    "serial_number": "Serial number if present",
    "control_number": "Control number if present",
    "other_identifiers": ["Other alphanumeric identifiers"]
  },

  "authenticity_markers": {
    "has_digital_signature": false,
    "seal_description": "Description of seal or stamp",
    "authentication_code": "Auth code or hash",
    "has_qr_code": false,
    "has_barcode": false,
    "certificate_number": "Certificate number if shown"
  },

  "key_insights": [
    "First insight about watermark purpose",
    "Second insight about document status and confidentiality"
  ],

  "summary": "1-2 sentence summary indicating status, confidentiality, and key metadata",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Watermarks often have low contrast — extract what's visible
- Status keywords to look for: DRAFT, FINAL, APPROVED, PENDING, REJECTED, VOID, COPY, SAMPLE
- Confidentiality keywords: PUBLIC, INTERNAL, CONFIDENTIAL, SECRET, TOP SECRET, PROPRIETARY, RESTRICTED
- Date formats vary — parse carefully (MM/DD/YYYY, DD-MM-YYYY, ISO 8601, etc.)
- Document IDs may be alphanumeric codes or reference numbers
- Organization names may be abbreviated or in logo form
- Note if watermark indicates handling restrictions or distribution limitations
