
# MCQ Generator - AI-Powered Educational Assessment Tool 📚

Professional Web-Based Solution for Auto-Generating MCQ Papers with Smart Visual Integration

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
 web application transforms educational PDF content into professional Multiple Choice Question (MCQ) papers using AI-powered content analysis. Built for educators, trainers, and educational institutions who need to quickly create assessments from textbook chapters, standards documents, or any educational material.



## Key Features

- 🌐 Complete Web Interface - Intuitive drag-and-drop GUI built with Flask
- 🤖 AI-Powered Generation - Uses OpenAI GPT for intelligent question creation
- 🎚️ Complexity Control - Adjustable Easy/Medium/Hard distribution with real-time sliders
- 🖼️ Basic Image Integration - Extracts and assigns images to relevant questions
- 📄 Professional PDF Output - Print-ready MCQ and answer key generation
- 🎨 Modern UI/UX - Dark theme with responsive design

### Current Image Capabilities ⚠️
The current version includes basic image extraction and assignment that works to some extent:

- ✅ Successfully extracts images from PDFs with proper transparency handling
- ✅ Filters out very small/decorative images and QR codes
- ✅ Assigns images to questions containing visual keywords
- ⚠️ Limited accuracy in matching specific diagrams to related questions
- 🔮 Advanced image-text mapping planned for future versions using AI models



## Real world Application

- Educational Institutions: Generate chapter-wise assessments from textbooks
- Corporate Training: Create compliance tests from policy documents
- Online Learning: Build question banks for LMS integration
- Certification Bodies: Develop standardized assessments from technical standards
## 🏗️ Complete Solution Architecture

### Project Structure

    mcq-generator/
    ├── app.py                   # Main Flask application server
    ├── requirements.txt         # Python package dependencies
    ├── .env                     # Environment variables (API keys, config)
    │
    ├── 📁 mcq_core/             # Core processing modules
    │   ├── extractor.py          # PDF text/image extraction engine
    │   ├── generator.py          # AI-powered MCQ generation
    │   ├── pdf_utils.py          # Professional PDF creation utilities
    │   └── 📁 fonts/            # Custom fonts for PDF generation DejaVu font family for Unicode support
    │
    ├── 📁 static/               # Web interface assets
    │   └── style.css             # Modern responsive styling
    │
    ├── 📁 templates/            # HTML templates
    │   └── index.html            # Main web interface
    │
    ├── 📁 uploads/              # Temporary PDF storage
    ├── 📁 output/               # Generated MCQ and answer PDFs
    └── 📁 temp_images/          # Extracted images cache


### Core Components


| Component | File    | Purpose|   Technology                |
| :-------- | :------- | :---------- | :---------- |
| WebServer | app.py | Request handling, file management, orchestration| Flask, Python|
| PDF Extractor | mcq_core/extractor.py | PDF parsing, image extraction, source tracking| PyMuPDF, PIL |
| AI Generator | mcq_core/generator.py | Question generation, complexity control| OpenAI GPT-3.5-turbo |
| PDF Creator | mcq_core/pdf_utils.py | Professional PDF creation, formatting| FPDF2, custom fonts |
| Web Interface | templates/index.html| User interaction, file upload, configuration| HTML5, Jinja2 |
| Styling | static/style.css| Modern UI, dark theme, responsive design| CSS3, Flexbox/Grid |




### 📦 Dependencies & Requirements

Python Packages (requirements.txt)

```bash
    Flask                       # Web framework for GUI interface
    openai                      # AI-powered question generation  
    PyPDF2                      # Additional PDF processing support
    fpdf                        # PDF creation and formatting
    python-dotenv               # Environment variable management
    tiktoken                    # OpenAI token counting and management
    pillow                      # Image processing and manipulation
    numpy                       # Numerical operations 
```

### System Requirements

- Python: 3.8 or higher
- Memory: 4GB RAM minimum (8GB recommended)
- Storage: 500MB free space for processing
- API: OpenAI API key for question generation


## 🚀 Installation & Setup

### 1. Environment Variable

```bash
    # Clone or download the project
    git clone https://github.com/tnagendran81/ai-based-mcq-generator
    cd mcq-generator

    # Create virtual environment
    python -m venv venv

    # Activate virtual environment
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    # Install dependencies (fix numphy to numpy)
    pip install Flask openai PyPDF2 fpdf python-dotenv tiktoken pillow numpy
```
### 2. Configuration
Create .env file in the root directory:

```bash
    # OpenAI Configuration
    OPENAI_API_KEY=your_openai_api_key_here

    # Flask Configuration
    SECRET_KEY=your-secret-key-change-this-in-production
    FLASK_ENV=development

    # File Processing Limits
    MAX_FILE_SIZE=16777216    # 16MB in bytes
    MAX_PAGES=50              # Maximum pages to process
    MAX_QUESTIONS=100         # Maximum questions to generate
```

### 3. Run Application

```bash
    # Start the Flask development server
    python app.py

    # Access the application at:
    # http://localhost:5000
```



```bash

```
## 🎮 How to Use

#### Step 1: Access Web Interface
- Open browser and navigate to http://localhost:5000
- You'll see the modern dark-themed interface
#### Step 2: Upload PDF
- File Selection: Use the file input or drag-and-drop zone
- Validation: System accepts PDF files up to 16MB
- Confirmation: Green success message confirms upload
#### Step 3: Configure Generation Parameters
- ##### Basic Settings
    - Pages: Select range (1-50 pages)
    - Questions: Choose count (5-50 questions)
- ##### Complexity Distribution (Interactive Sliders)
    - Easy (0-100%): Basic recall, definitions, direct facts
    - Medium (0-100%): Application, understanding, relationships
    - Hard (0-100%): Analysis, synthesis, critical thinking
    The system automatically normalizes percentages to total 100%.
- ##### Preset Options Available
    - Balanced: Equal distribution across difficulty levels
    - Student-Friendly: More easy questions for beginners
    - Challenging: Emphasis on harder analytical questions
#### Step 4 Generate & Download
- Click "Generate MCQs" - Processing begins
- Wait for completion - Typically 30-90 seconds depending on content
- Download Results:
    - mcqs_[session_id].pdf - Student question paper
    - answers_[session_id].pdf - Educator answer key with explanations


## 🔧 Detailed Component Analysis

### Flask Application (app.py)
#### Key Functions:
- index() - Main route handling GET/POST requests with comprehensive validation
- add_image_references_to_mcqs() - Basic image-question association using keywords
- cleanup_temp_files() - Secure temporary file management
- download_file() - Secure file download with path validation
- Error handling for file size limits, invalid uploads, and processing failures

#### Security Features:
- File type validation (PDF only)
- Size limits (16MB max)
- Directory traversal prevention
- Session-based temporary file isolation

### PDF Extractor (mcq_core/extractor.py)
#### Advanced Features:
- Two-pass image mapping for accurate source page tracking
- Transparency mask handling for complex images (solves black image issues)
- CMYK to RGB color space conversion for proper image display
- Quality filtering: size, brightness, aspect ratio validation
- Educational content detection vs decorative elements

#### Image Processing Pipeline:
- Extract all images with source page mapping
- Apply transparency masks where present
- Convert color spaces for compatibility
- Filter by size and quality metrics
- Verify brightness to avoid blank images

### MCQ Generator (mcq_core/generator.py)
#### AI-Powered Features:
- Text chunking for large documents (600 words per chunk)
- Complexity-aware prompt engineering with specific instructions
- OpenAI GPT-3.5-turbo integration with error handling
- Response parsing with answer marker removal
- Explanation generation for each correct answer

#### Complexity Algorithm:
- Easy: Direct recall, definitions, basic facts
- Medium: Understanding relationships, application concepts
- Hard: Analysis, synthesis, critical thinking

### PDF Creator (mcq_core/pdf_utils.py)
#### Professional Features:
- Unicode character normalization for mathematical symbols
- Smart image sizing and centering in PDF layout
- Multi-page layout with automatic page breaks
- Source page attribution for academic integrity
- Separate answer key with explanations and correct options
## 🖼️ Image Capabilities & Limitations

### Current Implementation (v2.0)
#### What Works:
- ✅ Robust image extraction from PDFs with proper handling of:
    - Transparency masks and alpha channels
    - CMYK to RGB color conversion
    - Various image formats (PNG, JPEG, etc.)
- ✅ Basic quality filtering removes:
    - Very small images (<100x100 pixels)
    - Very large background images (>2000x2000 pixels)
    - Completely black/dark images
- ✅ Keyword-based assignment to questions containing:
    - 'figure', 'diagram', 'graph', 'chart', 'table'
    - 'example', 'shown', 'following', 'given'
    - Subject-specific terms like 'angle', 'triangle', 'circle'

#### Current Limitations:
- ⚠️ Generic matching - doesn't understand image content semantically
- ⚠️ May assign irrelevant images to questions with visual keywords
- ⚠️ No caption analysis - doesn't read figure captions for context
- ⚠️ Sequential assignment - first available image goes to first matching question

#### Planned Enhancements (v2.1+)

- Advanced Image-Text Matching:
    - 🔮 CLIP-based semantic matching for understanding image content
    - 🔮 Caption extraction and NLP for context-aware assignment
    - 🔮 Spatial layout analysis for images near related text
    - 🔮 Machine learning models trained on educational content

## 🛠️ Version History & Roadmap

### v1.0 - Foundation
- ✅ Basic PDF text extraction
- ✅ Simple MCQ generation via OpenAI
- ✅ Command-line interface
- ❌ No image handling
- ❌ No complexity control

### v1.5 - Core Improvements
- ✅ Advanced image extraction with transparency
- ✅ Smart filtering of decorative images
- ✅ Unicode support for mathematical symbols
- ✅ Professional PDF formatting
- ❌ Still command-line based

### v2.0 - Web Interface (Current)
- ✅ Complete Flask-based web application
- ✅ Interactive complexity control sliders
- ✅ Modern responsive web interface
- ✅ Real-time parameter validation
- ✅ Secure file handling and downloads
- ✅ Basic image-question association
- ✅ Professional PDF generation with fonts
- ✅ Comprehensive error handling

### v2.1 - Enhanced Image Intelligence (Planned)
- 🔄 CLIP-based multimodal matching for accurate image-text pairing
- 🔄 Caption extraction and analysis from PDF text
- 🔄 Spatial layout analysis for contextual image placement
- 🔄 Content-aware filtering using computer vision
- 🔄 User feedback system for improving matches

### v2.2 - Advanced Features (Future)
- 🔄 Multi-language support
- 🔄 Batch PDF processing
- 🔄 Question difficulty analysis using psychometrics
- 🔄 Export to LMS formats (Moodle, Canvas, etc.)
- 🔄 User accounts and session management
- 🔄 Cloud deployment with Docker
## 🎯 Best Practices & Tips

### For Best Results with Images:
1. Use PDFs with clear, educational diagrams rather than scanned documents
2. Ensure images are properly embedded (not just overlaid text)
3. Review generated questions and manually verify image relevance
4. Consider the current limitations when planning question types

### For Optimal Question Quality:
1. Use well-structured educational content with clear concepts
2. Provide sufficient text (at least 2-3 pages) for variety
3. Adjust complexity distribution based on your audience
4. Review and edit generated questions before final use
## 🌐 Production Deployment
### Local Development
```bash
python app.py
```
### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
### Docker Deployment
```bash
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```
## 🐛 Troubleshooting
### Common Issues
- "No extractable text found in the PDF":
    - Ensure PDF contains selectable text (not scanned images)
    - Try OCR preprocessing for scanned documents
- "MCQ generation failed":
    - Check OpenAI API key in .env file
    - Verify API key has sufficient credits
    - Check internet connectivity
- Images appear black or corrupted:
    - This is largely resolved in v2.0 with transparency handling
    - If issues persist, check original PDF image quality
- Questions don't match images well:
    - This is expected with current basic matching
    - Advanced semantic matching coming in v2.1+
## Contributing

- Fork the repository
- Create feature branch (git checkout -b feature/ImageEnhancement)
- Follow Python PEP 8 style guidelines
- Add tests for new functionality
- Submit pull request

### Priority Areas for Contribution:

- 🔥 Image-text semantic matching using CLIP or similar models
- 🔥 Caption extraction from PDF text for better context
- 🔥 UI/UX improvements for better user experience
- 🔥 Question quality metrics and validation

## Acknowledgements

- OpenAI - GPT models enabling intelligent question generation
- PyMuPDF Team - Robust PDF processing with image handling
- Flask Community - Excellent web framework and ecosystem
- Educational Community - Feedback driving continuous improvement


### 🎓 Transforming Education Through AI - Currently Handling Images at Basic Level, Advanced Matching Coming Soon!
