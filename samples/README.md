# Sample Resume Files

This directory contains sample resume files for testing the AI Resume Analyzer application.

## Files Included

### Text Files (Source Content)
- `sample_resume_en.txt` - English resume content for John Smith
- `sample_resume_ro.txt` - Romanian resume content for Maria Popescu
- `sample_job.txt` - Sample job description for testing job matching features

### Required PDF Files (To Be Generated)
You need to convert the text files to PDF format for testing:

1. **sample_resume_en.pdf** - Convert `sample_resume_en.txt` to PDF
2. **sample_resume_ro.pdf** - Convert `sample_resume_ro.txt` to PDF
3. **sample_resume_scanned.jpg** - Create a scanned/image version for OCR testing

## How to Create PDF Files

### Method 1: Using Online Converters
1. Copy content from `.txt` files
2. Paste into Google Docs or Microsoft Word
3. Format as a professional resume
4. Export/Save as PDF

### Method 2: Using Python (Automated)
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf_from_text(text_file, pdf_file):
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    
    # Simple text rendering (you may want to improve formatting)
    lines = content.split('\n')
    y = height - 50
    
    for line in lines:
        if y < 50:  # Start new page if needed
            c.showPage()
            y = height - 50
        c.drawString(50, y, line[:80])  # Limit line length
        y -= 15
    
    c.save()

# Create PDFs
create_pdf_from_text('sample_resume_en.txt', 'sample_resume_en.pdf')
create_pdf_from_text('sample_resume_ro.txt', 'sample_resume_ro.pdf')
```

### Method 3: Using pandoc (Command Line)
```bash
# Install pandoc first
pandoc sample_resume_en.txt -o sample_resume_en.pdf
pandoc sample_resume_ro.txt -o sample_resume_ro.pdf
```

## Creating Scanned Image for OCR Testing

To create `sample_resume_scanned.jpg`:

1. Create a PDF from `sample_resume_en.txt`
2. Print the PDF to paper
3. Scan the paper at 150-300 DPI
4. Save as JPG format
5. Optionally add some scanning artifacts (slight rotation, shadows) to test OCR robustness

### Alternative: Simulate Scanned Image
You can create a simulated scanned image using image processing:

```python
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_scanned_resume_image():
    # Create a white background
    img = Image.new('RGB', (2480, 3508), 'white')  # A4 size at 300 DPI
    draw = ImageDraw.Draw(img)
    
    # Add resume text (simplified version)
    font = ImageFont.load_default()
    
    resume_text = """
    JOHN SMITH
    Software Engineer
    
    Email: john.smith@email.com
    Phone: +1 (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years...
    [Add more content as needed]
    """
    
    # Draw text
    draw.text((100, 100), resume_text, fill='black', font=font)
    
    # Add some scanning artifacts
    # Slight rotation
    img = img.rotate(0.5, expand=True, fillcolor='white')
    
    # Add some noise
    np_img = np.array(img)
    noise = np.random.normal(0, 5, np_img.shape).astype(np.uint8)
    np_img = np.clip(np_img + noise, 0, 255)
    
    img = Image.fromarray(np_img)
    img.save('sample_resume_scanned.jpg', 'JPEG', quality=85)

create_scanned_resume_image()
```

## Testing the Files

Once you have created the PDF and image files, you can test them with the application:

1. Start the application: `streamlit run app.py`
2. Upload each file type to test different extraction methods
3. Verify that text extraction works correctly for each format
4. Test the OCR fallback with the scanned image

## File Purposes

- **sample_resume_en.pdf**: Tests standard PDF text extraction
- **sample_resume_ro.pdf**: Tests multi-language support and Romanian text processing
- **sample_resume_scanned.jpg**: Tests OCR functionality and fallback mechanisms
- **sample_job.txt**: Tests job description analysis and skill gap comparison