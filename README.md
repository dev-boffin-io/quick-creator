Quick Creator Pro

Quick Creator Pro is a desktop application for quickly generating project structures, folders, and files.

This repository includes an "install.sh" script that creates, updates, and removes a Linux desktop entry for the application.

---

📁 Required Project Structure

Place "install.sh" in the same directory as the binary and icon:

project-folder/
│
├── quick_creator          ← Executable binary
├── quick_creator.png      ← PNG icon file
└── install.sh             ← Installer script

Expected names:

- Binary: "quick_creator"
- Icon: "quick_creator.png"

If you rename the binary, update the "APP_NAME" variable inside "install.sh".

---

🚀 Installation

User Install (Local)

Installs the desktop entry to:

~/.local/share/applications

Run:

chmod +x install.sh
./install.sh

No "sudo" required.

---

System-Wide Install

Installs the desktop entry to:

/usr/local/share/applications

Run:

sudo ./install.sh

This makes the application available for all users on the system.

---

🔄 Automatic Update

If a desktop entry already exists:

- If no changes are detected → the file is left untouched.
- If changes are detected → the entry is automatically updated.

No duplicate entries are created.

---

🗑 Uninstall

Remove User Entry

./install.sh remove

Remove System-Wide Entry

sudo ./install.sh remove

This removes only the generated ".desktop" file and refreshes the desktop database.

---

🔍 Validation Checks

Before creating the desktop entry, the installer verifies:

- The binary file exists
- The binary is executable
- The PNG icon file exists

If any of these checks fail, installation stops with an error message.

---

📌 Desktop Entry Template

The installer generates a desktop entry similar to:

[Desktop Entry]
Version=1.0
Name=Quick Creator Pro
Comment=Project & File Structure Builder
Exec=/absolute/path/to/quick_creator
Icon=/absolute/path/to/quick_creator.png
Terminal=false
Type=Application
Categories=Development;Utility;
StartupNotify=true

Absolute paths are generated automatically.

---

⚠ Important Notes

- Ensure the binary has execute permission:
  chmod +x quick_creator
- The icon must be a valid PNG file.
- If "update-desktop-database" is not available, installation will still complete.

---

🛠 Customization

You can modify the following variables inside "install.sh":

APP_NAME="quick_creator"
APP_TITLE="Quick Creator Pro"
APP_COMMENT="Project & File Structure Builder"

---

📦 Typical Workflow

Build binary
↓
Place icon in same directory
↓
chmod +x install.sh
↓
./install.sh
or
sudo ./install.sh

---

Quick Creator Pro will then appear in your system’s application menu and can be pinned to the dock like any other desktop application.
