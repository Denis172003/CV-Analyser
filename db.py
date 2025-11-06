"""
SQLite database module for local persistence of CV analysis history.

This module provides an optional local database layer for storing
analysis results when Supabase is not available or desired.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = "cv_analyzer.db"


class CVDatabase:
    """SQLite database manager for CV analysis history."""
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """
        Initialize database connection and create tables if needed.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """
        Initialize database schema and create tables with indexes.
        
        Creates tables for storing analysis history with timestamps
        and implements database initialization and migration functions.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create cv_records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cv_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        original_text TEXT NOT NULL,
                        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type TEXT NOT NULL,
                        file_size INTEGER,
                        language TEXT DEFAULT 'en',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create analysis_results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cv_id INTEGER NOT NULL,
                        strengths TEXT NOT NULL,  -- JSON array
                        weak_points TEXT NOT NULL,  -- JSON array
                        suggestions TEXT NOT NULL,  -- JSON array
                        top_skills TEXT NOT NULL,  -- JSON array
                        one_sentence_pitch TEXT NOT NULL,
                        compatibility_score INTEGER,
                        missing_skills TEXT,  -- JSON array
                        matching_skills TEXT,  -- JSON array
                        analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (cv_id) REFERENCES cv_records (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create job_descriptions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS job_descriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_title TEXT NOT NULL,
                        company_name TEXT,
                        job_text TEXT NOT NULL,
                        required_skills TEXT,  -- JSON array
                        preferred_skills TEXT,  -- JSON array
                        experience_level TEXT DEFAULT 'mid',
                        industry_keywords TEXT,  -- JSON array
                        department TEXT,
                        employment_type TEXT DEFAULT 'full-time',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create video_records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS video_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cv_id INTEGER NOT NULL,
                        video_path TEXT,
                        generation_method TEXT NOT NULL DEFAULT 'moviepy',
                        script_data TEXT NOT NULL,  -- JSON
                        style_preferences TEXT,  -- JSON
                        status TEXT DEFAULT 'pending',
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (cv_id) REFERENCES cv_records (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create indexes for efficient querying of analysis history
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cv_records_created_at ON cv_records(created_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cv_records_filename ON cv_records(filename)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cv_records_language ON cv_records(language)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_results_cv_id ON analysis_results(cv_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_results_analyzed_at ON analysis_results(analyzed_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_descriptions_created_at ON job_descriptions(created_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_descriptions_company ON job_descriptions(company_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_records_cv_id ON video_records(cv_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_records_status ON video_records(status)')
                
                # Create full-text search virtual table for CV content
                cursor.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS cv_search 
                    USING fts5(id, filename, original_text, content='cv_records', content_rowid='id')
                ''')
                
                # Create triggers to keep FTS table in sync
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS cv_search_insert AFTER INSERT ON cv_records BEGIN
                        INSERT INTO cv_search(rowid, filename, original_text) 
                        VALUES (new.id, new.filename, new.original_text);
                    END
                ''')
                
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS cv_search_delete AFTER DELETE ON cv_records BEGIN
                        INSERT INTO cv_search(cv_search, rowid, filename, original_text) 
                        VALUES('delete', old.id, old.filename, old.original_text);
                    END
                ''')
                
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS cv_search_update AFTER UPDATE ON cv_records BEGIN
                        INSERT INTO cv_search(cv_search, rowid, filename, original_text) 
                        VALUES('delete', old.id, old.filename, old.original_text);
                        INSERT INTO cv_search(rowid, filename, original_text) 
                        VALUES (new.id, new.filename, new.original_text);
                    END
                ''')
                
                conn.commit()
                logger.info(f"Database initialized successfully at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise Exception(f"Database initialization failed: {str(e)}")
    
    def migrate_database(self) -> None:
        """
        Perform database migrations for schema updates.
        
        This function handles database schema migrations when
        the application is updated with new table structures.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check current schema version
                cursor.execute("PRAGMA user_version")
                current_version = cursor.fetchone()[0]
                
                # Migration to version 1: Add job_id column to analysis_results
                if current_version < 1:
                    try:
                        cursor.execute('ALTER TABLE analysis_results ADD COLUMN job_id INTEGER')
                        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_results_job_id ON analysis_results(job_id)')
                        logger.info("Migrated to schema version 1: Added job_id column")
                    except sqlite3.OperationalError:
                        # Column might already exist
                        pass
                
                # Migration to version 2: Add optimization_advice column
                if current_version < 2:
                    try:
                        cursor.execute('ALTER TABLE analysis_results ADD COLUMN optimization_advice TEXT')
                        logger.info("Migrated to schema version 2: Added optimization_advice column")
                    except sqlite3.OperationalError:
                        # Column might already exist
                        pass
                
                # Update schema version
                if current_version < 2:
                    cursor.execute("PRAGMA user_version = 2")
                    conn.commit()
                    logger.info("Database migration completed")
                
        except sqlite3.Error as e:
            logger.error(f"Database migration failed: {str(e)}")
            raise Exception(f"Migration failed: {str(e)}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection with row factory for dict-like access.
        
        Returns:
            SQLite connection with row factory
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def close(self) -> None:
        """Close database connection and cleanup resources."""
        # SQLite connections are closed automatically when using context managers
        # This method is provided for compatibility
        pass


# Global database instance
_db_instance: Optional[CVDatabase] = None


def get_database(db_path: str = DEFAULT_DB_PATH) -> CVDatabase:
    """
    Get or create global database instance.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        CVDatabase instance
    """
    global _db_instance
    
    if _db_instance is None or _db_instance.db_path != db_path:
        _db_instance = CVDatabase(db_path)
    
    return _db_instance


def init_database(db_path: str = DEFAULT_DB_PATH) -> CVDatabase:
    """
    Initialize database with schema and return instance.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Initialized CVDatabase instance
    """
    db = get_database(db_path)
    db.migrate_database()  # Run any pending migrations
    return db

def store_cv_analysis(
    resume_text: str,
    analysis_data: Dict,
    metadata: Dict,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Store CV analysis results with metadata in SQLite database.
    
    Args:
        resume_text: Extracted text from the resume
        analysis_data: Analysis results from AI processing
        metadata: File metadata (filename, size, type, etc.)
        db_path: Path to SQLite database file
        
    Returns:
        CV record ID
        
    Raises:
        Exception: If database operation fails
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Store CV record
            cursor.execute('''
                INSERT INTO cv_records (filename, original_text, file_type, file_size, language)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                metadata.get('filename', 'unknown.pdf'),
                resume_text,
                metadata.get('file_type', 'pdf'),
                metadata.get('file_size', 0),
                metadata.get('language', 'en')
            ))
            
            cv_id = cursor.lastrowid
            
            # Store analysis results
            cursor.execute('''
                INSERT INTO analysis_results (
                    cv_id, strengths, weak_points, suggestions, top_skills,
                    one_sentence_pitch, compatibility_score, missing_skills, matching_skills
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cv_id,
                json.dumps(analysis_data.get('strengths', [])),
                json.dumps(analysis_data.get('weak_points', [])),
                json.dumps(analysis_data.get('suggestions', [])),
                json.dumps(analysis_data.get('top_skills', [])),
                analysis_data.get('one_sentence_pitch', ''),
                analysis_data.get('compatibility_score'),
                json.dumps(analysis_data.get('missing_skills', [])),
                json.dumps(analysis_data.get('matching_skills', []))
            ))
            
            conn.commit()
            logger.info(f"Successfully stored CV analysis with ID: {cv_id}")
            return cv_id
            
    except sqlite3.Error as e:
        logger.error(f"Failed to store CV analysis: {str(e)}")
        raise Exception(f"Database storage failed: {str(e)}")


def get_analysis_history(limit: int = 50, db_path: str = DEFAULT_DB_PATH) -> List[Dict]:
    """
    Retrieve analysis history with timestamps and metadata.
    
    Args:
        limit: Maximum number of records to return
        db_path: Path to SQLite database file
        
    Returns:
        List of CV records with analysis data
        
    Raises:
        Exception: If database query fails
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    cv.id, cv.filename, cv.original_text, cv.file_type, cv.file_size,
                    cv.language, cv.created_at, cv.updated_at,
                    ar.strengths, ar.weak_points, ar.suggestions, ar.top_skills,
                    ar.one_sentence_pitch, ar.compatibility_score, ar.missing_skills,
                    ar.matching_skills, ar.analyzed_at
                FROM cv_records cv
                LEFT JOIN analysis_results ar ON cv.id = ar.cv_id
                ORDER BY cv.created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                record = {
                    'id': row['id'],
                    'filename': row['filename'],
                    'original_text': row['original_text'],
                    'file_type': row['file_type'],
                    'file_size': row['file_size'],
                    'language': row['language'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                
                # Add analysis results if available
                if row['strengths']:
                    record['analysis'] = {
                        'strengths': json.loads(row['strengths']),
                        'weak_points': json.loads(row['weak_points']),
                        'suggestions': json.loads(row['suggestions']),
                        'top_skills': json.loads(row['top_skills']),
                        'one_sentence_pitch': row['one_sentence_pitch'],
                        'compatibility_score': row['compatibility_score'],
                        'missing_skills': json.loads(row['missing_skills'] or '[]'),
                        'matching_skills': json.loads(row['matching_skills'] or '[]'),
                        'analyzed_at': row['analyzed_at']
                    }
                
                results.append(record)
            
            logger.info(f"Retrieved {len(results)} analysis records")
            return results
            
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve analysis history: {str(e)}")
        raise Exception(f"Database query failed: {str(e)}")


def search_analysis_history(
    query: str,
    filters: Optional[Dict] = None,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict]:
    """
    Search analysis history using full-text search and optional filters.
    
    Args:
        query: Search query string
        filters: Optional filters (language, date range, etc.)
        db_path: Path to SQLite database file
        
    Returns:
        List of matching CV records
        
    Raises:
        Exception: If search operation fails
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build search query with FTS
            search_sql = '''
                SELECT 
                    cv.id, cv.filename, cv.original_text, cv.file_type, cv.file_size,
                    cv.language, cv.created_at, cv.updated_at,
                    ar.strengths, ar.weak_points, ar.suggestions, ar.top_skills,
                    ar.one_sentence_pitch, ar.compatibility_score, ar.missing_skills,
                    ar.matching_skills, ar.analyzed_at
                FROM cv_search
                JOIN cv_records cv ON cv_search.rowid = cv.id
                LEFT JOIN analysis_results ar ON cv.id = ar.cv_id
                WHERE cv_search MATCH ?
            '''
            
            params = [query]
            
            # Add filters
            if filters:
                if 'language' in filters:
                    search_sql += ' AND cv.language = ?'
                    params.append(filters['language'])
                
                if 'date_from' in filters:
                    search_sql += ' AND cv.created_at >= ?'
                    params.append(filters['date_from'])
                
                if 'date_to' in filters:
                    search_sql += ' AND cv.created_at <= ?'
                    params.append(filters['date_to'])
            
            search_sql += ' ORDER BY cv.created_at DESC'
            
            cursor.execute(search_sql, params)
            
            results = []
            for row in cursor.fetchall():
                record = {
                    'id': row['id'],
                    'filename': row['filename'],
                    'original_text': row['original_text'],
                    'file_type': row['file_type'],
                    'file_size': row['file_size'],
                    'language': row['language'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                
                # Add analysis results if available
                if row['strengths']:
                    record['analysis'] = {
                        'strengths': json.loads(row['strengths']),
                        'weak_points': json.loads(row['weak_points']),
                        'suggestions': json.loads(row['suggestions']),
                        'top_skills': json.loads(row['top_skills']),
                        'one_sentence_pitch': row['one_sentence_pitch'],
                        'compatibility_score': row['compatibility_score'],
                        'missing_skills': json.loads(row['missing_skills'] or '[]'),
                        'matching_skills': json.loads(row['matching_skills'] or '[]'),
                        'analyzed_at': row['analyzed_at']
                    }
                
                results.append(record)
            
            logger.info(f"Search returned {len(results)} results for query: {query}")
            return results
            
    except sqlite3.Error as e:
        logger.error(f"Failed to search analysis history: {str(e)}")
        raise Exception(f"Search operation failed: {str(e)}")


def get_cv_by_id(cv_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict]:
    """
    Retrieve a specific CV record by ID with analysis data.
    
    Args:
        cv_id: CV record ID
        db_path: Path to SQLite database file
        
    Returns:
        CV record with analysis data or None if not found
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    cv.id, cv.filename, cv.original_text, cv.file_type, cv.file_size,
                    cv.language, cv.created_at, cv.updated_at,
                    ar.strengths, ar.weak_points, ar.suggestions, ar.top_skills,
                    ar.one_sentence_pitch, ar.compatibility_score, ar.missing_skills,
                    ar.matching_skills, ar.analyzed_at
                FROM cv_records cv
                LEFT JOIN analysis_results ar ON cv.id = ar.cv_id
                WHERE cv.id = ?
            ''', (cv_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            record = {
                'id': row['id'],
                'filename': row['filename'],
                'original_text': row['original_text'],
                'file_type': row['file_type'],
                'file_size': row['file_size'],
                'language': row['language'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            
            # Add analysis results if available
            if row['strengths']:
                record['analysis'] = {
                    'strengths': json.loads(row['strengths']),
                    'weak_points': json.loads(row['weak_points']),
                    'suggestions': json.loads(row['suggestions']),
                    'top_skills': json.loads(row['top_skills']),
                    'one_sentence_pitch': row['one_sentence_pitch'],
                    'compatibility_score': row['compatibility_score'],
                    'missing_skills': json.loads(row['missing_skills'] or '[]'),
                    'matching_skills': json.loads(row['matching_skills'] or '[]'),
                    'analyzed_at': row['analyzed_at']
                }
            
            return record
            
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve CV by ID: {str(e)}")
        return None


def update_cv_record(cv_id: int, updates: Dict, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Update a CV record with new data.
    
    Args:
        cv_id: CV record ID to update
        updates: Dictionary of fields to update
        db_path: Path to SQLite database file
        
    Returns:
        True if update successful, False otherwise
        
    Raises:
        Exception: If update operation fails
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for field, value in updates.items():
                if field in ['filename', 'original_text', 'file_type', 'file_size', 'language']:
                    set_clauses.append(f'{field} = ?')
                    params.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            # Add updated_at timestamp
            set_clauses.append('updated_at = CURRENT_TIMESTAMP')
            params.append(cv_id)
            
            update_sql = f'''
                UPDATE cv_records 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            '''
            
            cursor.execute(update_sql, params)
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Successfully updated CV record: {cv_id}")
                return True
            else:
                logger.warning(f"No CV record found with ID: {cv_id}")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Failed to update CV record: {str(e)}")
        raise Exception(f"Update operation failed: {str(e)}")


def delete_cv_record(cv_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Delete a CV record and all associated analysis data.
    
    Args:
        cv_id: CV record ID to delete
        db_path: Path to SQLite database file
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete CV record (cascades to analysis_results and video_records)
            cursor.execute('DELETE FROM cv_records WHERE id = ?', (cv_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Successfully deleted CV record: {cv_id}")
                return True
            else:
                logger.warning(f"No CV record found with ID: {cv_id}")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Failed to delete CV record: {str(e)}")
        return False


def cleanup_old_records(days_old: int = 30, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Clean up old CV records and analysis data for maintenance.
    
    Args:
        days_old: Delete records older than this many days
        db_path: Path to SQLite database file
        
    Returns:
        Number of records deleted
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete old records
            cursor.execute('''
                DELETE FROM cv_records 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days_old))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} old CV records")
            return deleted_count
            
    except sqlite3.Error as e:
        logger.error(f"Failed to cleanup old records: {str(e)}")
        return 0


def get_database_stats(db_path: str = DEFAULT_DB_PATH) -> Dict:
    """
    Get database statistics for monitoring and maintenance.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Dictionary with database statistics
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get record counts
            cursor.execute('SELECT COUNT(*) FROM cv_records')
            cv_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM analysis_results')
            analysis_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM video_records')
            video_count = cursor.fetchone()[0]
            
            # Get database file size
            db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            
            # Get oldest and newest records
            cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM cv_records')
            date_range = cursor.fetchone()
            
            stats = {
                'cv_records': cv_count,
                'analysis_results': analysis_count,
                'video_records': video_count,
                'database_size_bytes': db_size,
                'oldest_record': date_range[0],
                'newest_record': date_range[1]
            }
            
            return stats
            
    except sqlite3.Error as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        return {}


def store_video_record(
    cv_id: int,
    script_data: Dict,
    video_path: str,
    generation_method: str = 'moviepy',
    style_preferences: Optional[Dict] = None,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Store video generation record in database.
    
    Args:
        cv_id: Associated CV record ID
        script_data: Video script and timing data
        video_path: Path to generated video file
        generation_method: 'gemini' or 'moviepy'
        style_preferences: Optional video style settings
        db_path: Path to SQLite database file
        
    Returns:
        Video record ID
    """
    try:
        db = get_database(db_path)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO video_records (
                    cv_id, video_path, generation_method, script_data, 
                    style_preferences, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                cv_id,
                video_path,
                generation_method,
                json.dumps(script_data),
                json.dumps(style_preferences or {}),
                'completed'
            ))
            
            video_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Successfully stored video record with ID: {video_id}")
            return video_id
            
    except sqlite3.Error as e:
        logger.error(f"Failed to store video record: {str(e)}")
        raise Exception(f"Video record storage failed: {str(e)}")