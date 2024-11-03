import subprocess


def get_links():
    subprocess.run(["python", "get_links.py"])


def scrape_data():
    subprocess.run(["python", "scrape_data.py"])


def export_data():
    subprocess.run(["python", "export_sheet.py"])


def clear_data():
    subprocess.run(["python", "clear_data.py"])


def main():
    while True:
        print("\nPlease choose an option:")
        print("1. Get Links")
        print("2. Scrape Data")
        print("3. Export Data")
        print("4. Clear Data")
        print("5. Exit")

        choice = input("Enter the number of the task you want to perform: ")

        if choice == "1":
            print("Running 'Get Links'...")
            get_links()
        elif choice == "2":
            print("Running 'Scrape Data'...")
            scrape_data()
        elif choice == "3":
            print("Running 'Export Data'...")
            export_data()
        elif choice == "4":
            print("Running 'Clear Data'...")
            clear_data()
        elif choice == "5":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
