"""
Setup script for NBA Shorts AI
Helps verify installation and create necessary directories
"""

import os
import sys
from pathlib import Path
import subprocess


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        print("   Install: https://ffmpeg.org/download.html")
        return False


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False


def check_env_file():
    """Check if .env file exists and is configured"""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found")
        print("   Copy env_example.txt to .env and add your API key")
        return False
    
    with open(env_path) as f:
        content = f.read()
        if "your_api_key_here" in content:
            print("⚠️  .env file exists but not configured")
            print("   Add your OpenRouter API key to .env")
            return False
        elif "OPENROUTER_API_KEY" in content:
            print("✅ .env file is configured")
            return True
    
    print("⚠️  .env file exists but may not be properly configured")
    return False


def create_directories():
    """Create necessary output directories"""
    dirs = ["output", "output/clips"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Created output directories")


def main():
    """Run setup checks"""
    print("=" * 50)
    print("NBA Shorts AI - Setup Verification")
    print("=" * 50)
    print()
    
    # Check Python version
    python_ok = check_python_version()
    print()
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    print()
    
    # Check .env file
    env_ok = check_env_file()
    print()
    
    # Create directories
    create_directories()
    print()
    
    print("=" * 50)
    if python_ok and ffmpeg_ok and env_ok:
        print("✅ All checks passed! Ready to run.")
        print()
        print("Start the app with:")
        print("  streamlit run main.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
    print("=" * 50)


if __name__ == "__main__":
    main()

