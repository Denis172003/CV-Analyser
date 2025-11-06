#!/usr/bin/env python3
"""
Supabase Session Pooler Setup Script

This script helps configure Supabase for optimal session pooler usage
and validates the database connection.
"""

import os
import sys
from dotenv import load_dotenv
from database import test_database_connection, init_supabase_client

# Load environment variables
load_dotenv()


def print_pooler_info():
    """Print information about Supabase session pooler."""
    print("📚 SUPABASE SESSION POOLER INFORMATION")
    print("=" * 60)
    print()
    print("Session pooler provides:")
    print("• Better connection management for serverless applications")
    print("• Automatic connection pooling and load balancing")
    print("• Reduced connection overhead and improved performance")
    print("• Built-in connection retry and failover mechanisms")
    print()
    print("PostgreSQL Connection String Format:")
    print("postgresql://postgres.PROJECT_REF:PASSWORD@HOST:5432/postgres")
    print()
    print("Example:")
    print("postgresql://postgres.abc123def:mypassword@aws-0-eu-central-1.pooler.supabase.com:5432/postgres")
    print()
    print("Connection Details:")
    print("• Host: aws-X-REGION.pooler.supabase.com")
    print("• Port: 5432")
    print("• Database: postgres")
    print("• User: postgres.PROJECT_REF")
    print("• Pool Mode: session")
    print()
    print("To get your connection details:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings > Database")
    print("4. Find 'Connection pooling' section")
    print("5. Copy the connection string")
    print()


def validate_current_config():
    """Validate current Supabase configuration."""
    print("🔍 VALIDATING CURRENT CONFIGURATION")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_port = os.getenv('SUPABASE_DB_PORT')
    db_name = os.getenv('SUPABASE_DB_NAME')
    db_user = os.getenv('SUPABASE_DB_USER')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    database_url = os.getenv('DATABASE_URL')
    use_pooler = os.getenv('USE_SESSION_POOLER', 'false').lower() == 'true'
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    print(f"SUPABASE_DB_HOST: {'✅ Set' if db_host else '❌ Missing'}")
    print(f"SUPABASE_DB_PORT: {'✅ Set' if db_port else '❌ Missing'}")
    print(f"SUPABASE_DB_NAME: {'✅ Set' if db_name else '❌ Missing'}")
    print(f"SUPABASE_DB_USER: {'✅ Set' if db_user else '❌ Missing'}")
    print(f"SUPABASE_DB_PASSWORD: {'✅ Set' if db_password else '❌ Missing'}")
    print(f"DATABASE_URL: {'✅ Set' if database_url else '❌ Missing'}")
    print(f"USE_SESSION_POOLER: {'✅ Enabled' if use_pooler else '⚠️  Disabled'}")
    print()
    
    if not supabase_key:
        print("❌ SUPABASE_KEY is required for both direct and pooler connections")
        return False
    
    if use_pooler:
        required_params = [db_host, db_user, db_password]
        if not all(required_params):
            print("❌ Missing required session pooler parameters:")
            if not db_host:
                print("   • SUPABASE_DB_HOST")
            if not db_user:
                print("   • SUPABASE_DB_USER")
            if not db_password:
                print("   • SUPABASE_DB_PASSWORD")
            return False
        
        # Validate user format
        if not db_user.startswith('postgres.'):
            print("❌ Invalid SUPABASE_DB_USER format")
            print("   Expected: postgres.PROJECT_REF")
            return False
    
    if not use_pooler and not supabase_url:
        print("❌ SUPABASE_URL is required when USE_SESSION_POOLER=false")
        return False
    
    return True


def test_connection():
    """Test database connection with current configuration."""
    print("🧪 TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        conn_info = test_database_connection()
        
        if conn_info['status'] == 'connected':
            print("✅ Connection successful!")
            print(f"   Connection type: {conn_info['connection_type']}")
            print(f"   URL: {conn_info['url']}")
            print(f"   Schema: {conn_info['schema']}")
            print(f"   Test query: {'✅ Success' if conn_info['test_query_success'] else '❌ Failed'}")
            return True
        else:
            print("❌ Connection failed!")
            print(f"   Error: {conn_info.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


def setup_pooler_config():
    """Interactive setup for session pooler configuration."""
    print("⚙️  INTERACTIVE POOLER SETUP")
    print("=" * 60)
    
    # Get current values
    current_url = os.getenv('SUPABASE_URL', '')
    current_key = os.getenv('SUPABASE_KEY', '')
    current_host = os.getenv('SUPABASE_DB_HOST', '')
    current_user = os.getenv('SUPABASE_DB_USER', '')
    current_password = os.getenv('SUPABASE_DB_PASSWORD', '')
    
    print("Please provide your Supabase session pooler configuration:")
    print()
    
    # Get individual parameters
    print("You can find these details in:")
    print("Supabase Dashboard > Settings > Database > Connection pooling")
    print()
    
    # Get host
    db_host = input(f"Database Host [{current_host}]: ").strip()
    if not db_host:
        db_host = current_host
    if not db_host:
        print("❌ Database host is required")
        return False
    
    # Get user
    db_user = input(f"Database User [{current_user}]: ").strip()
    if not db_user:
        db_user = current_user
    if not db_user:
        print("❌ Database user is required")
        return False
    
    # Validate user format and extract project reference
    if not db_user.startswith('postgres.'):
        print("❌ Invalid user format. Expected: postgres.PROJECT_REF")
        return False
    
    project_ref = db_user.split('.')[1]
    
    # Get password
    db_password = input(f"Database Password [{('*' * len(current_password)) if current_password else ''}]: ").strip()
    if not db_password:
        db_password = current_password
    if not db_password:
        print("❌ Database password is required")
        return False
    
    # Get API key
    api_key = input(f"Supabase API Key [{current_key[:20]}...]: ").strip()
    if not api_key:
        api_key = current_key
    if not api_key:
        print("❌ API key is required")
        return False
    
    # Generate URLs and connection string
    direct_url = f"https://{project_ref}.supabase.co"
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:5432/postgres"
    
    print()
    print("Generated configuration:")
    print(f"Project Reference: {project_ref}")
    print(f"Database Host: {db_host}")
    print(f"Database User: {db_user}")
    print(f"Direct URL: {direct_url}")
    print(f"Database Password: {'*' * len(db_password)}")
    print()
    
    # Ask for preference
    use_pooler = input("Use session pooler? (recommended) [Y/n]: ").strip().lower()
    use_pooler = use_pooler != 'n'
    
    # Update .env file
    env_updates = []
    env_updates.append(f"SUPABASE_URL={direct_url}")
    env_updates.append(f"SUPABASE_KEY={api_key}")
    env_updates.append(f"SUPABASE_DB_HOST={db_host}")
    env_updates.append(f"SUPABASE_DB_PORT=5432")
    env_updates.append(f"SUPABASE_DB_NAME=postgres")
    env_updates.append(f"SUPABASE_DB_USER={db_user}")
    env_updates.append(f"SUPABASE_DB_PASSWORD={db_password}")
    env_updates.append(f"DATABASE_URL={database_url}")
    env_updates.append(f"USE_SESSION_POOLER={'true' if use_pooler else 'false'}")
    
    print()
    print("Configuration to add to .env file:")
    print("-" * 40)
    for line in env_updates:
        # Hide password in display
        if 'PASSWORD=' in line or 'DATABASE_URL=' in line:
            key, value = line.split('=', 1)
            if 'PASSWORD=' in line:
                print(f"{key}={'*' * len(value)}")
            else:
                # Hide password in DATABASE_URL
                import re
                masked_url = re.sub(r'(:)([^@]+)(@)', r'\1' + '*' * 8 + r'\3', value)
                print(f"{key}={masked_url}")
        else:
            print(line)
    print("-" * 40)
    
    update_env = input("Update .env file automatically? [Y/n]: ").strip().lower()
    if update_env != 'n':
        try:
            # Read existing .env
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add new values
            updated_keys = set()
            for i, line in enumerate(env_lines):
                for update in env_updates:
                    key = update.split('=')[0]
                    if line.startswith(f"{key}="):
                        env_lines[i] = update + '\n'
                        updated_keys.add(key)
                        break
            
            # Add new keys
            for update in env_updates:
                key = update.split('=')[0]
                if key not in updated_keys:
                    env_lines.append(update + '\n')
            
            # Write updated .env
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            print("✅ .env file updated successfully")
            
            # Reload environment
            load_dotenv(override=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update .env file: {str(e)}")
            print("Please update manually using the configuration above.")
            return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 SUPABASE SESSION POOLER SETUP")
    print("=" * 60)
    print()
    
    while True:
        print("Choose an option:")
        print("1. 📚 Show pooler information")
        print("2. 🔍 Validate current configuration")
        print("3. 🧪 Test database connection")
        print("4. ⚙️  Interactive pooler setup")
        print("5. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            print_pooler_info()
        elif choice == "2":
            if validate_current_config():
                print("✅ Configuration looks good!")
            else:
                print("❌ Configuration issues found. Please fix them.")
        elif choice == "3":
            if test_connection():
                print("✅ Database connection is working!")
            else:
                print("❌ Database connection failed. Check your configuration.")
        elif choice == "4":
            if setup_pooler_config():
                print("✅ Configuration setup complete!")
                print("Run option 3 to test the new configuration.")
            else:
                print("❌ Setup failed. Please try again.")
        elif choice == "5":
            print("👋 Setup complete!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()