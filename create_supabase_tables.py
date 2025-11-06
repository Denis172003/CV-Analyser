#!/usr/bin/env python3
"""
Supabase Database Table Creation Script

This script creates all necessary tables for the AI Resume Analyzer
using direct PostgreSQL connection to Supabase.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_connection():
    """Get PostgreSQL connection to Supabase database."""
    
    # Try to get connection string first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    
    # Fallback to individual parameters
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_port = os.getenv('SUPABASE_DB_PORT', '5432')
    db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
    db_user = os.getenv('SUPABASE_DB_USER')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    if not all([db_host, db_user, db_password]):
        raise Exception(
            "Missing database connection parameters. Please set either:\n"
            "1. DATABASE_URL, or\n"
            "2. SUPABASE_DB_HOST, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD"
        )
    
    return psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )


def create_tables():
    """Create all necessary tables for the AI Resume Analyzer."""
    
    sql_commands = [
        # Enable UUID extension
        """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """,
        
        # CV Records Table
        """
        CREATE TABLE IF NOT EXISTS cv_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id TEXT,
            filename VARCHAR(255) NOT NULL,
            original_text TEXT NOT NULL,
            file_type VARCHAR(10) NOT NULL,
            file_size INTEGER,
            language VARCHAR(5) DEFAULT 'en',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Job Descriptions Table
        """
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id TEXT,
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
        
        # Analysis Results Table
        """
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
            optimization_advice JSONB DEFAULT '{}',
            analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Video Records Table
        """
        CREATE TABLE IF NOT EXISTS video_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            cv_id UUID REFERENCES cv_records(id) ON DELETE CASCADE,
            video_url TEXT,
            generation_method VARCHAR(20) NOT NULL,
            script_data JSONB NOT NULL,
            style_preferences JSONB DEFAULT '{}',
            status VARCHAR(20) DEFAULT 'pending',
            gemini_job_id VARCHAR(255),
            generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create indexes for performance
        """
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
        CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON job_descriptions(user_id);
        """,
        
        # Full-text search index
        """
        CREATE INDEX IF NOT EXISTS idx_cv_records_text_search 
        ON cv_records USING gin(to_tsvector('english', original_text));
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_job_descriptions_text_search 
        ON job_descriptions USING gin(to_tsvector('english', job_text));
        """
    ]
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print("🔗 Connected to Supabase database successfully!")
        print(f"📊 Creating {len(sql_commands)} database objects...")
        
        for i, sql in enumerate(sql_commands, 1):
            try:
                print(f"   {i:2d}. Executing SQL command...")
                cursor.execute(sql)
                conn.commit()
                print(f"   ✅ Command {i} executed successfully")
            except Exception as e:
                print(f"   ❌ Error in command {i}: {str(e)}")
                conn.rollback()
                continue
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


def verify_tables():
    """Verify that all tables were created successfully."""
    
    verification_queries = [
        "SELECT COUNT(*) FROM cv_records;",
        "SELECT COUNT(*) FROM job_descriptions;", 
        "SELECT COUNT(*) FROM analysis_results;",
        "SELECT COUNT(*) FROM video_records;"
    ]
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print("\n🔍 Verifying table creation...")
        
        for query in verification_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                table_name = query.split('FROM ')[1].split(';')[0]
                print(f"   ✅ {table_name}: {count} records")
            except Exception as e:
                table_name = query.split('FROM ')[1].split(';')[0]
                print(f"   ❌ {table_name}: Error - {str(e)}")
        
        cursor.close()
        conn.close()
        
        print("✅ Table verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


def insert_sample_data():
    """Insert sample data for testing."""
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print("\n📝 Inserting sample data...")
        
        # Insert sample CV record
        cursor.execute("""
            INSERT INTO cv_records (filename, original_text, file_type, file_size, language)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            'sample_resume.pdf',
            'John Doe\nSoftware Engineer\n\nExperience:\n- 5 years Python development\n- React and Node.js expertise\n- Team leadership experience\n\nSkills:\nPython, JavaScript, React, Node.js, PostgreSQL, AWS',
            'pdf',
            2048,
            'en'
        ))
        
        cv_id = cursor.fetchone()[0]
        print(f"   ✅ Sample CV record created: {cv_id}")
        
        # Insert sample analysis result
        cursor.execute("""
            INSERT INTO analysis_results (
                cv_id, strengths, weak_points, suggestions, top_skills, one_sentence_pitch
            ) VALUES (%s, %s, %s, %s, %s, %s);
        """, (
            cv_id,
            '[{"text": "Strong technical skills", "evidence": "5 years Python development experience"}]',
            '[{"text": "Could add more metrics", "location": "Experience", "reason": "Lacks quantifiable achievements"}]',
            '[{"for": "Experience", "suggestion": "Add specific metrics and project outcomes"}]',
            ['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL'],
            'Hi, I am John Doe, a software engineer with 5 years of Python development experience.'
        ))
        
        print(f"   ✅ Sample analysis result created")
        
        # Insert sample job description
        cursor.execute("""
            INSERT INTO job_descriptions (
                job_title, company_name, job_text, required_skills, experience_level
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            'Senior Software Engineer',
            'Tech Corp',
            'We are looking for a Senior Software Engineer with Python and React experience...',
            ['Python', 'React', 'PostgreSQL'],
            'senior'
        ))
        
        job_id = cursor.fetchone()[0]
        print(f"   ✅ Sample job description created: {job_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Sample data inserted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Sample data insertion failed: {str(e)}")
        return False


def main():
    """Main function to set up the database."""
    
    print("🤖 AI RESUME ANALYZER - DATABASE SETUP")
    print("=" * 50)
    
    # Check environment variables
    if not any([
        os.getenv('DATABASE_URL'),
        all([os.getenv('SUPABASE_DB_HOST'), os.getenv('SUPABASE_DB_USER'), os.getenv('SUPABASE_DB_PASSWORD')])
    ]):
        print("❌ Missing database configuration!")
        print("\nPlease set either:")
        print("1. DATABASE_URL environment variable, or")
        print("2. SUPABASE_DB_HOST, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD")
        print("\nCheck your .env file configuration.")
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        print("❌ Failed to create tables")
        sys.exit(1)
    
    # Verify tables
    if not verify_tables():
        print("❌ Failed to verify tables")
        sys.exit(1)
    
    # Ask user if they want sample data
    try:
        response = input("\n❓ Do you want to insert sample data for testing? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            insert_sample_data()
    except KeyboardInterrupt:
        print("\n\n👋 Setup completed without sample data.")
    
    print("\n🎉 Database setup completed successfully!")
    print("You can now run the AI Resume Analyzer application.")


if __name__ == "__main__":
    main()