# Implementation Plan

- [x] 1. Set up project structure and core configuration
  - Create directory structure with parsing.py, ai_integration.py, tts_video.py, app.py modules
  - Set up requirements.txt with streamlit, openai, pdfplumber, python-docx, edge-tts, moviepy, requests
  - Create .env template file for OPENAI_API_KEY and NUTRIENT credentials
  - Initialize basic project structure following modular design
  - _Requirements: 6.1, 6.2, 7.1, 7.4_

- [-] 2. Implement text extraction functionality (parsing.py)
  - [x] 2.1 Create PDF text extraction using pdfplumber
    - Write extract_text_pdf function with error handling for corrupted files
    - Handle various PDF formats and encoding issues
    - Return clean text with proper whitespace handling
    - _Requirements: 1.1_

  - [x] 2.2 Create DOCX text extraction using python-docx
    - Write extract_text_docx function for Word documents
    - Extract text while preserving paragraph structure
    - Handle document format errors gracefully
    - _Requirements: 1.2_

  - [x] 2.3 Implement text quality assessment
    - Write needs_nutrient_ocr function to detect poor extraction quality
    - Check for multi-column layouts, excessive whitespace, and formatting artifacts
    - Use character density and readability metrics for assessment
    - _Requirements: 1.3_

  - [x] 2.4 Add Nutrient OCR fallback integration
    - Implement call_nutrient_ocr function with API integration
    - Handle multipart form data for file uploads to Nutrient service
    - Add error handling for API failures, rate limits, and network issues
    - _Requirements: 1.3_

  - [x] 2.5 Write unit tests for text extraction functions
    - Test PDF extraction with sample files of different formats
    - Test DOCX extraction with various document structures
    - Mock Nutrient API responses for testing fallback behavior
    - _Requirements: 6.5_

- [x] 3. Build AI analysis engine (ai_integration.py)
  - [x] 3.1 Implement GPT API integration with structured prompts
    - Write call_gpt_analysis function using OpenAI Chat Completions API
    - Create system prompt for structured JSON resume analysis
    - Implement JSON response parsing and validation with error handling
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Add language detection and multi-language support
    - Implement automatic language detection for English/Romanian text
    - Ensure GPT responses match detected resume language
    - Handle mixed-language content appropriately
    - _Requirements: 2.4_

  - [x] 3.3 Implement retry logic and error handling
    - Add exponential backoff for API failures with maximum 2 attempts
    - Handle rate limiting and network errors gracefully
    - Implement JSON extraction from malformed responses using regex
    - _Requirements: 2.5_

  - [x] 3.4 Create pitch script generation
    - Write generate_pitch_script function to format analysis data for video
    - Structure content into intro, skills, achievement, and closing segments
    - Calculate timing distribution for 10-second total duration
    - _Requirements: 3.1_

  - [x] 3.5 Add job description comparison functionality
    - Implement score_resume_vs_job function for skill gap analysis
    - Create keyword overlap scoring algorithm with weighted matching
    - Generate missing skills recommendations and compatibility scores
    - _Requirements: 4.2, 4.3, 4.4_

  - [x] 3.6 Write unit tests for AI integration functions
    - Mock OpenAI API calls for testing analysis functionality
    - Test JSON parsing with various response formats and edge cases
    - Validate skill comparison algorithms with known datasets
    - _Requirements: 6.5_

- [x] 4. Develop video generation system (tts_video.py)
  - [x] 4.1 Implement text-to-speech audio generation
    - Write synthesize_audio function using edge-tts library
    - Support English and Romanian voices with quality selection
    - Handle audio file output in WAV format for video composition
    - _Requirements: 3.2_

  - [x] 4.2 Create animated slide generation
    - Write create_animated_slides function using moviepy
    - Implement text animations with fade-in, slide, and fade-out effects
    - Time animations to match audio segments with proper synchronization
    - _Requirements: 3.3_

  - [x] 4.3 Build video composition system
    - Write make_video function to combine audio and visual elements
    - Ensure proper synchronization between audio duration and animations
    - Output H.264 encoded MP4 files for browser compatibility
    - _Requirements: 3.3, 3.4_

  - [x] 4.4 Add video timing and segment distribution
    - Implement timing distribution across intro, skills, achievement, closing
    - Ensure 10-second total duration with smooth transitions between segments
    - Handle variable content lengths with dynamic timing adjustment
    - _Requirements: 3.5_

  - [x] 4.5 Write tests for video generation functions
    - Test audio synthesis with sample text in multiple languages
    - Validate video composition and timing accuracy
    - Check output format compatibility and file integrity
    - _Requirements: 6.5_

- [x] 5. Build Streamlit user interface (app.py)
  - [x] 5.1 Create main application layout and file upload
    - Set up Streamlit app with sidebar for controls and main area for results
    - Implement file upload component supporting PDF and DOCX files
    - Add job description text input area with optional functionality
    - _Requirements: 1.4, 4.1_

  - [x] 5.2 Implement file processing workflow and progress tracking
    - Display extracted text in expandable/collapsible section for verification
    - Show processing progress indicators for text extraction and AI analysis
    - Handle file upload validation with clear error messages for unsupported formats
    - _Requirements: 1.5, 7.3_

  - [x] 5.3 Create analysis results display
    - Format and display AI analysis results with structured bullet points
    - Show strengths, weaknesses, and suggestions in organized sections
    - Implement skill gap analysis display when job description is provided
    - _Requirements: 2.3, 4.3_

  - [x] 5.4 Add video generation and playback functionality
    - Implement "Generate Pitch" button with progress tracking for video creation
    - Display generated video using Streamlit's native video player component
    - Show video generation status and handle errors with user-friendly messages
    - _Requirements: 3.4_

  - [x] 5.5 Implement download functionality
    - Add download buttons for analysis suggestions as formatted text file
    - Enable video download for generated pitch videos
    - Provide analysis results export in structured format
    - _Requirements: 5.1, 5.2_

  - [x] 5.6 Add user experience enhancements
    - Implement helpful progress messages during long-running operations
    - Add comprehensive error handling with user-friendly error messages
    - Create responsive layout that works on different screen sizes
    - _Requirements: 7.3_

- [x] 6. Create sample data and documentation
  - [x] 6.1 Prepare sample resume files for testing
    - Create sample_resume_en.pdf with realistic English resume content
    - Create sample_resume_ro.pdf with Romanian resume content
    - Add sample_resume_scanned.jpg for OCR testing scenarios
    - _Requirements: 6.3_

  - [x] 6.2 Write sample job description for testing
    - Create sample_job.txt with comprehensive job requirements and skills
    - Include technical and soft skills for testing comparison features
    - Structure content to test skill gap analysis functionality
    - _Requirements: 6.4_

  - [x] 6.3 Create comprehensive README documentation
    - Write step-by-step setup and installation instructions
    - Document API key configuration for OpenAI and Nutrient
    - Include usage examples, troubleshooting guide, and demo checklist
    - _Requirements: 6.2_

  - [x] 6.4 Add utility functions and helpers (utils.py)
    - Create text cleaning functions for resume preprocessing
    - Implement language detection utilities using text analysis
    - Add file path management helpers for cross-platform compatibility
    - _Requirements: 7.5_

- [x] 7. Implement optional persistence layer (db.py)
  - [x] 7.1 Create SQLite database schema
    - Design tables for storing analysis history with timestamps
    - Implement database initialization and migration functions
    - Create indexes for efficient querying of analysis history
    - _Requirements: 5.4_

  - [x] 7.2 Add database operations
    - Write functions to save analysis results with metadata
    - Implement history querying and retrieval functions
    - Add data cleanup and maintenance operations
    - _Requirements: 5.4_

  - [x] 7.3 Integrate history panel in UI
    - Add history display section to Streamlit interface
    - Enable loading and reviewing previous analyses
    - Implement history search and filtering functionality
    - _Requirements: 5.5_

- [x] 8. Implement job description matching and CV optimization (ai_integration.py enhancements)
  - [x] 8.1 Add job description analysis functionality
    - Implement analyze_job_description function to extract skills, requirements, and culture
    - Create structured JSON parsing for job requirements and responsibilities
    - Add language detection support for job descriptions in English/Romanian
    - _Requirements: 7.1, 7.2_

  - [x] 8.2 Implement CV-job matching engine
    - Create generate_cv_optimization_advice function for tailored recommendations
    - Implement skill gap analysis with compatibility scoring algorithm
    - Add missing skills identification with learning suggestions
    - _Requirements: 7.3, 7.4_

  - [x] 8.3 Add CV optimization recommendation system
    - Implement keyword optimization advice for ATS compatibility
    - Create section-specific improvement recommendations (Skills, Summary, Experience)
    - Add tailoring suggestions for job-specific CV customization
    - _Requirements: 7.4, 7.5_

  - [x] 8.4 Enhance existing functions for job integration
    - Update score_resume_vs_job function with improved matching algorithms
    - Add helper functions for critical skill identification and experience alignment
    - Implement interview preparation focus area generation
    - _Requirements: 7.3, 7.4_

- [x] 9. Enhance database schema for job matching (database.py & setup_database.py)
  - [x] 9.1 Add job descriptions table and relationships
    - Create job_descriptions table with skills, requirements, and metadata fields
    - Update analysis_results table to include job_id and optimization_advice
    - Add proper foreign key relationships and cascading deletes
    - _Requirements: 7.1, 7.5_

  - [x] 9.2 Implement job description storage and retrieval
    - Create store_job_description function for saving job postings with analysis
    - Implement get_job_descriptions function for retrieving saved jobs
    - Add search_job_descriptions function with full-text search capabilities
    - _Requirements: 7.2, 7.4_

  - [x] 9.3 Add CV-job matching database operations
    - Implement store_cv_analysis_with_job function for linking CVs to jobs
    - Create get_cv_job_matches function for retrieving job compatibility history
    - Add database indexes for efficient job matching queries
    - _Requirements: 7.2, 7.4_

  - [x] 9.4 Update database security for job data
    - Extend row-level security policies to cover job_descriptions table
    - Add user authentication checks for job data access
    - Implement data validation for job description fields
    - _Requirements: 7.5_

- [x] 10. Enhance video generation for job-specific content (gemini_video.py updates)
  - [x] 10.1 Add job-specific video generation functions
    - Implement create_job_specific_video function for position-tailored videos
    - Create _create_job_tailored_script function for job-focused content
    - Add _determine_job_style function for industry-appropriate styling
    - _Requirements: 8.1, 8.2_

  - [x] 10.2 Enhance interview preparation video creation
    - Update create_interview_prep_video to accept job analysis parameters
    - Modify _create_interview_script to prioritize job-relevant skills
    - Add job-specific talking points and interview tips generation
    - _Requirements: 8.3, 8.4_

  - [x] 10.3 Implement job-focused video optimization
    - Add skill prioritization based on job requirements matching
    - Implement dynamic style selection based on job industry and culture
    - Create optimization metadata extraction for video enhancement
    - _Requirements: 8.2, 8.5_

  - [x] 10.4 Add job matching integration to video workflow
    - Integrate CV optimization advice into video script generation
    - Add job compatibility scoring to video metadata
    - Implement key improvements highlighting in video content
    - _Requirements: 8.4, 8.5_

- [x] 11. Create comprehensive testing for job matching features
  - [x] 11.1 Write job description analysis tests
    - Test job requirement extraction with various job posting formats
    - Validate skill identification and experience level detection
    - Test company culture and responsibility analysis accuracy
    - _Requirements: 9.5_

  - [x] 11.2 Add CV-job matching algorithm tests
    - Test compatibility scoring with known CV-job pairs
    - Validate missing skills identification and prioritization
    - Test optimization advice generation with edge cases
    - _Requirements: 9.5_

  - [x] 11.3 Create job-specific video generation tests
    - Test job-tailored script generation with different industries
    - Validate style selection based on job analysis
    - Test integration of optimization advice into video content
    - _Requirements: 9.5_

  - [x] 11.4 Add database integration tests for job matching
    - Test job description storage and retrieval operations
    - Validate CV-job linking and compatibility tracking
    - Test search functionality and performance with large datasets
    - _Requirements: 9.5_

- [x] 12. Update Streamlit UI for job matching workflow (app.py enhancements)
  - [x] 12.1 Add job description input interface
    - Create job description text area with formatting options
    - Add company name and job title input fields
    - Implement job description validation and preprocessing
    - _Requirements: 7.1_

  - [x] 12.2 Implement job-CV matching results display
    - Create compatibility score visualization with progress bars
    - Add missing skills display with priority indicators
    - Implement optimization advice presentation with actionable items
    - _Requirements: 7.3, 7.4_

  - [x] 12.3 Add job-specific video generation interface
    - Create job-tailored video generation options
    - Add industry style selection based on job analysis
    - Implement job-specific interview tips display
    - _Requirements: 8.2, 8.4_

  - [x] 12.4 Implement job matching history and tracking
    - Add job matching history panel with saved analyses
    - Create progress tracking for CV improvements over time
    - Implement job application success rate monitoring
    - _Requirements: 7.4, 7.5_

- [x] 13. Create demonstration and documentation for job matching
  - [x] 13.1 Create job matching demonstration script
    - Write demo_job_matching.py with complete workflow examples
    - Include sample job descriptions and CV optimization scenarios
    - Add compatibility scoring and advice generation demonstrations
    - _Requirements: 9.2_

  - [x] 13.2 Write comprehensive job matching documentation
    - Create JOB_MATCHING_FEATURES.md with detailed feature descriptions
    - Document CV optimization workflow and best practices
    - Include technical implementation details and API references
    - _Requirements: 9.2_

  - [x] 13.3 Add job matching to main README
    - Update README.md with job matching setup instructions
    - Add job description input and optimization workflow documentation
    - Include troubleshooting guide for job matching features
    - _Requirements: 9.2_

  - [x] 13.4 Create sample job descriptions for testing
    - Add sample_jobs directory with various industry job postings
    - Include job descriptions for tech, business, creative, and academic roles
    - Create job-CV matching test scenarios with expected outcomes
    - _Requirements: 9.3_

- [x] 14. Add deployment and packaging scripts
  - [x] 14.1 Create run script for easy startup
    - Write run.sh script for one-command application launch
    - Include environment setup and dependency installation checks
    - Add error handling for missing dependencies or API keys
    - _Requirements: 9.2_

  - [x] 14.2 Add demo preparation utilities
    - Create demo script with sample spoken presentation lines
    - Prepare 60-second pitch script for hackathon judges
    - Include quick demo checklist and troubleshooting tips
    - _Requirements: 9.2_

  - [x] 14.3 Write integration tests
    - Test complete end-to-end workflow with sample resume data
    - Validate API integrations and file processing pipeline
    - Test error handling and edge cases across all modules
    - _Requirements: 9.5_