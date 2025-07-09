import time, hid, psutil, platform, os

DEVICE_CONFIGS = {
    (0x3633, 0x0008): {
        "name": "AG620",
        "mode": "complex",
        "rearrange_digits": True,
        "packet_size": 64
    },
    (0x3633, 0x0009): {
        "name": "AG400",
        "mode": "complex",
        "rearrange_digits": True,
        "packet_size": 64
    },
    (0x3633, 0x000A): {
        "name": "Unknown_A",
        "mode": "complex",
        "rearrange_digits": False,
        "packet_size": 64
    }
}

class DeepCoolController:
    def __init__(self):
        self.device = None
        self.device_config = None
        self.is_windows = platform.system() == 'Windows'

    def find_and_connect_device(self) -> bool:
        print("Scanning for DeepCool digital coolers...")
        devices = hid.enumerate()
        found_devices = []
        for device_info in devices:
            vid = device_info['vendor_id']
            pid = device_info['product_id']
            if (vid, pid) in DEVICE_CONFIGS:
                found_devices.append((vid, pid, device_info))
        if not found_devices:
            print("No supported DeepCool digital coolers found!")
            print("Supported models:")
            for (vid, pid), config in DEVICE_CONFIGS.items():
                print(f"  - {config['name']} (VID:0x{vid:04X}, PID:0x{pid:04X})")
            return False
        if len(found_devices) > 1:
            print("Multiple DeepCool devices found:")
            for i, (vid, pid, info) in enumerate(found_devices):
                config = DEVICE_CONFIGS[(vid, pid)]
                print(f"  {i+1}. {config['name']} - {info.get('product_string', 'Unknown')}")
            try:
                choice = int(input("Select device (1-{}): ".format(len(found_devices)))) - 1
                if 0 <= choice < len(found_devices):
                    vid, pid, device_info = found_devices[choice]
                else:
                    print("Invalid choice")
                    return False
            except (ValueError, KeyboardInterrupt):
                print("No device selected")
                return False
        else:
            vid, pid, device_info = found_devices[0]
        self.device_config = DEVICE_CONFIGS[(vid, pid)]
        print(f"Connecting to {self.device_config['name']} (VID:0x{vid:04X}, PID:0x{pid:04X})...")
        try:
            self.device = hid.device()
            self.device.open(vid, pid)
            self.device.set_nonblocking(1)
            manufacturer = self.device.get_manufacturer_string() or "Unknown"
            product = self.device.get_product_string() or "Unknown"
            serial = self.device.get_serial_number_string() or "Unknown"
            print(f"Connected successfully!")
            print(f"  Manufacturer: {manufacturer}")
            print(f"  Product: {product}")
            print(f"  Serial: {serial}")
            print(f"  Model: {self.device_config['name']}")
            print(f"  Mode: {self.device_config['mode']}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def get_bar_value(self, input_value: int) -> int:
        return max(1, (input_value - 1) // 10 + 1)

    def create_packet(self, value: int = 0, mode: str = 'util') -> bytes:
        if not self.device_config:
            raise RuntimeError("Device not connected")
        if self.device_config['mode'] == 'complex':
            return self._create_complex_packet(value, mode)
        else:
            return self._create_simple_packet(value, mode)

    def _create_complex_packet(self, value: int = 0, mode: str = 'util') -> bytes:
        base_data = [16] + [0] * 63
        numbers = [int(char) for char in str(value)]
        base_data[2] = self.get_bar_value(value)
        if mode == 'start':
            base_data[1] = 170
            return bytes(base_data)
        elif mode == 'temp':
            base_data[1] = 19
        elif mode == 'util':
            base_data[1] = 76
        else:
            raise ValueError(f"Unknown mode: {mode}")
        if len(numbers) == 1:
            base_data[5] = numbers[0]
        elif len(numbers) == 2:
            base_data[4] = numbers[0]
            base_data[5] = numbers[1]
        elif len(numbers) == 3:
            base_data[3] = numbers[0]
            base_data[4] = numbers[1]
            base_data[5] = numbers[2]
        elif len(numbers) == 4:
            base_data[3] = numbers[0]
            base_data[4] = numbers[1]
            base_data[5] = numbers[2]
            base_data[6] = numbers[3]
        if self.device_config and self.device_config.get('rearrange_digits', False):
            temp_first_digit = base_data[4]
            temp_second_digit = base_data[5]
            base_data[5] = base_data[3]
            base_data[3] = temp_first_digit
            base_data[4] = temp_second_digit
        return bytes(base_data)

    def _create_simple_packet(self, value: int = 0, mode: str = 'util') -> bytes:
        if mode == 'start':
            return bytes([0x10, 0x01])
        elif mode == 'temp':
            return bytes([0x01, value])
        elif mode == 'util':
            return bytes([0x02, value])
        return bytes([0x00])

    def get_cpu_temperature(self) -> int:
        # Try LibreHardwareMonitor first (Windows, most accurate)
        if self.is_windows:
            try:
                temp = get_librehardwaremonitor_temp()
                if temp is not None:
                    return temp
            except Exception as e:
                print(f"Warning: LibreHardwareMonitor temperature read failed: {e}")

        # Try psutil (Linux/Unix)
        try:
            if not self.is_windows:
                sensors_func = getattr(psutil, 'sensors_temperatures', None)
                if sensors_func:
                    sensors = sensors_func()
                    for sensor_name, sensor_list in sensors.items():
                        if any(keyword in sensor_name.lower() for keyword in ['k10temp', 'coretemp', 'cpu', 'processor']):
                            if sensor_list:
                                return round(sensor_list[0].current)
                    for sensor_name, sensor_list in sensors.items():
                        if sensor_list:
                            return round(sensor_list[0].current)
        except Exception as e:
            print(f"Warning: Could not read temperature ({e}), using estimation")

        return 0

    def get_cpu_usage(self) -> int:
        try:
            return round(psutil.cpu_percent(interval=0.1))
        except Exception:
            return 0

    def initialize_display(self) -> bool:
        if not self.device:
            return False
        try:
            print("Initializing display...")
            init_packet = self.create_packet(mode='start')
            self.device.write(init_packet)
            time.sleep(1)
            print("Display initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize display: {e}")
            return False

    def send_temperature(self, temp: int) -> bool:
        if not self.device:
            return False
        try:
            packet = self.create_packet(value=temp, mode='temp')
            self.device.write(packet)
            return True
        except Exception as e:
            print(f"Failed to send temperature: {e}")
            return False

    def send_usage(self, usage: int) -> bool:
        if not self.device:
            return False
        try:
            packet = self.create_packet(value=usage, mode='util')
            self.device.write(packet)
            return True
        except Exception as e:
            print(f"Failed to send usage: {e}")
            return False

    def run_monitoring_loop(self, show_temp: bool = True, show_usage: bool = True,
                          interval: float = 2.0, alternating: bool = True):
        if not self.device or not self.device_config:
            print("No device connected!")
            return
        print(f"\nStarting monitoring loop for {self.device_config['name']}")
        print(f"Temperature: {'ON' if show_temp else 'OFF'}")
        print(f"CPU Usage: {'ON' if show_usage else 'OFF'}")
        print(f"Update interval: {interval} seconds")
        if show_temp and show_usage:
            print(f"Mode: {'Alternating' if alternating else 'Simultaneous'}")
        print("Press Ctrl+C to stop\n")
        cycle = 0
        try:
            while True:
                temp = self.get_cpu_temperature()
                usage = self.get_cpu_usage()
                if show_temp and show_usage:
                    if alternating:
                        if cycle % 2 == 0:
                            self.send_temperature(temp)
                            print(f"Cycle {cycle}: Temperature {temp}°C")
                        else:
                            self.send_usage(usage)
                            print(f"Cycle {cycle}: CPU Usage {usage}%")
                    else:
                        self.send_temperature(temp)
                        time.sleep(0.1)
                        self.send_usage(usage)
                        print(f"Cycle {cycle}: Temp {temp}°C, Usage {usage}%")
                elif show_temp:
                    self.send_temperature(temp)
                    print(f"Cycle {cycle}: Temperature {temp}°C")
                elif show_usage:
                    self.send_usage(usage)
                    print(f"Cycle {cycle}: CPU Usage {usage}%")
                cycle += 1
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped by user")

    def test_display(self):
        if not self.device or not self.device_config:
            print("No device connected!")
            return
        print(f"\nTesting {self.device_config['name']} display...")
        test_values = [
            (25, 'temp', "25°C"),
            (50, 'temp', "50°C"),
            (75, 'temp', "75°C"),
            (25, 'util', "25%"),
            (50, 'util', "50%"),
            (75, 'util', "75%"),
        ]
        for value, mode, description in test_values:
            print(f"Displaying {description}...")
            if mode == 'temp':
                self.send_temperature(value)
            else:
                self.send_usage(value)
            time.sleep(2)
            response = input(f"Do you see {description} on display? (y/n/q): ")
            if response.lower() == 'q':
                break
            elif response.lower() == 'y':
                print(f"✓ {description} working correctly")
            else:
                print(f"✗ {description} not displaying correctly")

    def close(self):
        if self.device:
            try:
                self.device.close()
                print("Device connection closed")
            except:
                pass
            self.device = None

def get_librehardwaremonitor_temp():
    """
    Get CPU Package temperature using LibreHardwareMonitor.
    Requires LibreHardwareMonitorLib.dll in LibreHardwareMonitor-net472 subdirectory.
    Returns temperature in Celsius or None if failed.
    """
    try:
        import clr
        import sys

        # Path to LibreHardwareMonitor DLL
        dll_dir = os.path.abspath("LibreHardwareMonitor")
        dll_path = os.path.join(dll_dir, "LibreHardwareMonitorLib.dll")

        if not os.path.exists(dll_path):
            return None  # Silent fail if DLL not found

        # Add DLL directory to path and change to it
        if dll_dir not in sys.path:
            sys.path.insert(0, dll_dir)

        original_cwd = os.getcwd()
        os.chdir(dll_dir)

        try:
            # Load the DLL
            clr.AddReference("LibreHardwareMonitorLib") # type: ignore
            import LibreHardwareMonitor.Hardware as Hardware # type: ignore

            # Create computer object and enable CPU monitoring
            computer = Hardware.Computer()
            computer.IsCpuEnabled = True

            # Try to open hardware access (may require admin privileges)
            try:
                computer.Open()
            except Exception:
                # Silent fail if cannot access hardware
                return None

            # Look for CPU Package temperature sensor only
            for hardware in computer.Hardware:
                if hardware.HardwareType == Hardware.HardwareType.Cpu:
                    hardware.Update()
                    for sensor in hardware.Sensors:
                        if (sensor.SensorType == Hardware.SensorType.Temperature and
                            sensor.Name and sensor.Value is not None):
                            # Only return CPU Package temperature
                            if "package" in sensor.Name.lower():
                                temp = float(sensor.Value)
                                computer.Close()
                                # Sanity check
                                # Mitigate spikes: ignore sudden jumps from previous value (store last value as attribute)
                                if not hasattr(get_librehardwaremonitor_temp, "_last_temp"):
                                        get_librehardwaremonitor_temp._last_temp = temp
                                last_temp = get_librehardwaremonitor_temp._last_temp
                                if (temp - last_temp) > last_temp * 0.10:
                                        # Ignore spike, return last value
                                        print(f"Spike detected: {temp}°C (last: {last_temp}°C), ignoring")
                                        return round(last_temp)
                                get_librehardwaremonitor_temp._last_temp = temp
                                return round(temp)

            computer.Close()
            return None

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    except ImportError:
        return None  # pythonnet not available
    except Exception:
        return None  # Any other error
