# SoftWhere
Program License Inventory System in Python

🛠️ Software License Inventory System

A Python-based console application for managing software licenses and tracking usage across users and devices. It features a login system with role-based access (Admin and Employee), license expiration checks, usage monitoring, and CSV export.

🚀 Features

- ✅ User registration with role-based access (Admin / Employee)
- 🔐 Secure login with password hashing (SHA-256)
- 📦 Add, view, search, and delete software license records
- 📆 Automatic detection of expired licenses
- 📊 Track software usage counts and limits
- 📤 Export license data to CSV
- 🧑‍💼 Admin panel with user management
- 📁 Data persistence using JSON files

🧰 Requirements

- Python 3.x
- `pyfiglet` (`pip install pyfiglet`)
- `termcolor` (`pip install termcolor`)
- `stdiomask` (`pip install stdiomask`)

📂 File Structure

project-folder/

users.json # Stores user login data
licenses.json # Stores software license records
licenses_export.csv # (Optional) Exported data file
license_inventory.py # Main Python script (this project)
README.md # This file
