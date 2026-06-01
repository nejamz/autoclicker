import time
import threading
import pyautogui
import keyboard

# --- HOTKEY CONFIGURATION ---
SET_POINT_A = "f2"  
SET_POINT_B = "f3"  
TOGGLE_KEY = "f4"   
EXIT_KEY = "f8"     
# ----------------------------

class UniversalClicker:
    def __init__(self, mode, delay):
        self.mode = mode          
        self.delay = delay        
        self.running = False
        self.active = True
        self.point_a = None
        self.point_b = None
        self.current_target = "A"
        self.pause_event = threading.Event()

    def set_a(self):
        self.point_a = pyautogui.position()
        print(f"[📍] Point A saved at: {self.point_a}")

    def set_b(self):
        if self.mode == 1:
            print("[ℹ️] You are in 1-Point mode. No need to set Point B.")
            return
        self.point_b = pyautogui.position()
        print(f"[📍] Point B saved at: {self.point_b}")

    def toggle(self):
        if self.point_a is None:
            print("[⚠️] Error: You must set Point A (F2) first!")
            return
        if self.mode == 2 and self.point_b is None:
            print("[⚠️] Error: You are in 2-Point mode. You must also set Point B (F3)!")
            return
        
        self.running = not self.running
        if self.running:
            print(f"\n[▶] Autoclicker STARTED (Speed: {self.delay}s delay)")
            self.current_target = "A"
        else:
            print("\n[⏸] Autoclicker PAUSED")
            # Signal the main thread that we are paused so it can prompt for a speed change
            self.pause_event.set()

    def exit(self):
        print("\n[🛑] Closing script...")
        self.active = False
        self.running = False
        self.pause_event.set() # Unblock main thread input if waiting

    def robust_click(self, coordinates):
        try:
            pyautogui.moveTo(coordinates[0], coordinates[1])
            pyautogui.mouseDown()
            time.sleep(0.05)
            pyautogui.mouseUp()
        except Exception as e:
            print(f"Click injection failed: {e}")

    def click_loop(self):
        while self.active:
            if self.running:
                if self.mode == 1:
                    self.robust_click(self.point_a)
                else:
                    if self.current_target == "A":
                        self.robust_click(self.point_a)
                        self.current_target = "B"
                    else:
                        self.robust_click(self.point_b)
                        self.current_target = "A"
                
                time.sleep(self.delay)
            else:
                time.sleep(0.1)

def main():
    print("=====================================")
    print("   SPEED-ADJUSTABLE AUTOCLICKER     ")
    print("=====================================")
    
    while True:
        try:
            mode = int(input("Choose Mode -> Enter 1 (Single Point) or 2 (Dual Point): "))
            if mode in [1, 2]:
                break
            print("Invalid choice. Please type 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            delay = float(input("Enter click speed delay in seconds (e.g., 0.5): "))
            if delay >= 0:
                break
            print("Delay cannot be negative.")
        except ValueError:
            print("Please enter a valid decimal number.")

    print("\n=== Setup Controls ===")
    print(f"-> Hover mouse and press [{SET_POINT_A.upper()}] to set Point A")
    if mode == 2:
        print(f"-> Hover mouse and press [{SET_POINT_B.upper()}] to set Point B")
    print(f"-> Press [{TOGGLE_KEY.upper()}] to Start / Pause")
    print(f"-> Press [{EXIT_KEY.upper()}] to Exit")
    print("=====================================\n")

    clicker = UniversalClicker(mode, delay)
    
    click_thread = threading.Thread(target=clicker.click_loop)
    click_thread.start()

    keyboard.add_hotkey(SET_POINT_A, clicker.set_a)
    keyboard.add_hotkey(SET_POINT_B, clicker.set_b)
    keyboard.add_hotkey(TOGGLE_KEY, clicker.toggle)
    keyboard.add_hotkey(EXIT_KEY, clicker.exit)

    # Main thread watches for pause triggers to change speeds
    while clicker.active:
        clicker.pause_event.wait() # Sleep here until F4 is pressed to pause
        if not clicker.active:
            break
            
        print("--- Speed Adjustment Option ---")
        new_speed = input(f"Enter new delay speed (or press ENTER to keep current {clicker.delay}s): ").strip()
        
        if new_speed:
            try:
                clicker.delay = float(new_speed)
                print(f"[⚙️] Speed updated! New delay: {clicker.delay}s")
            except ValueError:
                print("[⚠️] Invalid number entered. Keeping previous speed.")
        else:
            print("[ℹ️] Speed unchanged.")
            
        print(f"Ready to resume. Press [{TOGGLE_KEY.upper()}] to run again.\n")
        clicker.pause_event.clear() # Reset the event listener

    click_thread.join()

if __name__ == "__main__":
    main()
