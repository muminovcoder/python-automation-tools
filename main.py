import argparse
import sys
from pathlib import Path

TOOLS = {
    "1": {"name": "File Organizer", "module": "file_organizer", "desc": "Organize files by extension"},
    "2": {"name": "Backup Manager", "module": "backup_manager", "desc": "Automated backup with scheduling"},
    "3": {"name": "PDF Merger", "module": "pdf_merger", "desc": "Merge multiple PDF files"},
    "4": {"name": "CSV Validator", "module": "csv_validator", "desc": "Validate and clean CSV data"},
    "5": {"name": "Web Scraper", "module": "web_scraper", "desc": "Extract data from websites"},
}


def show_menu():
    print("\n" + "=" * 50)
    print("  PYTHON AUTOMATION TOOLS")
    print("=" * 50)
    for key, tool in TOOLS.items():
        print(f"  [{key}] {tool['name']} - {tool['desc']}")
    print("  [0] Exit")
    print("=" * 50)


def run_tool(choice: str):
    tool = TOOLS.get(choice)
    if not tool:
        print("Invalid choice!")
        return False
    try:
        module = __import__(tool["module"])
        if hasattr(module, "main"):
            module.main()
        else:
            print(f"{tool['name']} module has no main() function")
        return True
    except ImportError as e:
        print(f"Error loading {tool['module']}: {e}")
        print(f"Make sure {tool['module']}.py exists in the current directory")
        return False
    except Exception as e:
        print(f"Error running {tool['name']}: {e}")
        return False


def cli_mode():
    parser = argparse.ArgumentParser(description="Python Automation Tools")
    parser.add_argument("tool", nargs="?", choices=[str(i) for i in range(1, 6)],
                        help="Tool number to run directly")
    args = parser.parse_args()
    if args.tool:
        run_tool(args.tool)
    else:
        interactive_mode()


def interactive_mode():
    while True:
        show_menu()
        choice = input("\nSelect a tool (0-5): ").strip()
        if choice == "0":
            print("Goodbye!")
            sys.exit(0)
        run_tool(choice)
        input("\nPress Enter to continue...")


def main():
    if len(sys.argv) > 1:
        cli_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
