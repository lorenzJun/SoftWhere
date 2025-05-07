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
            print("Error: Input cannot be empty. Please try again.")
            continue

        if is_password:
            if len(user_input) < 4:
                print("Error: Password must be at least 4 characters long.")
                continue

        if is_number:
            if not user_input.isdigit():
                print("Error: Please enter a valid number.")
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
        print("Error: Passwords do not match!")
        return

    while True:
        role = validate_input("Role (admin/employee): ").lower()
        if role in ['admin', 'employee']:
            break
        print("Error: Role must be either 'admin' or 'employee'")

    users = load_users()

    for user in users:
        if user['username'] == username:
            print("Username already exists!")
            return

    users.append({
        "username": username,
        "password": hash_password(password),
        "role": role
    })
    save_users(users)
    print("User registered successfully!")

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
            print("Invalid choice. Please enter 1 or 2.")

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
        print("\n--- Add New License ---")
        
        # Collect license details from user
        license = {
            "software": validate_input("Software Name: "),
            "license_key": validate_input("License Key: "),
            "user": validate_input("Assigned To (Name): "),
            "assigned_device": validate_input("Assigned Device: "),
            "install_date": validate_input("Install Date (YYYY-MM-DD): "),
            "expiry_date": validate_input("Expiry Date (YYYY-MM-DD): "),
            "usage_limit": validate_input("Usage Limit: ", is_number=True),
            "current_usage": validate_input("Current Usage: ", is_number=True),
            "status": "active"
        }

        # Display the entered license details
        print("\n--- License Details ---")
        for key, value in license.items():
            print(f"{key.capitalize().replace('_', ' ')}: {value}")
        
        # Ask for confirmation
        confirm = validate_input("\nDo you want to save this license? (y/n): ").lower()
        if confirm != 'y':
            print("License not saved.")
        else:
            # Check if license already exists
            if any(lic['license_key'] == license['license_key'] for lic in licenses):
                print("License with this key already exists!")
            else:
                licenses.append(license)
                save_licenses(licenses)
                print("License added successfully!")

        # Ask user if they want to add more licenses
        if input("\nAdd another license? (y/n): ").lower() != 'y':
            break

# Display all licenses
def view_licenses():
    licenses = load_licenses()
    if not licenses:
        print("\nNo licenses found in the system.")
        return

    print("\n--- All Licenses ---")
    for i, lic in enumerate(licenses, 1):
        print(f"{i}. {lic['software']} - Key: {lic['license_key']} (User: {lic['user']})")

# Search licenses by software name
def search_license():
    licenses = load_licenses()
    if not licenses:
        print("\nNo licenses found in the system.")
        return

    # Convert user input to lowercase for case-insensitive search
    keyword = validate_input("\nEnter software name to search: ").strip().lower()
    found = [lic for lic in licenses if keyword in lic['software'].lower()]
    
    if found:
        print("\n--- Search Results ---")
        for lic in found:
            print(json.dumps(lic, indent=4))
    else:
        print("No license found.")

# Check and display expired licenses
def check_expired():
    licenses = load_licenses()
    if not licenses:
        print("\nNo licenses found in the system.")
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
        print("No expired licenses found.")

    save_licenses(licenses) # Save any status changes

# Update the usage count for a specific software
def update_usage_count():
    licenses = load_licenses()
    if not licenses:
        print("\nNo licenses found in the system.")
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
        print("Software not found.")

# Delete license entries based on software name
def delete_license():
    licenses = load_licenses()
    if not licenses:
        print("\nNo licenses found in the system.")
        return

    software = validate_input("\nEnter software name to delete: ").strip().lower()
    original_count = len(licenses)

    # Case-insensitive comparison
    licenses = [lic for lic in licenses if software not in lic['software'].lower()]

    if len(licenses) != original_count:
        save_licenses(licenses)
        print("License deleted.")
    else:
        print("No matching license found.")

# Export license data to a CSV file
def export_to_csv():
    import csv
    licenses = load_licenses()
    if not licenses:
        print("\nNo licenses found to export.")
        return

    # Write license data to CSV file
    with open("licenses_export.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=licenses[0].keys())
        writer.writeheader()
        writer.writerows(licenses)
    print("Licenses exported to licenses_export.csv")

# ------------------ MAIN MENU ------------------

# Admin menu with full access
def admin_menu():
    while True:
        try:
            # Display ASCII-style header
            menu_gui = pyfiglet.figlet_format("Admin License Inventory Menu")
            print(colored(menu_gui, "green"))

            # Admin options
            print("[1] Register New User")
            print("[2] Add New License")
            print("[3] View All Licenses")
            print("[4] Search License")
            print("[5] Check Expired Licenses")
            print("[6] Update Usage Count")
            print("[7] Delete License")
            print("[8] Export to CSV")
            print(colored("[9] Logout", "red"))

            # Get user input
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
            elif choice == 7:
                delete_license()
            elif choice == 8:
                export_to_csv()
            elif choice == 9:
                print(colored("Logging out...", "red"))
                return  # Return to login menu 
            else:
                print("Invalid choice. Please enter a number between 1-9.")
        except ValueError:
            print("Invalid input. Please try again.")

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
                print("Invalid choice. Please enter a number between 1-5.")
        except ValueError:
            print("Invalid input. Please try again.")

# ------------------ ENTRY POINT ------------------

if __name__ == "__main__":
    # Initial user check for first-time setup
    users = load_users()

    # If no users exist, force admin creation
    if not users:
        print("\n=== FIRST-TIME SETUP ===")
        print("No existing accounts found. Create an admin account.")
        username = validate_input("Admin username: ")
        password = validate_input("Admin password (Must be at least 4 characters long): ", is_password=True)

        users.append({
            "username": username,
            "password": hash_password(password),
            "role": "admin"
        })
        save_users(users)
        print("\nAdmin account created successfully! Please login.\n")

    # Main program loop
    while True:
        role = login_menu()  # Get role or None for exit
        
        if role is None:  # User chose to exit
            break
        elif role == 'admin':
            admin_menu()
        elif role == 'employee':
            employee_menu()