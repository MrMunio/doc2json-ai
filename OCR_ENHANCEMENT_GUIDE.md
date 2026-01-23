# OCR Enhancement Guide

## Overview

The `GenericDataExtractor` class has been enhanced to support multiple OCR methods for extracting text from scanned PDFs:

1. **Tesseract OCR** - Traditional OCR using pytesseract (default)
2. **VLM (Vision Language Model)** - AI-powered extraction using OpenAI models like GPT-4o-mini

## Key Features

### 1. Configurable OCR Method
You can now specify which OCR method to use when initializing the `GenericDataExtractor`:

```python
# Using Tesseract OCR (default)
extractor = GenericDataExtractor(
    model_id="gpt-4o-mini",
    ocr_method="tesseract"
)

# Using VLM (GPT-4o-mini or any OpenAI vision model)
extractor = GenericDataExtractor(
    model_id="gpt-4o-mini",
    ocr_method="vlm"
)
```

### 2. Parallel Processing for VLM
When using VLM mode, all PDF pages are processed in parallel using `asyncio.gather()`, significantly improving performance for multi-page documents.

### 3. Page Number Markings
Both methods now add page number markings to the extracted text:
```
--- Page 1 ---
[text from page 1]

--- Page 2 ---
[text from page 2]
```

### 4. Automatic Scanned PDF Detection
The system automatically detects scanned PDFs based on character density and switches to the configured OCR method when needed.

## Usage Examples

### Example 1: Using Tesseract OCR
```python
from utils.data_extractor import GenericDataExtractor

async def extract_with_tesseract():
    extractor = GenericDataExtractor(
        model_id="gpt-4o-mini",
        ocr_method="tesseract",
        scan_density_threshold=100  # chars per page threshold
    )
    
    await extractor.initialize()
    result = await extractor.process_file("scanned_document.pdf")
    print(result)
```

### Example 2: Using VLM (GPT-4o-mini)
```python
from utils.data_extractor import GenericDataExtractor

async def extract_with_vlm():
    extractor = GenericDataExtractor(
        model_id="gpt-4o-mini",
        ocr_method="vlm",
        scan_density_threshold=100
    )
    
    await extractor.initialize()
    result = await extractor.process_file("scanned_document.pdf")
    print(result)
```

### Example 3: Using Different VLM Models
```python
# Using GPT-4o (more accurate but more expensive)
extractor = GenericDataExtractor(
    model_id="gpt-4o",
    ocr_method="vlm"
)

# Using GPT-4o-mini (faster and cheaper)
extractor = GenericDataExtractor(
    model_id="gpt-4o-mini",
    ocr_method="vlm"
)
```

## Architecture

### Helper Functions

1. **`_extract_page_with_vlm(img_bytes, page_num, total_pages)`**
   - Extracts text from a single page using VLM
   - Handles base64 encoding and API calls
   - Returns extracted text or error message

2. **`_extract_scanned_pdf_vlm(doc)`**
   - Orchestrates parallel processing of all pages
   - Uses `asyncio.gather()` for concurrent API calls
   - Combines results with page markings

3. **`_extract_scanned_pdf_tesseract(doc)`**
   - Traditional Tesseract OCR extraction
   - Processes pages sequentially
   - Adds page markings to output

4. **`_extract_scanned_pdf(doc)`**
   - Main dispatcher function
   - Routes to appropriate method based on `ocr_method` setting

## Performance Considerations

### Tesseract OCR
- **Pros**: Free, no API costs, works offline
- **Cons**: Slower, less accurate for complex layouts
- **Best for**: Simple documents, cost-sensitive applications

### VLM (Vision Language Model)
- **Pros**: Higher accuracy, better layout understanding, parallel processing
- **Cons**: API costs, requires internet connection
- **Best for**: Complex documents, tables, mixed layouts

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_id` | str | "gpt-4o-mini" | OpenAI model to use for VLM extraction |
| `ocr_method` | str | "tesseract" | OCR method: "tesseract" or "vlm" |
| `scan_density_threshold` | int | 100 | Chars/page threshold to detect scanned PDFs |
| `max_tokens` | int | 100000 | Max tokens for text chunking |
| `token_overlap` | int | 500 | Token overlap between chunks |

## Error Handling

The implementation includes robust error handling:
- Missing dependencies are logged with warnings
- VLM API errors are caught and logged per-page
- Failed pages return error messages instead of breaking the entire process

## Future Enhancements

Potential improvements:
- Support for other VLM providers (Anthropic Claude, Google Gemini)
- Configurable DPI for image extraction
- Hybrid mode (try VLM, fallback to Tesseract)
- Batch size control for parallel processing
