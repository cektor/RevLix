#!/usr/bin/env python3
# -----| Coder By Fatih ÖNDER (CekToR) |-----
# -----| GitHub:https://github.com/cektor
import sys
import subprocess
import os
import tempfile
import glob
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QComboBox, QTextEdit, 
                             QFileDialog, QProgressBar, QCheckBox, QGroupBox, 
                             QGridLayout, QMessageBox, QRadioButton, QButtonGroup, QDesktopWidget,
                             QMenuBar, QAction, QDialog, QScrollArea)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QIcon, QPixmap, QDesktopServices
from PyQt5.QtCore import QUrl

# Qt platform plugin sorununu çözmek için ortam değişkenlerini ayarla
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_PLUGIN_PATH'] = ''


class PhotorecWorker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    progress_signal = pyqtSignal(str)
    
    def __init__(self, device, output_dir, file_types, scan_mode, filesystem, language='tr'):
        super().__init__()
        self.device = device
        self.output_dir = output_dir
        self.file_types = file_types
        self.scan_mode = scan_mode  # 'whole' veya 'free'
        self.filesystem = filesystem  # 'ext2/ext3', 'ntfs', 'fat32' vs.
        self.language = language
    
    def tr(self, key, *args):
        """Çeviri fonksiyonu"""
        text = TRANSLATIONS.get(self.language, {}).get(key, key)
        if args:
            return text.format(*args)
        return text
        
    def run(self):
        try:
            # Photorec konfigürasyon dosyası oluştur
            config_content = self.create_photorec_config()
            
            # Geçici config dosyası (sadece log için)
            config_file = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
                    f.write(config_content)
                    config_file = f.name
            except:
                pass
            
            base_cmd = ['sudo'] if os.geteuid() != 0 else []
            
            # Photorec komutunu doğru parametrelerle çalıştır
            self.output_signal.emit(self.tr('preparing_recovery'))
            
            # Photorec için basit ve çalışan komut yapısı - çıktı dizinini doğru ayarla
            cmd = base_cmd + ['photorec', '/d', self.output_dir + '/', '/cmd', self.device]
            
            # Photorec otomatik parametreleri
            if self.scan_mode == 'free':
                # Boş alan taraması için
                cmd.extend(['partition_none', 'search'])
            else:
                # Tüm disk taraması için - en basit hali
                cmd.extend(['search'])
           
            self.progress_signal.emit("🔄 Kurtarma çalışıyor...")
            line_count = 0
            
            # Gerçek zamanlı çıktı okuma
            while True:
                # Process durumunu kontrol et
                if process.poll() is not None:
                    break
                    
                # Stdout'u oku
                output = process.stdout.readline()
                if output:
                    line = output.strip()
                    if line:
                        line_count += 1
                        # İlerleme bilgilerini filtrele ve göster
                        if any(keyword in line.lower() for keyword in ['recovered', 'elapsed', 'remaining', 'pass', 'sector']):
                            self.output_signal.emit(f"🔄 {line}")
                            self.progress_signal.emit(f"📊 Tarama devam ediyor... ({line_count} satır)")
                        elif any(keyword in line.lower() for keyword in ['error', 'warning', 'failed', 'unable']):
                            self.output_signal.emit(f"⚠️ {line}")
                        elif any(keyword in line.lower() for keyword in ['found', 'jpg', 'png', 'pdf', 'doc', 'mp3', 'mp4']):
                            self.output_signal.emit(f"📄 {line}")
                            self.progress_signal.emit(f"📄 Dosyalar bulunuyor...")
                        elif 'photorec' in line.lower() and 'data recovery' in line.lower():
                   
                            self.progress_signal.emit(self.tr('recovery_started'))
                        else:
                            self.output_signal.emit(line)
                            if line_count % 10 == 0:  # Her 10 satırda bir güncelle
                                self.progress_signal.emit(f"⚡ İşlem aktif... ({line_count} satır)")
            
                    # Otomatik girişler - Enter tuşları
                    inputs = "\n" * 10  # 10 kez Enter
                    stdout, stderr = simple_process.communicate(input=inputs, timeout=30)
                    
                    if stdout:
                        for line in stdout.split('\n'):
                            if line.strip():
                                self.output_signal.emit(f"📋 {line.strip()}")
                    
                    if stderr:
                        for line in stderr.split('\n'):
                            if line.strip():
                                self.output_signal.emit(f"⚠️ {line.strip()}")
                                
                except subprocess.TimeoutExpired:
                    self.output_signal.emit("⏰ Alternatif komut zaman aşımı")
                    simple_process.kill()
                except Exception as e:
                    self.output_signal.emit(f"❌ Alternatif komut hatası: {str(e)}")
            else:
                self.output_signal.emit(f"\n{self.tr('recovery_completed_normally')}")
            
            self.output_signal.emit(f"\n{self.tr('checking_results')}")
            
            # Sonuçları kontrol et
            recovered_dirs = []
            total_files = 0
            
            if os.path.exists(self.output_dir):
                files = os.listdir(self.output_dir)
                recovered_dirs = [f for f in files if f.startswith('recup_dir')]
                
                if recovered_dirs:
                    for rec_dir in recovered_dirs:
                        rec_path = os.path.join(self.output_dir, rec_dir)
                        if os.path.isdir(rec_path):
                            try:
                                dir_files = os.listdir(rec_path)
                                file_count = len([f for f in dir_files if os.path.isfile(os.path.join(rec_path, f))])
                                total_files += file_count
                                self.output_signal.emit(f"📁 {rec_dir}: {self.tr('files_found', file_count)}")
                            except:
                                pass
                    
                    self.output_signal.emit(f"\n{self.tr('recovery_success', len(recovered_dirs))}")
                    self.output_signal.emit(self.tr('total_files_recovered', total_files))
                    self.output_signal.emit(self.tr('location', self.output_dir))
                    
                    # Dosya türlerini analiz et
                    file_types_found = {}
                    for rec_dir in recovered_dirs:
                        rec_path = os.path.join(self.output_dir, rec_dir)
                        if os.path.isdir(rec_path):
                            try:
                                for f in os.listdir(rec_path):
                                    if os.path.isfile(os.path.join(rec_path, f)):
                                        ext = f.split('.')[-1].lower() if '.' in f else 'unknown'
                                        file_types_found[ext] = file_types_found.get(ext, 0) + 1
                            except:
                                pass
                    
                    if file_types_found:
                        self.output_signal.emit(f"\n{self.tr('found_file_types')}")
                        for ext, count in sorted(file_types_found.items(), key=lambda x: x[1], reverse=True):
                            self.output_signal.emit(self.tr('file_type_count', ext.upper(), count))
                else:
                    self.output_signal.emit(f"\n{self.tr('no_recovery_dirs')}")
                    
                    # Doğrudan çıktı dizinindeki dosyaları kontrol et
                    all_files = [f for f in files if os.path.isfile(os.path.join(self.output_dir, f))]
                    if all_files:
                        self.output_signal.emit(f"📄 {len(all_files)} {self.tr('files_found_direct')}")
                        # İlk birkaç dosyayı listele
                        for i, f in enumerate(all_files[:5]):
                            self.output_signal.emit(f"  - {f}")
                        if len(all_files) > 5:
                            self.output_signal.emit(f"  ... {self.tr('more_files', len(all_files)-5)}")
                    else:
                        self.output_signal.emit(f"\n{self.tr('possible_reasons')}")
                        self.output_signal.emit(self.tr('reason_disk_clean'))
                        self.output_signal.emit(self.tr('reason_wrong_disk'))
                        self.output_signal.emit(self.tr('reason_file_type'))
                        self.output_signal.emit(self.tr('reason_filesystem'))
                        self.output_signal.emit(self.tr('reason_disk_damaged'))
                        self.output_signal.emit(f"\n{self.tr('suggestions')}")
                        self.output_signal.emit(self.tr('suggestion_root'))
                        self.output_signal.emit(self.tr('suggestion_connection'))
                        self.output_signal.emit(self.tr('suggestion_different_disk'))
                        self.output_signal.emit(self.tr('suggestion_permissions'))
                        self.output_signal.emit(self.tr('suggestion_testdisk'))
                        self.output_signal.emit(f"\n{self.tr('manual_test')}")
                        self.output_signal.emit(f"  sudo photorec /d {self.output_dir} {self.device}")
            else:
                self.output_signal.emit("\n❌ Çıktı dizini erişilemez veya oluşturulamadı")
                self.output_signal.emit(f"Kontrol edilen dizin: {self.output_dir}")
            
            # Başarı durumunu belirle - return code 0 olmasa bile dosya kurtarılmış olabilir
            success = (return_code == 0) or (len(recovered_dirs) > 0 and total_files > 0)
            self.finished_signal.emit(success)
            
            # Config dosyasını temizle
            if config_file:
                try:
                    os.unlink(config_file)
                except:
                    pass
            
  
    
    def update_ui_texts(self):
        """UI metinlerini güncelle"""
        self.setWindowTitle(self.tr('window_title'))
        self.title_label.setText(self.tr('window_title'))
        self.disk_group.setTitle(self.tr('disk_selection'))
        self.disk_label.setText(self.tr('disk'))
        self.output_group.setTitle(self.tr('output_directory'))
        if self.output_label.text() == 'Seçilmedi' or self.output_label.text() == 'Not Selected':
            self.output_label.setText(self.tr('not_selected'))
        self.output_btn.setText(self.tr('select_directory'))
        self.scan_group.setTitle(self.tr('scan_options'))
        self.scan_mode_label.setText(self.tr('scan_mode'))
        self.whole_disk_radio.setText(self.tr('whole_disk'))
        self.free_space_radio.setText(self.tr('free_space_only'))
        self.filesystem_label.setText(self.tr('file_system'))
        self.start_btn.setText(self.tr('start_recovery'))
        self.stop_btn.setText(self.tr('stop'))
        self.status_label.setText(self.tr('ready'))
        self.help_menu.setTitle(self.tr('help'))
        self.about_action.setText(self.tr('about'))
        self.language_menu.setTitle(self.tr('language'))
        
        # Filesystem combo güncelle
        current_fs = self.filesystem_combo.currentIndex()
        self.filesystem_combo.clear()
        self.filesystem_combo.addItems([
            self.tr('auto_detect'),
            'ext2/ext3/ext4', 
            'NTFS',
            'FAT32',
            'exFAT',
            'HFS+',
            'UFS'
        ])
        self.filesystem_combo.setCurrentIndex(current_fs)
    
    def load_logo(self):
        """Logo dosyasını yükle"""
        try:
            # Logo dosyasını /usr/share/pixmaps dizininde ara
            logo_path = '/usr/share/pixmaps/revlixlo.png'
            
            if os.path.exists(logo_path):
                self.logo_pixmap = QPixmap(logo_path)
                self.logo_icon = QIcon(logo_path)
                # Pencere ikonunu ayarla
                self.setWindowIcon(self.logo_icon)
            else:
                self.logo_pixmap = None
                self.logo_icon = None
        except Exception as e:
            print(f"Logo yüklenemedi: {e}")
            self.logo_pixmap = None
            self.logo_icon = None
    
    def center_window(self):
        """Pencereyi ekranın ortasına konumlandır"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
    def init_ui(self):
        self.setWindowTitle("RevLix - Data Recovery Tool")
        #self.setFixedSize(500, 600)
        self.center_window()
        
        # Menü çubuğu
        menubar = self.menuBar()
        
        # Dil menüsü
        self.language_menu = menubar.addMenu(self.tr('language'))
        
        turkish_action = QAction(self.tr('turkish'), self)
        turkish_action.triggered.connect(lambda: self.change_language('tr'))
        self.language_menu.addAction(turkish_action)
        
        english_action = QAction(self.tr('english'), self)
        english_action.triggered.connect(lambda: self.change_language('en'))
        self.language_menu.addAction(english_action)
        
        # Yardım menüsü
        self.help_menu = menubar.addMenu(self.tr('help'))
        
        self.about_action = QAction(self.tr('about'), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Başlık ve logo
        header_layout = QHBoxLayout()
        
        # Logo
        if self.logo_pixmap:
            logo_label = QLabel()
            scaled_logo = self.logo_pixmap.scaled(32, 32, 1, 1)  # 32x32 boyutunda
            logo_label.setPixmap(scaled_logo)
            header_layout.addWidget(logo_label)
        
        # Başlık
        self.title_label = QLabel(self.tr('window_title'))
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4ff; margin-left: 10px;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Disk seçimi
        self.disk_group = QGroupBox(self.tr('disk_selection'))
        disk_layout = QVBoxLayout(self.disk_group)
        
        self.disk_combo = QComboBox()
        self.refresh_disks()
        self.disk_label = QLabel(self.tr('disk'))
        disk_layout.addWidget(self.disk_label)
        disk_layout.addWidget(self.disk_combo)
        
        layout.addWidget(self.disk_group)
        
        # Çıktı dizini
        self.output_group = QGroupBox(self.tr('output_directory'))
        output_layout = QHBoxLayout(self.output_group)
        
        self.output_label = QLabel(self.tr('not_selected'))
        self.output_btn = QPushButton(self.tr('select_directory'))
        self.output_btn.clicked.connect(self.select_output_dir)
        
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        layout.addWidget(self.output_group)
        
        # Tarama seçenekleri
        self.scan_group = QGroupBox(self.tr('scan_options'))
        scan_layout = QVBoxLayout(self.scan_group)
        
        # Tarama modu
        mode_layout = QHBoxLayout()
        self.scan_mode_label = QLabel(self.tr('scan_mode'))
        mode_layout.addWidget(self.scan_mode_label)
        
        self.scan_mode_group = QButtonGroup()
        self.whole_disk_radio = QRadioButton(self.tr('whole_disk'))
        self.free_space_radio = QRadioButton(self.tr('free_space_only'))
        self.whole_disk_radio.setChecked(True)
        
        self.scan_mode_group.addButton(self.whole_disk_radio, 0)
        self.scan_mode_group.addButton(self.free_space_radio, 1)
        
        mode_layout.addWidget(self.whole_disk_radio)
        mode_layout.addWidget(self.free_space_radio)
        mode_layout.addStretch()
        scan_layout.addLayout(mode_layout)
        
        # Dosya sistemi seçimi
        fs_layout = QHBoxLayout()
        self.filesystem_label = QLabel(self.tr('file_system'))
        fs_layout.addWidget(self.filesystem_label)
        
        self.filesystem_combo = QComboBox()
        self.filesystem_combo.addItems([
            self.tr('auto_detect'),
            'ext2/ext3/ext4', 
            'NTFS',
            'FAT32',
            'exFAT',
            'HFS+',
            'UFS'
        ])
        
        fs_layout.addWidget(self.filesystem_combo)
        fs_layout.addStretch()
        scan_layout.addLayout(fs_layout)
        
        layout.addWidget(self.scan_group)
        
        # Dosya türleri bölümü gizlendi - şimdilik kullanılmayacak
        self.file_checkboxes = {}  # Boş dictionary, tüm türler aranacak
        
        # Kontrol butonları
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton(self.tr('start_recovery'))
        self.start_btn.clicked.connect(self.start_recovery)
        self.stop_btn = QPushButton(self.tr('stop'))
        self.stop_btn.clicked.connect(self.stop_recovery)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)
        
      
        
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #ffffff;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #404040;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
            }
            QCheckBox {
                spacing: 5px;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 3px;
            }
            QRadioButton {
                spacing: 5px;
                color: #ffffff;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 9px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 6px 12px;
                border-radius: 3px;
                color: #ffffff;
                min-width: 60px;
            }
        """)
        
    def refresh_disks(self):
        current_selection = self.disk_combo.currentData()
        self.disk_combo.clear()
        
        try:
            # Disk bilgilerini al
            result = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME,SIZE,MODEL,VENDOR'], 
                                  capture_output=True, text=True)
            
            # Disk etiketlerini ayrı komutla al
            label_result = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME,LABEL'], 
                                        capture_output=True, text=True)
            
            # Etiketleri dictionary'de sakla
            disk_labels = {}
            for line in label_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(None, 1)
                    if len(parts) >= 2:
                        disk_labels[parts[0]] = parts[1]
            
            new_disk_list = []
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(None, 3)  # En fazla 4 parçaya böl
                    if len(parts) >= 2:
                        name = parts[0]
                        size = parts[1]
                        model = parts[2] if len(parts) > 2 else 'Bilinmeyen'
                        vendor = parts[3] if len(parts) > 3 else ''
                        label = disk_labels.get(name, '')
                        
                        device_path = f"/dev/{name}"
                        new_disk_list.append(device_path)
                        
                        # Disk etiketini kontrol et
                        if label and label.strip():
                            disk_label = f'"{label.strip()}"'
                        elif vendor and model != 'Bilinmeyen':
                            disk_label = f"{vendor} {model}".strip()
                        elif model != 'Bilinmeyen':
                            disk_label = model
                        else:
                            disk_label = "Bilinmeyen Disk"
                        
                        disk_name = f"/dev/{name} ({size}) - {disk_label}"
                        self.disk_combo.addItem(disk_name, device_path)
            
            # Disk değişikliği kontrolü
            if new_disk_list != self.last_disk_list and hasattr(self, 'output_text'):
                added = set(new_disk_list) - set(self.last_disk_list)
                removed = set(self.last_disk_list) - set(new_disk_list)
                
                if added:
                    for disk in added:
                        self.output_text.append(self.tr('disk_connected', disk))
                if removed:
                    for disk in removed:
                        self.output_text.append(self.tr('disk_disconnected', disk))
                        
            self.last_disk_list = new_disk_list
            
            # Önceki seçimi geri yükle
            if current_selection:
                for i in range(self.disk_combo.count()):
                    if self.disk_combo.itemData(i) == current_selection:
                        self.disk_combo.setCurrentIndex(i)
                        break
            
            if self.disk_combo.count() == 0:
                self.disk_combo.addItem(self.tr('no_disk_found'), None)
                
        except Exception as e:
            if hasattr(self, 'output_text'):
                self.output_text.append(self.tr('disk_list_error', str(e)))
            self.disk_combo.addItem(self.tr('disk_list_error_msg'), None)
            
    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, self.tr('select_directory'))
        if dir_path:
            # Seçilen dizinin kendisini kullan, üst dizinine çıkma
            self.output_label.setText(dir_path)
            # Dizinin yazılabilir olup olmadığını kontrol et
            if not os.access(dir_path, os.W_OK):
                QMessageBox.warning(self, self.tr('warning'), self.tr('directory_not_writable', dir_path))
            
    def show_about(self):
        """Hakkında dialogunu göster"""
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr('about_title'))
        dialog.setFixedSize(700, 600)  # Biraz daha geniş ve uzun
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 2px solid #404040;
                border-radius: 10px;
            }
            QLabel {
                color: #ffffff;
            }
            .title {
                font-size: 24px;
                font-weight: bold;
                color: #00d4ff;
                margin: 15px;
            }
            .subtitle {
                font-size: 14px;
                color: #888888;
            }
            .section-title {
                font-size: 16px;
                font-weight: bold;
                color: #00ff00;
                margin-top: 20px;
            }
            .content {
                font-size: 12px;
                line-height: 1.6;
                color: #ffffff;
            }
            .links {
                color: #00d4ff;
                text-decoration: none;
            }
            .thanks {
                font-style: italic;
                color: #888888;
            }
            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Logo ve başlık
        header_layout = QHBoxLayout()
        if self.logo_pixmap:
            logo_label = QLabel()
            scaled_logo = self.logo_pixmap.scaled(80, 80, 1, 1)
            logo_label.setPixmap(scaled_logo)
            header_layout.addWidget(logo_label)

        title_layout = QVBoxLayout()
        title = QLabel("RevLix")
        title.setProperty('class', 'title')
        subtitle = QLabel("Data Recovery Tool for PhotoRec")
        subtitle.setProperty('class', 'subtitle')
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)

        # Program bilgisi
        info_section = QLabel()
        info_section.setProperty('class', 'section-title')
        if self.current_language == 'tr':
            info_section.setText("📋 Program Bilgileri")
        else:
            info_section.setText("📋 Program Information")
        scroll_layout.addWidget(info_section)

        # Program açıklaması eklendi
        description = QLabel()
        description.setProperty('class', 'content')
        if self.current_language == 'tr':
            description.setText("""
RevLix, silinmiş verilerinizi kurtarmak için geliştirilmiş güçlü bir veri kurtarma aracıdır.
Bu program PhotoRec alt yapısını kullanır ve PhotoRec için grafiksel kullanıcı arayüzü sunar.
Bu Program Hiçbir Garanti Vermez. Kullanıcı Tüm Sorumluluğu Üstlenir.
        """)
        else:
            description.setText("""
RevLix is a powerful data recovery tool developed to recover deleted files.
This program uses PhotoRec infrastructure and provides graphical user interface for PhotoRec.
This Program Makes No Warranties. The User Assumes All Responsibility.
        """)
        description.setWordWrap(True)
        scroll_layout.addWidget(description)

        features = QLabel()
        if self.current_language == 'tr':
            features.setText("""
• Güçlü veri kurtarma motoru
• Tüm disk türlerini destekler (HDD, SSD, USB, SD Kart)
• Çoklu dosya sistemi desteği
• Otomatik disk algılama ve izleme
• Gerçek zamanlı ilerleme takibi
• Kolay kullanımlı grafiksel arayüz
• Otomatik root yetki yönetimi
• Otomatik dosya izinleri düzeltme
        """)
        else:
            features.setText("""
• Powerful data recovery engine
• Supports all disk types (HDD, SSD, USB, SD Card)
• Multiple file system support
• Automatic disk detection and monitoring
• Real-time progress tracking
• Easy-to-use graphical interface
• Automatic root privilege management
• Automatic file permission correction
        """)
        features.setProperty('class', 'content')
        scroll_layout.addWidget(features)

        # Tarama modları
        modes_section = QLabel()
        modes_section.setProperty('class', 'section-title')
        if self.current_language == 'tr':
            modes_section.setText("🔍 Tarama Modları")
        else:
            modes_section.setText("🔍 Scan Modes")
        scroll_layout.addWidget(modes_section)

        modes = QLabel()
        if self.current_language == 'tr':
            modes.setText("""
• Tüm Disk Tarama: Kapsamlı ve detaylı tarama
• Boş Alan Tarama: Hızlı silinen dosya tarama
        """)
        else:
            modes.setText("""
• Whole Disk Scan: Comprehensive and detailed scan
• Free Space Scan: Fast deleted file scan
        """)
        modes.setProperty('class', 'content')
        scroll_layout.addWidget(modes)

        # Geliştirici bilgileri
        dev_section = QLabel()
        dev_section.setProperty('class', 'section-title')
        dev_section.setText("👨‍💻 Developer Information")
        scroll_layout.addWidget(dev_section)

        developers = QLabel()
        developers.setTextFormat(1)  # Qt.RichText
        developers.linkActivated.connect(lambda url: QDesktopServices.openUrl(QUrl(url)))
        if self.current_language == 'tr':
            developers.setText("""
<span style='color: #00d4ff; font-weight: bold;'>Geliştiriciler:</span><br>
• A. Serhat KILIÇOĞLU (shampuan)<br>
  <a href='https://github.com/shampuan' style='color: #00d4ff;'>github.com/shampuan</a><br>
• Fatih ÖNDER (CekToR)<br>
  <a href='https://github.com/cektor' style='color: #00d4ff;'>github.com/cektor</a><br>
<br>
<span style='color: #00d4ff; font-weight: bold;'>Şirket:</span><br>
ALG Yazılım & Elektronik Inc.<br>
<a href='mailto:info@algyazilim.com' style='color: #00d4ff;'>info@algyazilim.com</a><br>
<a href='https://algyazilim.com' style='color: #00d4ff;'>algyazilim.com</a><br>
<a href='https://github.com/cektor/RevLix' style='color: #00d4ff;'>github.com/cektor/RevLix</a>
        """)
        else:
            developers.setText("""
<span style='color: #00d4ff; font-weight: bold;'>Developers:</span><br>
• A. Serhat KILIÇOĞLU (shampuan)<br>
  <a href='https://github.com/shampuan' style='color: #00d4ff;'>github.com/shampuan</a><br>
• Fatih ÖNDER (CekToR)<br>
  <a href='https://github.com/cektor' style='color: #00d4ff;'>github.com/cektor</a><br>
<br>
<span style='color: #00d4ff; font-weight: bold;'>Company:</span><br>
ALG Software & Electronics Inc.<br>
<a href='mailto:info@algyazilim.com' style='color: #00d4ff;'>info@algyazilim.com</a><br>
<a href='https://algyazilim.com' style='color: #00d4ff;'>algyazilim.com</a><br>
<a href='https://github.com/cektor/RevLix' style='color: #00d4ff;'>github.com/cektor/RevLix</a>
        """)
        developers.setProperty('class', 'content')
        scroll_layout.addWidget(developers)

        # Teknik bilgiler
        tech_section = QLabel()
        tech_section.setProperty('class', 'section-title')
        if self.current_language == 'tr':
            tech_section.setText("🔧 Teknik Bilgiler")
        else:
            tech_section.setText("🔧 Technical Information")
        scroll_layout.addWidget(tech_section)

        tech = QLabel()
        if self.current_language == 'tr':
            tech.setText("""
• Lisans: ALG Yazılım Inc. Lisansı
• Alt Yapı: PhotoRec (TestDisk Paketi)
• Geliştirme: Python 3 + PyQt5
• RevLix Program Sürümü: 1.0.0
        """)
        else:
            tech.setText("""
• License: ALG Software Inc. License
• Backend: PhotoRec (TestDisk Package)
• Development: Python 3 + PyQt5
• RevLix Program Version: 1.0.0
        """)
        tech.setProperty('class', 'content')
        scroll_layout.addWidget(tech)

        # Teşekkür
        thanks = QLabel()
        if self.current_language == 'tr':
            thanks.setText("""
🙏 Teşekkürler:
Bu program, açık kaynak PhotoRec projesinin güçlü veri kurtarma
motorunu kullanmaktadır. PhotoRec geliştiricilerine teşekkürler.
        """)
        else:
            thanks.setText("""
🙏 Thanks:
This program uses the powerful data recovery
engine of the open source PhotoRec project. Thanks to PhotoRec developers.
        """)
        thanks.setProperty('class', 'thanks')
        scroll_layout.addWidget(thanks)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Kapat butonu
        close_btn = QPushButton(self.tr('close'))
        close_btn.clicked.connect(dialog.close)
        close_btn.setFixedWidth(120)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        dialog.exec_()
    
    # Dosya türü fonksiyonları kaldırıldı - şimdilik kullanılmayacak
            
    def start_recovery(self):
        device = self.disk_combo.currentData()
        output_dir = self.output_label.text()
        
        if not device:
            QMessageBox.warning(self, self.tr('error'), self.tr('select_disk'))
            return
            
        if output_dir == self.tr('not_selected'):
            QMessageBox.warning(self, self.tr('error'), self.tr('select_output'))
            return
            
        # Çıktı dizini kontrolü
        if not os.path.exists(output_dir):
            QMessageBox.critical(self, self.tr('error'), f"{self.tr('directory_not_exist')}\n{output_dir}")
            return
            
        if not os.access(output_dir, os.W_OK):
            reply = QMessageBox.question(self, self.tr('warning'), f"{self.tr('no_write_permission')}\n{output_dir}\n\n{self.tr('continue_anyway')}",
                              QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            
        selected_types = [ft for ft, cb in self.file_checkboxes.items() if cb.isChecked()]
        
        # Tarama modu
        scan_mode = 'free' if self.free_space_radio.isChecked() else 'whole'
        
        # Dosya sistemi
        fs_text = self.filesystem_combo.currentText()
        filesystem = None
        if fs_text != self.tr('auto_detect'):
            fs_map = {
                "ext2/ext3/ext4": "ext2",
                "NTFS": "ntfs", 
                "FAT32": "fat32",
                "exFAT": "exfat",
                "HFS+": "hfs",
                "UFS": "ufs"
            }
            filesystem = fs_map.get(fs_text)
        
        # PhotoRec kontrolü - artık başlangıçta yapılıyor
        try:
            subprocess.run(['which', 'photorec'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, self.tr('error'), f"{self.tr('telemetry_not_found')}\n\n{self.tr('install_error_msg')}")
            return
            
        # Disk erişim kontrolü
        if not os.path.exists(device):
            QMessageBox.critical(self, self.tr('error'), f"{self.tr('disk_not_found')} {device}\n\n{self.tr('refresh_disk_list')}")
            return
            
        # Root yetkisi zaten kontrol edildi, program her zaman root ile başlıyor
            
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText(self.tr('starting_recovery'))
        self.output_text.clear()
        
        self.worker = PhotorecWorker(device, output_dir, selected_types, scan_mode, filesystem, self.current_language)
        self.worker.output_signal.connect(self.update_output)
        self.worker.finished_signal.connect(self.recovery_finished)
        self.worker.progress_signal.connect(self.update_status)
        self.worker.start()
        
    # restart_with_sudo artık gerekli değil - program zaten root ile başlıyor
        
  
        # Çıktı klasörünün ve PhotoRec'in oluşturduğu tüm klasörlerin izinlerini düzelt
        output_dir = self.output_label.text()
        if output_dir != self.tr('not_selected') and os.path.exists(output_dir):
            try:
                # Ana çıktı klasörünü düzelt
                subprocess.run(['chmod', '-R', '777', output_dir], check=True)
                
                # PhotoRec'in oluşturduğu .1, .2 vb. klasörleri bul ve düzelt
                parent_dir = os.path.dirname(output_dir)
                base_name = os.path.basename(output_dir)
                
                for item in os.listdir(parent_dir):
                    if item.startswith(base_name + '.'):
                        extra_dir = os.path.join(parent_dir, item)
                        if os.path.isdir(extra_dir):
                            subprocess.run(['chmod', '-R', '777', extra_dir], check=True)
                            self.output_text.append(f"📁 {self.tr('additional_folder_permissions')} {extra_dir}")
                
                self.output_text.append(f"📁 {self.tr('all_output_permissions_fixed')}")
            except Exception as e:
                self.output_text.append(f"⚠️ İzin düzeltme hatası: {str(e)}")
        
        if success:
            self.output_text.append(f"\n✅ {self.tr('recovery_completed_success')}")
            QMessageBox.information(self, self.tr('success'), self.tr('recovery_completed'))
        else:
            self.output_text.append("\n❌ Kurtarma işlemi durdu veya hata oluştu.")

    def check_photorec_installation(self):
        """PhotoRec kurulumunu kontrol et ve gerekirse kur"""
        try:
            # PhotoRec'in kurulu olup olmadığını kontrol et
            result = subprocess.run(['which', 'photorec'], capture_output=True, text=True)
            if result.returncode == 0:
                self.output_text.append(self.tr('telemetry_found'))
                photorec_path = result.stdout.strip()
              #  self.output_text.append(f"📍 Konum: {photorec_path}")
                
                # Sürüm bilgisini al
                try:
                    version_result = subprocess.run(['photorec', '/version'], capture_output=True, text=True, timeout=5)
                    if version_result.stdout:
                        version_line = version_result.stdout.split('\n')[0]
                      #  self.output_text.append(f"📋 {version_line}")
                except:
                    pass
                    
                return True
            else:
                self.output_text.append("⚠️ Kurtarma Telemetrisi Bulunamadı!")
                self.install_photorec()
                return False
                
        except Exception as e:
            self.output_text.append(f"❌ Kurtarma telemetrisi kontrolü başarısız: {str(e)}")
            return False
    
    def install_photorec(self):
        """PhotoRec'i otomatik kur"""
        self.output_text.append("\n🔄 Kurtarma telemetrisi otomatik kurulumu başlatılıyor...")
        
        # Kullanıcıdan onay al
        reply = QMessageBox.question(self, self.tr('telemetry_required'), 
                                   self.tr('install_question'),
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.output_text.append("📦 testdisk paketi kuruluyor...")
                self.output_text.append("⏳ Bu işlem birkaç dakika sürebilir, lütfen bekleyin...")
                
                # Kurulum komutunu çalıştır
                process = subprocess.Popen(['pkexec', 'sh', '-c', 'apt update && apt install -y testdisk'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
                
                # Kurulum çıktısını göster
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        if line:
                            self.output_text.append(f"📦 {line}")
                
                return_code = process.wait()
                
                if return_code == 0:
                    self.output_text.append("\n✅ Kurtarma telemetrisi başarıyla kuruldu!")
                    # Kurulumu tekrar kontrol et
                    if self.check_photorec_installation():
                        QMessageBox.information(self, self.tr('success'), self.tr('install_ready'))
                    else:
                        QMessageBox.warning(self, "Uyarı", "Kurulum tamamlandı ancak Kurtarma telemetrisi hala bulunamıyor.")
                else:
                    self.output_text.append(f"\n❌ Kurulum başarısız (çıkış kodu: {return_code})")
                    QMessageBox.critical(self, "Hata", "Kurtarma telemetrisi kurulumu başarısız oldu.\n\nManuel kurulum için:\nsudo apt update && sudo apt install testdisk")
                    
            except Exception as e:
                self.output_text.append(f"\n❌ Kurulum hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Kurtarma telemetrisi kurulumu sırasında hata oluştu:\n{str(e)}\n\nManuel kurulum için:\nsudo apt update && sudo apt install testdisk")
        else:
            self.output_text.append("\n⚠️ Kurtarma telemetrisi kurulumu iptal edildi.")
            self.output_text.append("\n📝 Manuel kurulum için:")
            self.output_text.append("  sudo apt update")
            self.output_text.append("  sudo apt install testdisk")
            
            # Başlat butonunu devre dışı bırak
            self.start_btn.setEnabled(False)
            self.start_btn.setText("❌ Kurtarma telemetrisi Gerekli")
    
    def setup_disk_monitor(self):
        """Disk değişikliklerini izlemek için timer kur"""
        self.disk_timer = QTimer()
        self.disk_timer.timeout.connect(self.refresh_disks)
        self.disk_timer.start(2000)  # 2 saniyede bir kontrol et

def check_and_request_root():
    """Root yetkisi kontrol et ve gerekirse iste"""
    if os.geteuid() != 0:
        print("⚠️ Program root yetkisi gerektiriyor...")
        print("🔄 Sudo ile yeniden başlatılıyor...")
        
        try:
            # Mevcut script yolunu al
            script_path = os.path.abspath(__file__)
            python_path = sys.executable
            
            # X11 display bilgilerini koru
            display = os.environ.get('DISPLAY', ':0')
            xauth = os.environ.get('XAUTHORITY', '')
            
            # pkexec ile yeniden başlat - display bilgilerini koru
            env_cmd = ['env', f'DISPLAY={display}']
            if xauth:
                env_cmd.append(f'XAUTHORITY={xauth}')
            
            cmd = ['pkexec'] + env_cmd + [python_path, script_path]
            subprocess.run(cmd)
            sys.exit(0)
            
        except Exception as e:
            print(f"❌ Root yetkisi alınamadı: {str(e)}")
            print("\n📝 Manuel olarak çalıştırın:")
            print(f"sudo python3 {script_path}")
            sys.exit(1)
    else:
        print("✅ Root yetkisiyle çalışıyor.")


    
    # Program her zaman root yetkisiyle başlatılıyor
    window.output_text.append(window.tr('superuser_running'))
    window.output_text.append("")
    window.output_text.append(window.tr('usage_tips'))
    window.output_text.append(window.tr('tip_disk_selection'))
    window.output_text.append(window.tr('tip_all_types'))
    window.output_text.append(window.tr('tip_free_space'))
    window.output_text.append(window.tr('tip_whole_disk'))
    window.output_text.append(window.tr('tip_time_warning'))
    window.output_text.append(window.tr('tip_output_location') + "\n")
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
