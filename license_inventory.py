import json
from datetime import datetime
import hashlib
import os   
import pyfiglet
from termcolor import colored
import stdiomask

# Get directory of current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define file paths for storing users and license data
USER_FILE = os.path.join(SCRIPT_DIR, "users.json")
LICENSE_FILE = os.path.join(SCRIPT_DIR, "licenses.json")

# ------------------ Error Handling and Input Validation ------------------

# Validate user input with checks for passwords and numbers
def validate_input(prompt, is_password=False, is_number=False, hide_input=False):
    while True:
        if is_password and hide_input:
            # Use stdiomask for password input (shows asterisks)
            user_input = stdiomask.getpass(prompt, mask='*')
        else:
            user_input = input(prompt).strip()

        if not user_input:
            print(colored("Error: Input cannot be empty. Please try again.", "red"))
            continue

        if is_password:
            if len(user_input) < 4:
                print(colored("Error: Password must be at least 4 characters long.", "red"))
                continue

        if is_number:
            if not user_input.isdigit():
                print(colored("Error: Please enter a valid number.", "red"))
                continue
            return int(user_input)

        return user_input

# ------------------ LOGIN SYSTEM ------------------

# Load user data from JSON file
def load_users():
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return [] # Return empty list if file doesn't exist

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
    print("\n=== Register New User ===")
    username = validate_input("New username: ")
    
    # First password entry (visible)
    password = validate_input("New password (Must be at least 4 characters long): ", is_password=True)
    
    # Password confirmation (visible)
    confirm_password = validate_input("Confirm password: ", is_password=True)
    
    if password != confirm_password:
        print(colored("Error: Passwords do not match!", "red"))
        return

    while True:
        role = validate_input("Role (admin/employee): ").lower()
        if role in ['admin', 'employee']:
            break
        print(colored("Error: Role must be either 'admin' or 'employee'", "red"))

    users = load_users()

    for user in users:
        if user['username'] == username:
            print(colored("Username already exists!", "red"))
            return

    users.append({
        "username": username,
        "password": hash_password(password),
        "role": role
    })
    save_users(users)
    print(colored("User registered successfully!", "green"))

def login_menu():
    while True:
        title = pyfiglet.figlet_format("SOFTWHERE")
        print(colored(title, "blue"))
        print(colored("[1] Login", "green"))
        print(colored("[2] Exit Program", "red"))
        
        choice = validate_input("Enter your choice: ", is_number=True)
        
        if choice == 1:
            users = load_users()
            print("\n=== Employee Login ===")
            username = validate_input("Username: ").strip()
            # Password input with asterisks during login
            password = validate_input("Password: ", is_password=True, hide_input=True)
            
            user_exists = any(user['username'] == username for user in users)
            
            if not user_exists:
                print(colored("Error: Username not found.", "red"))
                continue
            
            hashed = hash_password(password)
            for user in users:
                if user['username'] == username and user['password'] == hashed:
                    print(colored(f"Login successful! Welcome, {username} ({user['role']})\n", "green"))
                    return user['role']
            
            print(colored("Error: Incorrect password.", "red"))
            
        elif choice == 2:
            print(colored("Exiting program. Goodbye!", "red"))
            return None
        else:
            print(colored("Invalid choice. Please enter 1 or 2.", "red"))

# ------------------ LICENSE SYSTEM ------------------

# Load license records from file
def load_licenses():
    try:
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return [] # Return empty list if no file exists

# Save license records to file
def save_licenses(licenses):
    with open(LICENSE_FILE, 'w') as f:
        json.dump(licenses, f, indent=4)

# Add a new software license to the system  
def add_license():
    while True:
        licenses = load_licenses()
        users = load_users()  # Load users for validation
        
        print("\n--- Add New License ---")
        
        # Collect license details from user
        license = {
            "software": validate_input("Software Name: "),
            "license_key": validate_input("License Key: "),
        }
        
        # Validate assigned user exists in users.json
        while True:
            assigned_user = validate_input("Assigned To (Username): ")
            user_exists = any(user['username'] == assigned_user for user in users)
            if user_exists:
                license["user"] = assigned_user
                break
            print(colored(f"Error: User '{assigned_user}' not found in system. Please enter a valid username.", "red"))
        
        # Function to validate date format
        def validate_date(prompt):
            while True:
                date_str = validate_input(prompt)
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                    return date_str
                except ValueError:
                    print(colored("Error: Invalid date format. Please use YYYY-MM-DD format (e.g., 2023-12-31)", "red"))
        
        # Get and validate install date
        license["install_date"] = validate_date("Install Date (YYYY-MM-DD): ")
        
        # Get and validate expiry date (must be after install date)
        while True:
            license["expiry_date"] = validate_date("Expiry Date (YYYY-MM-DD): ")
            install_date = datetime.strptime(license["install_date"], "%Y-%m-%d")
            expiry_date = datetime.strptime(license["expiry_date"], "%Y-%m-%d")
            
            if expiry_date <= install_date:
                print(colored("Error: Expiry date must be after install date.", "red"))
            else:
                break
        
        # Rest of the license details
        license.update({
            "assigned_device": validate_input("Assigned Device: "),
            "usage_limit": validate_input("Usage Limit: ", is_number=True),
            "current_usage": validate_input("Current Usage: ", is_number=True),
            "status": "active"
        })

        # Display the entered license details
        print("\n--- License Details ---")
        for key, value in license.items():
            print(f"{key.capitalize().replace('_', ' ')}: {value}")
        
        # Ask for confirmation
        confirm = validate_input("\nDo you want to save this license? (y/n): ").lower()
        if confirm != 'y':
            print(colored("License not saved.", "red"))
        else:
            # Check if license already exists
            if any(lic['license_key'] == license['license_key'] for lic in licenses):
                print(colored("License with this key already exists!", "red"))
            else:
                licenses.append(license)
                save_licenses(licenses)
                print(colored("License added successfully!", "green"))

        # Ask user if they want to add more licenses
        if input("\nAdd another license? (y/n): ").lower() != 'y':
            break

# Display all licenses
def view_licenses():
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found in the system.", "red"))
        return

    print("\n--- All Licenses ---")
    for i, lic in enumerate(licenses, 1):
        print(f"{i}. {lic['software']} - Key: {lic['license_key']} (User: {lic['user']})")

# Search licenses by software name
def search_license():
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found in the system.", "red"))
        return

    # Convert user input to lowercase for case-insensitive search
    keyword = validate_input("\nEnter software name to search: ").strip().lower()
    found = [lic for lic in licenses if keyword in lic['software'].lower()]
    
    if found:
        print("\n--- Search Results ---")
        for lic in found:
            print(json.dumps(lic, indent=4))
    else:
        print(colored("No license found.", "red"))

# Check and display expired licenses
def check_expired():
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found in the system.", "red"))
        return

    today = datetime.now().date()
    print("\n--- Expired Licenses ---")
    expired_found = False

    for lic in licenses:
        try:
            expiry = datetime.strptime(lic['expiry_date'], "%Y-%m-%d").date()
            if expiry < today:
                lic['status'] = 'expired' # Update status to expired
                print(f"{lic['software']} expired on {lic['expiry_date']}")
                expired_found = True
        except ValueError:
            print(f"Invalid date format for {lic['software']}")

    if not expired_found:
        print(colored("No expired licenses found.", "red"))

    save_licenses(licenses) # Save any status changes

# Update the usage count for a specific software
def update_usage_count():
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found in the system.", "red"))
        return

    software = validate_input("\nEnter software name to update usage: ").strip().lower()
    found = False

    for lic in licenses:
        # Compare with lowercase version of stored software name
        if software in lic['software'].lower():
            new_usage = validate_input("New usage count: ", is_number=True)
            lic['current_usage'] = new_usage
            save_licenses(licenses)
            print("Usage updated.")
            found = True
            break

    if not found:
        print(colored("Software not found.", "red"))

def edit_license():
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found in the system.", "red"))
        return

    # Search for licenses (case-insensitive)
    keyword = validate_input("\nEnter software name to edit: ").strip().lower()
    found = [lic for lic in licenses if keyword in lic['software'].lower()]
    
    if not found:
        print(colored("No licenses found with that name.", "red"))
        return
    
    # Display matching licenses
    print("\n--- Matching Licenses ---")
    for i, lic in enumerate(found, 1):
        print(f"{i}. {lic['software']} (Key: {lic['license_key']})")
    
    # Select license to edit
    choice = validate_input("\nSelect license to edit (number): ", is_number=True)
    if choice < 1 or choice > len(found):
        print(colored("Invalid selection.", "red"))
        return
    
    license_to_edit = found[choice-1]
    original_key = license_to_edit['license_key']

    # Continuous editing loop
    while True:
        # Display editable fields
        print("\n--- Editable Fields ---")
        fields = [
            "software", "license_key", "user", "assigned_device",
            "install_date", "expiry_date", "usage_limit", "current_usage", "status"
        ]
        for i, field in enumerate(fields, 1):
            print(f"{i}. {field.replace('_', ' ').title()}")

        # Get field choice
        field_choice = validate_input("\nChoose field to edit (1-9) or 0 to cancel: ", is_number=True)
        if field_choice == 0:
            break
        if field_choice < 1 or field_choice > 9:
            print(colored("Invalid choice.", "red"))
            continue

        field_name = fields[field_choice-1]
        new_value = validate_input(f"Enter new {field_name.replace('_', ' ')} (current: {license_to_edit[field_name]}): ")

        # Special validation for key fields
        if field_name == "license_key" and new_value != original_key:
            if any(lic['license_key'] == new_value for lic in licenses):
                print(colored("Error: This license key already exists!", "red"))
                continue

        # Validate date formats
        if field_name in ["install_date", "expiry_date"]:
            try:
                datetime.strptime(new_value, "%Y-%m-%d")
            except ValueError:
                print(colored("Invalid date format! Use YYYY-MM-DD.", "red"))
                continue

        # Validate number fields
        if field_name in ["usage_limit", "current_usage"]:
            if not new_value.isdigit():
                print(colored("Error: Must be a number!", "red"))
                continue
            new_value = int(new_value)

        # Validate status field
        if field_name == "status":
            if new_value.lower() not in ["active", "expired"]:
                print(colored("Error: Status must be 'active' or 'expired'", "red"))
                continue
            new_value = new_value.lower()

        # Update and save
        license_to_edit[field_name] = new_value
        save_licenses(licenses)
        print(colored("License updated successfully!", "green"))

        # Ask for another edit
        if input("\nEdit another field? (y/n): ").lower() != 'y':
            break

# Delete license entries based on software name
def delete_license():
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found in the system.", "orange"))
        return

    view_licenses()
    software = validate_input("\nEnter software name to delete: ").strip().lower()
    # Find all matching licenses (case-insensitive)
    matching_licenses = [lic for lic in licenses if software in lic['software'].lower()]

    if not matching_licenses:
        print(colored("No matching license found.", "orange"))
        return

    if len(matching_licenses) == 1:
        # If only one match, show details and confirm deletion
        lic = matching_licenses[0]
        print("\n--- Matching License ---")
        print(f"Software: {lic['software']}")
        print(f"License Key: {lic['license_key']}")
        print(f"Assigned To: {lic['user']}")
        print(f"Expiry Date: {lic['expiry_date']}")
        
        confirm = validate_input("\nAre you sure you want to delete this license? (y/n): ").lower()
        if confirm == 'y':
            licenses.remove(lic)
            save_licenses(licenses)
            print(colored("License deleted successfully!", "green"))
    else:
        # If multiple matches, show list and let user choose
        print("\n--- Multiple Matching Licenses ---")
        for i, lic in enumerate(matching_licenses, 1):
            print(f"\n{i}. Software: {lic['software']}")
            print(f"   License Key: {lic['license_key']}")
            print(f"   Assigned To: {lic['user']}")
            print(f"   Expiry Date: {lic['expiry_date']}")

        while True:
            choice = validate_input("\nEnter the number of the license to delete (or 0 to cancel): ", is_number=True)
            if choice == 0:
                return
            if 1 <= choice <= len(matching_licenses):
                selected_license = matching_licenses[choice-1]
                confirm = validate_input(f"Are you sure you want to delete license '{selected_license['software']}' (Key: {selected_license['license_key']})? (y/n): ").lower()
                if confirm == 'y':
                    licenses.remove(selected_license)
                    save_licenses(licenses)
                    print(colored("License deleted successfully!", "green"))
                break
            else:
                print(colored(f"Please enter a number between 1 and {len(matching_licenses)} or 0 to cancel.", "red"))

# Export license data to a CSV file
def export_to_csv():
    import csv
    licenses = load_licenses()
    if not licenses:
        print(colored("\nNo licenses found to export.", "red"))
        return

    # Write license data to CSV file
    with open("licenses_export.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=licenses[0].keys())
        writer.writeheader()
        writer.writerows(licenses)
    print(colored("Licenses exported to licenses_export.csv", "green"))

# ------------------ MAIN MENU ------------------

# Admin menu with full access
def admin_menu():
    while True:
        try:
            menu_gui = pyfiglet.figlet_format("Admin License Inventory Menu")
            print(colored(menu_gui, "green"))

            print("[1] Register New User")
            print("[2] Add New License")
            print("[3] View All Licenses")
            print("[4] Search License")
            print("[5] Check Expired Licenses")
            print("[6] Update Usage Count")
            print("[7] Edit License")  # NEW OPTION
            print("[8] Delete License")
            print("[9] Export to CSV")
            print(colored("[10] Logout", "red"))  # Updated logout number

            choice = validate_input("\nEnter your choice: ", is_number=True)
            if choice == 1:
                register_user()
            elif choice == 2:
                add_license()
            elif choice == 3:
                view_licenses()
            elif choice == 4:
                search_license()
            elif choice == 5:
                check_expired()
            elif choice == 6:
                update_usage_count()
            elif choice == 7:  # NEW CASE
                edit_license()
            elif choice == 8:
                delete_license()
            elif choice == 9:
                export_to_csv()
            elif choice == 10:  # Updated from 9
                print(colored("Logging out...", "red"))
                return
            else:
                print(colored("Invalid choice. Please enter a number between 1-10.", "red"))
        except ValueError:
            print(colored("Invalid input. Please try again.", "red"))

def employee_menu():
    while True:
        try:
            # Display ASCII-style header
            menu_gui = pyfiglet.figlet_format("Employee License Inventory Menu")
            print(menu_gui)

            # Employee options
            print("[1] View All Licenses")
            print("[2] Search License")
            print("[3] Check Expired Licenses")
            print("[4] Update Usage Count")
            print(colored("[5] Logout", "red"))

            # Get user input
            choice = validate_input("Enter your choice: ", is_number=True)

            if choice == 1:
                view_licenses()
            elif choice == 2:
                search_license()
            elif choice == 3:
                check_expired()
            elif choice == 4:
                update_usage_count()
            elif choice == 5:
                print(colored("Logging out...", "red"))
                return  # Return to login menu
            else:
                print(colored("Invalid choice. Please enter a number between 1-5.", "red"))
        except ValueError:
            print(colored("Invalid input. Please try again.", "red"))

# ------------------ ENTRY POINT ------------------

if __name__ == "__main__":
    # Initial user check for first-time setup
    users = load_users()

    # If no users exist, force admin creation
    if not users:
        title = pyfiglet.figlet_format("SOFTWHERE")
        print(colored(title, "blue"))
        print("\n=== FIRST-TIME SETUP ===")
        print(colored("No existing accounts found. Create an admin account.", "blue"))
        username = validate_input("Admin username: ")
        password = validate_input("Admin password (Must be at least 4 characters long): ", is_password=True)

        users.append({
            "username": username,
            "password": hash_password(password),
            "role": "admin"
        })
        save_users(users)
        print(colored("\nAdmin account created successfully! Please login.\n", "green"))

    # Main program loop
    while True:
        role = login_menu()  # Get role or None for exit
        
        if role is None:  # User chose to exit
            break
        elif role == 'admin':
            admin_menu()
        elif role == 'employee':
            employee_menu()
