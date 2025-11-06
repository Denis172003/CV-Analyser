# Requirements Document

## Introduction

The AI-Powered Resume Analyzer is a web application designed for hackathon teams to quickly analyze resumes and generate personalized video pitches. The system extracts text from uploaded resumes, provides AI-powered analysis including strengths and weaknesses, and creates a 10-second auto-generated video pitch. The application supports both English and Romanian languages and includes job description comparison functionality.

## Glossary

- **Resume_Analyzer_System**: The complete web application including UI, backend processing, and video generation components
- **Text_Extraction_Module**: Component responsible for extracting text from PDF and DOCX files
- **AI_Analysis_Engine**: OpenAI GPT-powered component that analyzes resume content and generates structured feedback
- **Video_Generation_Module**: Component that creates animated video pitches using text-to-speech and moviepy
- **Nutrient_OCR_Service**: External OCR service used as fallback for complex or scanned documents
- **Streamlit_UI**: Web-based user interface for file uploads and result display
- **Pitch_Video**: 10-second MP4 video containing animated text and synthesized audio

## Requirements

### Requirement 1

**User Story:** As a hackathon participant, I want to upload resume files in multiple formats, so that I can analyze any resume regardless of its original format.

#### Acceptance Criteria

1. WHEN a user uploads a PDF file, THE Resume_Analyzer_System SHALL extract text using pdfplumber library
2. WHEN a user uploads a DOCX file, THE Resume_Analyzer_System SHALL extract text using python-docx library
3. IF the extracted text appears messy or multi-column, THEN THE Resume_Analyzer_System SHALL use Nutrient_OCR_Service as fallback
4. THE Resume_Analyzer_System SHALL support file uploads through the Streamlit_UI interface
5. THE Resume_Analyzer_System SHALL display the extracted text to the user for verification

### Requirement 2

**User Story:** As a recruiter, I want to receive structured AI analysis of resumes, so that I can quickly identify candidate strengths and areas for improvement.

#### Acceptance Criteria

1. WHEN resume text is extracted, THE AI_Analysis_Engine SHALL call OpenAI GPT API with structured prompt
2. THE AI_Analysis_Engine SHALL return JSON containing strengths, weak_points, suggestions, top_skills, and one_sentence_pitch
3. THE Resume_Analyzer_System SHALL display analysis results as formatted bullets in the Streamlit_UI
4. THE AI_Analysis_Engine SHALL automatically detect resume language and respond in English or Romanian
5. THE AI_Analysis_Engine SHALL include retry logic for failed API calls with maximum 2 attempts

### Requirement 3

**User Story:** As a job seeker, I want to generate a personalized video pitch from my resume, so that I can create engaging presentations for potential employers.

#### Acceptance Criteria

1. WHEN user clicks Generate Pitch button, THE Video_Generation_Module SHALL create synthesized audio using edge-tts
2. THE Video_Generation_Module SHALL generate animated text slides using moviepy library
3. THE Video_Generation_Module SHALL combine audio and visual elements into 10-second MP4 file
4. THE Pitch_Video SHALL be playable inline within the Streamlit_UI
5. THE Video_Generation_Module SHALL distribute timing across script parts with proper synchronization

### Requirement 4

**User Story:** As a hiring manager, I want to compare resumes against job descriptions, so that I can identify skill gaps and candidate fit.

#### Acceptance Criteria

1. WHEN job description is provided, THE Resume_Analyzer_System SHALL accept job description text input
2. THE AI_Analysis_Engine SHALL perform keyword-overlap analysis between resume and job description
3. THE Resume_Analyzer_System SHALL display skill gap analysis and missing skills list
4. THE Resume_Analyzer_System SHALL calculate and display compatibility score
5. WHERE job description is not provided, THE Resume_Analyzer_System SHALL skip comparison functionality

### Requirement 5

**User Story:** As a user, I want to download analysis results and suggestions, so that I can save and reference the feedback later.

#### Acceptance Criteria

1. THE Resume_Analyzer_System SHALL provide download button for suggestions as text file
2. THE Resume_Analyzer_System SHALL provide download button for generated Pitch_Video
3. THE Resume_Analyzer_System SHALL allow users to save analysis results locally
4. WHERE SQLite persistence is implemented, THE Resume_Analyzer_System SHALL store analysis history
5. THE Resume_Analyzer_System SHALL display analysis history in optional history panel

### Requirement 6

**User Story:** As a developer, I want clear setup instructions and sample data, so that I can quickly run and test the application.

#### Acceptance Criteria

1. THE Resume_Analyzer_System SHALL include requirements.txt with all necessary dependencies
2. THE Resume_Analyzer_System SHALL include README.md with step-by-step setup instructions
3. THE Resume_Analyzer_System SHALL provide sample resumes in English and Romanian
4. THE Resume_Analyzer_System SHALL include sample job description for testing
5. THE Resume_Analyzer_System SHALL include unit tests for core parsing and AI integration functions

### Requirement 7

**User Story:** As a student, I want to input job descriptions and get specific advice on how to tailor my CV, so that I can optimize my application for each position.

#### Acceptance Criteria

1. THE Resume_Analyzer_System SHALL accept job description text input from users
2. THE AI_Analysis_Engine SHALL analyze job descriptions to extract required skills, responsibilities, and company culture
3. THE Resume_Analyzer_System SHALL compare CV content against job requirements and calculate compatibility scores
4. THE Resume_Analyzer_System SHALL generate specific optimization advice including missing skills and keyword recommendations
5. THE Resume_Analyzer_System SHALL store job descriptions and matching results in Supabase_Database for future reference

### Requirement 8

**User Story:** As a student preparing for interviews, I want job-specific video content that helps me practice presenting my strengths for particular positions, so that I can increase my interview success rate.

#### Acceptance Criteria

1. THE Video_Generation_Module SHALL create job-tailored interview preparation videos when job descriptions are provided
2. THE Resume_Analyzer_System SHALL prioritize job-relevant skills and experience in video content
3. THE Video_Generation_Module SHALL incorporate CV optimization advice into video scripts
4. THE Resume_Analyzer_System SHALL provide job-specific interview tips and talking points
5. THE Video_Generation_Module SHALL select appropriate visual styles based on job industry and company culture

### Requirement 9

**User Story:** As a hackathon team member, I want modular code structure, so that multiple developers can work on different components simultaneously.

#### Acceptance Criteria

1. THE Resume_Analyzer_System SHALL separate functionality into distinct modules: parsing.py, ai_integration.py, tts_video.py, database.py, gemini_video.py
2. THE Resume_Analyzer_System SHALL implement clear function interfaces with proper docstrings
3. THE Resume_Analyzer_System SHALL include error handling and user-friendly error messages
4. THE Resume_Analyzer_System SHALL use environment variables for API key configuration
5. THE Resume_Analyzer_System SHALL maintain relative file paths for cross-environment compatibility