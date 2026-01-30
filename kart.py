import os
import shutil
import time
import sqlite3
from datetime import datetime

# --- CONFIGURATION ---
EARTH_PATH = r"C:\Users\Sean\Documents\GitHub\willow"
PENDING_PATH = os.path.join(EARTH_PATH, "artifacts", "pending")
L5_PATH = os.path.join(EARTH_PATH, "artifacts", "narrative")
L6_PATH = os.path.join(EARTH_PATH, "artifacts", "specs")
DB_PATH = os.path.join(EARTH_PATH, "willow_index.db")

# --- DEFINITIONS ---
# L5: Narrative, Creative, "Our Bob", The Mann Convergence
L5_KEYWORDS = ["chapter", "draft", "prologue", "mann", "christoph", "thriller", "fictional", "narrative", "book", "story"]

# L6: Operational, Legal, Technical, FOIA, NVIDIA
L6_KEYWORDS = ["spec", "legal", "foia", "nvidia", "report", "governance", "ai usage", "framework", "technical", "instruction"]

def classify_iron(filename):
    """
    Decides the destination based on the filename.
    Returns: (destination_path, category_label)
    """
    fn_lower = filename.lower()
    
    # Check L5 (Narrative)
    if any(keyword in fn_lower for keyword in L5_KEYWORDS):
        return L5_PATH, "L5_NARRATIVE"
    
    # Check L6 (Specs)
    if any(keyword in fn_lower for keyword in L6_KEYWORDS):
        return L6_PATH, "L6_SPECS"
    
    return None, "UNCLASSIFIED"

def refine_ore():
    """
    Scans the 'Pending' folder and sorts files into L5 or L6.
    """
    if not os.path.exists(PENDING_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure destinations exist
    os.makedirs(L5_PATH, exist_ok=True)
    os.makedirs(L6_PATH, exist_ok=True)

    for filename in os.listdir(PENDING_PATH):
        file_path = os.path.join(PENDING_PATH, filename)
        
        # Skip directories, only process files
        if not os.path.isfile(file_path):
            continue

        destination_dir, category = classify_iron(filename)

        if destination_dir:
            try:
                # Move the file
                shutil.move(file_path, os.path.join(destination_dir, filename))
                
                # Update the Nervous System
                cursor.execute("""
                    UPDATE file_registry 
                    SET status='SORTED', category=? 
                    WHERE filename=?
                """, (category, filename))
                
                # If the file wasn't in the DB (e.g., manual placement), insert it
                if cursor.rowcount == 0:
                    cursor.execute("""
                        INSERT INTO file_registry (filename, ingest_date, category, status)
                        VALUES (?, ?, ?, 'SORTED')
                    """, (filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), category))

                conn.commit()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Refined: {filename} -> {category}")
            
            except Exception as e:
                print(f"Error refining {filename}: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("Initializing Kartikeya Refinery [Sorting Logic]...")
    
    while True:
        refine_ore()
        time.sleep(15) # Pulse check every 15 seconds