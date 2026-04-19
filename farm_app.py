import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (

    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
    QDialog, QFormLayout, QTextEdit, QMessageBox, QDateEdit,
    QScrollArea, QSizePolicy, QGridLayout, QTabWidget, QDoubleSpinBox,
    QFileDialog, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

# ── ReportLab ──────────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ── Google Sheets ──────────────────────────────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

SHEET_NAME = "FarmManagementApp"
SHEET_ID   = "17MAgmBf5dN98-BjsSEbWscdsj1kNUzxeQf1DNOUhYtk"

# Always find credentials.json next to the exe or script
if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(sys.executable)
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = os.path.join(_APP_DIR, "credentials.json")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

EXPENSE_CATEGORIES = [
    "Basic Supplies", "Building Supplies", "Chemicals", "Electric",
    "Farm Insurance", "Feed", "Fuel/Diesel", "Gas", "Gravel",
    "Lyme/Fertilizer", "Livestock", "Meds", "Minerals", "Other",
    "Parts", "Real Estate Taxes", "Repairs & Maintenance", "Seeds",
    "Truck Interest", "Truck Mileage", "Truck Taxes", "WiFi"
]
DRIVE_FOLDER_ID = "1P21kf7tJ5uSV19VoiA5NC8Hm0k-Jy7Vr"

# ── Google Drive Upload ────────────────────────────────────────────────────────
def upload_receipt_image(filepath, filename, creds_file=CREDENTIALS_FILE):
    """Upload an image to Google Drive and return the shareable view URL."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        file_metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
        media = MediaFileUpload(filepath, resumable=True)
        uploaded = service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        file_id = uploaded.get("id")
        # Make publicly viewable
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()
        return f"https://drive.google.com/uc?id={file_id}"
    except Exception as e:
        print(f"Drive upload error: {e}")
        return ""

# ── Theme ──────────────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":      "#111A11",
    "bg_mid":       "#1B2A1B",
    "bg_panel":     "#243324",
    "bg_row_alt":   "#1F2E1F",
    "accent":       "#6B8F47",
    "accent_light": "#8FB562",
    "accent_dim":   "#3D5C2A",
    "tan":          "#A89F72",
    "tan_light":    "#C8BC8A",
    "text":         "#E8E8DC",
    "text_dim":     "#9A9A82",
    "border":       "#3A4F2E",
    "danger":       "#C0392B",
    "danger_dark":  "#922B21",
    "success":      "#2ECC71",
    "warning":      "#F39C12",
    "header_bg":    "#0D160D",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}
#sidebar {{
    background-color: {COLORS['bg_mid']};
    border-right: 2px solid {COLORS['border']};
    min-width: 200px;
    max-width: 200px;
}}
#app_title {{
    font-size: 16px;
    font-weight: bold;
    color: {COLORS['accent_light']};
    padding: 18px 16px 6px 16px;
    letter-spacing: 1px;
}}
#app_subtitle {{
    font-size: 10px;
    color: {COLORS['tan']};
    padding: 0px 16px 16px 16px;
    letter-spacing: 2px;
}}
QPushButton#nav_btn {{
    background-color: transparent;
    color: {COLORS['text_dim']};
    border: none;
    border-left: 3px solid transparent;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#nav_btn:hover {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
    border-left: 3px solid {COLORS['accent_dim']};
}}
QPushButton#nav_btn[active="true"] {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['accent_light']};
    border-left: 3px solid {COLORS['accent']};
    font-weight: bold;
}}
#content_area {{
    background-color: {COLORS['bg_dark']};
    padding: 0px;
}}
#page_header {{
    background-color: {COLORS['header_bg']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 16px 24px;
}}
#page_title {{
    font-size: 22px;
    font-weight: bold;
    color: {COLORS['accent_light']};
    letter-spacing: 1px;
}}
#page_subtitle {{
    font-size: 11px;
    color: {COLORS['tan']};
    letter-spacing: 1px;
}}
QPushButton#primary_btn {{
    background-color: {COLORS['accent']};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 12px;
}}
QPushButton#primary_btn:hover {{ background-color: {COLORS['accent_light']}; }}
QPushButton#danger_btn {{
    background-color: {COLORS['danger']};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 12px;
}}
QPushButton#danger_btn:hover {{ background-color: {COLORS['danger_dark']}; }}
QPushButton#secondary_btn {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px 18px;
    font-size: 12px;
}}
QPushButton#secondary_btn:hover {{
    background-color: {COLORS['bg_mid']};
    border-color: {COLORS['accent_dim']};
}}
QTableWidget {{
    background-color: {COLORS['bg_mid']};
    alternate-background-color: {COLORS['bg_row_alt']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    gridline-color: {COLORS['border']};
    selection-background-color: {COLORS['accent_dim']};
    font-size: 12px;
}}
QTableWidget::item {{ padding: 6px 10px; border: none; }}
QHeaderView::section {{
    background-color: {COLORS['header_bg']};
    color: {COLORS['tan_light']};
    padding: 8px 10px;
    border: none;
    border-right: 1px solid {COLORS['border']};
    border-bottom: 2px solid {COLORS['accent_dim']};
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 1px;
}}
QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {{
    border: 1px solid {COLORS['accent']};
}}
QCalendarWidget QToolButton {{
    color: {COLORS['text']};
    background-color: {COLORS['bg_panel']};
    border: none;
    padding: 4px 8px;
    font-size: 13px;
    font-weight: bold;
}}
QCalendarWidget QToolButton:hover {{
    background-color: {COLORS['accent_dim']};
}}
QCalendarWidget QToolButton#qt_calendar_prevmonth,
QCalendarWidget QToolButton#qt_calendar_nextmonth {{
    color: {COLORS['accent_light']};
    font-size: 16px;
    font-weight: bold;
}}
QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background-color: {COLORS['header_bg']};
    border-bottom: 1px solid {COLORS['border']};
}}
QCalendarWidget QAbstractItemView {{
    background-color: {COLORS['bg_mid']};
    color: {COLORS['text']};
    selection-background-color: {COLORS['accent_dim']};
    selection-color: {COLORS['text']};
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS['accent_dim']};
    border: none;
    width: 16px;
}}
QComboBox::drop-down {{
    border: none;
    background-color: {COLORS['accent_dim']};
    width: 24px;
    border-radius: 0px 4px 4px 0px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
    selection-background-color: {COLORS['accent_dim']};
    border: 1px solid {COLORS['border']};
}}
#stat_card {{
    background-color: {COLORS['bg_panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 16px;
}}
#stat_value {{
    font-size: 28px;
    font-weight: bold;
    color: {COLORS['accent_light']};
}}
#stat_label {{
    font-size: 11px;
    color: {COLORS['text_dim']};
    letter-spacing: 1px;
}}
QDialog {{ background-color: {COLORS['bg_mid']}; }}
QLabel {{ color: {COLORS['text']}; }}
QScrollBar:vertical {{
    background: {COLORS['bg_mid']};
    width: 8px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {COLORS['accent_dim']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {COLORS['bg_mid']};
    height: 8px;
}}
QScrollBar::handle:horizontal {{
    background: {COLORS['accent']};
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{ background: {COLORS['accent_light']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
QFrame#divider {{
    background-color: {COLORS['border']};
    max-height: 1px;
}}
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['bg_dark']};
}}
QTabBar::tab {{
    background-color: {COLORS['bg_mid']};
    color: {COLORS['text_dim']};
    padding: 8px 20px;
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    font-size: 12px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['accent_light']};
    border-top: 2px solid {COLORS['accent']};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
}}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────
def safe_float(val):
    try:
        return float(str(val).replace(",", "").replace("$", "") or 0)
    except:
        return 0.0

def make_page_header(title, subtitle):
    header = QWidget()
    header.setObjectName("page_header")
    layout = QVBoxLayout(header)
    layout.setContentsMargins(24, 14, 24, 14)
    layout.setSpacing(2)
    t = QLabel(title)
    t.setObjectName("page_title")
    s = QLabel(subtitle)
    s.setObjectName("page_subtitle")
    layout.addWidget(t)
    layout.addWidget(s)
    return header

def make_table(headers):
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.setShowGrid(False)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    return table

# ── Google Sheets Backend ──────────────────────────────────────────────────────
class SheetsBackend:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.connected = False
        self._connect()

    def _connect(self):
        if not GSPREAD_AVAILABLE or not os.path.exists(CREDENTIALS_FILE):
            return
        try:
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            try:
                self.spreadsheet = self.client.open_by_key(SHEET_ID)
            except Exception:
                self.spreadsheet = self.client.open(SHEET_NAME)
            self._ensure_sheets()
            self.connected = True
        except Exception as e:
            print(f"Sheets connection error: {e}")

    def _ensure_sheets(self):
        existing = [ws.title for ws in self.spreadsheet.worksheets()]
        sheets_config = {
            "Cattle":         ["ID", "Tag", "Birth Date", "Mother", "Father", "Classification", "Tag/Band Status", "Status"],
            "CattleArchive":  ["ID", "Tag", "Birth Date", "Mother", "Father", "Classification", "Tag/Band Status", "Status", "Archived Date"],
            "Expenses":       ["ID", "Date", "Invoice #", "Vendor"] + EXPENSE_CATEGORIES + ["Total", "Notes", "Receipt Image"],
            "Income":         ["ID", "Date", "Description", "Amount"],
            "Notes":          ["ID", "Date", "Title", "Body"],
        }
        for sheet_name, headers in sheets_config.items():
            if sheet_name not in existing:
                ws = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                ws.append_row(headers)
            else:
                ws = self.spreadsheet.worksheet(sheet_name)
                if not ws.row_values(1):
                    ws.append_row(headers)
        if "Sheet1" in existing:
            try:
                self.spreadsheet.del_worksheet(self.spreadsheet.worksheet("Sheet1"))
            except:
                pass

    def get_sheet(self, name):
        if not self.connected:
            return None
        return self.spreadsheet.worksheet(name)

    def get_all_records(self, sheet_name):
        ws = self.get_sheet(sheet_name)
        if not ws:
            return []
        try:
            return ws.get_all_records()
        except:
            return []

    def append_row(self, sheet_name, row_data):
        ws = self.get_sheet(sheet_name)
        if ws:
            ws.append_row(row_data)

    def update_row(self, sheet_name, row_index, row_data):
        ws = self.get_sheet(sheet_name)
        if ws:
            for col, val in enumerate(row_data, start=1):
                ws.update_cell(row_index + 2, col, val)

    def delete_row(self, sheet_name, row_index):
        ws = self.get_sheet(sheet_name)
        if ws:
            ws.delete_rows(row_index + 2)

    def next_id(self, sheet_name):
        records = self.get_all_records(sheet_name)
        if not records:
            return 1
        ids = [int(r.get("ID", 0)) for r in records if str(r.get("ID", "")).isdigit()]
        return max(ids) + 1 if ids else 1


# ── Local Demo Store ───────────────────────────────────────────────────────────
class LocalStore:
    def __init__(self):
        self.connected = False
        self.data = {
            "Cattle": [
                {"ID": 1, "Tag": "#001", "Birth Date": "2021-03-15", "Mother": "#00X", "Father": "Bull #B01", "Classification": "Heifer", "Tag/Band Status": "Tagged & Banded", "Status": "Active"},
                {"ID": 2, "Tag": "#002", "Birth Date": "2022-07-04", "Mother": "#001", "Father": "Bull #B01", "Classification": "Bull",   "Tag/Band Status": "Tagged Only",     "Status": "Active"},
            ],
            "CattleArchive": [
                {"ID": 3, "Tag": "#003", "Birth Date": "2019-11-20", "Mother": "Unknown", "Father": "Unknown", "Classification": "Heifer", "Tag/Band Status": "Tagged & Banded", "Status": "Sold", "Archived Date": "2025-01-05"},
            ],
            "Expenses": [
                {"ID": 1, "Date": "2025-02-01", "Invoice #": "INV-001", "Vendor": "Tractor Supply", "Feed": 320.00, "Parts": 0, "Chemicals": 0, "Meds": 0, "Basic Supplies": 45.00, "Building Supplies": 0, "Livestock": 0, "Electric": 0, "Gravel": 0, "Repairs & Maintenance": 0, "Gas": 0, "WiFi": 0, "Truck Interest": 0, "Farm Insurance": 0, "Real Estate Taxes": 0, "Truck Taxes": 0, "Truck Mileage": 0, "Fuel/Diesel": 0, "Seeds": 0, "Lime/Fertilizer": 0, "Minerals": 0, "Other": 0, "Total": 365.00, "Notes": "", "Receipt Image": ""},
                {"ID": 2, "Date": "2025-02-14", "Invoice #": "INV-002", "Vendor": "Ace Hardware", "Feed": 0, "Parts": 145.00, "Chemicals": 0, "Meds": 0, "Basic Supplies": 0, "Building Supplies": 78.00, "Livestock": 0, "Electric": 0, "Gravel": 0, "Repairs & Maintenance": 0, "Gas": 0, "WiFi": 0, "Truck Interest": 0, "Farm Insurance": 0, "Real Estate Taxes": 0, "Truck Taxes": 0, "Truck Mileage": 0, "Fuel/Diesel": 0, "Seeds": 0, "Lime/Fertilizer": 0, "Minerals": 0, "Other": 0, "Total": 223.00, "Notes": "", "Receipt Image": ""},
                {"ID": 3, "Date": "2025-03-10", "Invoice #": "INV-003", "Vendor": "Co-op Farm Store", "Feed": 210.00, "Parts": 0, "Chemicals": 55.00, "Meds": 120.00, "Basic Supplies": 0, "Building Supplies": 0, "Livestock": 0, "Electric": 0, "Gravel": 0, "Repairs & Maintenance": 0, "Gas": 0, "WiFi": 0, "Truck Interest": 0, "Farm Insurance": 0, "Real Estate Taxes": 0, "Truck Taxes": 0, "Truck Mileage": 0, "Fuel/Diesel": 0, "Seeds": 0, "Lime/Fertilizer": 0, "Minerals": 0, "Other": 0, "Total": 385.00, "Notes": "", "Receipt Image": ""},
            ],
            "Income": [
                {"ID": 1, "Date": "2025-01-15", "Description": "Livestock Sale — Spring Calves", "Amount": 4800.00},
                {"ID": 2, "Date": "2025-03-20", "Description": "Hay Sale", "Amount": 650.00},
            ],
            "Notes": [
                {"ID": 1, "Date": "2025-03-01", "Title": "Spring Vaccination Schedule", "Body": "All cattle due for Blackleg + IBR booster in April. Contact Doc Harris."},
                {"ID": 2, "Date": "2025-03-10", "Title": "North Fence Project",         "Body": "Replace 3 posts on north pasture border. Need 6x 8ft posts, wire staples, and barbed wire roll."},
            ],
        }

    def get_all_records(self, sheet_name):
        return list(self.data.get(sheet_name, []))

    def append_row(self, sheet_name, row_data):
        pass

    def next_id(self, sheet_name):
        records = self.data.get(sheet_name, [])
        if not records:
            return 1
        return max(int(r.get("ID", 0)) for r in records) + 1

    def update_row(self, sheet_name, row_index, row_data):
        pass

    def delete_row(self, sheet_name, row_index):
        pass


# ── Dialogs ───────────────────────────────────────────────────────────────────

class CattleDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Add Cow" if not record else "Edit Cow")
        self.setMinimumWidth(400)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("🐄  " + ("Add New Cow" if not self.record else "Edit Cow"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.tag_input    = QLineEdit()
        self.tag_input.setPlaceholderText("e.g. #001")
        self.birth_input  = QDateEdit()
        self.birth_input.setCalendarPopup(True)
        self.birth_input.setDate(QDate.currentDate())
        self.birth_input.setDisplayFormat("yyyy-MM-dd")
        self.mother_input = QLineEdit()
        self.mother_input.setPlaceholderText("Mother's tag")
        self.father_input = QLineEdit()
        self.father_input.setPlaceholderText("Father's tag")
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Sold", "Deceased"])

        self.classification_input = QComboBox()
        self.classification_input.addItems(["Bull", "Heifer", "Stillborn"])

        self.tag_status_input = QComboBox()
        self.tag_status_input.addItems(["Tagged & Banded", "Tagged Only", "Banded Only", "Neither"])

        form.addRow("Tag:",            self.tag_input)
        form.addRow("Birth Date:",     self.birth_input)
        form.addRow("Mother:",         self.mother_input)
        form.addRow("Father:",         self.father_input)
        form.addRow("Classification:", self.classification_input)
        form.addRow("Tag/Band Status:", self.tag_status_input)
        form.addRow("Status:",         self.status_input)
        layout.addLayout(form)

        if self.record:
            self.tag_input.setText(str(self.record.get("Tag", "")))
            bd = str(self.record.get("Birth Date", ""))
            if bd:
                try:
                    self.birth_input.setDate(QDate.fromString(bd, "yyyy-MM-dd"))
                except:
                    pass
            self.mother_input.setText(str(self.record.get("Mother", "")))
            self.father_input.setText(str(self.record.get("Father", "")))
            idx = self.status_input.findText(str(self.record.get("Status", "Active")))
            if idx >= 0:
                self.status_input.setCurrentIndex(idx)
            idx2 = self.classification_input.findText(str(self.record.get("Classification", "Bull")))
            if idx2 >= 0:
                self.classification_input.setCurrentIndex(idx2)
            idx3 = self.tag_status_input.findText(str(self.record.get("Tag/Band Status", "Tagged & Banded")))
            if idx3 >= 0:
                self.tag_status_input.setCurrentIndex(idx3)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Save")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "Tag":              self.tag_input.text().strip(),
            "Birth Date":       self.birth_input.date().toString("yyyy-MM-dd"),
            "Mother":           self.mother_input.text().strip(),
            "Father":           self.father_input.text().strip(),
            "Classification":   self.classification_input.currentText(),
            "Tag/Band Status":  self.tag_status_input.currentText(),
            "Status":           self.status_input.currentText(),
        }


class ExpenseDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Add Receipt" if not record else "Edit Receipt")
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("🧾  " + ("New Receipt" if not self.record else "Edit Receipt"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        # Date + Vendor
        top_form = QFormLayout()
        top_form.setSpacing(10)
        top_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.vendor_input = QLineEdit()
        self.vendor_input.setPlaceholderText("e.g. Tractor Supply, Ace Hardware...")

        self.invoice_input = QLineEdit()
        self.invoice_input.setPlaceholderText("e.g. INV-00123  (optional)")

        top_form.addRow("Date:",      self.date_input)
        top_form.addRow("Invoice #:", self.invoice_input)
        top_form.addRow("Vendor:",    self.vendor_input)
        layout.addLayout(top_form)

        # Divider
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(div)

        # Category grid
        cat_lbl = QLabel("Line Items  —  fill in any that apply:")
        cat_lbl.setStyleSheet(f"color: {COLORS['tan_light']}; font-weight: bold; font-size: 12px;")
        layout.addWidget(cat_lbl)

        grid = QGridLayout()
        grid.setSpacing(8)
        self.cat_inputs = {}
        for i, cat in enumerate(EXPENSE_CATEGORIES):
            row, col = divmod(i, 2)
            lbl = QLabel(cat + ":")
            lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px;")
            spin = QDoubleSpinBox()
            spin.setPrefix("$")
            spin.setDecimals(2)
            spin.setMinimum(0.00)
            spin.setMaximum(999999.99)
            spin.setSingleStep(1.00)
            spin.setValue(0.00)
            spin.setFixedWidth(140)
            grid.addWidget(lbl,  row, col * 2)
            grid.addWidget(spin, row, col * 2 + 1)
            self.cat_inputs[cat] = spin

        layout.addLayout(grid)

        # Total display
        self.total_lbl = QLabel("Total: $0.00")
        self.total_lbl.setStyleSheet(f"color: {COLORS['accent_light']}; font-size: 15px; font-weight: bold; padding-top: 6px;")
        layout.addWidget(self.total_lbl)

        for spin in self.cat_inputs.values():
            spin.valueChanged.connect(self._update_total)

        # Notes
        div2 = QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(div2)

        notes_lbl = QLabel("Notes:")
        notes_lbl.setStyleSheet(f"color: {COLORS['tan_light']}; font-weight: bold; font-size: 12px;")
        layout.addWidget(notes_lbl)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Any additional details or differentiations for this receipt...")
        self.notes_input.setFixedHeight(60)
        layout.addWidget(self.notes_input)

        # Receipt photo
        div3 = QFrame()
        div3.setObjectName("divider")
        div3.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(div3)

        self._image_url  = ""
        self._local_path = ""

        photo_row = QHBoxLayout()
        photo_btn = QPushButton("📷  Attach Receipt Photo")
        photo_btn.setObjectName("secondary_btn")
        photo_btn.clicked.connect(self._pick_image)
        self.photo_lbl = QLabel("No image attached")
        self.photo_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        photo_row.addWidget(photo_btn)
        photo_row.addWidget(self.photo_lbl)
        photo_row.addStretch()
        layout.addLayout(photo_row)

        # Prefill if editing
        if self.record:
            bd = str(self.record.get("Date", ""))
            if bd:
                try:
                    self.date_input.setDate(QDate.fromString(bd, "yyyy-MM-dd"))
                except:
                    pass
            self.vendor_input.setText(str(self.record.get("Vendor", "")))
            self.invoice_input.setText(str(self.record.get("Invoice #", "")))
            for cat in EXPENSE_CATEGORIES:
                val = safe_float(self.record.get(cat, 0))
                self.cat_inputs[cat].setValue(val)
            existing_url = str(self.record.get("Receipt Image", ""))
            if existing_url:
                self._image_url = existing_url
                self.photo_lbl.setText("📷  Image attached")
                self.photo_lbl.setStyleSheet(f"color: {COLORS['success']}; font-size: 11px;")
            self.notes_input.setPlainText(str(self.record.get("Notes", "")))

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Save Receipt")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _update_total(self):
        total = sum(spin.value() for spin in self.cat_inputs.values())
        self.total_lbl.setText(f"Total: ${total:,.2f}")

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Receipt Image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*)"
        )
        if not path:
            return
        self._local_path = path
        filename = os.path.basename(path)
        self.photo_lbl.setText(f"📎  {filename}  (uploading on save...)")
        self.photo_lbl.setStyleSheet(f"color: {COLORS['warning']}; font-size: 11px;")

    def get_data(self):
        cats  = {cat: self.cat_inputs[cat].value() for cat in EXPENSE_CATEGORIES}
        total = sum(cats.values())

        # Upload image if a new one was picked
        image_url = self._image_url
        if self._local_path and os.path.exists(self._local_path):
            try:
                from googleapiclient.discovery import build
                vendor   = self.vendor_input.text().strip().replace(" ", "_")
                date_str = self.date_input.date().toString("yyyy-MM-dd")
                ext      = os.path.splitext(self._local_path)[1]
                fname    = f"receipt_{date_str}_{vendor}{ext}"
                uploaded = upload_receipt_image(self._local_path, fname)
                if uploaded:
                    image_url = uploaded
                    self.photo_lbl.setText("📷  Image attached")
                    self.photo_lbl.setStyleSheet(f"color: {COLORS['success']}; font-size: 11px;")
                else:
                    QMessageBox.warning(self, "Upload Failed",
                        "Image could not be uploaded to Google Drive.\nCheck your internet connection and credentials.")
            except ImportError:
                QMessageBox.warning(self, "Missing Library",
                    "Google Drive upload requires an extra library.\n\n"
                    "Run this in PowerShell:\n"
                    "pip install google-api-python-client")
            except Exception as e:
                QMessageBox.warning(self, "Upload Error", f"Upload failed:\n{str(e)}")

        return {
            "Date":          self.date_input.date().toString("yyyy-MM-dd"),
            "Invoice #":     self.invoice_input.text().strip(),
            "Vendor":        self.vendor_input.text().strip(),
            **cats,
            "Total":         total,
            "Notes":         self.notes_input.toPlainText().strip(),
            "Receipt Image": image_url,
        }


class NoteDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Add Note" if not record else "Edit Note")
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📋  " + ("Add Note" if not self.record else "Edit Note"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Spring Vaccination Schedule")

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Write your note here...")
        self.body_input.setFixedHeight(180)

        form.addRow("Date:",  self.date_input)
        form.addRow("Title:", self.title_input)
        form.addRow("Body:",  self.body_input)
        layout.addLayout(form)

        if self.record:
            bd = str(self.record.get("Date", ""))
            if bd:
                try:
                    self.date_input.setDate(QDate.fromString(bd, "yyyy-MM-dd"))
                except:
                    pass
            self.title_input.setText(str(self.record.get("Title", "")))
            self.body_input.setPlainText(str(self.record.get("Body", "")))

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Save")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "Date":  self.date_input.date().toString("yyyy-MM-dd"),
            "Title": self.title_input.text().strip(),
            "Body":  self.body_input.toPlainText().strip(),
        }


# ── Pages ─────────────────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setObjectName("content_area")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(make_page_header("🌿  Farm Dashboard", "OVERVIEW AT A GLANCE"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(24, 24, 24, 24)
        inner_layout.setSpacing(20)

        # Stat cards — Active Herd / Total Expenses / Available Balance
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        self.card_herd     = self._stat_card("🐄", "0",     "ACTIVE HERD")
        self.card_expenses = self._stat_card("📉", "$0.00", "TOTAL EXPENSES")
        self.card_balance  = self._stat_card("💰", "$0.00", "AVAILABLE BALANCE")
        for card in [self.card_herd, self.card_expenses, self.card_balance]:
            cards_row.addWidget(card)
        inner_layout.addLayout(cards_row)

        # Recent Cattle
        inner_layout.addWidget(self._section_label("Recent Cattle"))
        self.recent_cattle_table = make_table(["Tag", "Birth Date", "Status"])
        self.recent_cattle_table.setMaximumHeight(180)
        inner_layout.addWidget(self.recent_cattle_table)

        # Recent Expenses
        inner_layout.addWidget(self._section_label("Recent Expenses"))
        self.recent_expense_table = make_table(["Date", "Vendor", "Total"])
        self.recent_expense_table.setMaximumHeight(180)
        inner_layout.addWidget(self.recent_expense_table)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

    def _stat_card(self, icon, value, label):
        card = QFrame()
        card.setObjectName("stat_card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(4)
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        val_lbl  = QLabel(value)
        val_lbl.setObjectName("stat_value")
        lbl      = QLabel(label)
        lbl.setObjectName("stat_label")
        lay.addWidget(icon_lbl)
        lay.addWidget(val_lbl)
        lay.addWidget(lbl)
        card._value_label = val_lbl
        return card

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {COLORS['tan_light']}; font-size: 13px; font-weight: bold; letter-spacing: 1px; padding-top: 8px;")
        return lbl

    def refresh(self):
        cattle   = self.backend.get_all_records("Cattle")
        expenses = self.backend.get_all_records("Expenses")
        income   = self.backend.get_all_records("Income")

        active       = sum(1 for c in cattle if str(c.get("Status", "")).lower() == "active")
        total_exp    = sum(safe_float(e.get("Total", 0)) for e in expenses)
        total_inc    = sum(safe_float(i.get("Amount", 0)) for i in income)
        avail        = total_inc - total_exp

        self.card_herd._value_label.setText(str(active))
        self.card_expenses._value_label.setText(f"${total_exp:,.2f}")
        self.card_balance._value_label.setText(f"${avail:,.2f}")
        self.card_balance._value_label.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {COLORS['success'] if avail >= 0 else COLORS['danger']};")

        # Recent cattle
        self.recent_cattle_table.setRowCount(0)
        for rd in cattle[-5:]:
            row = self.recent_cattle_table.rowCount()
            self.recent_cattle_table.insertRow(row)
            for col, key in enumerate(["Tag", "Birth Date", "Status"]):
                item = QTableWidgetItem(str(rd.get(key, "")))
                if key == "Status":
                    color = COLORS['success'] if rd.get(key) == "Active" else COLORS['warning']
                    item.setForeground(QColor(color))
                self.recent_cattle_table.setItem(row, col, item)
        self.recent_cattle_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Recent expenses
        self.recent_expense_table.setRowCount(0)
        for rd in expenses[-5:]:
            row = self.recent_expense_table.rowCount()
            self.recent_expense_table.insertRow(row)
            for col, key in enumerate(["Date", "Vendor", "Total"]):
                val = str(rd.get(key, ""))
                if key == "Total":
                    try:
                        item = QTableWidgetItem(f"${safe_float(val):,.2f}")
                        item.setForeground(QColor(COLORS['danger']))
                    except:
                        item = QTableWidgetItem(val)
                else:
                    item = QTableWidgetItem(val)
                self.recent_expense_table.setItem(row, col, item)
        self.recent_expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


class CattlePage(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.records         = []
        self.archive_records = []
        self.setObjectName("content_area")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(make_page_header("🐄  Cattle", "HERD MANAGEMENT"))

        # Tabs: Active Herd / Archive
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # ── Active Herd tab ──
        herd_widget = QWidget()
        herd_layout = QVBoxLayout(herd_widget)
        herd_layout.setContentsMargins(0, 0, 0, 0)
        herd_layout.setSpacing(0)

        herd_toolbar = self._make_toolbar(
            show_status_filter=True,
            add_cb=self._add,
            edit_cb=self._edit,
            del_cb=self._archive,       # "Delete" sends to archive
            del_label="📦  Archive"
        )
        herd_layout.addWidget(herd_toolbar)

        self.table = make_table(["Tag", "Birth Date", "Mother", "Father", "Classification", "Tag/Band Status", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        herd_layout.addWidget(self.table)

        # ── Archive tab ──
        arch_widget = QWidget()
        arch_layout = QVBoxLayout(arch_widget)
        arch_layout.setContentsMargins(0, 0, 0, 0)
        arch_layout.setSpacing(0)

        arch_toolbar = self._make_toolbar(
            show_status_filter=False,
            add_cb=None,
            edit_cb=self._edit_archive,
            del_cb=self._delete_archive,
            del_label="🗑  Delete"
        )
        arch_layout.addWidget(arch_toolbar)

        self.archive_table = make_table(["Tag", "Birth Date", "Mother", "Father", "Classification", "Tag/Band Status", "Status", "Archived Date"])
        self.archive_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        arch_layout.addWidget(self.archive_table)

        self.tabs.addTab(herd_widget,  "🐄  Active Herd")
        self.tabs.addTab(arch_widget, "📦  Archive")
        layout.addWidget(self.tabs)

    def _make_toolbar(self, show_status_filter, add_cb, edit_cb, del_cb, del_label):
        toolbar = QWidget()
        toolbar.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-bottom: 1px solid {COLORS['border']};")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 10, 16, 10)

        if show_status_filter:
            self.status_filter = QComboBox()
            self.status_filter.addItems(["All", "Active", "Sold", "Deceased"])
            self.status_filter.currentTextChanged.connect(self._filter)
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("🔍  Search by tag...")
            self.search_input.setFixedWidth(200)
            self.search_input.textChanged.connect(self._filter)
            tb.addWidget(QLabel("Filter:"))
            tb.addWidget(self.status_filter)
            tb.addWidget(self.search_input)
        else:
            self.arch_search = QLineEdit()
            self.arch_search.setPlaceholderText("🔍  Search archive...")
            self.arch_search.setFixedWidth(200)
            self.arch_search.textChanged.connect(self._filter_archive)
            tb.addWidget(self.arch_search)

        tb.addStretch()

        edit_btn = QPushButton("✏  Edit")
        edit_btn.setObjectName("secondary_btn")
        edit_btn.clicked.connect(edit_cb)
        tb.addWidget(edit_btn)

        del_btn = QPushButton(del_label)
        del_btn.setObjectName("danger_btn")
        del_btn.clicked.connect(del_cb)
        tb.addWidget(del_btn)

        if add_cb:
            add_btn = QPushButton("＋  Add Cow")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(add_cb)
            tb.addWidget(add_btn)

        return toolbar

    def refresh(self):
        self.records         = self.backend.get_all_records("Cattle")
        self.archive_records = self.backend.get_all_records("CattleArchive")
        self._render(self.records)
        self._render_archive(self.archive_records)

    def _render(self, records):
        self.table.setRowCount(0)
        for rd in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(["Tag", "Birth Date", "Mother", "Father", "Classification", "Tag/Band Status", "Status"]):
                item = QTableWidgetItem(str(rd.get(key, "")))
                if key == "Status":
                    color = COLORS['success'] if rd.get(key) == "Active" else COLORS['warning'] if rd.get(key) == "Sold" else COLORS['danger']
                    item.setForeground(QColor(color))
                self.table.setItem(row, col, item)
        # Store record IDs hidden for lookup
        self.table._records = records

    def _render_archive(self, records):
        self.archive_table.setRowCount(0)
        for rd in records:
            row = self.archive_table.rowCount()
            self.archive_table.insertRow(row)
            for col, key in enumerate(["Tag", "Birth Date", "Mother", "Father", "Classification", "Tag/Band Status", "Status", "Archived Date"]):
                item = QTableWidgetItem(str(rd.get(key, "")))
                if key == "Status":
                    item.setForeground(QColor(COLORS['warning'] if rd.get(key) == "Sold" else COLORS['danger']))
                self.archive_table.setItem(row, col, item)
        self.archive_table._records = records

    def _filter(self):
        search = self.search_input.text().lower()
        status = self.status_filter.currentText()
        filtered = [r for r in self.records
                    if (status == "All" or r.get("Status") == status)
                    and (not search or search in str(r.get("Tag", "")).lower())]
        self._render(filtered)

    def _filter_archive(self):
        search = self.arch_search.text().lower()
        filtered = [r for r in self.archive_records
                    if not search or search in str(r.get("Tag", "")).lower()]
        self._render_archive(filtered)

    def _get_selected_record(self, table, records_attr):
        row = table.currentRow()
        if row < 0:
            return None, None
        rec_list = getattr(table, "_records", getattr(self, records_attr))
        if row >= len(rec_list):
            return None, None
        return rec_list[row], row

    def _add(self):
        dlg = CattleDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            new_id = self.backend.next_id("Cattle")
            row = [new_id, data["Tag"], data["Birth Date"], data["Mother"],
                   data["Father"], data["Classification"],
                   data["Tag/Band Status"], data["Status"]]
            self.backend.append_row("Cattle", row)
            self.refresh()

    def _edit(self):
        record, idx = self._get_selected_record(self.table, "records")
        if record is None:
            QMessageBox.information(self, "Select a Row", "Please select a cow to edit.")
            return
        dlg = CattleDialog(self, record)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            row_data = [record.get("ID"), data["Tag"], data["Birth Date"], data["Mother"],
                        data["Father"], data["Classification"],
                        data["Tag/Band Status"], data["Status"]]
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), idx)
            self.backend.update_row("Cattle", full_idx, row_data)
            self.refresh()

    def _archive(self):
        record, idx = self._get_selected_record(self.table, "records")
        if record is None:
            QMessageBox.information(self, "Select a Row", "Please select a cow to archive.")
            return
        tag = record.get("Tag", "")
        confirm = QMessageBox.question(self, "Archive Cow",
            f"Move {tag} to the Archive? (Sold / Deceased cattle)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            today = QDate.currentDate().toString("yyyy-MM-dd")
            arch_id = self.backend.next_id("CattleArchive")
            arch_row = [arch_id, record.get("Tag"), record.get("Birth Date"),
                        record.get("Mother"), record.get("Father"),
                        record.get("Classification"),
                        record.get("Tag/Band Status"), record.get("Status"), today]
            self.backend.append_row("CattleArchive", arch_row)
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), idx)
            self.backend.delete_row("Cattle", full_idx)
            self.refresh()

    def _edit_archive(self):
        record, idx = self._get_selected_record(self.archive_table, "archive_records")
        if record is None:
            QMessageBox.information(self, "Select a Row", "Please select a record to edit.")
            return
        dlg = CattleDialog(self, record)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            archived_date = record.get("Archived Date", "")
            row_data = [record.get("ID"), data["Tag"], data["Birth Date"], data["Mother"],
                        data["Father"], data["Classification"],
                        data["Tag/Band Status"], data["Status"], archived_date]
            full_idx = next((i for i, r in enumerate(self.archive_records) if r.get("ID") == record.get("ID")), idx)
            self.backend.update_row("CattleArchive", full_idx, row_data)
            self.refresh()

    def _delete_archive(self):
        record, idx = self._get_selected_record(self.archive_table, "archive_records")
        if record is None:
            QMessageBox.information(self, "Select a Row", "Please select a record to delete.")
            return
        tag = record.get("Tag", "")
        confirm = QMessageBox.question(self, "Confirm Delete",
            f"Permanently delete archive record for {tag}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            full_idx = next((i for i, r in enumerate(self.archive_records) if r.get("ID") == record.get("ID")), idx)
            self.backend.delete_row("CattleArchive", full_idx)
            self.refresh()


# ── Report Dialog ─────────────────────────────────────────────────────────────

class ReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Report")
        self.setMinimumWidth(420)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("📄  Generate Income / Expense Report")
        title.setObjectName("page_title")
        layout.addWidget(title)

        # Period selection
        period_lbl = QLabel("Report Period:")
        period_lbl.setStyleSheet(f"color: {COLORS['tan_light']}; font-weight: bold;")
        layout.addWidget(period_lbl)

        self.period_group = QButtonGroup(self)
        self.radio_ytd  = QRadioButton("Year to Date (Jan 1 – Today)")
        self.radio_full = QRadioButton("Full Calendar Year")
        self.radio_ytd.setChecked(True)
        self.period_group.addButton(self.radio_ytd,  0)
        self.period_group.addButton(self.radio_full, 1)

        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for y in range(current_year, current_year - 6, -1):
            self.year_combo.addItem(str(y))

        layout.addWidget(self.radio_ytd)
        layout.addWidget(self.radio_full)

        year_row = QHBoxLayout()
        year_row.addWidget(QLabel("  Year:"))
        year_row.addWidget(self.year_combo)
        year_row.addStretch()
        layout.addLayout(year_row)

        # Income field
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(div)

        income_lbl = QLabel("Income (Annual Livestock Sale):")
        income_lbl.setStyleSheet(f"color: {COLORS['tan_light']}; font-weight: bold;")
        layout.addWidget(income_lbl)

        income_note = QLabel("Enter the total income received from livestock sales this year.")
        income_note.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        income_note.setWordWrap(True)
        layout.addWidget(income_note)

        self.income_spin = QDoubleSpinBox()
        self.income_spin.setPrefix("$")
        self.income_spin.setDecimals(2)
        self.income_spin.setMinimum(0.00)
        self.income_spin.setMaximum(9999999.99)
        self.income_spin.setSingleStep(100.00)
        self.income_spin.setValue(0.00)
        self.income_spin.setFixedWidth(180)
        layout.addWidget(self.income_spin)

        # Buttons
        btn_row = QHBoxLayout()
        gen_btn = QPushButton("📄  Generate PDF")
        gen_btn.setObjectName("primary_btn")
        gen_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(gen_btn)
        layout.addLayout(btn_row)

    def get_options(self):
        year = int(self.year_combo.currentText())
        ytd  = self.radio_ytd.isChecked()
        return {
            "year":   year,
            "ytd":    ytd,
            "income": self.income_spin.value(),
        }


def generate_farm_report(records, options, filepath):
    """Generate a PDF Income/Expense report using ReportLab."""
    year   = options["year"]
    ytd    = options["ytd"]
    income = options["income"]
    today  = datetime.now()

    # Filter records by year (and YTD if selected)
    def in_range(r):
        date_str = str(r.get("Date", ""))
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            if d.year != year:
                return False
            if ytd and d > today:
                return False
            return True
        except:
            return False

    filtered = [r for r in records if in_range(r)]

    # Totals
    cat_totals = {cat: sum(safe_float(r.get(cat, 0)) for r in filtered) for cat in EXPENSE_CATEGORIES}
    grand_total = sum(cat_totals.values())
    net = income - grand_total

    # Period label
    if ytd:
        period_label = f"Year to Date  —  Jan 1, {year} through {today.strftime('%B %d, %Y')}"
    else:
        period_label = f"Full Calendar Year  —  {year}"

    # ── Build PDF ──
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Colors — Black & White
    DARK_GREEN  = rl_colors.white
    MID_GREEN   = rl_colors.HexColor("#F5F5F5")
    ACCENT      = rl_colors.black
    ACCENT_LT   = rl_colors.black
    TAN         = rl_colors.black
    TEXT_DIM    = rl_colors.HexColor("#555555")
    RED         = rl_colors.black
    WHITE       = rl_colors.black
    BLACK       = rl_colors.black
    SUCCESS     = rl_colors.black
    ROW_ALT     = rl_colors.HexColor("#EEEEEE")

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle("rpt_title",
        fontSize=22, textColor=ACCENT_LT, fontName="Helvetica-Bold",
        spaceAfter=4, alignment=TA_CENTER)
    style_sub = ParagraphStyle("rpt_sub",
        fontSize=10, textColor=TAN, fontName="Helvetica",
        spaceAfter=2, alignment=TA_CENTER)
    style_period = ParagraphStyle("rpt_period",
        fontSize=9, textColor=TEXT_DIM, fontName="Helvetica",
        spaceAfter=16, alignment=TA_CENTER)
    style_section = ParagraphStyle("rpt_section",
        fontSize=13, textColor=ACCENT_LT, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=6)
    style_normal = ParagraphStyle("rpt_normal",
        fontSize=10, textColor=WHITE, fontName="Helvetica")
    style_small = ParagraphStyle("rpt_small",
        fontSize=8, textColor=TEXT_DIM, fontName="Helvetica")

    story = []

    # Header
    story.append(Paragraph("🌿  Farm Management", style_title))
    story.append(Paragraph("INCOME / EXPENSE REPORT", style_sub))
    story.append(Paragraph(period_label, style_period))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    # ── Summary Cards ──
    story.append(Paragraph("Financial Summary", style_section))

    net_color = SUCCESS if net >= 0 else RED
    summary_data = [
        ["Total Income", "Total Expenses", "Net Balance"],
        [f"${income:,.2f}", f"${grand_total:,.2f}", f"${net:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), MID_GREEN),
        ("BACKGROUND",   (0, 1), (-1, 1), DARK_GREEN),
        ("TEXTCOLOR",    (0, 0), (-1, 0), TAN),
        ("TEXTCOLOR",    (0, 1), (0, 1),  SUCCESS),
        ("TEXTCOLOR",    (1, 1), (1, 1),  RED),
        ("TEXTCOLOR",    (2, 1), (2, 1),  net_color),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",     (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("FONTSIZE",     (0, 1), (-1, 1), 16),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [MID_GREEN, DARK_GREEN]),
        ("BOX",          (0, 0), (-1, -1), 1, ACCENT),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, ACCENT),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 18))

    # ── Category Breakdown ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=8))
    story.append(Paragraph("Expense Breakdown by Category", style_section))

    cat_data = [["Category", "Total Spent", "% of Expenses"]]
    for cat in EXPENSE_CATEGORIES:
        amt = cat_totals[cat]
        pct = (amt / grand_total * 100) if grand_total > 0 else 0
        cat_data.append([cat, f"${amt:,.2f}", f"{pct:.1f}%"])
    cat_data.append(["TOTAL", f"${grand_total:,.2f}", "100%"])

    cat_table = Table(cat_data, colWidths=[3.0 * inch, 2.0 * inch, 1.5 * inch])
    row_colors = []
    for i in range(len(cat_data)):
        bg = MID_GREEN if i % 2 == 0 else DARK_GREEN
        row_colors.append(("BACKGROUND", (0, i), (-1, i), bg))

    cat_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), rl_colors.HexColor("#0D160D")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), TAN),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("TEXTCOLOR",     (0, 1), (-1, -2), WHITE),
        ("FONTNAME",      (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -2), 10),
        # Last row (total)
        ("BACKGROUND",    (0, -1), (-1, -1), rl_colors.HexColor("#0D160D")),
        ("TEXTCOLOR",     (0, -1), (-1, -1), ACCENT_LT),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, -1), (-1, -1), 11),
        ("ALIGN",         (1, 0),  (-1, -1), "RIGHT"),
        ("ALIGN",         (0, 0),  (0, -1),  "LEFT"),
        ("BOX",           (0, 0),  (-1, -1), 1, ACCENT),
        ("INNERGRID",     (0, 0),  (-1, -1), 0.5, rl_colors.HexColor("#3A4F2E")),
        ("TOPPADDING",    (0, 0),  (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 7),
        ("LEFTPADDING",   (0, 0),  (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0),  (-1, -1), 10),
    ] + row_colors
    cat_table.setStyle(TableStyle(cat_style))
    story.append(cat_table)
    story.append(Spacer(1, 18))

    # ── Individual Receipts ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=8))
    story.append(Paragraph(f"All Receipts  ({len(filtered)} transactions)", style_section))

    if filtered:
        rec_headers = ["Date", "Vendor"] + EXPENSE_CATEGORIES + ["Total"]
        col_w = [0.75 * inch, 1.4 * inch] + [0.72 * inch] * len(EXPENSE_CATEGORIES) + [0.75 * inch]
        rec_data = [rec_headers]
        for r in sorted(filtered, key=lambda x: str(x.get("Date", ""))):
            row_vals = [
                str(r.get("Date", "")),
                str(r.get("Vendor", "")),
            ]
            for cat in EXPENSE_CATEGORIES:
                v = safe_float(r.get(cat, 0))
                row_vals.append(f"${v:,.2f}" if v > 0 else "—")
            row_vals.append(f"${safe_float(r.get('Total', 0)):,.2f}")
            rec_data.append(row_vals)

        rec_table = Table(rec_data, colWidths=col_w, repeatRows=1)
        rec_row_colors = []
        for i in range(1, len(rec_data)):
            bg = MID_GREEN if i % 2 == 1 else DARK_GREEN
            rec_row_colors.append(("BACKGROUND", (0, i), (-1, i), bg))

        rec_style = [
            ("BACKGROUND",    (0, 0), (-1, 0), rl_colors.HexColor("#0D160D")),
            ("TEXTCOLOR",     (0, 0), (-1, 0), TAN),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 7),
            ("TEXTCOLOR",     (0, 1), (-1, -1), WHITE),
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 1), (-1, -1), 7),
            ("ALIGN",         (2, 0), (-1, -1), "RIGHT"),
            ("ALIGN",         (0, 0), (1, -1),  "LEFT"),
            ("BOX",           (0, 0), (-1, -1), 1, ACCENT),
            ("INNERGRID",     (0, 0), (-1, -1), 0.3, rl_colors.HexColor("#3A4F2E")),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ] + rec_row_colors
        rec_table.setStyle(TableStyle(rec_style))
        story.append(rec_table)
    else:
        story.append(Paragraph("No receipts found for this period.", style_small))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=6))
    footer_text = f"Generated {today.strftime('%B %d, %Y at %I:%M %p')}  |  Farm Management App"
    story.append(Paragraph(footer_text, ParagraphStyle("footer",
        fontSize=8, textColor=TEXT_DIM, fontName="Helvetica", alignment=TA_CENTER)))

    # Build with dark background
    def dark_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(rl_colors.white)
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)


class FinancesPage(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.records = []
        self.income_records = []
        self.setObjectName("content_area")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(make_page_header("💰  Finances", "EXPENSE TRACKING"))

        # Expense Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-bottom: 1px solid {COLORS['border']};")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 10, 16, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search vendor...")
        self.search_input.setFixedWidth(220)
        self.search_input.textChanged.connect(self._filter)

        add_btn = QPushButton("＋  Add Receipt")
        add_btn.setObjectName("primary_btn")
        add_btn.clicked.connect(self._add)

        edit_btn = QPushButton("✏  Edit")
        edit_btn.setObjectName("secondary_btn")
        edit_btn.clicked.connect(self._edit)

        del_btn = QPushButton("🗑  Delete")
        del_btn.setObjectName("danger_btn")
        del_btn.clicked.connect(self._delete)

        report_btn = QPushButton("📄  Generate Report")
        report_btn.setObjectName("secondary_btn")
        report_btn.clicked.connect(self._generate_report)

        tb.addWidget(self.search_input)
        tb.addStretch()
        tb.addWidget(report_btn)
        tb.addWidget(edit_btn)
        tb.addWidget(del_btn)
        tb.addWidget(add_btn)

        income_btn = QPushButton("＋  Add Income")
        income_btn.setObjectName("secondary_btn")
        income_btn.clicked.connect(self._add_income)
        tb.addWidget(income_btn)
        layout.addWidget(toolbar)

        # Expense Table
        headers = ["Date", "Invoice #", "Vendor"] + EXPENSE_CATEGORIES + ["Total", "📷"]
        self.table = make_table(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)

    def refresh(self):
        self.records = self.backend.get_all_records("Expenses")
        self.income_records = self.backend.get_all_records("Income")
        self._update_totals()
        self._render(self.records)

    def _update_totals(self):
        pass  # Totals are rendered inside _render as the last row

    def _render(self, records):
        self.table.setRowCount(0)
        keys = ["Date", "Invoice #", "Vendor"] + EXPENSE_CATEGORIES + ["Total", "📷"]

        # Expense rows
        for rd in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(keys):
                if key == "📷":
                    url = str(rd.get("Receipt Image", "")).strip()
                    has_image = url and url != "0" and url.startswith("http")
                    item = QTableWidgetItem("📷" if has_image else "·")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                    item.setForeground(QColor(COLORS['accent_light'] if has_image else COLORS['text_dim']))
                    item.setToolTip("Click to view receipt image" if has_image else "No image attached")
                elif key in EXPENSE_CATEGORIES or key == "Total":
                    val = rd.get(key, "")
                    fval = safe_float(val)
                    item = QTableWidgetItem(f"${fval:,.2f}" if fval > 0 else "—")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    if key == "Total":
                        item.setForeground(QColor(COLORS['danger']))
                    elif fval > 0:
                        item.setForeground(QColor(COLORS['tan']))
                    else:
                        item.setForeground(QColor(COLORS['text_dim']))
                else:
                    item = QTableWidgetItem(str(rd.get(key, "")))
                self.table.setItem(row, col, item)

        # Income rows — shown inline with green styling
        for rd in self.income_records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(keys):
                if key == "Date":
                    item = QTableWidgetItem(str(rd.get("Date", "")))
                elif key == "Vendor":
                    item = QTableWidgetItem(f"📈  {rd.get('Description', '')}")
                    item.setForeground(QColor(COLORS['success']))
                elif key == "Total":
                    amt = safe_float(rd.get("Amount", 0))
                    item = QTableWidgetItem(f"${amt:,.2f}")
                    item.setForeground(QColor(COLORS['success']))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item = QTableWidgetItem("")
                    item.setForeground(QColor(COLORS['text_dim']))
                item.setBackground(QColor(COLORS['bg_row_alt']))
                self.table.setItem(row, col, item)

        # Tag records for edit/delete identification
        self.table._records = records
        self.table._income_offset = len(records)

        # Totals row
        cat_totals = {cat: sum(safe_float(r.get(cat, 0)) for r in self.records) for cat in EXPENSE_CATEGORIES}
        grand_exp  = sum(safe_float(r.get("Total", 0)) for r in self.records)
        grand_inc  = sum(safe_float(r.get("Amount", 0)) for r in self.income_records)
        grand_net  = grand_inc - grand_exp

        totals_row = self.table.rowCount()
        self.table.insertRow(totals_row)
        for col, key in enumerate(keys):
            if key == "Date":
                item = QTableWidgetItem("TOTALS")
                item.setForeground(QColor(COLORS['tan_light']))
                font = QFont(); font.setBold(True); item.setFont(font)
            elif key in ("Invoice #", "Vendor", "📷"):
                item = QTableWidgetItem("")
            elif key == "Total":
                net_color = COLORS['success'] if grand_net >= 0 else COLORS['danger']
                item = QTableWidgetItem(f"Net: ${grand_net:,.2f}")
                item.setForeground(QColor(net_color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                font = QFont(); font.setBold(True); item.setFont(font)
            else:
                val = cat_totals.get(key, 0)
                item = QTableWidgetItem(f"${val:,.2f}" if val > 0 else "—")
                item.setForeground(QColor(COLORS['tan'] if val > 0 else COLORS['text_dim']))
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                font = QFont(); font.setBold(True); item.setFont(font)
            item.setBackground(QColor(COLORS['header_bg']))
            self.table.setItem(totals_row, col, item)

    def _on_cell_clicked(self, row, col):
        camera_col = 3 + len(EXPENSE_CATEGORIES) + 1  # Date+Invoice+#+Vendor + cats + Total
        if col != camera_col:
            return
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        url = str(record.get("Receipt Image", "")).strip()
        if not url or url == "0" or not url.startswith("http"):
            QMessageBox.information(self, "No Image", "No receipt image attached to this transaction.")
            return
        self._view_image(url, record.get("Vendor", ""))

    def _view_image(self, url, vendor):
        try:
            import urllib.request
            from PyQt6.QtGui import QPixmap
            from PyQt6.QtWidgets import QScrollArea

            dlg = QDialog(self)
            dlg.setWindowTitle(f"Receipt — {vendor}")
            dlg.setMinimumSize(500, 600)
            dlg.setStyleSheet(STYLESHEET)
            lay = QVBoxLayout(dlg)
            lay.setContentsMargins(12, 12, 12, 12)

            lbl = QLabel("Loading image...")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {COLORS['text_dim']};")

            scroll = QScrollArea()
            scroll.setWidget(lbl)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            lay.addWidget(scroll)

            close_btn = QPushButton("Close")
            close_btn.setObjectName("secondary_btn")
            close_btn.clicked.connect(dlg.accept)
            lay.addWidget(close_btn)

            dlg.show()
            QApplication.processEvents()

            # Fetch image bytes
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()

            pixmap = QPixmap()
            pixmap.loadFromData(data)
            if pixmap.isNull():
                lbl.setText("Could not load image.")
            else:
                scaled = pixmap.scaled(480, 700,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(scaled)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            dlg.exec()
        except Exception as e:
            QMessageBox.warning(self, "Image Error", f"Could not load image:\n{str(e)}")

    def _filter(self):
        search = self.search_input.text().lower()
        filtered = [r for r in self.records
                    if not search or search in str(r.get("Vendor", "")).lower()]
        self._render(filtered)

    def _add(self):
        dlg = ExpenseDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            new_id = self.backend.next_id("Expenses")
            row = [new_id, data["Date"], data["Invoice #"], data["Vendor"]] + \
                  [data[cat] for cat in EXPENSE_CATEGORIES] + \
                  [data["Total"], data["Notes"], data["Receipt Image"]]
            self.backend.append_row("Expenses", row)
            self.refresh()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a Row", "Please select a transaction to edit.")
            return
        income_offset = getattr(self.table, "_income_offset", len(self.records))
        totals_row = income_offset + len(self.income_records)
        if row >= totals_row:
            return  # Totals row — not editable

        # Income row
        if row >= income_offset:
            inc_idx = row - income_offset
            if inc_idx >= len(self.income_records):
                return
            record = self.income_records[inc_idx]
            dlg = IncomeDialog(self, record)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                data = dlg.get_data()
                full_idx = next((i for i, r in enumerate(self.income_records) if r.get("ID") == record.get("ID")), inc_idx)
                self.backend.update_row("Income", full_idx,
                    [record.get("ID"), data["Date"], data["Description"], data["Amount"]])
                self.refresh()
            return

        # Expense row
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        dlg = ExpenseDialog(self, record)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            row_data = [record.get("ID"), data["Date"], data["Invoice #"], data["Vendor"]] + \
                       [data[cat] for cat in EXPENSE_CATEGORIES] + \
                       [data["Total"], data["Notes"], data["Receipt Image"]]
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), row)
            self.backend.update_row("Expenses", full_idx, row_data)
            self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a Row", "Please select a transaction to delete.")
            return
        income_offset = getattr(self.table, "_income_offset", len(self.records))
        totals_row = income_offset + len(self.income_records)
        if row >= totals_row:
            return

        # Income row
        if row >= income_offset:
            inc_idx = row - income_offset
            if inc_idx >= len(self.income_records):
                return
            record = self.income_records[inc_idx]
            confirm = QMessageBox.question(self, "Confirm Delete",
                f"Delete income: '{record.get('Description', '')}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                full_idx = next((i for i, r in enumerate(self.income_records) if r.get("ID") == record.get("ID")), inc_idx)
                self.backend.delete_row("Income", full_idx)
                self.refresh()
            return

        # Expense row
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        confirm = QMessageBox.question(self, "Confirm Delete",
            f"Delete receipt from '{record.get('Vendor', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), row)
            self.backend.delete_row("Expenses", full_idx)
            self.refresh()

    def _generate_report(self):
        if not REPORTLAB_AVAILABLE:
            QMessageBox.warning(self, "Missing Library",
                "reportlab is not installed.\nRun: pip install reportlab")
            return

        dlg = ReportDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        options = dlg.get_options()
        year    = options["year"]
        suffix  = f"YTD_{year}" if options["ytd"] else f"Full_{year}"
        default_name = f"FarmReport_{suffix}.pdf"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report As", default_name,
            "PDF Files (*.pdf);;All Files (*)"
        )
        if not filepath:
            return

        try:
            generate_farm_report(self.records, options, filepath)
            QMessageBox.information(self, "Report Generated",
                f"Report saved successfully:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")

    def _add_income(self):
        dlg = IncomeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            new_id = self.backend.next_id("Income")
            self.backend.append_row("Income", [new_id, data["Date"], data["Description"], data["Amount"]])
            self.refresh()


class NotesPage(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.records = []
        self.setObjectName("content_area")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(make_page_header("📋  Notes", ""))

        toolbar = QWidget()
        toolbar.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-bottom: 1px solid {COLORS['border']};")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 10, 16, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search notes...")
        self.search_input.setFixedWidth(260)
        self.search_input.textChanged.connect(self._filter)

        add_btn = QPushButton("＋  Add Note")
        add_btn.setObjectName("primary_btn")
        add_btn.clicked.connect(self._add)

        edit_btn = QPushButton("✏  Edit")
        edit_btn.setObjectName("secondary_btn")
        edit_btn.clicked.connect(self._edit)

        del_btn = QPushButton("🗑  Delete")
        del_btn.setObjectName("danger_btn")
        del_btn.clicked.connect(self._delete)

        tb.addWidget(self.search_input)
        tb.addStretch()
        tb.addWidget(edit_btn)
        tb.addWidget(del_btn)
        tb.addWidget(add_btn)
        layout.addWidget(toolbar)

        # Split: list left / preview right
        split = QWidget()
        split_layout = QHBoxLayout(split)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)

        self.table = make_table(["Date", "Title"])
        self.table.setMaximumWidth(380)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self._preview)

        preview = QWidget()
        preview.setStyleSheet(f"background-color: {COLORS['bg_panel']}; border-left: 1px solid {COLORS['border']};")
        prev_layout = QVBoxLayout(preview)
        prev_layout.setContentsMargins(24, 20, 24, 20)
        prev_layout.setSpacing(6)

        self.preview_title = QLabel("Select a note to preview")
        self.preview_title.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {COLORS['tan_light']};")
        self.preview_title.setWordWrap(True)
        self.preview_date = QLabel("")
        self.preview_date.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']}; margin-bottom: 10px;")
        self.preview_body = QTextEdit()
        self.preview_body.setReadOnly(True)
        self.preview_body.setStyleSheet(f"background-color: transparent; border: none; color: {COLORS['text']}; font-size: 13px;")

        prev_layout.addWidget(self.preview_title)
        prev_layout.addWidget(self.preview_date)
        prev_layout.addWidget(self.preview_body)

        split_layout.addWidget(self.table)
        split_layout.addWidget(preview, 1)

        layout.addWidget(split, 1)

    def refresh(self):
        self.records = self.backend.get_all_records("Notes")
        self._render(self.records)

    def _render(self, records):
        self.table.setRowCount(0)
        for rd in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(rd.get("Date", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(rd.get("Title", ""))))
        self.table._records = records

    def _filter(self):
        search = self.search_input.text().lower()
        filtered = [r for r in self.records
                    if not search or search in str(r.get("Title", "")).lower()
                    or search in str(r.get("Body", "")).lower()]
        self._render(filtered)

    def _preview(self):
        row = self.table.currentRow()
        if row < 0:
            return
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        self.preview_title.setText(str(record.get("Title", "")))
        self.preview_date.setText(f"📅  {record.get('Date', '')}")
        self.preview_body.setPlainText(str(record.get("Body", "")))

    def _add(self):
        dlg = NoteDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            new_id = self.backend.next_id("Notes")
            self.backend.append_row("Notes", [new_id, data["Date"], data["Title"], data["Body"]])
            self.refresh()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a Row", "Please select a note to edit.")
            return
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        dlg = NoteDialog(self, record)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), row)
            self.backend.update_row("Notes", full_idx,
                [record.get("ID"), data["Date"], data["Title"], data["Body"]])
            self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a Row", "Please select a note to delete.")
            return
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        confirm = QMessageBox.question(self, "Confirm Delete",
            f"Delete note: '{record.get('Title', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), row)
            self.backend.delete_row("Notes", full_idx)
            self.refresh()


# ── Main Window ───────────────────────────────────────────────────────────────
# ── Income Dialog ─────────────────────────────────────────────────────────────
class IncomeDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Add Income" if not record else "Edit Income")
        self.setMinimumWidth(400)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📈  " + ("Add Income" if not self.record else "Edit Income"))
        title.setObjectName("page_title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("e.g. Livestock Sale, Hay Sale...")

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setPrefix("$")
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimum(0.00)
        self.amount_input.setMaximum(9999999.99)
        self.amount_input.setSingleStep(100.00)
        self.amount_input.setValue(0.00)

        form.addRow("Date:",        self.date_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Amount:",      self.amount_input)
        layout.addLayout(form)

        if self.record:
            bd = str(self.record.get("Date", ""))
            if bd:
                try:
                    self.date_input.setDate(QDate.fromString(bd, "yyyy-MM-dd"))
                except:
                    pass
            self.desc_input.setText(str(self.record.get("Description", "")))
            self.amount_input.setValue(safe_float(self.record.get("Amount", 0)))

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Save")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "Date":        self.date_input.date().toString("yyyy-MM-dd"),
            "Description": self.desc_input.text().strip(),
            "Amount":      self.amount_input.value(),
        }


# ── Income Page ───────────────────────────────────────────────────────────────
class IncomePage(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.records = []
        self.setObjectName("content_area")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(make_page_header("📈  Income", "SALES & REVENUE"))

        # Total bar
        total_bar = QWidget()
        total_bar.setStyleSheet(f"background-color: {COLORS['bg_panel']}; border-bottom: 1px solid {COLORS['border']};")
        tb_layout = QHBoxLayout(total_bar)
        tb_layout.setContentsMargins(24, 8, 24, 8)
        self.total_lbl = QLabel("Total Income: $0.00")
        self.total_lbl.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold; font-size: 14px;")
        tb_layout.addWidget(self.total_lbl)
        tb_layout.addStretch()
        layout.addWidget(total_bar)

        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet(f"background-color: {COLORS['bg_mid']}; border-bottom: 1px solid {COLORS['border']};")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 10, 16, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search description...")
        self.search_input.setFixedWidth(240)
        self.search_input.textChanged.connect(self._filter)

        add_btn = QPushButton("＋  Add Income")
        add_btn.setObjectName("primary_btn")
        add_btn.clicked.connect(self._add)

        edit_btn = QPushButton("✏  Edit")
        edit_btn.setObjectName("secondary_btn")
        edit_btn.clicked.connect(self._edit)

        del_btn = QPushButton("🗑  Delete")
        del_btn.setObjectName("danger_btn")
        del_btn.clicked.connect(self._delete)

        tb.addWidget(self.search_input)
        tb.addStretch()
        tb.addWidget(edit_btn)
        tb.addWidget(del_btn)
        tb.addWidget(add_btn)
        layout.addWidget(toolbar)

        self.table = make_table(["Date", "Description", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def refresh(self):
        self.records = self.backend.get_all_records("Income")
        total = sum(safe_float(r.get("Amount", 0)) for r in self.records)
        self.total_lbl.setText(f"Total Income: ${total:,.2f}")
        self._render(self.records)

    def _render(self, records):
        self.table.setRowCount(0)
        for rd in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(["Date", "Description", "Amount"]):
                val = str(rd.get(key, ""))
                if key == "Amount":
                    item = QTableWidgetItem(f"${safe_float(val):,.2f}")
                    item.setForeground(QColor(COLORS['success']))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item = QTableWidgetItem(val)
                self.table.setItem(row, col, item)
        self.table._records = records

    def _filter(self):
        search = self.search_input.text().lower()
        filtered = [r for r in self.records
                    if not search or search in str(r.get("Description", "")).lower()]
        self._render(filtered)

    def _add(self):
        dlg = IncomeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            new_id = self.backend.next_id("Income")
            self.backend.append_row("Income", [new_id, data["Date"], data["Description"], data["Amount"]])
            self.refresh()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a Row", "Please select an entry to edit.")
            return
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        dlg = IncomeDialog(self, record)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), row)
            self.backend.update_row("Income", full_idx,
                [record.get("ID"), data["Date"], data["Description"], data["Amount"]])
            self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a Row", "Please select an entry to delete.")
            return
        rec_list = getattr(self.table, "_records", self.records)
        if row >= len(rec_list):
            return
        record = rec_list[row]
        confirm = QMessageBox.question(self, "Confirm Delete",
            f"Delete income entry: '{record.get('Description', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            full_idx = next((i for i, r in enumerate(self.records) if r.get("ID") == record.get("ID")), row)
            self.backend.delete_row("Income", full_idx)
            self.refresh()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌿 T. Harris Farms")
        self.setMinimumSize(1100, 700)
        self.resize(1400, 820)
        self.setStyleSheet(STYLESHEET)

        backend = SheetsBackend()
        self.store      = backend if backend.connected else LocalStore()
        self._demo_mode = not backend.connected

        self._build_ui()
        self._nav_to(0)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)

        title_lbl = QLabel("T. HARRIS")
        title_lbl.setObjectName("app_title")
        sub_lbl = QLabel("FARMS")
        sub_lbl.setObjectName("app_subtitle")
        sl.addWidget(title_lbl)
        sl.addWidget(sub_lbl)

        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.HLine)
        sl.addWidget(div)

        nav_items = [("🏠", "Dashboard"), ("🐄", "Cattle"), ("💰", "Finances"), ("📋", "Notes")]
        self.nav_buttons = []
        for i, (icon, label) in enumerate(nav_items):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("nav_btn")
            btn.clicked.connect(lambda checked, idx=i: self._nav_to(idx))
            sl.addWidget(btn)
            self.nav_buttons.append(btn)

        sl.addStretch()
        status_lbl = QLabel("🟢 Connected" if not self._demo_mode else "🟡 Demo Mode")
        status_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 10px; padding: 12px 16px;")
        sl.addWidget(status_lbl)

        update_btn = QPushButton("⬆  Check for Updates")
        update_btn.setObjectName("secondary_btn")
        update_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_dim']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 10px;
                margin: 0px 12px 12px 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_panel']};
                color: {COLORS['text']};
                border-color: {COLORS['accent_dim']};
            }}
        """)
        update_btn.clicked.connect(self._check_for_updates)
        sl.addWidget(update_btn)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")

        self.dashboard_page = DashboardPage(self.store)
        self.cattle_page    = CattlePage(self.store)
        self.finances_page  = FinancesPage(self.store)
        self.notes_page     = NotesPage(self.store)

        self.pages = [self.dashboard_page, self.cattle_page, self.finances_page, self.notes_page]
        for page in self.pages:
            self.stack.addWidget(page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

    def _check_for_updates(self):
        import urllib.request
        import shutil

        GITHUB_VERSION_URL = "https://raw.githubusercontent.com/paleharbor/tharris-farms/main/version.txt"
        GITHUB_EXE_URL     = "https://github.com/paleharbor/tharris-farms/raw/main/dist/T.Harris%20Farm.exe"
        VERSION_FILE       = os.path.join(_APP_DIR, "version.txt")
        NEW_EXE            = os.path.join(_APP_DIR, "T.Harris Farm.exe")

        try:
            # Get current local version
            local_version = "0.0"
            if os.path.exists(VERSION_FILE):
                with open(VERSION_FILE, "r", encoding="utf-8-sig") as f:
                    local_version = f.read().strip()

            # Get latest version from GitHub
            req = urllib.request.Request(GITHUB_VERSION_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                remote_version = resp.read().decode("utf-8-sig").strip()

            if remote_version == local_version:
                QMessageBox.information(self, "Up to Date", "✅  T. Harris Farms is already up to date.")
                return

            confirm = QMessageBox.question(self, "Update Available",
                f"A new update is available (v{remote_version}).\n\nDownload and install now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm != QMessageBox.StandardButton.Yes:
                return

            # Download new exe to temp file
            temp_exe = NEW_EXE + ".tmp"
            req2 = urllib.request.Request(GITHUB_EXE_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=120) as resp:
                with open(temp_exe, "wb") as f:
                    shutil.copyfileobj(resp, f)

            # Write a batch script to replace the exe after app closes
            bat_path = os.path.join(_APP_DIR, "update.bat")
            with open(bat_path, "w") as bat:
                bat.write(f'@echo off\n')
                bat.write(f'timeout /t 2 /nobreak >nul\n')
                bat.write(f'move /y "{temp_exe}" "{NEW_EXE}"\n')
                bat.write(f'del "%~f0"\n')

            # Update version file
            with open(VERSION_FILE, "w", encoding="utf-8") as f:
                f.write(remote_version)

            import subprocess
            subprocess.Popen(["cmd", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW)

            QMessageBox.information(self, "Update Complete",
                f"✅  Updated to v{remote_version}!\n\nPlease close and reopen the app.")

        except Exception as e:
            QMessageBox.warning(self, "Update Failed", f"Could not check for updates:\n{str(e)}")

    def _nav_to(self, idx):
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == idx else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.stack.setCurrentIndex(idx)
        self.pages[idx].refresh()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
