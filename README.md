<a href="#">
    <img src="https://raw.githubusercontent.com/pedromxavier/flag-badges/main/badges/TR.svg" alt="made in TR">
</a>

# RevLix (Recovery Linux) - Data Recovery Tool
RevLix is a powerful data recovery tool developed to recover deleted files on Linux systems. This program uses the PhotoRec infrastructure and provides a graphical user interface (GUI) for PhotoRec.


**Note:** Special thanks to [A. Serhet KILIÇOĞLU (Shampuan)](https://github.com/shampuan) for his significant contributions to the development and design.



<h1 align="center">RevLix Logo</h1>

<p align="center">
  <img src="revlixlo.png" alt="RevLix Logo" width="150" height="150">
</p>

# RevLix Data Recovery Tool

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Linux-green.svg" alt="Platform">
  <img src="https://img.shields.io/badge/GUI-PyQt5-orange.svg" alt="GUI Framework">
  <img src="https://img.shields.io/badge/License-GPL--3.0-red.svg" alt="License">
</div>

## 🔍 Overview

**RevLix** is a comprehensive, professional-grade data recovery tool designed to recover deleted files and repair damaged storage devices. Built with a modern PyQt5 interface, it integrates multiple powerful recovery engines into a single, user-friendly application.

### ✨ Key Features

- **🔧 Five Recovery Modes**: PhotoRec, TestDisk, ddrescue, foremost, and S.M.A.R.T. analysis
- **💾 Universal Storage Support**: HDD, SSD, USB drives, SD cards, NVMe drives
- **📁 Multi-Filesystem**: NTFS, FAT32, ext2/3/4, exFAT, HFS+, and more
- **🎯 Real-time Progress Tracking**: Live monitoring of recovery operations
- **🌐 Dual Language Support**: English and Turkish interfaces
- **🛡️ Automatic Privilege Management**: Seamless root access handling
- **📊 Advanced Reporting**: HTML/PDF export for S.M.A.R.T. analysis

## 🚀 Recovery Modes

### 1. 📂 Data Recovery (PhotoRec)
- **Full Disk Scan**: Comprehensive deep scanning
- **Free Space Scan**: Quick deleted file recovery
- **File Type Filtering**: Selective recovery by file extensions
- **Real-time Progress**: Live scan monitoring

### 2. 🔧 Partition Recovery (TestDisk)
- **Safe Analysis Mode**: Read-only partition analysis
- **Advanced Terminal Repair**: Full TestDisk functionality
- **Manual Command Support**: Expert-level control
- **Partition Table Reconstruction**: MBR/GPT repair

### 3. 💿 Disk Imaging (ddrescue)
- **Error Correction**: Advanced bad sector handling
- **Configurable Block Size**: Optimized performance
- **Resume Capability**: Continue interrupted operations
- **Progress Visualization**: Real-time imaging status

### 4. 🖼️ Image Recovery (foremost)
- **File Carving**: Extract files from disk images
- **Multiple Format Support**: Wide range of file types
- **Batch Processing**: Handle multiple images
- **Metadata Preservation**: Maintain file integrity

### 5. 🏥 Disk Health (S.M.A.R.T.)
- **Health Assessment**: Comprehensive disk analysis
- **Predictive Failure**: Early warning system
- **Detailed Reports**: HTML/PDF export options
- **Temperature Monitoring**: Real-time thermal data

## 🛠️ Installation

Linux (based debian) Terminal: Linux (debian based distributions) To install directly from Terminal.
```bash
wget -O Setup_Linux64.deb https://github.com/cektor/RevLix/releases/download/1.1.0/Setup_Linux64.deb && sudo apt install ./Setup_Linux64.deb && sudo apt-get install -f -y
```

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-pyqt5 testdisk gddrescue foremost smartmontools

# Fedora/RHEL
sudo dnf install python3 python3-pip python3-qt5 testdisk ddrescue foremost smartmontools

# Arch Linux
sudo pacman -S python python-pip python-pyqt5 testdisk ddrescue foremost smartmontools
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RevLix.git
   cd RevLix
   ```

2. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Make executable**
   ```bash
   chmod +x revlix.py
   ```

4. **Install system-wide (optional)**
   ```bash
   sudo cp revlix.py /usr/bin/revlix
   sudo cp revlix.desktop /usr/share/applications/
   sudo cp revlixlo.png /usr/share/pixmaps/
   ```

## 🎮 Usage

### Quick Start

```bash
# Run from source
python3 revlix.py

# Or if installed system-wide
revlix
```

### Basic Workflow

1. **Launch RevLix** and select your preferred language
2. **Choose Recovery Mode** from the tabbed interface
3. **Select Target Device** from the automatically detected list
4. **Configure Options** (file types, output directory, etc.)
5. **Start Recovery** and monitor progress in real-time
6. **Review Results** in the specified output directory

### Advanced Usage

#### Command Line Options
```bash
python3 revlix.py --help                    # Show help
python3 revlix.py --lang en                 # Force English
python3 revlix.py --lang tr                 # Force Turkish
python3 revlix.py --debug                   # Enable debug mode
```

#### Configuration Files
- User preferences: `~/.config/revlix/settings.conf`
- Recovery profiles: `~/.config/revlix/profiles/`
- Log files: `~/.local/share/revlix/logs/`

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 18.04+, Fedora 30+, or equivalent)
- **Python**: 3.8 or higher
- **RAM**: 2 GB minimum, 4 GB recommended
- **Storage**: 100 MB for application, additional space for recovered files
- **Display**: 800x700 minimum resolution

### Recommended Requirements
- **RAM**: 8 GB or more for large disk operations
- **Storage**: SSD for faster processing
- **Display**: 1920x1080 for optimal experience

## 🔒 Security & Safety

### Data Protection
- **Read-only Operations**: Safe analysis modes prevent data corruption
- **Backup Verification**: Always verify backups before recovery
- **Progress Logging**: Detailed operation logs for audit trails

### Privilege Management
- **Automatic Elevation**: Seamless root access when required
- **Minimal Permissions**: Only requests necessary privileges
- **Secure Cleanup**: Proper cleanup of temporary files

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/RevLix.git
cd RevLix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for all functions
- Include type hints where appropriate

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This program makes no warranties. The user assumes all responsibility.**

RevLix is provided "as is" without warranty of any kind. Always backup your data before performing recovery operations. The developers are not responsible for any data loss or system damage.

## 🙏 Acknowledgments

RevLix integrates several excellent open-source tools:
- **PhotoRec/TestDisk** - CGSecurity
- **ddrescue** - GNU Project
- **foremost** - US Air Force Office of Special Investigations
- **smartmontools** - Smartmontools Team

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/cektor/RevLix/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cektor/RevLix/discussions)
- **Wiki**: [Project Wiki](https://github.com/cektor/RevLix/wiki)

## 🗺️ Roadmap

- [ ] Windows support
- [ ] macOS support
- [ ] Network recovery capabilities
- [ ] Cloud storage integration
- [ ] Mobile device support
- [ ] Automated recovery scheduling

---

<div align="center">
  <strong>Made with ❤️ for data recovery professionals and enthusiasts</strong>
</div>


