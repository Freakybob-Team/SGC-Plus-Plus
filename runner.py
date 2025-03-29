"""
SGC++ program runner

This program runs the SGC++ program!!! meaning that SGC++ offically works on any device with python (hopefully)!!!!
"""
import os
import json
import subprocess
import argparse
def find_file(message, filter_func):
    selected_path = None
    items = os.listdir(".")
    items = [item for item in items if not item.startswith('.')] 
    filtered_items = [item for item in items if filter_func(item)]
    if filtered_items:
        print(f"\nAvailable {message}:")
        for idx, item in enumerate(filtered_items, 1):
            print(f"{idx}. {item}")
        while True:
            try:
                choice = int(input(f"select a {message} by number, or press 0 to enter the path manually: "))
                if choice == 0:
                    selected_path = input(f"Enter the path to the {message}: ").strip()
                    if os.path.exists(selected_path):
                        selected_path = os.path.abspath(selected_path)
                        break
                    else:
                        print("path does not exist...")
                elif 1 <= choice <= len(filtered_items):
                    selected_path = os.path.abspath(filtered_items[choice - 1])
                    break
            except ValueError:
                pass 
            print(f"vro is it that hard :sob:")
    else:
        selected_path = input(f"enter the path to the {message}: ").strip()
        if os.path.exists(selected_path):
            selected_path = os.path.abspath(selected_path)
        else:
            print("no exist...")
    return selected_path
def get_config_path():
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, "SGC++")  
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")
def save_config(main_py_path):
    config_path = get_config_path()
    config = {"main_py_path": os.path.abspath(main_py_path)}
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        print(f"main.py path saved to {config_path}!")
    except IOError as e:
        print(f"Error saving configuration: {e}")
def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config.get("main_py_path")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading configuration: {e}")
    return None
def execute_script(main_py_path, sgcx_path):
    try:
        subprocess.run(["python", main_py_path, sgcx_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"error executing {sgcx_path}: {e}")
    except FileNotFoundError as e:
        print(f"not found but uhh here: {e}")
def main():
    parser = argparse.ArgumentParser(description="Run SGC++ programs.")
    parser.add_argument("sgcx_file", nargs="?", help="Path to the .sgcx file.")
    args = parser.parse_args()
    if args.sgcx_file:
        main_py_path = load_config()
        if not main_py_path:
            print("main.py config has not been done, plz do that before run")
        else:
            print("-" * 50)
            execute_script(main_py_path, args.sgcx_file)
    else:
        while True:
            print("|" * 50)
            print("=" * 50)
            print("SGC++ Runner Menu:")
            print("1. run SGC++ program")
            print("2. configure main.py path")
            print("3. exit")
            print("=" * 50)
            choice = input(">>> ")
            if choice == "1":
                sgcx_path = find_file("SGCX file", lambda x: x.lower().endswith(".sgcx"))
                if sgcx_path:
                    main_py_path = load_config()
                    if not main_py_path:
                        print("main.py config has not been done, plz do that before run")
                    else:
                        print("-" * 50)
                        execute_script(main_py_path, sgcx_path)
            elif choice == "2":
                main_py_path = input("enter path for main.py: ").strip()
                if os.path.exists(main_py_path):
                    save_config(main_py_path)
                else:
                    print(f"{main_py_path} no exist...")
            elif choice == "3":
                print("bai bai !!!!")
                break
            else:
                print("no work because invald")
if __name__ == "__main__":
    main()
