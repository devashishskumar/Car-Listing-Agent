#!/usr/bin/env python3
"""
Setup script for Car Listing Agent
"""

import os
import sys

def create_env_file():
    """Create .env file with user's API key"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return True
    
    print("🔧 Setting up your OpenAI API key...")
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    try:
        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("📦 Checking dependencies...")
    
    # Map module names to their import names
    modules = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',  # beautifulsoup4 is imported as bs4
        'openai': 'openai',
        'python-dotenv': 'dotenv'  # python-dotenv is imported as dotenv
    }
    
    missing = []
    
    for module_name, import_name in modules.items():
        try:
            __import__(import_name)
            print(f"✅ {module_name}")
        except ImportError:
            print(f"❌ {module_name}")
            missing.append(module_name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚗 Car Listing Agent - Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Create .env file
    if create_env_file():
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now run the Car Agent:")
        print("  python car_agent.py")
        print("\nOr test it with:")
        print("  python test_agent.py")
    else:
        print("\n❌ Setup failed")

if __name__ == "__main__":
    main()
