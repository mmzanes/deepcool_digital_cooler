# DeepCool Digital Cooler Controller

A universal Python controller for DeepCool digital display coolers that provides real-time CPU temperature and usage monitoring with cross-platform support.

## 🚀 Features

- **Universal Device Support**: Auto-detects DeepCool AG400, AG620, and compatible models
- **Real CPU Temperature**: Uses LibreHardwareMonitor for accurate temperature readings
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Multiple Display Modes**: Temperature, CPU usage, or both (alternating/simultaneous)
- **Robust Fallbacks**: Multiple temperature sources with automatic fallback
- **Easy Setup**: Simple installation and configuration

## 📋 Supported Devices

| Model | VID:PID | Status |
|-------|---------|--------|
| AG620 | 0x3633:0x0008 | ✅ Fully Supported |
| AG400 | 0x3633:0x0009 | ✅ Fully Supported |
| Other DeepCool Digital | 0x3633:0x000A | ⚠️ Basic Support |

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- USB connection to DeepCool digital cooler
- For best temperature accuracy on Windows: LibreHardwareMonitor

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

1. Connect your DeepCool digital cooler via USB
2. Run the controller:
   ```bash
   python main.py
   ```
3. Select your preferred monitoring mode from the menu

## 🎮 Usage

### Interactive Menu Options

1. **Temperature Monitoring** - Display real-time CPU temperature
2. **CPU Usage Monitoring** - Display CPU usage percentage
3. **Both (Alternating)** - Switch between temperature and usage every cycle
4. **Test Display** - Verify display functionality with test values
5. **Quit** - Exit the application

### Example Output

```
DeepCool Digital Cooler Controller
==================================
Universal Windows/Linux Support

Scanning for DeepCool digital coolers...
Connecting to AG620 (VID:0x3633, PID:0x0008)...
Connected successfully!
  Manufacturer: DeepCool
  Product: AG-DIGITAL
  Serial: 400A3F564C38
  Model: AG620
  Mode: complex

Starting monitoring loop for AG620
Temperature: ON
Update interval: 2.0 seconds
Press Ctrl+C to stop

Cycle 0: Temperature 52°C
Cycle 1: Temperature 51°C
Cycle 2: Temperature 53°C
```

## 🌡️ Temperature Sources

The controller uses multiple temperature sources with automatic fallback:

1. **LibreHardwareMonitor** (Windows) - Most accurate, reads CPU Package temperature
2. **psutil** (Cross-platform) - Hardware sensors when available
3. **CPU Usage Estimation** - Fallback based on CPU load

## ⚙️ Configuration

### Device Configuration

The controller automatically detects supported devices using the `DEVICE_CONFIGS` in `deepcool_util.py`. You can add support for additional models by updating this configuration.

### Display Modes

- **Temperature Mode**: Shows CPU temperature in Celsius
- **Usage Mode**: Shows CPU usage as percentage
- **Alternating Mode**: Switches between temperature and usage
- **Simultaneous Mode**: Attempts to show both (device dependent)

## 🔧 Troubleshooting

### Common Issues

**Device Not Found**
- Ensure the cooler is connected
- Check Device Manager (Windows) or `lsusb` (Linux) for the device

**Temperature Shows 0°C**
- Run as Administrator on Windows for LibreHardwareMonitor access
- Install Visual Studio C++ Redistributable for pythonnet
- Check that LibreHardwareMonitor DLL is properly installed

**Permission Errors**
- Run the script as Administrator (Windows) or with sudo (Linux)
- Ensure your user has access to USB devices

### Debug Mode

For debugging, you can test temperature reading directly:

```python
from deepcool_util import get_librehardwaremonitor_temp
temp = get_librehardwaremonitor_temp()
print(f"CPU Temperature: {temp}°C")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Make your changes
4. Test with your DeepCool device
5. Submit a pull request

## 📄 License

This project is open source. Based on the work from [deepcool-digital-info](https://github.com/Algorithm0/deepcool-digital-info).

## 🙏 Acknowledgments

- Original protocol reverse engineering by [Algorithm0](https://github.com/Algorithm0/deepcool-digital-info)
- LibreHardwareMonitor team for the hardware monitoring library
- DeepCool for creating awesome digital coolers

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with your system details and error messages
