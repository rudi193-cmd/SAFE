import os
import shutil
from datetime import datetime

# --- HARDENED PATHS ---
DROP_ZONE   = r"G:\My Drive\Willow\Auth Users\Sweet-Pea-Rudi19\Drop"
PICKUP_ZONE = r"G:\My Drive\Willow\Auth Users\Sweet-Pea-Rudi19\Pickup"
WILLOW_ROOT = r"C:\Users\Sean\Documents\GitHub\willow"
PENDING     = os.path.join(WILLOW_ROOT, "artifacts", "pending")
VALIDATED   = os.path.join(WILLOW_ROOT, "artifacts", "validated")
SAFE_REPO   = r"C:\Users\Sean\Documents\GitHub\SAFE"

def intake():
    """Willow picks up the mess from the flat Drop folder."""
    print(f"[{datetime.now()}] Scanning Drop Zone...")
    for item in os.listdir(DROP_ZONE):
        src = os.path.join(DROP_ZONE, item)
        dst = os.path.join(PENDING, item)
        # Rule 4: Willow moves and deletes from Drop
        shutil.move(src, dst)
        print(f"Captured: {item}")

def delivery(filename):
    """Willow delivers processed results to your Pickup folder."""
    src = os.path.join(VALIDATED, filename)
    dst_pickup = os.path.join(PICKUP_ZONE, filename)
    dst_safe   = os.path.join(SAFE_REPO, filename)
    
    if os.path.exists(src):
        # Place in Pickup for you
        shutil.copy(src, dst_pickup)
        # Move to SAFE for the residency record
        shutil.move(src, dst_safe)
        print(f"Residency Verified: {filename} delivered to Pickup and SAFE.")

if __name__ == "__main__":
    intake()