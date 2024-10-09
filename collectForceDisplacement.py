# This program reads force, displacement, and calculates velocity, then plots in real-time
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

class ForceDisplacementApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.title("Force, Displacement, and Velocity Data Acquisition")
        self.geometry("1200x800")

        # Initialize serial variables
        self.force_port_var = ctk.StringVar(value="COM9")  # Default COM port for force sensor
        self.displacement_port_var = ctk.StringVar(value="COM8")  # Default COM port for displacement sensor
        self.baud_rate = 115200
        self.serial_force_connection = None
        self.serial_displacement_connection = None
        self.collecting_data = False  # Flag to control data collection

        # Data storage
        self.time_data = []
        self.force_data = []
        self.displacement_data = []
        self.velocity_data = []

        # UI elements for force port
        self.force_port_label = ctk.CTkLabel(self, text="Force Sensor COM Port:")
        self.force_port_label.grid(row=0, column=0, padx=20, pady=10)

        self.force_port_entry = ctk.CTkEntry(self, textvariable=self.force_port_var)
        self.force_port_entry.grid(row=0, column=1, padx=20, pady=10)

        # UI elements for displacement port
        self.displacement_port_label = ctk.CTkLabel(self, text="Displacement Sensor COM Port:")
        self.displacement_port_label.grid(row=1, column=0, padx=20, pady=10)

        self.displacement_port_entry = ctk.CTkEntry(self, textvariable=self.displacement_port_var)
        self.displacement_port_entry.grid(row=1, column=1, padx=20, pady=10)

        self.start_force_var = ctk.DoubleVar(value=0.05)  # Threshold to start recording
        self.readings_per_sec_var = ctk.IntVar(value=5)  # Readings per second

        self.force_label = ctk.CTkLabel(self, text="Start Force (N):")
        self.force_label.grid(row=2, column=0)

        self.start_force_entry = ctk.CTkEntry(self, textvariable=self.start_force_var)
        self.start_force_entry.grid(row=2, column=1)

        self.rps_label = ctk.CTkLabel(self, text="Readings per Second:")
        self.rps_label.grid(row=3, column=0)

        self.rps_entry = ctk.CTkEntry(self, textvariable=self.readings_per_sec_var)
        self.rps_entry.grid(row=3, column=1)

        self.start_button = ctk.CTkButton(self, text="Start Collection", command=self.start_collection)
        self.start_button.grid(row=4, column=0, padx=20, pady=20)

        self.stop_button = ctk.CTkButton(self, text="Stop Collection", command=self.stop_collection)
        self.stop_button.grid(row=4, column=1, padx=20, pady=20)

        self.save_button = ctk.CTkButton(self, text="Save Data", command=self.save_data)
        self.save_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Plot setup: Force vs Displacement
        self.fig, (self.ax_force_disp, self.ax_velocity_time) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})

        # Plot for force vs displacement
        self.displacement_data = deque(maxlen=100)
        self.force_data = deque(maxlen=100)
        self.line_force_disp, = self.ax_force_disp.plot([], [], 'r-')
        self.ax_force_disp.set_ylim(0, 25)
        self.ax_force_disp.set_xlim(0, 50)
        self.ax_force_disp.set_ylabel('Force (N)')
        self.ax_force_disp.set_xlabel('Displacement (mm)')

        # Plot for velocity vs time
        self.velocity_data = deque(maxlen=100)
        self.time_data = deque(maxlen=100)
        self.line_velocity_time, = self.ax_velocity_time.plot([], [], 'b-')
        self.ax_velocity_time.set_ylim(-10, 10)
        self.ax_velocity_time.set_xlim(0, 10)
        self.ax_velocity_time.set_ylabel('Velocity (mm/s)')
        self.ax_velocity_time.set_xlabel('Time (s)')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        self.anim = animation.FuncAnimation(self.fig, self.update_plot, interval=100)

        # Table setup
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=2, rowspan=7, padx=20, pady=20, sticky="nsew")

        self.table = ctk.CTkTextbox(self.table_frame, width=500, height=400)
        self.table.pack(fill=ctk.BOTH, expand=True)
        self.table.insert(ctk.END, "Time (s)\tForce (N)\tDisplacement (mm)\tVelocity (mm/s)\n")

        # Layout management
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(6, weight=1)

    def start_collection(self):
        self.collecting_data = True
        self.start_button.configure(state=ctk.DISABLED)
        threading.Thread(target=self.collect_data, daemon=True).start()

    def stop_collection(self):
        self.collecting_data = False
        self.start_button.configure(state=ctk.NORMAL)

    def collect_data(self):
        # Open serial connections for force and displacement
        try:
            self.serial_force_connection = serial.Serial(self.force_port_var.get(), self.baud_rate, timeout=0.2)
            self.serial_displacement_connection = serial.Serial(self.displacement_port_var.get(), self.baud_rate, timeout=0.2)
            print('Serial connections opened....')
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            messagebox.showerror("Serial Error", f"Error opening serial port: {e}")
            self.start_button.configure(state=ctk.NORMAL)
            return

        #self.serial_force_connection.write(bytes.fromhex("3f0d"))  # Send hex command for force sensor
        #print('3f0d')
        #self.serial_displacement_connection.write(bytes.fromhex("310d"))  # Send hex command for force sensor
        #print('310d')

        readings_per_sec = self.readings_per_sec_var.get()
        delay = 1 / readings_per_sec
        start_force = self.start_force_var.get()

        previous_displacement = 0
        previous_time = 0


        while True:
            #time.sleep(0.001)
            self.serial_force_connection.write(bytes.fromhex("3f0d"))
            raw_force_data = self.serial_force_connection.readline().decode('utf-8').strip()

            self.serial_displacement_connection.write(bytes.fromhex("310d"))  # Hex command for displacement
            raw_displacement_data = self.serial_displacement_connection.readline().decode('utf-8').strip()

            try:
                force_value = float(raw_force_data.replace(" N", ""))
                displacement_value = self.parse_displacement(raw_displacement_data)
                #print(f'{force_value}N and {displacement_value}mm')
            except ValueError:
                print('value error')
                continue

            if force_value >= start_force:
                start_time = time.time()
                initial_displacement = displacement_value  # Set displacement starting point to zero
                loop_start_time = time.time()
                self.last_table_update_index = 0  # Track last index of data added to the table  
                while self.collecting_data:
                    current_time = loop_start_time - start_time
                    self.serial_force_connection.write(bytes.fromhex("3f0d"))
                    raw_force_data = self.serial_force_connection.readline().decode('utf-8').strip()

                    self.serial_displacement_connection.write(bytes.fromhex("310d"))  # Hex command for displacement
                    raw_displacement_data = self.serial_displacement_connection.readline().decode('utf-8').strip()
                    

                    try:
                        force_value = float(raw_force_data.replace(" N", ""))
                        displacement_value = self.parse_displacement(raw_displacement_data)
                    except ValueError:
                        break

                    adjusted_displacement = abs(displacement_value - initial_displacement)  # Start at 0
                   
                    # Calculate velocity
                    if previous_time > 0:
                        delta_time = current_time - previous_time
                        delta_displacement = adjusted_displacement - previous_displacement
                        velocity_value = delta_displacement / delta_time if delta_time != 0 else 0
                    else:
                        velocity_value = 0

                    previous_displacement = adjusted_displacement
                    previous_time = current_time
                    
                    # Append data to storage lists
                    self.time_data.append(current_time)
                    self.force_data.append(force_value)
                    self.displacement_data.append(adjusted_displacement)
                    self.velocity_data.append(velocity_value)
                    
                    if len(self.time_data) % 5 == 0:  # Update every 5 iterations
                        # Update the force vs displacement graph
                        self.update_graph()
                        self.update_table()

                    loop_end_time = time.time()
                    loop_duration = loop_end_time - loop_start_time
                    
                    if loop_duration < delay:
                        time.sleep(delay - loop_duration)
                    loop_start_time = time.time()

    def update_table(self):
        # Update table with new entries since last update
        for i in range(self.last_table_update_index, len(self.time_data)):
            # Add new data rows to the table
            self.table.insert(ctk.END, f"{self.time_data[i]:.2f}\t{self.force_data[i]:.2f}\t"
                                    f"{self.displacement_data[i]:.2f}\t{self.velocity_data[i]:.2f}\n")
    
        # Scroll to the bottom of the table
        self.table.yview_moveto(1)

        # Update the last index to the current length of the data lists
        self.last_table_update_index = len(self.time_data)
        print(self.last_table_update_index)


    def update_graph(self):
        # Update the force vs displacement graph
        self.ax_force_disp.set_xlim(0, max(10, self.displacement_data[-1]))

        # Update the velocity vs time graph
        self.ax_velocity_time.set_xlim(0, max(10, self.time_data[-1]))

        # Update the canvas
        self.canvas.draw()

    def update_plot(self, frame):
        self.line_force_disp.set_data(self.displacement_data, self.force_data)
        self.line_velocity_time.set_data(self.time_data, self.velocity_data)
        return self.line_force_disp, self.line_velocity_time
    
    def parse_displacement(self, raw_data):
        # Example displacement format: "01A+00024.35"
        try:
            return float(raw_data[3:])  # Extract the number after "01A+"
        except ValueError:
            return 0

    def save_data(self):
        if not self.time_data or not self.force_data:
            messagebox.showwarning("No Data", "No data available to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        data_dict = {
            "Time (s)": self.time_data,
            "Force (N)": self.force_data,
            "Displacement (mm)": self.displacement_data,
            "Velocity (mm/s)": self.velocity_data
        }
        df = pd.DataFrame(data_dict)
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Data Saved", f"Data successfully saved to {file_path}")

    # Function to ensure all processes are killed on exit
    def on_closing(self):
        self.destroy()
        self.quit()

if __name__ == "__main__":
    app = ForceDisplacementApp()
    app.mainloop()
