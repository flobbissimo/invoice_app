"""
Main entry point for the application
"""
import sys
import traceback
from src import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Fatal error:", str(e))
        print("\nTraceback:")
        traceback.print_exc()
        input("\nPress Enter to exit...") 