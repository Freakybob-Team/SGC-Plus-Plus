"""
SGC++ program runner

This program runs the SGC++ program!!! meaning that SGC++ offically works on any device with python (hopefully)!!!!

-----------------------------------------------------------
cooked up by Squirrel Gay Acorns (5quirre1) :3
"""
import os
import json
import subprocess
import argparse
import time
import platform
from shutil import get_terminal_size
import sys
import threading
try:
    import inquirer
except ImportError:
    print("inquirer not installed.. installing it now..")
    os.system("pip install inquirer")
    import inquirer

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
def print_centered(text, width=None, color=None):
    if not width:
        width = get_terminal_size().columns
    if color:
        print(f"{color}{text.center(width)}{Colors.ENDC}")
    else:
        print(text.center(width))
def print_boxed(title, width=None):
    if not width:
        width = get_terminal_size().columns - 4
    print(f"┌{'─' * width}┐")
    print_centered(title, width)
    print(f"└{'─' * width}┘")
def find_file(message, filter_func):
    selected_path = None
    items = os.listdir(".")
    items = [item for item in items if not item.startswith('.')] 
    filtered_items = [item for item in items if filter_func(item)]
    if filtered_items:
        print(f"\n{Colors.HEADER}Available {message}:{Colors.ENDC}")
        for idx, item in enumerate(filtered_items, 1):
            print(f"  {Colors.BOLD}{idx}.{Colors.ENDC} {item}")
        print(f"\n  {Colors.BLUE}0.{Colors.ENDC} enter path: ")
        while True:
            try:
                choice = input(f"\n{Colors.BOLD}select a {message} by number, or press 0 to enter the path manually:{Colors.ENDC} ")
                if choice == "0":
                    selected_path = input(f"\n{Colors.BOLD}enter the path to the {message}:{Colors.ENDC} ").strip()
                    if os.path.exists(selected_path):
                        selected_path = os.path.abspath(selected_path)
                        break
                    else:
                        print(f"{Colors.FAIL}path does not exist...{Colors.ENDC}")
                elif choice.isdigit() and 1 <= int(choice) <= len(filtered_items):
                    selected_path = os.path.abspath(filtered_items[int(choice) - 1])
                    break
                else:
                    print(f"{Colors.WARNING}vro is it that hard :sob:{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.WARNING}vro is it that hard :sob:{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}no {message} found in the current directory...{Colors.ENDC}")
        selected_path = input(f"\n{Colors.BOLD}enter the path to the {message}:{Colors.ENDC} ").strip()
        if os.path.exists(selected_path):
            selected_path = os.path.abspath(selected_path)
        else:
            print(f"{Colors.FAIL}no exist...{Colors.ENDC}")
            return None
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
        print(f"{Colors.GREEN}main.py path saved to {config_path}!{Colors.ENDC}")
        return True
    except IOError as e:
        print(f"{Colors.FAIL}error saving configuration: {e}{Colors.ENDC}")
        return False
def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config.get("main_py_path")
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Colors.FAIL}error loading configuration: {e}{Colors.ENDC}")
    return None
def execute_script(main_py_path, sgcx_path):
    print(f"\n{Colors.HEADER}executing..{Colors.ENDC}")
    print(f"  {Colors.BOLD}interpreter:{Colors.ENDC} {main_py_path}")
    print(f"  {Colors.BOLD}program:{Colors.ENDC} {sgcx_path}")
    print("\n" + "─" * get_terminal_size().columns)
    try:
        subprocess.run(["python", main_py_path, sgcx_path], check=True)
        print("\n" + "─" * get_terminal_size().columns)
    except subprocess.CalledProcessError as e:
        print("\n" + "─" * get_terminal_size().columns)
        print(f"{Colors.FAIL}error executing {sgcx_path}: {e}{Colors.ENDC}")
    except FileNotFoundError as e:
        print(f"{Colors.FAIL}not found but uhh here: {e}{Colors.ENDC}")
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
def loading_animation(stop_event, text="Loading"):
    animations = [
        "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏",  
        "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",  
        "▉▊▋▌▍▎▏▎▍▌▋▊▉",    
        "←↖↑↗→↘↓↙",         
        "◢◣◤◥",             
        "◰◳◲◱",             
    ]
    animation = animations[1]  
    i = 0
    width = get_terminal_size().columns
    while not stop_event.is_set():
        frame = animation[i % len(animation)]
        sys.stdout.write(f"\r{text} {frame}".center(width))
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write('\r' + ' ' * width + '\r')
    sys.stdout.flush()
def show_splash():
    clear_screen()
    width = min(get_terminal_size().columns - 10, 60)
    stop_animation = threading.Event()
    animation_thread = threading.Thread(target=loading_animation, args=(stop_animation, "starting the sgc++ runner.."))
    animation_thread.daemon = True
    animation_thread.start()
    time.sleep(2)
    stop_animation.set()
    animation_thread.join()
    clear_screen()
    print("\n\n")
    print_centered("╔" + "═" * width + "╗", width + 2)
    print_centered("║" + " " * width + "║", width + 2)
    print_centered("║" + "SGC++ runner".center(width) + "║", width + 2, Colors.BOLD + Colors.BLUE)
    print_centered("║" + " " * width + "║", width + 2)
    print_centered("║" + "This program runs the SGC++ program!!!".center(width) + "║", width + 2)
    print_centered("║" + "meaning that SGC++ offically works on any device".center(width) + "║", width + 2)
    print_centered("║" + "with python (hopefully)!!!!".center(width) + "║", width + 2)
    print_centered("║" + " " * width + "║", width + 2)
    print_centered("╚" + "═" * width + "╝", width + 2)
    print("\n")
    print_centered("Loading..", width)
    for i in range(width + 1):
        progress = "█" * i + "░" * (width - i)
        percent = int(100 * i / width)
        sys.stdout.write(f"\r{progress} {percent}%".center(get_terminal_size().columns))
        sys.stdout.flush()
        if i < width * 0.2 or i > width * 0.8:
            time.sleep(0.01)
        else:
            time.sleep(0.02)
    print("\n\n")
    print_centered(f"{Colors.GREEN}ready!!{Colors.ENDC}", width)
    time.sleep(0.5)
def show_main_menu():
    clear_screen()
    width = get_terminal_size().columns - 10
    print("\n")
    print_boxed(f"{Colors.BOLD}SGC++ runner menu:{Colors.ENDC}", width)
    print("")
    main_py_path = load_config()
    if main_py_path:
        status = f"{Colors.GREEN}configured{Colors.ENDC}"
        print(f"  main.py path: {status} ({main_py_path})")
    else:
        status = f"{Colors.WARNING}Not Configured{Colors.ENDC}"
        print(f"  main.py path: {status}")
    print("\n  " + "=" * (width - 4))
    print(f"  {Colors.BLUE}1.{Colors.ENDC} run SGC++ program")
    print(f"  {Colors.BLUE}2.{Colors.ENDC} configure main.py path")
    print(f"  {Colors.BLUE}3.{Colors.ENDC} exit")
    print(f"  " + "=" * (width - 4))
    print("")
    return input(f"  {Colors.BOLD}>>>{Colors.ENDC} ")
def configure_path():
    clear_screen()
    print_boxed("Configure main.py path")
    print("")
    current_path = load_config()
    if current_path:
        print(f"  current path: {Colors.BLUE}{current_path}{Colors.ENDC}")
        print("")
        questions = [
            inquirer.List('confirm',
                          message=f"{Colors.WARNING}You already have a config for this, are you sure you want to edit it?{Colors.ENDC}",
                          choices=['Yes', 'No'],
                          default='No'),
        ]
        answers = inquirer.prompt(questions)
        if answers['confirm'] == 'No':
            print(f"\n{Colors.GREEN}configuration unchanged.{Colors.ENDC}")
            input(f"\n{Colors.BOLD}press enter to continue...{Colors.ENDC}")
            return  
    main_py_path = find_file("main.py file", lambda x: x.lower() == "main.py")
    if not main_py_path:
        main_py_path = input(f"\n{Colors.BOLD}Enter path for main.py:{Colors.ENDC} ").strip()
    if main_py_path and os.path.exists(main_py_path):
        save_config(main_py_path)
    else:
        print(f"{Colors.FAIL}{main_py_path} no exist...{Colors.ENDC}")
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
def run_program():
    clear_screen()
    print_boxed("run SGC++ program")
    print("")
    main_py_path = load_config()
    if not main_py_path:
        print(f"{Colors.FAIL}main.py config has not been done, plz do that before run{Colors.ENDC}")
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        return
    sgcx_path = find_file("SGCX file", lambda x: x.lower().endswith(".sgcx"))
    if sgcx_path:
        print(f"{Colors.BOLD}{'-' * 50}{Colors.ENDC}")
        execute_script(main_py_path, sgcx_path)
def main():
    parser = argparse.ArgumentParser(description="Run SGC++ programs.")
    parser.add_argument("sgcx_file", nargs="?", help="path to the sgc++ program!")
    args = parser.parse_args()
    if args.sgcx_file:
        main_py_path = load_config()
        if not main_py_path:
            print(f"{Colors.FAIL}main.py config has not been done, plz do that before run{Colors.ENDC}")
        else:
            print(f"{Colors.BOLD}{'-' * 50}{Colors.ENDC}")
            execute_script(main_py_path, args.sgcx_file)
    else:
        show_splash()
        while True:
            choice = show_main_menu()
            if choice == "1":
                run_program()
            elif choice == "2":
                configure_path()
            elif choice == "3":
                clear_screen()
                print("\n")
                print_centered(f"{Colors.GREEN}bai bai !!!{Colors.ENDC}")
                print("\n")
                time.sleep(1)
                break
            else:
                print(f"\n{Colors.WARNING}no work because invald{Colors.ENDC}")
                time.sleep(1)
if __name__ == "__main__":
    main()
