# This program reads force data from serial and plots in real-time
### DEPRACATED ###
import customtkinter as ctk
import serial
import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkinter import filedialog, messagebox

# Initialize the main window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ForceDataApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.title("Force Data Acquisition")
        self.geometry("1000x600")

        # Initialize serial variables
        self.port_var = ctk.StringVar(value="COM4")  # Default COM port
        self.baud_rate = 115200
        self.serial_connection = None
        self.collecting_data = False  # Flag to control data collection

        # Data storage
        self.time_data = []
        self.force_data = []

        # UI elements
        self.port_label = ctk.CTkLabel(self, text="COM Port:")
        self.port_label.grid(row=0, column=0, padx=20, pady=10)

        self.port_entry = ctk.CTkEntry(self, textvariable=self.port_var)
        self.port_entry.grid(row=0, column=1, padx=20, pady=10)

        self.start_force_var = ctk.DoubleVar(value=10.0)  # Threshold to start recording
        self.readings_per_sec_var = ctk.IntVar(value=10)  # Readings per second

        self.force_label = ctk.CTkLabel(self, text="Start Force (N):")
        self.force_label.grid(row=1, column=0)

        self.start_force_entry = ctk.CTkEntry(self, textvariable=self.start_force_var)
        self.start_force_entry.grid(row=1, column=1)

        self.rps_label = ctk.CTkLabel(self, text="Readings per Second:")
        self.rps_label.grid(row=2, column=0)

        self.rps_entry = ctk.CTkEntry(self, textvariable=self.readings_per_sec_var)
        self.rps_entry.grid(row=2, column=1)

        self.start_button = ctk.CTkButton(self, text="Start Collection", command=self.start_collection)
        self.start_button.grid(row=3, column=0, padx=20, pady=20)

        self.stop_button = ctk.CTkButton(self, text="Stop Collection", command=self.stop_collection)
        self.stop_button.grid(row=3, column=1, padx=20, pady=20)

        self.save_button = ctk.CTkButton(self, text="Save Data", command=self.save_data)
        self.save_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Plot setup
        self.fig, self.ax = plt.subplots()
        self.x_data = deque(maxlen=100)
        self.y_data = deque(maxlen=100)
        self.line, = self.ax.plot([], [], 'r-')
        self.ax.set_ylim(0, 50)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylabel('Force (N)')
        self.ax.set_xlabel('Time (s)')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        self.anim = animation.FuncAnimation(self.fig, self.update_plot, interval=100)

        # Table setup
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=2, rowspan=6, padx=20, pady=20, sticky="nsew")

        self.table = ctk.CTkTextbox(self.table_frame, width=300, height=400)
        self.table.pack(fill=ctk.BOTH, expand=True)
        self.table.insert(ctk.END, "Time (s)\tForce (N)\n")

        # Layout management
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(5, weight=1)

    # Start data collection
    def start_collection(self):
        self.collecting_data = True
        self.start_button.configure(state=ctk.DISABLED)
        threading.Thread(target=self.collect_data, daemon=True).start()

    # Stop data collection
    def stop_collection(self):
        self.collecting_data = False
        self.start_button.configure(state=ctk.NORMAL)

    # While collecting data
    def collect_data(self):
        # Open serial connection
        try:
            self.serial_connection = serial.Serial(self.port_var.get(), self.baud_rate, timeout=1)
            print('port opened....')
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            messagebox.showerror("Serial Error", f"Error opening serial port: {e}")
            self.start_button.configure(state=ctk.NORMAL)
            return

        self.serial_connection.write(bytes.fromhex("3f0d"))  # Send hex command
        print('3f0d')

        readings_per_sec = self.readings_per_sec_var.get()
        delay = 1 / readings_per_sec # calculate necessary delay in measurements for consistancy
        start_force = self.start_force_var.get()

        while True:
            time.sleep(delay)
            self.serial_connection.write(bytes.fromhex("3f0d"))
            raw_data = self.serial_connection.readline().decode('utf-8').strip()
            print(raw_data)

            try:
                force_value = float(raw_data.replace(" N", ""))
            except ValueError:
                continue

            if force_value >= start_force:
                start_time = time.time()
                while self.collecting_data:
                    self.serial_connection.write(bytes.fromhex("3f0d"))
                    raw_data = self.serial_connection.readline().decode('utf-8').strip()
                    print(raw_data)

                    try:
                        force_value = float(raw_data.replace(" N", ""))
                    except ValueError:
                        break
                    current_time = time.time() - start_time
                    self.time_data.append(current_time)
                    self.force_data.append(force_value)

                    self.x_data.append(current_time)
                    self.y_data.append(force_value)
                    self.ax.set_xlim(0, max(10, current_time))

                    self.table.insert(ctk.END, f"{current_time:.2f}\t{force_value:.2f}\n")
                    self.table.yview_moveto(1)

                    self.canvas.draw()
                    time.sleep(delay)

    def update_plot(self, frame):
        self.line.set_data(self.x_data, self.y_data)
        return self.line,

    def save_data(self):
        if not self.time_data or not self.force_data:
            messagebox.showwarning("No Data", "No data available to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        data_dict = {
            "Time (s)": self.time_data,
            "Force (N)": self.force_data
        }
        df = pd.DataFrame(data_dict)
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Data Saved", f"Data successfully saved to {file_path}")

    # Function to ensure all processes are killed on exit
    def on_closing(self):
        self.destroy()
        self.quit()

if __name__ == "__main__":
    app = ForceDataApp()
    app.mainloop()
