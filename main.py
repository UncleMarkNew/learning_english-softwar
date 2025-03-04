import tkinter as tk
import os
import sys
from pathlib import Path

# Add project directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

# Import application components
from database.db_manager import DBManager
from services.llm_processor import LLMProcessor
from ui.main_window import MainWindow

def main():
    """Main entry point for the application."""
    # Create root window
    root = tk.Tk()
    
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), "database", "files.db")
    db_manager = DBManager(db_path)
    
    # Try to initialize LLM processor with API key from environment
    llm_processor = None
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        try:
            llm_processor = LLMProcessor(api_key=api_key)
        except Exception as e:
            print(f"Error initializing LLM processor: {e}")
    
    # Create main window
    app = MainWindow(root, db_manager, llm_processor)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()
