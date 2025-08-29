#!/usr/bin/env python3
"""
Quick start script for demonstrating real-time chat functionality
"""

import os
import sys
import time
import subprocess

def main():
    """Start the Flask web application for real-time demo"""
    print("🚀 Starting Chat Application Real-time Demo")
    print("=" * 50)

    print("📋 Demo Instructions:")
    print("1. Flask server will start on http://localhost:5000")
    print("2. Open browser and go to http://localhost:5000")
    print("3. Login as different users in multiple tabs/windows")
    print("4. Send messages and watch real-time updates!")
    print()
    print("⚡ Real-time Features:")
    print("   • Dashboard: Updates every 5 seconds")
    print("   • Chat: Updates every 3 seconds")
    print("   • Notifications: Visual alerts for new messages")
    print()

    try:
        print("🌐 Starting Flask server...")
        print("Press Ctrl+C to stop the server")
        print()

        # Start Flask server
        cmd = [sys.executable, "web_app.py", "5000"]
        subprocess.run(cmd, cwd=os.path.dirname(__file__))

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Thanks for testing the real-time chat!")

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in a virtual environment: source venv/bin/activate")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Try running: python3 web_app.py")

if __name__ == "__main__":
    main()
