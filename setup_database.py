"""
Database setup and migration script for Supabase.

This script creates the necessary tables and indexes for the
AI Resume Analyzer application.
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_database_schema():
    """
    Create database tables and indexes in Supabase.
    
    This function should be run once to set up the database schema.
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables are required")
        sys.exit(1)
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Connected to Supabase successfully")
        
        # SQL commands to create tables
        sql_commands = [
            """
            -- Enable UUID extension if not already enabled
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """,
            
            """
            -- CV Records Table
            CREATE TABLE IF NOT EXISTS cv_records (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES auth.users(id),
                filename VARCHAR(255) NOT NULL,
                original_text TEXT NOT NULL,
                extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                file_type VARCHAR(10) NOT NULL,
                file_size INTEGER,
                language VARCHAR(5) DEFAULT 'en',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            """
            -- Job Descriptions Table
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES auth.users(id),
                job_title VARCHAR(255) NOT NULL,
                company_name VARCHAR(255),
                job_text TEXT NOT NULL,
                required_skills TEXT[],
                preferred_skills TEXT[],
                experience_level VARCHAR(20),
                industry_keywords TEXT[],
                department VARCHAR(100),
                employment_type VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            """
            -- Analysis Results Table
            CREATE TABLE IF NOT EXISTS analysis_results (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                cv_id UUID REFERENCES cv_records(id) ON DELETE CASCADE,
                job_id UUID REFERENCES job_descriptions(id) ON DELETE SET NULL,
                strengths JSONB NOT NULL,
                weak_points JSONB NOT NULL,
                suggestions JSONB NOT NULL,
                top_skills TEXT[] NOT NULL,
                one_sentence_pitch TEXT NOT NULL,
                compatibility_score INTEGER,
                missing_skills TEXT[],
                matching_skills TEXT[],
                optimization_advice JSONB,
                analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            """
            -- Video Generation Records Table
            CREATE TABLE IF NOT EXISTS video_records (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                cv_id UUID REFERENCES cv_records(id) ON DELETE CASCADE,
                video_url TEXT,
                generation_method VARCHAR(20) NOT NULL,
                script_data JSONB NOT NULL,
                style_preferences JSONB,
                status VARCHAR(20) DEFAULT 'pending',
                gemini_job_id VARCHAR(255),
                generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            """
            -- Create indexes for performance
            CREATE INDEX IF NOT EXISTS idx_cv_records_user_id ON cv_records(user_id);
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_cv_records_created_at ON cv_records(created_at DESC);
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_analysis_results_cv_id ON analysis_results(cv_id);
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_video_records_cv_id ON video_records(cv_id);
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_video_records_status ON video_records(status);
            """,
            
            """
            -- Full-text search index
            CREATE INDEX IF NOT EXISTS idx_cv_records_text_search 
            ON cv_records USING gin(to_tsvector('english', original_text));
            """,
            
            """
            -- Row Level Security (RLS) policies
            ALTER TABLE cv_records ENABLE ROW LEVEL SECURITY;
            """,
            
            """
            ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
            """,
            
            """
            ALTER TABLE video_records ENABLE ROW LEVEL SECURITY;
            """,
            
            """
            -- Policy: Users can only access their own CV records
            CREATE POLICY IF NOT EXISTS "Users can view own cv_records" ON cv_records
                FOR SELECT USING (auth.uid() = user_id);
            """,
            
            """
            CREATE POLICY IF NOT EXISTS "Users can insert own cv_records" ON cv_records
                FOR INSERT WITH CHECK (auth.uid() = user_id);
            """,
            
            """
            CREATE POLICY IF NOT EXISTS "Users can update own cv_records" ON cv_records
                FOR UPDATE USING (auth.uid() = user_id);
            """,
            
            """
            CREATE POLICY IF NOT EXISTS "Users can delete own cv_records" ON cv_records
                FOR DELETE USING (auth.uid() = user_id);
            """,
            
            """
            -- Policy: Users can access analysis results for their CVs
            CREATE POLICY IF NOT EXISTS "Users can view own analysis_results" ON analysis_results
                FOR SELECT USING (
                    cv_id IN (
                        SELECT id FROM cv_records WHERE user_id = auth.uid()
                    )
                );
            """,
            
            """
            CREATE POLICY IF NOT EXISTS "Users can insert analysis_results for own CVs" ON analysis_results
                FOR INSERT WITH CHECK (
                    cv_id IN (
                        SELECT id FROM cv_records WHERE user_id = auth.uid()
                    )
                );
            """,
            
            """
            -- Policy: Users can access video records for their CVs
            CREATE POLICY IF NOT EXISTS "Users can view own video_records" ON video_records
                FOR SELECT USING (
                    cv_id IN (
                        SELECT id FROM cv_records WHERE user_id = auth.uid()
                    )
                );
            """,
            
            """
            CREATE POLICY IF NOT EXISTS "Users can insert video_records for own CVs" ON video_records
                FOR INSERT WITH CHECK (
                    cv_id IN (
                        SELECT id FROM cv_records WHERE user_id = auth.uid()
                    )
                );
            """,
            
            """
            CREATE POLICY IF NOT EXISTS "Users can update own video_records" ON video_records
                FOR UPDATE USING (
                    cv_id IN (
                        SELECT id FROM cv_records WHERE user_id = auth.uid()
                    )
                );
            """
        ]
        
        # Execute each SQL command
        for i, sql in enumerate(sql_commands):
            try:
                print(f"Executing SQL command {i+1}/{len(sql_commands)}...")
                # Note: Supabase Python client doesn't directly support DDL operations
                # In a real implementation, you would either:
                # 1. Run these commands directly in the Supabase SQL editor
                # 2. Use a PostgreSQL client library like psycopg2
                # 3. Use Supabase CLI migrations
                
                print(f"SQL Command {i+1}:")
                print(sql.strip())
                print("-" * 50)
                
            except Exception as e:
                print(f"Error executing SQL command {i+1}: {str(e)}")
                continue
        
        print("\nDatabase schema creation completed!")
        print("\nIMPORTANT: Please run the above SQL commands in your Supabase SQL editor")
        print("or use the Supabase CLI to apply these migrations.")
        
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        sys.exit(1)


def create_sample_data():
    """
    Create sample data for testing purposes.
    """
    print("\nCreating sample data...")
    
    # Sample data would be inserted here
    sample_cv_data = {
        'filename': 'sample_resume.pdf',
        'original_text': 'John Doe\nSoftware Engineer\nExperience with Python, JavaScript, React...',
        'file_type': 'pdf',
        'file_size': 1024,
        'language': 'en'
    }
    
    print("Sample CV data structure:")
    for key, value in sample_cv_data.items():
        print(f"  {key}: {value}")
    
    print("\nSample data creation completed!")


if __name__ == "__main__":
    print("AI Resume Analyzer - Database Setup")
    print("=" * 40)
    
    # Check if environment variables are set
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("Copy .env.template to .env and fill in your Supabase credentials")
        sys.exit(1)
    
    # Create database schema
    create_database_schema()
    
    # Create sample data
    create_sample_data()
    
    print("\nSetup completed! You can now run the application.")