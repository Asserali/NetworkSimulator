import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
from tkinter import ttk, messagebox
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


class NetworkSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Asser Network Simulator")

        # Add a title to the canvas
        self.canvas_frame = tk.Frame(root, bg="RED")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas_title = tk.Label(self.canvas_frame, text=" Network Simulator", font=("Arial", 16, "bold"), bg="RED")
        canvas_title.pack(side=tk.TOP, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Buttons frame
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack()

        # Add buttons with custom colors
        network_devices_button = tk.Menubutton(button_frame, text="Network Devices", relief=tk.RAISED, bg="#ADD8E6",
                                               fg="black")
        network_devices_menu = tk.Menu(network_devices_button, tearoff=0)
        network_devices_button.config(menu=network_devices_menu)
        network_devices_menu.add_command(label="Add Switch", command=self.add_switch)
        network_devices_menu.add_command(label="Add Router", command=self.add_router)
        network_devices_menu.add_command(label="Add Server", command=self.add_server)
        network_devices_button.pack(side=tk.LEFT, padx=10, pady=5)

        end_devices_button = tk.Menubutton(button_frame, text="End Devices", relief=tk.RAISED, bg="#90EE90", fg="black")
        end_devices_menu = tk.Menu(end_devices_button, tearoff=0)
        end_devices_button.config(menu=end_devices_menu)
        end_devices_menu.add_command(label="Add PC", command=self.add_pc)
        end_devices_menu.add_command(label="Add Laptop", command=self.add_laptop)
        end_devices_menu.add_command(label="Add Printer", command=self.add_printer)
        end_devices_menu.add_command(label="Add Mobile", command=self.add_mobile)
        end_devices_menu.add_command(label="Add Tablet", command=self.add_tablet)
        end_devices_button.pack(side=tk.LEFT, padx=10, pady=5)

        tk.Button(button_frame, text="Show Topology", command=self.show_topology, bg="#FFD700", fg="black").pack(
            side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="Send Packet", command=self.send_packet, bg="#FF6347", fg="white").pack(
            side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="Ping Devices", command=self.ping_devices, bg="#4682B4", fg="white").pack(
            side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="Ethernet", command=self.start_ethernet_connection, bg="#8A2BE2", fg="white").pack(
            side=tk.LEFT, padx=10, pady=5)

        self.devices = {}
        self.device_counters = {"PC": 0, "Switch": 0, "Laptop": 0, "Server": 0, "Router": 0, "Printer": 0, "Mobile": 0,
                                "Tablet": 0}
        self.lines = []
        self.selected_device = None
        self.dragged_device = None
        self.ethernet_mode = False

        self.canvas.bind("<Double-1>", self.select_device_for_cable)
        self.canvas.bind("<Button-3>", self.show_context_menu)
        self.canvas.bind("<ButtonPress-1>", self.on_device_press)
        self.canvas.bind("<B1-Motion>", self.on_device_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_device_release)

        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Remove", command=self.remove_item)
        self.context_menu.add_command(label="Show Device Info", command=self.show_device_info)

    def update_status(self, message):
        self.status_bar.config(text=message)

    def add_pc(self):
        self.add_device("PC", "lightblue")

    def add_router(self):
        self.add_device("Router", "lightcyan")

    def add_switch(self):
        self.add_device("Switch", "lightgreen")

    def add_laptop(self):
        self.add_device("Laptop", "lightyellow")

    def add_server(self):
        self.add_device("Server", "lightcoral")

    def add_printer(self):
        self.add_device("Printer", "lightpink")

    def add_mobile(self):
        self.add_device("Mobile", "lightgray")

    def add_tablet(self):
        self.add_device("Tablet", "lightgoldenrodyellow")

    def generate_random_ip(self):
        return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def generate_random_mac(self):
        return ':'.join(''.join(random.choices(string.hexdigits[:16], k=2)) for _ in range(6))

    def add_device(self, device_type, color):
        self.device_counters[device_type] += 1
        device_name = f"{device_type}{self.device_counters[device_type]}"
        x, y = 100, 100
        device = self.canvas.create_rectangle(x, y, x + 50, y + 50, fill=color, outline="black", tags="device")
        label = self.canvas.create_text(x + 25, y + 25, text=device_name, fill="black", tags=("label", device))
        self.devices[device] = {
            "type": device_name,
            "lines": [],
            "label": label,
            "ip": self.generate_random_ip(),
            "mac": self.generate_random_mac(),
            "subnet": "255.255.255.0"
        }
        self.update_status(f"{device_name} added.")

    def select_device_for_cable(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.devices:
            if self.selected_device is None:
                self.selected_device = item
                self.update_status(f"Selected {self.devices[item]['type']} for connection.")
            else:
                if self.selected_device != item:
                    self.create_cable(self.selected_device, item)
                self.selected_device = None

    def create_cable(self, device1, device2):
        x1, y1, x2, y2 = self.canvas.coords(device1)
        x1, y1 = (x1 + x2) // 2, (y1 + y2) // 2
        x3, y3, x4, y4 = self.canvas.coords(device2)
        x3, y3 = (x3 + x4) // 2, (y3 + y4) // 2

        line = self.canvas.create_line(x1, y1, x3, y3, fill="black", width=2)
        self.lines.append(line)
        self.devices[device1]["lines"].append(line)
        self.devices[device2]["lines"].append(line)
        self.canvas.tag_raise(device1)
        self.canvas.tag_raise(device2)
        self.canvas.tag_raise(self.devices[device1]["label"])
        self.canvas.tag_raise(self.devices[device2]["label"])
        self.update_status(f"Connected {self.devices[device1]['type']} and {self.devices[device2]['type']}.")

    def start_ethernet_connection(self):
        self.ethernet_mode = True
        self.update_status("Ethernet mode activated. Click on two devices to connect them.")

    def update_line(self, line):
        device1, device2 = None, None
        for device, data in self.devices.items():
            if line in data["lines"]:
                if device1 is None:
                    device1 = device
                else:
                    device2 = device
                    break

        if device1 and device2:
            x1, y1, x2, y2 = self.canvas.coords(device1)
            x1, y1 = (x1 + x2) // 2, (y1 + y2) // 2
            x3, y3, x4, y4 = self.canvas.coords(device2)
            x3, y3 = (x3 + x4) // 2, (y3 + y4) // 2
            self.canvas.coords(line, x1, y1, x3, y3)

    def show_topology(self):
        G = nx.Graph()

        # Add nodes
        for device, data in self.devices.items():
            G.add_node(data["type"])

        # Add edges
        for device, data in self.devices.items():
            for line in data["lines"]:
                for other_device, other_data in self.devices.items():
                    if other_device != device and line in other_data["lines"]:
                        G.add_edge(data["type"], other_data["type"])

        # Draw the graph
        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=10,
                font_weight='bold')
        plt.title("Network Topology")
        plt.show()

        self.update_status("Topology displayed.")

    def ping_devices(self):
        # Check if there are devices
        if not self.devices:
            self.update_status("No devices available to ping.")
            return

        # Ask the user to select the source device and destination device for pinging
        ping_window = tk.Toplevel(self.root)
        ping_window.title("Ping Devices")

        # Source device selection
        tk.Label(ping_window, text="Source Device:").grid(row=0, column=0, padx=10, pady=10)
        source_var = tk.StringVar(ping_window)
        source_menu = ttk.Combobox(ping_window, textvariable=source_var)
        source_menu['values'] = [data["type"] for data in self.devices.values()]
        source_menu.grid(row=0, column=1, padx=10, pady=10)

        # Destination device selection
        tk.Label(ping_window, text="Destination Device:").grid(row=1, column=0, padx=10, pady=10)
        destination_var = tk.StringVar(ping_window)
        destination_menu = ttk.Combobox(ping_window, textvariable=destination_var)
        destination_menu['values'] = [data["type"] for data in self.devices.values()]
        destination_menu.grid(row=1, column=1, padx=10, pady=10)

        # Function to check if there is a path between source and destination (direct or indirect)
        def is_connected(source_device, destination_device, visited=None):
            if visited is None:
                visited = set()

            # If the source and destination are the same, they are trivially connected
            if source_device == destination_device:
                return True

            # Mark the current device as visited
            visited.add(source_device)

            # Check all the connected devices (lines) from the source device
            for line in self.devices[source_device]["lines"]:
                for neighbor_device, data in self.devices.items():
                    # If a device is connected to the source device and has not been visited yet
                    if line in data["lines"] and neighbor_device not in visited:
                        if is_connected(neighbor_device, destination_device, visited):
                            return True
            return False

        # Ping button
        def ping():
            source = source_var.get()
            destination = destination_var.get()

            # Find the corresponding devices based on the selection
            source_device = None
            destination_device = None
            for device, data in self.devices.items():
                if data["type"] == source:
                    source_device = device
                if data["type"] == destination:
                    destination_device = device

            if not source_device or not destination_device:
                messagebox.showerror("Error", "Both devices must be selected.")
                return

            # Check if the devices are connected (direct or indirect)
            if is_connected(source_device, destination_device):
                messagebox.showinfo("Ping Result", f"Ping successful from {source} to {destination}.")
            else:
                messagebox.showwarning("Ping Result", f"{source} is not connected to {destination}. Ping failed.")

            ping_window.destroy()  # Close the ping window after result

        tk.Button(ping_window, text="Ping", command=ping).grid(row=2, column=0, columnspan=2, pady=10)

    def show_context_menu(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.devices or item in self.lines:
            self.context_menu.post(event.x_root, event.y_root)
            self.context_menu.item = item

    def remove_item(self):
        item = self.context_menu.item
        if item in self.devices:
            for line in self.devices[item]["lines"]:
                if line in self.lines:  # Check if the line exists before removing
                    self.canvas.delete(line)
                    self.lines.remove(line)
            self.canvas.delete(self.devices[item]["label"])
            del self.devices[item]
            self.canvas.delete(item)
            self.update_status("Device removed.")
        elif item in self.lines:
            self.canvas.delete(item)
            if item in self.lines:  # Check if the line exists before removing
                self.lines.remove(item)
            for device, data in self.devices.items():
                if item in data["lines"]:
                    data["lines"].remove(item)
            self.update_status("Connection removed.")
        else:
            self.update_status("Warning: No valid item selected to remove.")

    def show_device_info(self):
        item = self.context_menu.item
        if item in self.devices:
            device_data = self.devices[item]
            info_window = tk.Toplevel(self.root)
            info_window.title(f"{device_data['type']} Info")

            tk.Label(info_window, text="Device Name:").grid(row=0, column=0, padx=10, pady=10)
            name_var = tk.StringVar(info_window, value=device_data["type"])
            tk.Entry(info_window, textvariable=name_var).grid(row=0, column=1, padx=10, pady=10)

            tk.Label(info_window, text="IP Address:").grid(row=1, column=0, padx=10, pady=10)
            ip_var = tk.StringVar(info_window, value=device_data["ip"])
            tk.Entry(info_window, textvariable=ip_var).grid(row=1, column=1, padx=10, pady=10)

            tk.Label(info_window, text="MAC Address:").grid(row=2, column=0, padx=10, pady=10)
            mac_var = tk.StringVar(info_window, value=device_data["mac"])
            tk.Entry(info_window, textvariable=mac_var).grid(row=2, column=1, padx=10, pady=10)

            tk.Label(info_window, text="Subnet Mask:").grid(row=3, column=0, padx=10, pady=10)
            subnet_var = tk.StringVar(info_window, value=device_data["subnet"])
            tk.Entry(info_window, textvariable=subnet_var).grid(row=3, column=1, padx=10, pady=10)

            def validate_ip(ip):
                parts = ip.split(".")
                if len(parts) != 4:
                    return False
                for part in parts:
                    if not part.isdigit() or not 0 <= int(part) <= 255:
                        return False
                return True

            def validate_mac(mac):
                if len(mac) != 17:
                    return False
                for i, char in enumerate(mac):
                    if i % 3 == 2:
                        if char != ':':
                            return False
                    elif char not in string.hexdigits:
                        return False
                return True

            def save_info():
                new_name = name_var.get()
                new_ip = ip_var.get()
                new_mac = mac_var.get()
                new_subnet = subnet_var.get()

                if not validate_ip(new_ip):
                    messagebox.showerror("Invalid IP", "Please enter a valid IP address.")
                    return

                if not validate_mac(new_mac):
                    messagebox.showerror("Invalid MAC", "Please enter a valid MAC address.")
                    return

                device_data["type"] = new_name
                device_data["ip"] = new_ip
                device_data["mac"] = new_mac
                device_data["subnet"] = new_subnet
                self.canvas.itemconfig(device_data["label"], text=device_data["type"])
                self.update_status(f"{device_data['type']} info updated.")
                info_window.destroy()

            tk.Button(info_window, text="Save", command=save_info).grid(row=4, column=0, columnspan=2, pady=10)

    def send_packet(self):
        if not self.devices:
            self.update_status("No devices available to send packets.")
            return

        packet_window = tk.Toplevel(self.root)
        packet_window.title("Send Packet")

        tk.Label(packet_window, text="Source Device:").grid(row=0, column=0, padx=10, pady=10)
        source_var = tk.StringVar(packet_window)
        source_menu = ttk.Combobox(packet_window, textvariable=source_var)
        source_menu['values'] = [data["type"] for data in self.devices.values()]
        source_menu.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(packet_window, text="Destination Device:").grid(row=1, column=0, padx=10, pady=10)
        destination_var = tk.StringVar(packet_window)
        destination_menu = ttk.Combobox(packet_window, textvariable=destination_var)
        destination_menu['values'] = [data["type"] for data in self.devices.values()]
        destination_menu.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(packet_window, text="Protocol:").grid(row=2, column=0, padx=10, pady=10)
        protocol_var = tk.StringVar(packet_window)
        protocol_menu = ttk.Combobox(packet_window, textvariable=protocol_var)
        protocol_menu['values'] = ["UDP", "TCP"]
        protocol_menu.grid(row=2, column=1, padx=10, pady=10)

        def send():
            source = source_var.get()
            destination = destination_var.get()
            protocol = protocol_var.get()

            source_device = None
            destination_device = None

            for device, data in self.devices.items():
                if data["type"] == source:
                    source_device = device
                if data["type"] == destination:
                    destination_device = device

            if not source_device or not destination_device:
                self.update_status("Invalid source or destination device.")
                return

            if protocol.upper() == "UDP":
                self.animate_packet(source_device, destination_device, protocol)
            elif protocol.upper() == "TCP":
                self.animate_packet(source_device, destination_device, protocol)
            else:
                self.update_status("Invalid protocol. Please enter UDP or TCP.")

            packet_window.destroy()

        tk.Button(packet_window, text="Send", command=send).grid(row=3, column=0, columnspan=2, pady=10)

    def animate_packet(self, source_device, destination_device, protocol):
        packet = self.canvas.create_oval(0, 0, 10, 10, fill="red")
        path = self.find_path(source_device, destination_device)
        if protocol.upper() == "TCP":
            path += path[::-1]  # For TCP, the packet returns to the source

        if path:
            self.move_packet(packet, path, 0)
        else:
            self.update_status("No path found between devices.")
            self.canvas.delete(packet)

    def move_packet(self, packet, path, index):
        if index < len(path) - 1:
            x1, y1, x2, y2 = self.canvas.coords(path[index])
            x1, y1 = (x1 + x2) // 2, (y1 + y2) // 2
            x3, y3, x4, y4 = self.canvas.coords(path[index + 1])
            x3, y3 = (x3 + x4) // 2, (y3 + y4) // 2

            self.animate_line(packet, x1, y1, x3, y3, path, index)
        else:
            self.canvas.delete(packet)
            self.update_status("Packet transmission complete.")
            messagebox.showinfo("Success", "Packet transmission complete.")

    def animate_line(self, packet, x1, y1, x2, y2, path, index):
        steps = 20
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps

        def step(i):
            if i <= steps:
                self.canvas.move(packet, dx, dy)
                self.root.after(50, step, i + 1)
            else:
                self.move_packet(packet, path, index + 1)

        self.canvas.coords(packet, x1 - 5, y1 - 5, x1 + 5, y1 + 5)
        step(0)

    def find_path(self, source_device, destination_device):
        # Simple BFS to find the path between source and destination
        queue = [(source_device, [source_device])]
        visited = set()

        while queue:
            current_device, path = queue.pop(0)
            if current_device == destination_device:
                return path

            visited.add(current_device)
            for line in self.devices[current_device]["lines"]:
                for device, data in self.devices.items():
                    if device != current_device and line in data["lines"] and device not in visited:
                        queue.append((device, path + [device]))

        return []

    def on_device_press(self, event):
        # Start dragging the selected device or handle Ethernet connection
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.devices:
            if self.ethernet_mode:
                if self.selected_device is None:
                    self.selected_device = item
                    self.update_status(f"Selected {self.devices[item]['type']} for Ethernet connection.")
                else:
                    if self.selected_device != item:
                        self.create_cable(self.selected_device, item)
                    self.selected_device = None
                    self.ethernet_mode = False
                    self.update_status("Ethernet connection complete.")
            else:
                x1, y1, x2, y2 = self.canvas.coords(item)
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.dragged_device = item
                    self.drag_data = {"x": event.x, "y": event.y}

    def on_device_motion(self, event):
        # Dragging the selected device
        if self.dragged_device:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.dragged_device, dx, dy)
            self.canvas.move(self.devices[self.dragged_device]["label"], dx, dy)
            for line in self.devices[self.dragged_device]["lines"]:
                self.update_line(line)
            self.drag_data = {"x": event.x, "y": event.y}

    def on_device_release(self, event):
        # Clear the dragged device data after releasing
        self.dragged_device = None
        self.drag_data = None


root = tk.Tk()
app = NetworkSimulator(root)
root.mainloop()