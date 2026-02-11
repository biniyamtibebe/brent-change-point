#!/usr/bin/env python
"""
Simple script to run the complete Brent Oil Price Analysis
"""
import os
import subprocess
import sys
import webbrowser
from threading import Timer

def run_flask():
    """Start Flask backend"""
    print("🚀 Starting Flask backend...")
    os.chdir('app/backend')
    subprocess.run([sys.executable, 'app.py'])

def open_browser():
    """Open browser after delay"""
    webbrowser.open('http://127.0.0.1:5000')
    webbrowser.open('app/frontend/simple-dashboard.html')

def main():
    print("=" * 60)
    print("BRENT OIL PRICE ANALYSIS DASHBOARD")
    print("=" * 60)
    
    print("\nOptions:")
    print("1. Run full dashboard (Flask + Browser)")
    print("2. Run Flask API only")
    print("3. Open HTML dashboard only")
    print("4. Run data analysis pipeline")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        # Open browser after 2 seconds
        Timer(2, open_browser).start()
        run_flask()
        
    elif choice == '2':
        run_flask()
        
    elif choice == '3':
        dashboard_path = os.path.abspath('app/frontend/simple-dashboard.html')
        if os.path.exists(dashboard_path):
            webbrowser.open(f'file://{dashboard_path}')
            print(f"✓ Dashboard opened: {dashboard_path}")
        else:
            print("✗ Dashboard file not found. Run option 4 first.")
            
    elif choice == '4':
        print("\n📊 Running data analysis pipeline...")
        os.chdir('..')
        subprocess.run([sys.executable, 'run_analysis.py'])
        
    else:
        print("Invalid choice")

if __name__ == '__main__':
    main()