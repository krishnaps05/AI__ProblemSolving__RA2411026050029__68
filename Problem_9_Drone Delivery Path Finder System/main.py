"""
main.py
=======
Entry point for the Drone Delivery Path Finder System.
"""

import tkinter as tk
from ui import DroneDeliveryApp

def main():
    root = tk.Tk()
    # Set app icon or other global settings here if needed
    app = DroneDeliveryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
