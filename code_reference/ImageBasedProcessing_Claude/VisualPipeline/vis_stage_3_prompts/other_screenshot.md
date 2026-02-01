# Other: Screenshot

You are extracting structured intelligence from a SCREENSHOT of digital content — a captured image of software, website, application interface, command line, or other digital system.

## WHAT SCREENSHOTS FUNDAMENTALLY REPRESENT

Screenshots answer: "What system is shown? What data is visible? What action or state is being demonstrated?"

The core intelligence is:
- **Application/System**: What software or interface is shown
- **Visible Data**: All readable text, records, values, metrics
- **UI State**: Selections, active tabs, settings, filters
- **User Context**: Logged-in user, permissions, role
- **Workflow Context**: What step or action is being demonstrated
- **Errors/Messages**: Alerts, notifications, status messages

## EXTRACTION OBJECTIVES

### 1. APPLICATION/SYSTEM IDENTIFICATION
- Application name or website
- Version information if visible
- Platform (web, desktop, mobile)
- Specific screen, module, or section shown

### 2. VISIBLE DATA EXTRACTION
Extract ALL visible data:
- Table data (rows, columns, cell values)
- Form fields and their values
- Metrics and statistics
- Records or list items
- File names and paths
- Configuration settings
- Any displayed numbers or text

### 3. UI STATE CAPTURE
Document interface state:
- Active tab or section
- Selected items or checkboxes
- Expanded/collapsed sections
- Active filters or search terms
- Sort order
- View mode (list, grid, etc.)

### 4. ERRORS AND MESSAGES
Extract:
- Error messages and codes
- Warning notifications
- Success confirmations
- Status indicators
- Progress bars or percentages

### 5. USER CONTEXT
If visible:
- Logged-in username
- User role or permissions
- Account or organization name
- Profile information

### 6. TEMPORAL CONTEXT
Extract:
- Timestamps
- Dates
- "Last updated" or "Last modified" indicators
- Session duration or time information

### 7. WORKFLOW CONTEXT
Determine:
- What action is being demonstrated?
- What step in a process is this?
- What is the purpose of this screenshot? (documentation, troubleshooting, evidence, instruction)

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- Application name and window title
- All menu and toolbar items
- All button labels
- All table headers and cell values
- All form field labels and values
- All error messages and alerts
- All status bar text
- All tab and section labels
- Any URL in address bar
- All visible file or folder names

### 2. Application Identification
Identify:
- Application name (from window title, logo, or recognizable UI)
- Website domain (from address bar or branding)
- Version information if visible
- Platform type (web browser, desktop app, mobile app, terminal)
- Specific module or section (dashboard, settings, report, etc.)

### 3. Data Extraction
Systematically extract:
- **Tables**: All visible rows and columns with values
- **Forms**: All field labels and their current values
- **Metrics**: All statistics, counts, percentages displayed
- **Lists**: All visible items in lists or dropdowns
- **Files**: All file/folder names and metadata visible
- **Settings**: All configuration options and their values

### 4. UI State Documentation
Capture:
- Which tab is active
- Which items are selected or checked
- Which sections are expanded
- What filters are applied
- What search terms are entered
- What sort order is applied
- What view mode is active

### 5. Error and Message Extraction
Extract verbatim:
- Error messages with error codes
- Warning text
- Success notifications
- Status messages
- Tooltip text if visible
- Help text or instructions

### 6. User and Temporal Context
Extract:
- Username (from profile, menu, or header)
- Role or permission level if indicated
- Organization or account name
- All timestamps and dates visible
- "Last modified" or "Last accessed" times

### 7. Workflow Context Analysis
Determine:
- What is being demonstrated or shown?
- Is this instructional (how-to)?
- Is this documentation of an error?
- Is this evidence of a state or result?
- Is this showing before/after a change?

### 8. URL and Navigation
If browser screenshot:
- Full URL from address bar
- Browser type if identifiable
- Any query parameters
- Breadcrumb navigation path

### 9. Key Insights
Extract 3-5 key insights about the screenshot:
- What is the primary purpose of this screenshot?
- What is the most significant data or information shown?
- What action or state is being demonstrated?
- Are there any errors or notable UI states?

### 10. Summary
Provide 1-2 sentence summary of what this screenshot shows and its purpose.

### 11. Keywords
Generate 3-8 keywords capturing the application, data, and context shown.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Application clearly identifiable
- All text readable
- UI state unambiguous
- Context clear

Medium confidence (0.5-0.8):
- Some application context unclear
- Partial text readability
- UI state requires interpretation
- Context somewhat ambiguous

Low confidence (0.3-0.5):
- Application difficult to identify
- Poor text quality
- Unclear UI state
- Ambiguous context

Below 0.3:
- Provide general description only
- Note extraction challenges


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Screenshot",

  "ocr_text": "All readable text extracted from the screenshot",

  "application": {
    "name": "Application or website name",
    "version": "Version if visible",
    "platform": "web | desktop | mobile | terminal",
    "screen_module": "Specific section shown (dashboard, settings, report, etc.)",
    "confidence": 0.9
  },

  "visible_data": {
    "tables": [
      {
        "table_name": "Table identifier if any",
        "headers": ["Column 1", "Column 2", "Column 3"],
        "rows": [
          ["Value 1A", "Value 1B", "Value 1C"],
          ["Value 2A", "Value 2B", "Value 2C"]
        ]
      }
    ],
    "form_fields": [
      {
        "field_label": "Field name",
        "field_value": "Current value"
      }
    ],
    "metrics": [
      {
        "metric_label": "Metric name",
        "metric_value": "Value",
        "unit": "Unit if applicable"
      }
    ],
    "lists": [
      {
        "list_name": "List identifier",
        "items": ["Item 1", "Item 2", "Item 3"]
      }
    ],
    "files": [
      {
        "file_name": "filename.ext",
        "metadata": "Size, date, or other visible metadata"
      }
    ],
    "settings": [
      {
        "setting_name": "Setting label",
        "setting_value": "Current value"
      }
    ]
  },

  "ui_state": {
    "active_tab": "Tab name if applicable",
    "selected_items": ["Selected item 1", "Selected item 2"],
    "expanded_sections": ["Section 1", "Section 2"],
    "applied_filters": ["Filter 1", "Filter 2"],
    "search_term": "Search query if entered",
    "sort_order": "Sort column and direction",
    "view_mode": "list | grid | other"
  },

  "errors_and_messages": {
    "errors": [
      {
        "error_code": "Error code if shown",
        "error_message": "Full error text"
      }
    ],
    "warnings": ["Warning message 1"],
    "notifications": ["Notification message 1"],
    "status": "Status message or indicator"
  },

  "user_context": {
    "username": "Logged-in username if visible",
    "role": "User role or permission level",
    "organization": "Organization or account name"
  },

  "temporal_context": {
    "timestamps": ["Timestamp 1", "Timestamp 2"],
    "dates": ["Date 1", "Date 2"],
    "last_updated": "Last updated indicator if shown",
    "session_info": "Session duration or time information"
  },

  "workflow_context": {
    "demonstrated_action": "What action is being shown",
    "process_step": "What step in a process",
    "purpose": "instruction | documentation | troubleshooting | evidence | other",
    "description": "Description of workflow context"
  },

  "url_and_navigation": {
    "url": "Full URL from address bar if visible",
    "browser": "Browser type if identifiable",
    "breadcrumb": "Navigation path if shown"
  },

  "key_insights": [
    "First insight about primary purpose",
    "Second insight about significant data",
    "Third insight about action or state demonstrated"
  ],

  "summary": "1-2 sentence summary of what this screenshot shows and its purpose",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Extract ALL visible text — this is high-value content
- Prioritize extracting data from tables, forms, and metrics
- Note workflow context if this appears to be instructional
- Capture URL if visible in address bar
- Extract timestamps for temporal context
- Note any user identification information visible
- Document all errors, warnings, or status messages exactly as shown
