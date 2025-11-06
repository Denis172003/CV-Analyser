"""
Supabase database integration module for CV storage and management.

This module handles all database operations including CV storage,
analysis results persistence, and user data management.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import psycopg2
import psycopg2.extras
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database connection
_db_connection = None
_supabase_client = None


def get_database_connection():
    """
    Get PostgreSQL connection to Supabase database using session pooler.
    
    Returns:
        PostgreSQL connection object
        
    Raises:
        Exception: If database configuration is missing or connection fails
    """
    global _db_connection
    
    if _db_connection is None or _db_connection.closed:
        # Try to get connection string first
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            try:
                _db_connection = psycopg2.connect(database_url)
                logger.info("Database connected using DATABASE_URL")
                return _db_connection
            except Exception as e:
                logger.warning(f"DATABASE_URL connection failed: {str(e)}")
        
        # Fallback to individual parameters
        db_host = os.getenv('SUPABASE_DB_HOST')
        db_port = os.getenv('SUPABASE_DB_PORT', '5432')
        db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
        db_user = os.getenv('SUPABASE_DB_USER')
        db_password = os.getenv('SUPABASE_DB_PASSWORD')
        
        if not all([db_host, db_user, db_password]):
            raise Exception(
                "Missing database connection parameters. Please set:\n"
                "SUPABASE_DB_HOST, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD\n"
                "Or set DATABASE_URL with the full connection string"
            )
        
        try:
            _db_connection = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            logger.info(f"Database connected using session pooler (host: {db_host})")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise Exception(f"Database connection failed: {str(e)}")
    
    return _db_connection


def init_supabase_client():
    """
    Initialize and return Supabase client for compatibility.
    
    This function maintains compatibility with existing code that expects
    a Supabase client, but actually returns a wrapper around the PostgreSQL connection.
    
    Returns:
        Database connection wrapper that mimics Supabase client interface
        
    Raises:
        Exception: If database configuration is missing or connection fails
    """
    global _supabase_client
    
    if _supabase_client is None:
        # Create a wrapper class that mimics Supabase client interface
        class DatabaseClientWrapper:
            def __init__(self):
                self.connection = get_database_connection()
            
            def table(self, table_name):
                return DatabaseTableWrapper(table_name, self.connection)
        
        class DatabaseTableWrapper:
            def __init__(self, table_name, connection):
                self.table_name = table_name
                self.connection = connection
            
            def select(self, columns='*'):
                return DatabaseQueryWrapper(self.table_name, 'select', self.connection, columns)
            
            def insert(self, data):
                return DatabaseQueryWrapper(self.table_name, 'insert', self.connection, data)
            
            def update(self, data):
                return DatabaseQueryWrapper(self.table_name, 'update', self.connection, data)
            
            def delete(self):
                return DatabaseQueryWrapper(self.table_name, 'delete', self.connection)
        
        class DatabaseQueryWrapper:
            def __init__(self, table_name, operation, connection, data=None):
                self.table_name = table_name
                self.operation = operation
                self.connection = connection
                self.data = data
                self._filters = []
                self._limit = None
                self._order = None
                self._columns = data if operation == 'select' else '*'
            
            def eq(self, column, value):
                self._filters.append(f"{column} = %s")
                if not hasattr(self, '_filter_values'):
                    self._filter_values = []
                self._filter_values.append(value)
                return self
            
            def limit(self, count):
                self._limit = count
                return self
            
            def order(self, column, desc=False):
                self._order = f"{column} {'DESC' if desc else 'ASC'}"
                return self
            
            def execute(self):
                cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                try:
                    if self.operation == 'select':
                        query = f"SELECT {self._columns} FROM {self.table_name}"
                        params = []
                        
                        if self._filters:
                            query += " WHERE " + " AND ".join(self._filters)
                            params.extend(getattr(self, '_filter_values', []))
                        
                        if self._order:
                            query += f" ORDER BY {self._order}"
                        
                        if self._limit:
                            query += f" LIMIT {self._limit}"
                        
                        cursor.execute(query, params)
                        results = cursor.fetchall()
                        
                        # Convert to list of dicts for compatibility
                        data = [dict(row) for row in results]
                        
                    elif self.operation == 'insert':
                        if isinstance(self.data, list):
                            # Multiple inserts
                            data = []
                            for item in self.data:
                                columns = list(item.keys())
                                values = list(item.values())
                                placeholders = ', '.join(['%s'] * len(values))
                                query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
                                cursor.execute(query, values)
                                result = cursor.fetchone()
                                data.append(dict(result))
                        else:
                            # Single insert
                            columns = list(self.data.keys())
                            values = list(self.data.values())
                            placeholders = ', '.join(['%s'] * len(values))
                            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
                            cursor.execute(query, values)
                            result = cursor.fetchone()
                            data = [dict(result)]
                    
                    else:
                        data = []
                    
                    self.connection.commit()
                    
                    # Return mock response object
                    class MockResponse:
                        def __init__(self, data):
                            self.data = data
                    
                    return MockResponse(data)
                    
                except Exception as e:
                    self.connection.rollback()
                    raise e
                finally:
                    cursor.close()
        
        _supabase_client = DatabaseClientWrapper()
        logger.info("Database client wrapper initialized")
    
    return _supabase_client


def store_cv_analysis(
    resume_text: str,
    analysis_data: Dict,
    metadata: Dict,
    user_id: Optional[str] = None
) -> str:
    """
    Store CV data and analysis results in database.
    
    Args:
        resume_text: Extracted text from the resume
        analysis_data: Analysis results from AI processing
        metadata: File metadata (filename, size, type, etc.)
        user_id: Optional user ID for authenticated users
        
    Returns:
        CV record ID
        
    Raises:
        Exception: If database operation fails
    """
    try:
        conn = get_database_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Store CV record
        cursor.execute("""
            INSERT INTO cv_records (user_id, filename, original_text, file_type, file_size, language)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            user_id,
            metadata.get('filename', 'unknown.pdf'),
            resume_text,
            metadata.get('file_type', 'pdf'),
            metadata.get('file_size', 0),
            metadata.get('language', 'en')
        ))
        
        cv_result = cursor.fetchone()
        if not cv_result:
            raise Exception("Failed to store CV record")
        
        cv_id = cv_result['id']
        
        # Store analysis results
        cursor.execute("""
            INSERT INTO analysis_results (
                cv_id, strengths, weak_points, suggestions, top_skills, 
                one_sentence_pitch, compatibility_score, missing_skills, matching_skills
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            cv_id,
            json.dumps(analysis_data.get('strengths', [])),
            json.dumps(analysis_data.get('weak_points', [])),
            json.dumps(analysis_data.get('suggestions', [])),
            analysis_data.get('top_skills', []),
            analysis_data.get('one_sentence_pitch', ''),
            analysis_data.get('compatibility_score'),
            analysis_data.get('missing_skills', []),
            analysis_data.get('matching_skills', [])
        ))
        
        conn.commit()
        cursor.close()
        
        logger.info(f"Successfully stored CV analysis with ID: {cv_id}")
        return str(cv_id)
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        if 'cursor' in locals():
            cursor.close()
        logger.error(f"Failed to store CV analysis: {str(e)}")
        raise Exception(f"Database storage failed: {str(e)}")


def get_cv_history(user_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """
    Retrieve CV history for a user or all CVs if no user specified.
    
    Args:
        user_id: Optional user ID to filter results
        limit: Maximum number of records to return
        
    Returns:
        List of CV records with analysis data
        
    Raises:
        Exception: If database query fails
    """
    try:
        conn = get_database_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Build query with joins
        if user_id:
            cursor.execute("""
                SELECT 
                    cv.*, 
                    ar.strengths, ar.weak_points, ar.suggestions, ar.top_skills, 
                    ar.one_sentence_pitch, ar.compatibility_score, ar.analyzed_at,
                    COUNT(vr.id) as video_count
                FROM cv_records cv
                LEFT JOIN analysis_results ar ON cv.id = ar.cv_id
                LEFT JOIN video_records vr ON cv.id = vr.cv_id
                WHERE cv.user_id = %s
                GROUP BY cv.id, ar.id
                ORDER BY cv.created_at DESC
                LIMIT %s;
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT 
                    cv.*, 
                    ar.strengths, ar.weak_points, ar.suggestions, ar.top_skills, 
                    ar.one_sentence_pitch, ar.compatibility_score, ar.analyzed_at,
                    COUNT(vr.id) as video_count
                FROM cv_records cv
                LEFT JOIN analysis_results ar ON cv.id = ar.cv_id
                LEFT JOIN video_records vr ON cv.id = vr.cv_id
                GROUP BY cv.id, ar.id
                ORDER BY cv.created_at DESC
                LIMIT %s;
            """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        
        # Convert to list of dictionaries
        cv_records = []
        for row in results:
            record = dict(row)
            # Convert UUID to string for JSON serialization
            record['id'] = str(record['id'])
            cv_records.append(record)
        
        logger.info(f"Retrieved {len(cv_records)} CV records")
        return cv_records
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        logger.error(f"Failed to retrieve CV history: {str(e)}")
        raise Exception(f"Database query failed: {str(e)}")


def search_cvs(query: str, filters: Optional[Dict] = None, user_id: Optional[str] = None) -> List[Dict]:
    """
    Search CVs using full-text search and optional filters.
    
    Args:
        query: Search query string
        filters: Optional filters (language, date range, etc.)
        user_id: Optional user ID to filter results
        
    Returns:
        List of matching CV records
        
    Raises:
        Exception: If search operation fails
    """
    try:
        client = init_supabase_client()
        
        # Use PostgreSQL full-text search
        search_query = client.table('cv_records').select(
            '*, analysis_results(*)'
        ).text_search('original_text', query)
        
        if user_id:
            search_query = search_query.eq('user_id', user_id)
        
        if filters:
            if 'language' in filters:
                search_query = search_query.eq('language', filters['language'])
            
            if 'date_from' in filters:
                search_query = search_query.gte('created_at', filters['date_from'])
            
            if 'date_to' in filters:
                search_query = search_query.lte('created_at', filters['date_to'])
        
        result = search_query.execute()
        
        logger.info(f"Search returned {len(result.data)} results for query: {query}")
        return result.data
        
    except Exception as e:
        logger.error(f"Failed to search CVs: {str(e)}")
        raise Exception(f"Search operation failed: {str(e)}")


def update_cv_record(cv_id: str, updates: Dict) -> bool:
    """
    Update a CV record with new data.
    
    Args:
        cv_id: CV record ID to update
        updates: Dictionary of fields to update
        
    Returns:
        True if update successful, False otherwise
        
    Raises:
        Exception: If update operation fails
    """
    try:
        client = init_supabase_client()
        
        # Add updated_at timestamp
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        result = client.table('cv_records').update(updates).eq('id', cv_id).execute()
        
        if result.data:
            logger.info(f"Successfully updated CV record: {cv_id}")
            return True
        else:
            logger.warning(f"No CV record found with ID: {cv_id}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update CV record: {str(e)}")
        raise Exception(f"Update operation failed: {str(e)}")


def store_video_record(
    cv_id: str,
    script_data: Dict,
    generation_method: str = 'moviepy',
    style_preferences: Optional[Dict] = None,
    gemini_job_id: Optional[str] = None
) -> str:
    """
    Store video generation record in database.
    
    Args:
        cv_id: Associated CV record ID
        script_data: Video script and timing data
        generation_method: 'gemini' or 'moviepy'
        style_preferences: Optional video style settings
        gemini_job_id: Optional Gemini API job ID for tracking
        
    Returns:
        Video record ID
        
    Raises:
        Exception: If database operation fails
    """
    try:
        client = init_supabase_client()
        
        video_data = {
            'cv_id': cv_id,
            'script_data': script_data,
            'generation_method': generation_method,
            'style_preferences': style_preferences or {},
            'status': 'pending',
            'gemini_job_id': gemini_job_id
        }
        
        result = client.table('video_records').insert(video_data).execute()
        
        if not result.data:
            raise Exception("Failed to store video record")
        
        video_id = result.data[0]['id']
        logger.info(f"Successfully stored video record with ID: {video_id}")
        return video_id
        
    except Exception as e:
        logger.error(f"Failed to store video record: {str(e)}")
        raise Exception(f"Video record storage failed: {str(e)}")


def update_video_status(video_id: str, status: str, video_url: Optional[str] = None) -> bool:
    """
    Update video generation status and URL.
    
    Args:
        video_id: Video record ID
        status: New status ('pending', 'processing', 'completed', 'failed')
        video_url: Optional video URL when completed
        
    Returns:
        True if update successful, False otherwise
    """
    try:
        client = init_supabase_client()
        
        updates = {'status': status}
        if video_url:
            updates['video_url'] = video_url
        
        result = client.table('video_records').update(updates).eq('id', video_id).execute()
        
        if result.data:
            logger.info(f"Updated video status to {status} for ID: {video_id}")
            return True
        else:
            logger.warning(f"No video record found with ID: {video_id}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update video status: {str(e)}")
        return False


def test_database_connection() -> Dict[str, Any]:
    """
    Test database connection and return connection info.
    
    Returns:
        Dictionary with connection status and details
    """
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Test connection with a simple query
        cursor.execute("SELECT COUNT(*) FROM cv_records;")
        count = cursor.fetchone()[0]
        cursor.close()
        
        # Get connection info
        db_host = os.getenv('SUPABASE_DB_HOST')
        db_user = os.getenv('SUPABASE_DB_USER')
        database_url = os.getenv('DATABASE_URL')
        
        # Determine connection details
        if database_url:
            connection_url = f"PostgreSQL via DATABASE_URL ({db_host})"
        else:
            connection_url = f"PostgreSQL session pooler ({db_host})"
        
        connection_info = {
            'status': 'connected',
            'connection_type': 'session_pooler',
            'url': connection_url,
            'schema': 'public',
            'test_query_success': True,
            'cv_records_count': count
        }
        
        logger.info(f"Database connection test successful: session_pooler")
        return connection_info
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'connection_type': 'unknown',
            'test_query_success': False
        }


def get_cv_by_id(cv_id: str) -> Optional[Dict]:
    """
    Retrieve a specific CV record by ID.
    
    Args:
        cv_id: CV record ID
        
    Returns:
        CV record with analysis data or None if not found
    """
    try:
        client = init_supabase_client()
        
        result = client.table('cv_records').select(
            '*, analysis_results(*), video_records(*)'
        ).eq('id', cv_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            return None
            
    except Exception as e:
        logger.error(f"Failed to retrieve CV by ID: {str(e)}")
        return None


def store_job_description(
    job_text: str,
    job_analysis: Dict,
    user_id: Optional[str] = None,
    company_name: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Store job description and analysis in database.
    
    Args:
        job_text: Original job description text
        job_analysis: Analysis results from analyze_job_description
        user_id: Optional user ID for authenticated users
        company_name: Optional company name
        metadata: Optional metadata dictionary with additional job info
        
    Returns:
        Job description record ID
        
    Raises:
        Exception: If database operation fails
    """
    try:
        client = init_supabase_client()
        
        # Use metadata if provided, otherwise use function parameters
        if metadata:
            company_name = metadata.get('company_name', company_name)
            job_title = metadata.get('job_title', job_analysis.get('job_title', 'Unknown Position'))
        else:
            job_title = job_analysis.get('job_title', 'Unknown Position')
        
        job_data = {
            'user_id': user_id,
            'job_title': job_title,
            'company_name': company_name,
            'job_text': job_text,
            'required_skills': job_analysis.get('required_skills', []),
            'preferred_skills': job_analysis.get('preferred_skills', []),
            'experience_level': job_analysis.get('experience_level', 'mid'),
            'industry_keywords': job_analysis.get('industry_keywords', []),
            'department': job_analysis.get('department', ''),
            'employment_type': job_analysis.get('employment_type', 'full-time')
        }
        
        result = client.table('job_descriptions').insert(job_data).execute()
        
        if not result.data:
            raise Exception("Failed to store job description")
        
        job_id = result.data[0]['id']
        logger.info(f"Successfully stored job description with ID: {job_id}")
        return job_id
        
    except Exception as e:
        logger.error(f"Failed to store job description: {str(e)}")
        raise Exception(f"Job description storage failed: {str(e)}")


def get_job_descriptions(user_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """
    Retrieve job descriptions for a user.
    
    Args:
        user_id: Optional user ID to filter results
        limit: Maximum number of records to return
        
    Returns:
        List of job description records
    """
    try:
        client = init_supabase_client()
        
        query = client.table('job_descriptions').select('*').order('created_at', desc=True).limit(limit)
        
        if user_id:
            query = query.eq('user_id', user_id)
        
        result = query.execute()
        
        logger.info(f"Retrieved {len(result.data)} job descriptions")
        return result.data
        
    except Exception as e:
        logger.error(f"Failed to retrieve job descriptions: {str(e)}")
        raise Exception(f"Job description query failed: {str(e)}")


def store_cv_analysis_with_job(
    resume_text: str,
    analysis_data: Dict,
    metadata: Dict,
    job_id: Optional[str] = None,
    optimization_advice: Optional[Dict] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Store CV analysis with optional job description matching.
    
    Args:
        resume_text: Extracted text from the resume
        analysis_data: Analysis results from AI processing
        metadata: File metadata (filename, size, type, etc.)
        job_id: Optional job description ID for matching
        optimization_advice: Optional CV optimization advice
        user_id: Optional user ID for authenticated users
        
    Returns:
        CV record ID
    """
    try:
        client = init_supabase_client()
        
        # Store CV record
        cv_data = {
            'user_id': user_id,
            'filename': metadata.get('filename', 'unknown.pdf'),
            'original_text': resume_text,
            'file_type': metadata.get('file_type', 'pdf'),
            'file_size': metadata.get('file_size', 0),
            'language': metadata.get('language', 'en')
        }
        
        cv_result = client.table('cv_records').insert(cv_data).execute()
        
        if not cv_result.data:
            raise Exception("Failed to store CV record")
        
        cv_id = cv_result.data[0]['id']
        
        # Store analysis results with job matching
        analysis_record = {
            'cv_id': cv_id,
            'job_id': job_id,
            'strengths': analysis_data.get('strengths', []),
            'weak_points': analysis_data.get('weak_points', []),
            'suggestions': analysis_data.get('suggestions', []),
            'top_skills': analysis_data.get('top_skills', []),
            'one_sentence_pitch': analysis_data.get('one_sentence_pitch', ''),
            'compatibility_score': analysis_data.get('compatibility_score'),
            'missing_skills': analysis_data.get('missing_skills', []),
            'matching_skills': analysis_data.get('matching_skills', []),
            'optimization_advice': optimization_advice or {}
        }
        
        analysis_result = client.table('analysis_results').insert(analysis_record).execute()
        
        if not analysis_result.data:
            raise Exception("Failed to store analysis results")
        
        logger.info(f"Successfully stored CV analysis with job matching for CV ID: {cv_id}")
        return cv_id
        
    except Exception as e:
        logger.error(f"Failed to store CV analysis with job: {str(e)}")
        raise Exception(f"Database storage failed: {str(e)}")


def get_cv_job_matches(cv_id: str) -> List[Dict]:
    """
    Get all job matches for a specific CV.
    
    Args:
        cv_id: CV record ID
        
    Returns:
        List of job matches with compatibility scores
    """
    try:
        client = init_supabase_client()
        
        result = client.table('analysis_results').select(
            '*, job_descriptions(*)'
        ).eq('cv_id', cv_id).execute()
        
        matches = []
        for record in result.data:
            if record.get('job_descriptions'):
                matches.append({
                    'job_info': record['job_descriptions'],
                    'compatibility_score': record.get('compatibility_score', 0),
                    'missing_skills': record.get('missing_skills', []),
                    'matching_skills': record.get('matching_skills', []),
                    'optimization_advice': record.get('optimization_advice', {}),
                    'analyzed_at': record.get('analyzed_at')
                })
        
        logger.info(f"Retrieved {len(matches)} job matches for CV: {cv_id}")
        return matches
        
    except Exception as e:
        logger.error(f"Failed to retrieve CV job matches: {str(e)}")
        return []


def search_job_descriptions(query: str, filters: Optional[Dict] = None, user_id: Optional[str] = None) -> List[Dict]:
    """
    Search job descriptions using full-text search.
    
    Args:
        query: Search query string
        filters: Optional filters (experience_level, employment_type, etc.)
        user_id: Optional user ID to filter results
        
    Returns:
        List of matching job description records
    """
    try:
        client = init_supabase_client()
        
        search_query = client.table('job_descriptions').select('*').text_search('job_text', query)
        
        if user_id:
            search_query = search_query.eq('user_id', user_id)
        
        if filters:
            if 'experience_level' in filters:
                search_query = search_query.eq('experience_level', filters['experience_level'])
            
            if 'employment_type' in filters:
                search_query = search_query.eq('employment_type', filters['employment_type'])
        
        result = search_query.execute()
        
        logger.info(f"Job search returned {len(result.data)} results for query: {query}")
        return result.data
        
    except Exception as e:
        logger.error(f"Failed to search job descriptions: {str(e)}")
        raise Exception(f"Job search failed: {str(e)}")


def delete_cv_record(cv_id: str) -> bool:
    """
    Delete a CV record and all associated data.
    
    Args:
        cv_id: CV record ID to delete
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        client = init_supabase_client()
        
        # Delete CV record (cascades to analysis_results and video_records)
        result = client.table('cv_records').delete().eq('id', cv_id).execute()
        
        if result.data:
            logger.info(f"Successfully deleted CV record: {cv_id}")
            return True
        else:
            logger.warning(f"No CV record found with ID: {cv_id}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to delete CV record: {str(e)}")
        return False