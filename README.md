# 🤖 AI-Powered Resume Analyzer

A comprehensive Streamlit web application that analyzes resumes using AI, generates personalized video pitches, and provides job matching capabilities. Built for hackathon teams to quickly evaluate resumes and create engaging presentations with advanced features like CV optimization and interview preparation.

## ✨ Features

### Core Functionality
- **📄 Smart Text Extraction**: Supports PDF and DOCX files with intelligent OCR fallback
- **🤖 AI-Powered Analysis**: GPT-based resume analysis with detailed strengths, weaknesses, and actionable suggestions
- **🎥 Advanced Video Generation**: Creates professional video pitches using Gemini Veo 3 API with MoviePy fallback
- **🌍 Multi-Language Support**: Full support for English and Romanian resumes and job descriptions
- **💼 Job Matching & CV Optimization**: Advanced skill gap analysis and tailored improvement recommendations

### Advanced Features
- **🎯 Job-Specific Video Content**: Generate interview preparation videos tailored to specific job requirements
- **📊 Compatibility Scoring**: Quantitative analysis of resume-job fit with detailed metrics
- **🗄️ Persistent Storage**: Supabase integration for CV history, job tracking, and progress monitoring
- **🔍 Smart Search**: Full-text search capabilities for stored CVs and job descriptions
- **📈 Progress Tracking**: Monitor CV improvements and application success rates over time

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **OpenAI API key** (Required)
- **Supabase account** (Required for persistence features)
- **Nutrient API credentials** (Optional, for OCR fallback)
- **Google AI Studio API key** (Optional, for advanced video generation)

### Step-by-Step Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd ai-resume-analyzer
   ```

2. **Create virtual environment** (Recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` file with your API credentials:
   ```env
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   
   # Optional
   NUTRIENT_API_KEY=your_nutrient_api_key_here
   GOOGLE_AI_API_KEY=your_google_ai_studio_key
   ```

5. **Initialize database**
   ```bash
   python setup_database.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   # Or use the convenience script
   ./run.sh
   ```

7. **Open your browser** to `http://localhost:8501`

## 📋 API Configuration Guide

### OpenAI API Setup (Required)

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key and add to your `.env` file
6. **Important**: Add billing information to your OpenAI account to avoid rate limits

### Supabase Setup (Required)

1. Visit [Supabase](https://supabase.com) and create a free account
2. Create a new project
3. Go to Settings > API
4. Copy the Project URL and anon/public key
5. Add both to your `.env` file
6. The database schema will be created automatically when you run `setup_database.py`

### Nutrient OCR Setup (Optional)

1. Visit [Nutrient](https://nutrient.io/) and create an account
2. Get your API credentials from the dashboard
3. Add to `.env` file for enhanced OCR capabilities
4. **Note**: The app works without this, using basic text extraction

### Google AI Studio Setup (Optional)

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to `.env` file for advanced video generation
4. **Note**: App falls back to MoviePy if not available

## 🏗️ Project Structure

```
ai-resume-analyzer/
├── app.py                    # Main Streamlit application and UI
├── parsing.py                # Text extraction from PDF/DOCX with OCR fallback
├── ai_integration.py         # OpenAI GPT integration and job matching
├── tts_video.py             # Basic video generation with TTS (fallback)
├── gemini_video.py          # Advanced video generation with Gemini Veo 3
├── database.py              # Supabase integration and data persistence
├── utils.py                 # Utility functions and helpers
├── setup_database.py        # Database initialization script
├── demo_job_matching.py     # Job matching feature demonstration
├── demo_new_features.py     # New features demonstration
├── requirements.txt         # Python dependencies
├── run.sh                   # Convenience startup script
├── .env.template           # Environment variables template
├── samples/                # Sample files for testing
│   ├── sample_resume_en.txt    # English resume sample
│   ├── sample_resume_ro.txt    # Romanian resume sample
│   ├── sample_job.txt          # Job description sample
│   └── README.md               # Sample files documentation
├── tests/                  # Test files
│   ├── test_parsing.py         # Text extraction tests
│   ├── test_ai_integration.py  # AI analysis tests
│   ├── test_tts_video.py       # Video generation tests
│   └── test_new_integrations.py # Integration tests
└── README.md              # This documentation
```

## 📝 Usage Guide

### Basic Workflow

1. **Upload Resume**
   - Drag and drop PDF or DOCX file into the upload area
   - Supported formats: PDF, DOCX
   - Maximum file size: 200MB
   - The app will automatically extract text and display it for verification

2. **Add Job Description** (Optional but Recommended)
   - Paste job requirements in the text area
   - Include technical skills, responsibilities, and requirements
   - This enables advanced job matching and CV optimization features

3. **Analyze Resume**
   - Click "Analyze Resume" to get AI-powered insights
   - View structured analysis with strengths, weaknesses, and suggestions
   - See skill gap analysis if job description was provided

4. **Generate Video Pitch**
   - Choose between basic (MoviePy) or advanced (Gemini) video generation
   - Creates personalized 10-second video pitch
   - Includes job-specific content if job description was provided

5. **Download Results**
   - Download analysis results as formatted text file
   - Download generated video in MP4 format
   - Save job matching reports for future reference

### Advanced Features

#### Job Matching & CV Optimization
- **Compatibility Scoring**: Get quantitative match percentage between CV and job
- **Missing Skills Analysis**: Identify skills gaps and learning opportunities
- **Keyword Optimization**: Receive ATS-friendly keyword suggestions
- **Tailored Recommendations**: Get specific advice for improving CV for target job

#### Video Generation Options
- **Basic Videos**: Fast generation using MoviePy with text animations
- **Advanced Videos**: Professional quality using Gemini Veo 3 with custom styling
- **Job-Specific Content**: Videos tailored to specific job requirements and industry
- **Interview Preparation**: Generate practice videos with job-relevant talking points

#### Data Persistence & History
- **CV History**: All analyzed resumes are saved for future reference
- **Job Tracking**: Keep track of job applications and compatibility scores
- **Progress Monitoring**: See improvements in CV optimization over time
- **Search & Filter**: Find previous analyses using full-text search

## 💼 Job Matching & CV Optimization Guide

### Job Description Input Setup

The job matching feature requires proper job description input to provide accurate optimization advice:

1. **Job Description Format**
   - Include complete job posting text with requirements, responsibilities, and qualifications
   - Ensure technical skills, soft skills, and experience requirements are clearly listed
   - Add company culture information and work environment details for better matching

2. **Optimal Job Description Structure**
   ```
   Job Title: [Position Name]
   Company: [Company Name]
   
   Requirements:
   - [Technical skills and tools]
   - [Years of experience]
   - [Educational requirements]
   
   Responsibilities:
   - [Key job duties]
   - [Project types]
   - [Team collaboration]
   
   Preferred Qualifications:
   - [Nice-to-have skills]
   - [Additional certifications]
   ```

### CV Optimization Workflow

#### Step 1: Upload and Analyze CV
1. Upload your resume in PDF or DOCX format
2. Review extracted text for accuracy
3. Get initial AI analysis with strengths and weaknesses

#### Step 2: Add Target Job Description
1. Paste the complete job posting in the job description text area
2. Include job title and company name for better context
3. Ensure all technical requirements and responsibilities are included

#### Step 3: Generate Job-Specific Analysis
1. Click "Analyze with Job Matching" to get compatibility analysis
2. Review compatibility score (0-100%) and detailed breakdown
3. Examine missing skills analysis with priority levels

#### Step 4: Review Optimization Recommendations
The system provides specific advice in several categories:

**Critical Missing Skills**
- High-priority skills absent from your CV
- Learning suggestions and certification recommendations
- Timeline estimates for skill acquisition

**Keyword Optimization**
- ATS-friendly keywords to add to your CV
- Exact phrases from job description to incorporate
- Section-specific keyword placement advice

**CV Section Improvements**
- Professional Summary tailoring suggestions
- Skills section optimization recommendations
- Experience section enhancement advice
- Education and certification additions

**Interview Preparation Focus**
- Key topics to prepare based on job requirements
- Relevant examples to practice from your experience
- Company culture alignment talking points

#### Step 5: Generate Job-Specific Video Content
1. Create interview preparation videos tailored to the specific job
2. Generate pitch videos that emphasize job-relevant skills
3. Practice with job-focused talking points and examples

### Job Matching Features

#### Compatibility Scoring Algorithm
The system calculates compatibility based on:
- **Skill Matching (40%)**: Technical and soft skills alignment
- **Experience Level (25%)**: Years of experience and seniority match
- **Industry Keywords (20%)**: Relevant terminology and domain knowledge
- **Responsibility Alignment (15%)**: Past experience matching job duties

#### Missing Skills Analysis
- **Critical Skills**: Must-have requirements missing from CV (High Priority)
- **Preferred Skills**: Nice-to-have qualifications not present (Medium Priority)
- **Industry Keywords**: Relevant terms for ATS optimization (Low Priority)

#### Optimization Advice Categories

**Section-Specific Recommendations**:
- **Professional Summary**: Tailor opening statement to job requirements
- **Skills Section**: Add missing technical and soft skills
- **Experience Section**: Emphasize relevant accomplishments
- **Education**: Highlight relevant coursework or certifications

**ATS Optimization**:
- Exact keyword matches from job description
- Proper keyword density and placement
- Industry-standard terminology usage
- Format optimization for applicant tracking systems

**Interview Preparation**:
- Key talking points based on job requirements
- Relevant examples from your experience
- Company culture alignment strategies
- Technical discussion preparation areas

### Job-Specific Video Generation

#### Advanced Video Features for Job Matching

**Job-Tailored Content**:
- Prioritizes skills that match job requirements
- Incorporates company culture elements
- Uses industry-appropriate terminology
- Emphasizes relevant experience and achievements

**Dynamic Style Selection**:
- **Tech Roles**: Technical interview style with code examples
- **Creative Roles**: Visual-focused style with portfolio highlights
- **Business Roles**: Professional corporate style
- **Academic Roles**: Research and education-focused approach
- **Startup Roles**: Dynamic, innovation-focused presentation

**Interview Preparation Videos**:
- Job-specific talking points and examples
- Practice scenarios based on job responsibilities
- Company culture alignment messaging
- Technical discussion preparation content

#### Video Optimization Metadata
Each generated video includes:
- Job compatibility score
- Key improvement areas highlighted
- Interview focus recommendations
- Industry-specific styling choices

### Progress Tracking and History

#### CV Improvement Monitoring
- Track compatibility scores across different job applications
- Monitor skill gap closure over time
- Measure keyword optimization improvements
- Review interview invitation success rates

#### Job Application History
- Save all job descriptions and matching results
- Compare compatibility scores across similar positions
- Track which optimization advice was most effective
- Monitor application success patterns

#### Search and Filter Capabilities
- Find previous job matches by company, role, or industry
- Filter by compatibility score ranges
- Search by specific skills or requirements
- Review optimization advice history

## 🔧 Development & Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest test_parsing.py
python -m pytest test_ai_integration.py
python -m pytest test_tts_video.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Development Setup

This project is designed for rapid hackathon development with modular components:

- **parsing.py**: Document text extraction with intelligent fallback
- **ai_integration.py**: AI analysis, job matching, and CV optimization
- **tts_video.py**: Basic video generation for reliable fallback
- **gemini_video.py**: Advanced video generation for professional results
- **database.py**: Data persistence and history management
- **app.py**: Streamlit UI orchestration and user experience

### Adding New Features

1. **Text Processing**: Extend `parsing.py` for new file formats
2. **AI Analysis**: Modify prompts in `ai_integration.py` for new analysis types
3. **Video Styles**: Add new templates in `gemini_video.py`
4. **UI Components**: Extend `app.py` with new Streamlit components
5. **Database Schema**: Update `database.py` and `setup_database.py` for new data types

## 🎯 Demo & Presentation

### Quick Demo Checklist

- [ ] **Environment Setup**: Verify all API keys are configured
- [ ] **Sample Data**: Ensure sample files are available in `samples/` directory
- [ ] **Database**: Run `python setup_database.py` to initialize
- [ ] **Application**: Start with `streamlit run app.py` or `./run.sh`
- [ ] **Test Upload**: Upload `samples/sample_resume_en.txt` (converted to PDF)
- [ ] **Job Matching**: Use `samples/sample_job.txt` for comparison
- [ ] **Video Generation**: Test both basic and advanced video options
- [ ] **Download**: Verify all download functions work correctly

### 60-Second Pitch Script

"Our AI Resume Analyzer transforms the hiring process with three key innovations:

1. **Smart Analysis** - Upload any resume format, get instant AI-powered insights with strengths, weaknesses, and actionable suggestions in English or Romanian.

2. **Job Matching** - Compare resumes against job descriptions with compatibility scoring, skill gap analysis, and tailored optimization advice.

3. **Video Pitches** - Generate professional 10-second video presentations using advanced AI, perfect for modern recruitment workflows.

Built with enterprise-grade APIs including OpenAI GPT, Gemini Veo 3, and Supabase, it's ready for production deployment while maintaining hackathon-speed development."

### Demonstration Flow

1. **Show Problem** (10 seconds): "Manual resume screening takes hours"
2. **Upload Demo** (15 seconds): Upload sample resume, show instant text extraction
3. **AI Analysis** (15 seconds): Display structured analysis results
4. **Job Matching** (10 seconds): Show compatibility score and missing skills
5. **Video Generation** (10 seconds): Generate and play video pitch

## 🚨 Troubleshooting

### Common Issues

#### "OpenAI API Error"
- **Check API Key**: Verify `OPENAI_API_KEY` in `.env` file
- **Billing Setup**: Ensure OpenAI account has billing information
- **Rate Limits**: Wait a few minutes if hitting rate limits
- **Network**: Check internet connection and firewall settings

#### "Supabase Connection Failed"
- **Check Credentials**: Verify `SUPABASE_URL` and `SUPABASE_KEY`
- **Database Setup**: Run `python setup_database.py`
- **Network**: Ensure Supabase project is accessible
- **Permissions**: Check if API key has required permissions

#### "Text Extraction Failed"
- **File Format**: Ensure file is valid PDF or DOCX
- **File Size**: Check if file is under 200MB limit
- **Corruption**: Try with a different file
- **OCR Fallback**: Configure Nutrient API for complex documents

#### "Video Generation Error"
- **Dependencies**: Ensure moviepy and edge-tts are installed
- **Disk Space**: Check available storage for video files
- **Audio Issues**: Verify edge-tts can access system audio
- **Gemini API**: Check Google AI Studio API key if using advanced features

#### "Job Matching Issues"
- **Low Compatibility Score**: Ensure job description includes detailed requirements and skills
- **Missing Skills Not Detected**: Check if job description contains clear skill requirements
- **Optimization Advice Generic**: Add more specific job responsibilities and requirements
- **Job Analysis Failed**: Verify job description is in English or Romanian
- **Database Storage Error**: Check Supabase connection and run `python setup_database.py`

#### "Streamlit Issues"
- **Port Conflict**: Try different port with `streamlit run app.py --server.port 8502`
- **Browser Cache**: Clear browser cache and cookies
- **Python Version**: Ensure Python 3.8+ is being used
- **Dependencies**: Reinstall requirements with `pip install -r requirements.txt --force-reinstall`

### Performance Optimization

- **API Caching**: Results are cached to reduce API calls
- **Async Processing**: Long operations show progress indicators
- **File Cleanup**: Temporary files are automatically cleaned up
- **Memory Management**: Large files are processed in chunks

### Getting Help

1. **Check Logs**: Look at Streamlit console output for detailed error messages
2. **Test Components**: Use individual demo scripts to isolate issues
3. **Sample Data**: Test with provided sample files first
4. **API Status**: Check status pages for OpenAI, Supabase, and other services

## 🤝 Contributing

This project welcomes contributions! Areas for improvement:

### High Priority
- **New File Formats**: Add support for RTF, TXT, or image files
- **Language Support**: Extend beyond English and Romanian
- **Video Templates**: Create industry-specific video styles
- **Mobile Optimization**: Improve mobile browser experience

### Medium Priority
- **Batch Processing**: Handle multiple resumes simultaneously
- **Export Formats**: Add PDF, Word, or Excel export options
- **Integration APIs**: Connect with ATS systems or job boards
- **Analytics Dashboard**: Add usage statistics and insights

### Low Priority
- **UI Themes**: Add dark mode and custom branding
- **Voice Options**: Expand TTS voice selection
- **Collaboration**: Add team features and sharing capabilities

## 📄 License

This project is open source and available under the MIT License.

---

**Built for Hackathons** 🏆 | **Production Ready** 🚀 | **AI Powered** 🤖