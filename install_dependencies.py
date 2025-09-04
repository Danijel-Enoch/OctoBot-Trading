#!/usr/bin/env python3
"""
Installation script for OctoBot-Trading custom dependencies
This script handles the installation of Git-based dependencies that setuptools can't handle directly.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print("🚀 Installing OctoBot-Trading with custom dependencies...")
    
    # Git dependencies that need to be installed first
    git_dependencies = [
        ("git+https://github.com/Danijel-Enoch/trading-backend.git", "Installing custom trading-backend"),
        ("git+https://github.com/Danijel-Enoch/ccxt.git@master#subdirectory=python", "Installing custom CCXT with WEEX support"),
    ]
    
    # Install Git dependencies
    for dependency, description in git_dependencies:
        if not run_command(f"pip install {dependency}", description):
            print(f"🛑 Failed to install {dependency}")
            sys.exit(1)
    
    # Install remaining standard dependencies
    requirements_file = "setup_requirements.txt"
    if os.path.exists(requirements_file):
        if not run_command(f"pip install -r {requirements_file}", f"Installing standard dependencies from {requirements_file}"):
            print(f"🛑 Failed to install dependencies from {requirements_file}")
            sys.exit(1)
    else:
        print(f"⚠️ {requirements_file} not found, skipping standard dependencies")
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Installed packages:")
    print("  ✅ Custom trading-backend from GitHub")
    print("  ✅ Custom CCXT with WEEX exchange support")
    print("  ✅ All other required dependencies")
    print("\n🔧 You can now use OctoBot-Trading with WEEX exchange support!")

if __name__ == "__main__":
    main()
