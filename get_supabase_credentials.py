#!/usr/bin/env python3
"""
Supabase Credentials Helper

This script helps you find and configure your Supabase credentials.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔑 SUPABASE CREDENTIALS SETUP GUIDE")
    print("=" * 50)
    print()
    
    print("To get your Supabase credentials:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project: vypybbpalqzhdzhvnwin")
    print("3. Go to Settings > API")
    print("4. Copy the following values:")
    print()
    
    print("📋 REQUIRED CREDENTIALS:")
    print("-" * 30)
    print("Project URL: https://vypybbpalqzhdzhvnwin.supabase.co")
    print("anon/public key: [Copy from API settings]")
    print()
    
    print("🔧 UPDATE YOUR .env FILE:")
    print("-" * 30)
    print("SUPABASE_URL=https://vypybbpalqzhdzhvnwin.supabase.co")
    print("SUPABASE_KEY=[paste your anon key here]")
    print()
    
    print("🔍 CURRENT CONFIGURATION:")
    print("-" * 30)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"SUPABASE_URL: {supabase_url if supabase_url else '❌ Not set'}")
    
    if supabase_key:
        if supabase_key == 'your_supabase_anon_key_here':
            print("SUPABASE_KEY: ❌ Placeholder value - needs real key")
        else:
            print(f"SUPABASE_KEY: ✅ Set ({supabase_key[:20]}...)")
    else:
        print("SUPABASE_KEY: ❌ Not set")
    
    print()
    
    # Check session pooler config
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_user = os.getenv('SUPABASE_DB_USER')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    print("🏊 SESSION POOLER CONFIGURATION:")
    print("-" * 30)
    print(f"SUPABASE_DB_HOST: {'✅ Set' if db_host else '❌ Not set'}")
    print(f"SUPABASE_DB_USER: {'✅ Set' if db_user else '❌ Not set'}")
    print(f"SUPABASE_DB_PASSWORD: {'✅ Set' if db_password else '❌ Not set'}")
    
    if db_host and db_user and db_password:
        print("✅ Session pooler configuration looks complete!")
    else:
        print("❌ Session pooler configuration incomplete")
    
    print()
    print("📝 NEXT STEPS:")
    print("1. Copy your anon key from Supabase dashboard")
    print("2. Update SUPABASE_KEY in your .env file")
    print("3. Run: python -c \"from database import test_database_connection; print(test_database_connection())\"")
    print("4. If successful, run: ./run.sh")

if __name__ == "__main__":
    main()