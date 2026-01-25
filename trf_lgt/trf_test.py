import tkinter as tk

# --- Traffic Light Simulator ---
# Purpose: A graphical simulation of a traffic light using color circles.
# Can be used to test detection algorithms by pointing a camera at the screen.

class SimpleTrafficLight:
    def __init__(self, root):
        self.root = root
        self.root.title("Светофор")
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(root, width=150, height=400, bg="#333")
        self.canvas.pack(pady=20)

        # Draw lamps (initially off - dark gray)
        self.red = self.canvas.create_oval(25, 25, 125, 125, fill="#1a1a1a")
        self.yellow = self.canvas.create_oval(25, 150, 125, 250, fill="#1a1a1a")
        self.green = self.canvas.create_oval(25, 275, 125, 375, fill="#1a1a1a")

        # Cycle states: (active_lamp, color, duration_ms)
        self.cycle = [
            (self.red, "red", 3000),      # Red for 3s
            (self.yellow, "yellow", 1000), # Yellow for 1s
            (self.green, "green", 3000),   # Green for 3s
            (self.yellow, "yellow", 1000)  # Yellow for 1s
        ]
        self.index = 0
        
        self.run_cycle()

    def run_cycle(self):
        """Updates the traffic light state recursively."""
        # 1. Turn off all lights (make them dark)
        self.canvas.itemconfig(self.red, fill="#1a1a1a")
        self.canvas.itemconfig(self.yellow, fill="#1a1a1a")
        self.canvas.itemconfig(self.green, fill="#1a1a1a")

        # 2. Получаем текущую лампу, цвет и время из списка
        light_obj, color_name, delay = self.cycle[self.index]

        # 3. Включаем нужную лампу
        self.canvas.itemconfig(light_obj, fill=color_name)

        # 4. Считаем индекс для следующего шага (0, 1, 2, 3 и снова 0)
        self.index = (self.index + 1) % len(self.cycle)

        # 5. Планируем следующий запуск
        self.root.after(delay, self.run_cycle)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTrafficLight(root)
    root.mainloop()