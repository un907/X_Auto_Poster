import sys
import os

# Mock customtkinter to avoid GUI errors during import if possible, 
# but main.py imports it at top level. 
# We might need to run this in an environment where tkinter works or just catch the error if it fails to open window,
# but we only want to test imports.
# However, main.py executes code at top level (e.g. migrate_data()).

print("Initial modules:", "google.generativeai" in sys.modules)

import main

print("After importing main:", "google.generativeai" in sys.modules)

if "google.generativeai" in sys.modules:
    print("FAILURE: google.generativeai was imported by main.py!")
else:
    print("SUCCESS: google.generativeai was NOT imported by main.py")

# Test Singleton and Lazy Load
print("Instantiating GeminiClient with dummy key...")
try:
    client1 = main.GeminiClient("dummy_key")
    print("After client1 init:", "google.generativeai" in sys.modules)
    
    client2 = main.GeminiClient("dummy_key")
    
    if client1 is client2:
        print("SUCCESS: GeminiClient is a Singleton")
    else:
        print("FAILURE: GeminiClient is NOT a Singleton")
        
except Exception as e:
    print(f"Error during GeminiClient usage: {e}")
