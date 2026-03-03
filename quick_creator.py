#!/usr/bin/env python3
import sys
import os
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QTextEdit, QPushButton,
    QFileDialog, QMessageBox,
    QListWidget, QRadioButton,
    QButtonGroup, QComboBox,
    QInputDialog, QTreeView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFileSystemModel

# ================= CONFIG =================
APP_NAME = "Quick Creator Pro"
CONFIG_FILE = os.path.expanduser("~/.quick_creator_locations.json")

EXECUTABLE_EXTS = (
    ".py", ".sh", ".bash", ".zsh", ".fish",
    ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx"
)

PROJECT_TEMPLATES = {
    "Custom (manual names)": [],
    "Basic Python Project": [
        "{project}/__init__.py",
        "{project}/main.py",
        "{project}/config.py",
        "tests/__init__.py",
        "tests/test_main.py",
        "requirements.txt",
        ".gitignore",
        "README.md",
    ],
    "Only folders (no files)": [
        "{project}/core",
        "{project}/ui",
        "{project}/assets",
        "{project}/tests",
    ],
}


class QuickCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1600, 1000)

        self.locations = self.load_locations()
        self.init_ui()

    # ================= UI =================
    def init_ui(self):
        self.setStyleSheet(self.get_stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ===== LEFT TREE =====
        self.model = QFileSystemModel()
        self.model.setRootPath("/")

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.tree.setColumnWidth(0, 350)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.doubleClicked.connect(self.add_tree_location)

        splitter.addWidget(self.tree)

        # ===== RIGHT WORKSPACE =====
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title")
        right_layout.addWidget(title)

        right_layout.addWidget(QLabel("Target Folders"))

        self.location_list = QListWidget()
        self.location_list.addItems(self.locations)
        self.location_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        right_layout.addWidget(self.location_list)

        loc_btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Folder")
        add_btn.clicked.connect(self.add_location)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_locations)
        loc_btn_layout.addWidget(add_btn)
        loc_btn_layout.addWidget(clear_btn)
        right_layout.addLayout(loc_btn_layout)

        right_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems(list(PROJECT_TEMPLATES.keys()))
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        right_layout.addWidget(self.template_combo)

        right_layout.addWidget(QLabel("Names / Structure"))
        self.names_input = QTextEdit()
        right_layout.addWidget(self.names_input)

        mode_layout = QHBoxLayout()
        self.folder_radio = QRadioButton("Folder")
        self.file_radio = QRadioButton("File")
        self.folder_radio.setChecked(True)

        group = QButtonGroup()
        group.addButton(self.folder_radio)
        group.addButton(self.file_radio)

        self.ext_combo = QComboBox()
        self.ext_combo.setEditable(True)
        self.ext_combo.addItems(sorted(set(EXECUTABLE_EXTS)))
        self.ext_combo.setCurrentText(".py")
        self.ext_combo.setEnabled(False)

        self.file_radio.toggled.connect(
            lambda checked: self.ext_combo.setEnabled(checked)
        )

        mode_layout.addWidget(self.folder_radio)
        mode_layout.addWidget(self.file_radio)
        mode_layout.addStretch()
        mode_layout.addWidget(QLabel("Default Extension:"))
        mode_layout.addWidget(self.ext_combo)

        right_layout.addLayout(mode_layout)

        btn_layout = QHBoxLayout()
        create_btn = QPushButton("CREATE")
        create_btn.clicked.connect(lambda: self.create_items(False))
        project_btn = QPushButton("CREATE PROJECT")
        project_btn.clicked.connect(lambda: self.create_items(True))
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(project_btn)
        right_layout.addLayout(btn_layout)

        splitter.addWidget(right_widget)
        splitter.setSizes([500, 1100])

    # ================= LOGIC =================
    def add_tree_location(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path) and path not in self.locations:
            self.locations.append(path)
            self.location_list.addItem(path)
            self.save_locations()

    def create_items(self, is_project=False):
        raw = self.names_input.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Error", "No names provided.")
            return

        names = []
        for line in raw.splitlines():
            names.extend([n.strip() for n in line.split(",") if n.strip()])

        selected_dirs = [i.text() for i in self.location_list.selectedItems()]
        if not selected_dirs:
            QMessageBox.warning(self, "Error", "Select at least one folder.")
            return

        default_ext = self.ext_combo.currentText().strip()

        for base in selected_dirs:
            for rel in names:
                full_path = os.path.join(base, rel)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                ext = os.path.splitext(rel)[1]
                if not ext and self.file_radio.isChecked() and not is_project:
                    full_path += default_ext

                if os.path.exists(full_path):
                    continue

                if "." in os.path.basename(full_path):
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(self.get_file_template(os.path.splitext(full_path)[1]))
                    self.make_executable_if_needed(full_path)
                else:
                    os.makedirs(full_path, exist_ok=True)

        QMessageBox.information(self, "Success", "Structure created successfully!")

    def make_executable_if_needed(self, path):
        ext = os.path.splitext(path)[1]
        if ext in EXECUTABLE_EXTS and os.name != "nt":
            current_mode = os.stat(path).st_mode
            os.chmod(path, current_mode | 0o111)

    def on_template_changed(self, template_name):
        template = PROJECT_TEMPLATES.get(template_name, [])
        if not template:
            self.names_input.clear()
            return

        project_name, ok = QInputDialog.getText(
            self, "Project Name", "Enter project folder name:", text="my-project"
        )
        if not ok:
            return

        paths = [p.format(project=project_name.strip()) for p in template]
        self.names_input.setPlainText("\n".join(paths))

    def add_location(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path and path not in self.locations:
            self.locations.append(path)
            self.location_list.addItem(path)
            self.save_locations()

    def clear_locations(self):
        self.locations.clear()
        self.location_list.clear()
        self.save_locations()

    def get_file_template(self, ext):
        templates = {
            ".py": "#!/usr/bin/env python3\n\nif __name__ == '__main__':\n    pass\n",
            ".sh": "#!/usr/bin/env bash\n\nset -euo pipefail\n",
            ".js": "// JavaScript file\n",
        }
        return templates.get(ext, "")

    def load_locations(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_locations(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.locations, f, indent=2)

    def get_stylesheet(self):
        return """
        QWidget { background:#18181b; color:#e5e7eb; font-size:32px; }
        QLabel#title { font-size:52px; font-weight:bold; color:#a5b4fc; }
        QTreeView { background:#111827; }
        QListWidget, QTextEdit { background:#1f2937; }
        QPushButton { background:#374151; padding:14px; }
        QPushButton:hover { background:#4b5563; }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickCreator()
    window.show()
    sys.exit(app.exec())
