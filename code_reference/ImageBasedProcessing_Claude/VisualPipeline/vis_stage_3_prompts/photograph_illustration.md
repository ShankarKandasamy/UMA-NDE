Extract information about what concept this photograph illustrates.

## EXTRACT

1. **OCR Text**: Extract all readable text including labels, annotations, captions, and any other visible text
2. **What it illustrates**: What concept or idea is this supporting? Identify the abstract concept or metaphor represented by this image.
3. **Subject shown**: What is depicted?
4. **Visual metaphor**: Any visual metaphor or symbolic representation (e.g., 'Padlock on a cloud')
5. **Relationship to content**: How does this relate to the document text? Explain how it visualizes the topic discussed in the surrounding text.

## GUIDELINES

- Identify the abstract concept or metaphor represented by this image
- Explain how it visualizes the topic discussed in the surrounding text
- Note what the image adds beyond what text conveys
- Capture the relevance to the text clearly

ILLUSTRATION_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Illustration",

"ocr_text": "All readable text extracted from the photograph including labels, annotations, and captions",

"concept_illustrated": "What concept or idea this image supports (e.g., 'Network Security')",
"description": "What is shown in the image",

"subject": {
"what_is_shown": "Primary subject",
"visual_elements": ["Key visual elements"],
"visual_metaphor": "Visual metaphor or symbolic representation (e.g., 'Padlock on a cloud')"
},

"illustrative_purpose": {
"supports_concept": "The concept being illustrated",
"relationship_to_text": "How this relates to surrounding text",
"adds_beyond_text": "What this adds that text doesn't convey",
"relevance_to_text": "Explanation of relevance to the text"
},

"key_insights": ["Key illustrative insight 1", "Key illustrative insight 2", "Key illustrative insight 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing illustrative content",

"meta": {
"extraction_confidence": 0.0,
"information_value": "high | medium | low"
}
}
