"""
SGC++ program runner
This program runs the SGC++ program!!! meaning that SGC++ offically works on any device with python (hopefully)!!!!!
-----------------------------------------------------------
cooked up by Squirrel Acorns (5quirre1) :3
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
    CYAN = '\033[96m'
    MAGENTA = '\033[35m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
def print_centered(text, width=None, color=None):
    if not width:
        width = get_terminal_size().columns
    if color:
        print(f"{color}{text.center(width)}{Colors.ENDC}")
    else:
        print(text.center(width))
def print_boxed(title, width=None, color=None):
    if not width:
        width = get_terminal_size().columns - 4
    print(f"┌{'─' * width}┐")
    if color:
        print_centered(title, width, color)
    else:
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
def save_config(config_data):
    config_path = get_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, indent=4, fp=f)
        print(f"{Colors.GREEN}Configuration saved to {config_path}!{Colors.ENDC}")
        return True
    except IOError as e:
        print(f"{Colors.FAIL}error saving configuration: {e}{Colors.ENDC}")
        return False
def load_config():
    config_path = get_config_path()
    default_config = {
        "main_py_path": None,
        "show_splash": True,
        "splash_duration": 2.0,
        "splash_color": "blue",
        "splash_style": "default",
        "progress_bar": True,
        "animation_style": 1,
        "theme": "default"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
            return config
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Colors.FAIL}error loading configuration: {e}{Colors.ENDC}")
            return default_config
    return default_config
def execute_script(main_py_path, sgcx_path):
    print(f"\n{Colors.HEADER}executing..{Colors.ENDC}")
    print(f"  {Colors.BOLD}interpreter:{Colors.ENDC} {main_py_path}")
    print(f"  {Colors.BOLD}program:{Colors.ENDC} {sgcx_path}")
    print("\n" + "─" * get_terminal_size().columns)
    try:
        subprocess.run(["python", main_py_path, sgcx_path], check=True)
        print("\n" + "─" * get_terminal_size().columns)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            print("\n" + "─" * get_terminal_size().columns)
            print(f"{Colors.FAIL}error executing {sgcx_path}: {e}{Colors.ENDC}")
    except FileNotFoundError as e:
        print(f"{Colors.FAIL}not found but uhh here: {e}{Colors.ENDC}")
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
def get_color_by_name(color_name):
    color_dict = {
        "blue": Colors.BLUE,
        "green": Colors.GREEN,
        "red": Colors.RED,
        "yellow": Colors.YELLOW,
        "magenta": Colors.MAGENTA,
        "cyan": Colors.CYAN,
        "header": Colors.HEADER,
        "default": Colors.BLUE
    }
    return color_dict.get(color_name.lower(), Colors.BLUE)
def loading_animation(stop_event, text="Loading", animation_style=1):
    animations = [
        "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏",
        " ▂▃▄▅▆▇█▇▆▅▄▃▂ ",
        "▉▊▋▌▍▎▏▎▍▌▋▊▉",
        "←↖↑↗→↘↓↙",
        "◢◣◤◥",
        "◰◳◲◱",
        "🌑🌒🌓🌔🌕🌖🌗🌘",
        ".oO°Oo.",
    ]
    if animation_style < 0 or animation_style >= len(animations):
        animation_style = 1
    animation = animations[animation_style]
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
def show_splash(config):
    if not config.get("show_splash", True):
        return
    clear_screen()
    width = min(get_terminal_size().columns - 10, 60)
    splash_color = get_color_by_name(config.get("splash_color", "blue"))
    splash_duration = float(config.get("splash_duration", 2.0))
    animation_style = int(config.get("animation_style", 1))
    splash_style = config.get("splash_style", "default")
    stop_animation = threading.Event()
    animation_thread = threading.Thread(
        target=loading_animation, 
        args=(stop_animation, "starting the sgc++ runner..", animation_style)
    )
    animation_thread.daemon = True
    animation_thread.start()
    time.sleep(splash_duration)
    stop_animation.set()
    animation_thread.join()
    clear_screen()
    print("\n\n")
    if splash_style == "minimal":
        print_centered("SGC++ Runner", width, splash_color + Colors.BOLD)
        print_centered("Starting...", width)
    elif splash_style == "ascii":
        ascii_art = [
           """
 #####   #####   #####              
#     # #     # #     #   #     #   
#       #       #         #     #   
 #####  #  #### #       ##### ##### 
      # #     # #         #     #   
#     # #     # #     #   #     #   
 #####   #####   #####              𝙍𝙐𝙉𝙉𝙀𝙍 𝒗1.1
           """
        ]
        for line in ascii_art:
            print_centered(line, width, splash_color)
        print_centered("Runner v1.1", width)
    else:
        print_centered("╔" + "═" * width + "╗", width + 2)
        print_centered("║" + " " * width + "║", width + 2)
        print_centered("║" + "SGC++ runner".center(width) + "║", width + 2, splash_color + Colors.BOLD)
        print_centered("║" + " " * width + "║", width + 2)
        print_centered("║" + "This program runs the SGC++ program!!!".center(width) + "║", width + 2)
        print_centered("║" + "meaning that SGC++ offically works on any device".center(width) + "║", width + 2)
        print_centered("║" + "with python (hopefully)!!!!".center(width) + "║", width + 2)
        print_centered("║" + " " * width + "║", width + 2)
        print_centered("╚" + "═" * width + "╝", width + 2)
    print("\n")
    if config.get("progress_bar", True):
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
def apply_theme(theme_name):
    themes = {
        "default": {
            "menu_color": Colors.BLUE,
            "title_color": Colors.BOLD,
            "highlight": Colors.GREEN
        },
        "dark": {
            "menu_color": Colors.CYAN,
            "title_color": Colors.BOLD + Colors.CYAN,
            "highlight": Colors.MAGENTA
        },
        "squirrel": {
            "menu_color": Colors.YELLOW,
            "title_color": Colors.BOLD + Colors.YELLOW,
            "highlight": Colors.RED
        },
        "pastel": {
            "menu_color": Colors.MAGENTA,
            "title_color": Colors.BOLD + Colors.MAGENTA,
            "highlight": Colors.CYAN
        }
    }
    return themes.get(theme_name, themes["default"])
def show_main_menu(config):
    clear_screen()
    width = get_terminal_size().columns - 10
    theme = apply_theme(config.get("theme", "default"))
    print("\n")
    print_boxed(f"SGC++ runner menu:", width, theme["title_color"])
    print("")
    main_py_path = config.get("main_py_path")
    if main_py_path:
        status = f"{Colors.GREEN}configured{Colors.ENDC}"
        print(f"  main.py path: {status} ({main_py_path})")
    else:
        status = f"{Colors.WARNING}Not Configured{Colors.ENDC}"
        print(f"  main.py path: {status}")
    splash_status = "Enabled" if config.get("show_splash", True) else "Disabled"
    if splash_status == "Disabled":
        oh = f"{Colors.FAIL}{splash_status}{Colors.ENDC}"
    else:
        oh = f"{Colors.GREEN}{splash_status}{Colors.ENDC}"
    print(f"  splash screen: {oh}")
    print(f"  theme: {theme['title_color']}{config.get('theme', 'default')}{Colors.ENDC}")
    print("\n  " + "=" * (width - 4))
    print(f"  {theme['menu_color']}1.{Colors.ENDC} run SGC++ program")
    print(f"  {theme['menu_color']}2.{Colors.ENDC} configure main.py path")
    print(f"  {theme['menu_color']}3.{Colors.ENDC} settings")
    print(f"  {theme['menu_color']}4.{Colors.ENDC} about")
    print(f"  {theme['menu_color']}5.{Colors.ENDC} exit")
    print(f"  " + "=" * (width - 4))
    print("")
    return input(f"  {theme['title_color']}>>>{Colors.ENDC} ")
def configure_path(config):
    clear_screen()
    print_boxed("Configure main.py path")
    print("")
    current_path = config.get("main_py_path")
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
            return config
    main_py_path = find_file("main.py file", lambda x: x.lower() == "main.py")
    if not main_py_path:
        main_py_path = input(f"\n{Colors.BOLD}Enter path for main.py:{Colors.ENDC} ").strip()
    if main_py_path and os.path.exists(main_py_path):
        config["main_py_path"] = main_py_path
        save_config(config)
    else:
        print(f"{Colors.FAIL}{main_py_path} no exist...{Colors.ENDC}")
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
    return config
def run_program(config):
    clear_screen()
    print_boxed("run SGC++ program")
    print("")
    main_py_path = config.get("main_py_path")
    if not main_py_path:
        print(f"{Colors.FAIL}main.py config has not been done, plz do that before run{Colors.ENDC}")
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        return
    sgcx_path = find_file("SGCX file", lambda x: x.lower().endswith(".sgcx"))
    if sgcx_path:
        print(f"{Colors.BOLD}{'-' * 50}{Colors.ENDC}")
        execute_script(main_py_path, sgcx_path)
def settings_menu(config):
    while True:
        clear_screen()
        width = get_terminal_size().columns - 10
        theme = apply_theme(config.get("theme", "default"))
        print("\n")
        print_boxed("    Settings Menu    ", width, theme["title_color"])
        print("\n")
        print(f"  {theme['title_color']}Current Configuration{Colors.ENDC}")
        print(f"  {theme['menu_color']}{'─' * (width - 4)}{Colors.ENDC}")
        settings = [
            ("Splash Screen", "show_splash", {'Enabled': f"{Colors.GREEN}Enabled{Colors.ENDC}", 'Disabled': f"{Colors.FAIL}Disabled{Colors.ENDC}"}, ""),
            ("Splash Style", "splash_style", None, ""),
            ("Splash Color", "splash_color", None, ""),
            ("Animation Style", "animation_style", None, ""),
            ("Progress Bar", "progress_bar", {'Enabled': f"{Colors.GREEN}Enabled{Colors.ENDC}", 'Disabled': f"{Colors.FAIL}Disabled{Colors.ENDC}"}, ""),
            ("Splash Duration", "splash_duration", None, " seconds"),
            ("Theme", "theme", None, "")
]
        for i, (label, key, value_map, suffix) in enumerate(settings + [(None, None, None, None)], 1):
            if label is None:
                print(f"  {theme['menu_color']}{'─' * (width - 4)}{Colors.ENDC}")
                print(f"  {theme['menu_color']}{i}.{Colors.ENDC} Return to Main Menu")
                continue
            suffix = suffix if suffix else ""
            value = config.get(key, "default" if key == "theme" or key == "splash_style" else (True if key in ["show_splash", "progress_bar"] else 1))
            if value_map:
                if isinstance(value, bool):
                    display_value = value_map['Enabled'] if value else value_map['Disabled']
                else:
                    display_value = value_map.get(value, value)
            else:
                if isinstance(value, bool):
                    display_value = f"{Colors.GREEN}Enabled{Colors.ENDC}" if value else f"{Colors.FAIL}Disabled{Colors.ENDC}"
                elif isinstance(value, (int, float)):
                    display_value = f"{theme['highlight']}{value}{Colors.ENDC}{suffix}"
                else:
                    display_value = f"{theme['highlight']}{value}{Colors.ENDC}"
            print(f"  {theme['menu_color']}{i}.{Colors.ENDC} {label}: {display_value}")
        print("\n")
        choice = input(f"  {theme['title_color']}Select option (1-{len(settings) + 1}):{Colors.ENDC} ")
        try:
            choice_num = int(choice)
            if choice_num == len(settings) + 1:
                break
            if 1 <= choice_num <= len(settings):
                option_name = settings[choice_num - 1][0]
                setting_key = settings[choice_num - 1][1]
                print(f"\n  {theme['title_color']}Changing {option_name}{Colors.ENDC}")
                if setting_key == "show_splash" or setting_key == "progress_bar":
                    questions = [
                        inquirer.List(setting_key,
                                    message=f'Enable {option_name.strip("🖼️ 📊 ")}?',
                                    choices=['Enabled', 'Disabled'],
                                    default='Enabled' if config.get(setting_key, True) else 'Disabled'),
                    ]
                    answers = inquirer.prompt(questions)
                    config[setting_key] = answers[setting_key] == 'Enabled'
                elif setting_key == "splash_style":
                    print("\n  Style Preview:")
                    print(f"  {theme['menu_color']}• default:{Colors.ENDC} Full boxed format with details")
                    print(f"  {theme['menu_color']}• minimal:{Colors.ENDC} Simple text only format")
                    print(f"  {theme['menu_color']}• ascii:{Colors.ENDC} ASCII art logo format")
                    questions = [
                        inquirer.List(setting_key,
                                    message='Select splash screen style:',
                                    choices=['default', 'minimal', 'ascii'],
                                    default=config.get(setting_key, 'default')),
                    ]
                    answers = inquirer.prompt(questions)
                    config[setting_key] = answers[setting_key]
                elif setting_key == "splash_color":
                    print("\n  Color Preview:")
                    colors = ['blue', 'green', 'red', 'yellow', 'magenta', 'cyan']
                    color_samples = {
                        'blue': Colors.BLUE,
                        'green': Colors.GREEN,
                        'red': Colors.RED,
                        'yellow': Colors.YELLOW,
                        'magenta': Colors.MAGENTA,
                        'cyan': Colors.CYAN
                    }
                    for color in colors:
                        print(f"  {theme['menu_color']}• {color}:{Colors.ENDC} {color_samples[color]}████████{Colors.ENDC}")
                    questions = [
                        inquirer.List(setting_key,
                                    message='Select splash screen color:',
                                    choices=colors,
                                    default=config.get(setting_key, 'blue')),
                    ]
                    answers = inquirer.prompt(questions)
                    config[setting_key] = answers[setting_key]
                elif setting_key == "animation_style":
                    print("\n  Animation Style Preview:")
                    animations = [
                        "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏",  
                        "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",  
                        "▉▊▋▌▍▎▏▎▍▌▋▊▉",    
                        "←↖↑↗→↘↓↙",         
                        "◢◣◤◥",             
                        "◰◳◲◱",
                        "🌑🌒🌓🌔🌕🌖🌗🌘",
                        ".oO°Oo.",
                    ]
                    for i, anim in enumerate(animations):
                        print(f"  {theme['menu_color']}{i}:{Colors.ENDC} {theme['highlight']}{anim}{Colors.ENDC}")
                    try:
                        print("")
                        anim_choice = int(input(f"  {theme['title_color']}enter animation style number (0-{len(animations)-1}):{Colors.ENDC} "))
                        if 0 <= anim_choice < len(animations):
                            config["animation_style"] = anim_choice
                        else:
                            print(f"\n  {Colors.WARNING}uhhhh vro invald so uhh using default (style 1).{Colors.ENDC}")
                            time.sleep(1)
                    except ValueError:
                        print(f"\n  {Colors.WARNING}uhhhh vro invald so uhh using default (style 1).{Colors.ENDC}")
                        time.sleep(1)
                elif setting_key == "splash_duration":
                    try:
                        current = config.get("splash_duration", 2.0)
                        print(f"\n  Current duration: {theme['highlight']}{current}{Colors.ENDC} seconds")
                        duration = float(input(f"\n  {theme['title_color']}enter splash duration in seconds (0.5-10.0):{Colors.ENDC} "))
                        if duration < 0.5:
                            print(f"\n  {Colors.WARNING}duration must be at least 0.5, setting to 0.5 seconds.{Colors.ENDC}")
                            duration = 0.5
                        elif duration > 10:
                            print(f"\n  {Colors.WARNING}maximum duration is 10 seconds.{Colors.ENDC}")
                            duration = 10
                        config["splash_duration"] = duration
                    except ValueError:
                        print(f"\n  {Colors.WARNING}grrrr stupid, using default.{Colors.ENDC}")
                        time.sleep(1)
                elif setting_key == "theme":
                    print("\n  Theme Preview:")
                    themes = ['default', 'dark', 'squirrel', 'pastel']
                    theme_descriptions = {
                        'default': f"{Colors.BLUE}Blue{Colors.ENDC} highlights with standard layout",
                        'dark': f"{Colors.CYAN}Cyan{Colors.ENDC} and {Colors.MAGENTA}Magenta{Colors.ENDC} cool tones",
                        'squirrel': f"{Colors.YELLOW}Yellow{Colors.ENDC} and {Colors.RED}Red{Colors.ENDC} autumn colors",
                        'pastel': f"{Colors.MAGENTA}Magenta{Colors.ENDC} and {Colors.CYAN}Cyan{Colors.ENDC} pastel palette"
                    }
                    for t in themes:
                        print(f"  {theme['menu_color']}• {t}:{Colors.ENDC} {theme_descriptions[t]}")
                    questions = [
                        inquirer.List(setting_key,
                                    message='Select theme:',
                                    choices=themes,
                                    default=config.get(setting_key, 'default')),
                    ]
                    answers = inquirer.prompt(questions)
                    config[setting_key] = answers[setting_key]
                save_success = save_config(config)
                if save_success:
                    print(f"\n  {Colors.GREEN}setting updated successfully!!{Colors.ENDC}")
                    time.sleep(1)
            else:
                print(f"\n  {Colors.WARNING}please enter a number between 1 and {len(settings) + 1}.{Colors.ENDC}")
                time.sleep(1)
        except ValueError:
            print(f"\n  {Colors.WARNING}enter valid number stupid{Colors.ENDC}")
            time.sleep(1)
    return config
def show_about():
    clear_screen()
    width = min(get_terminal_size().columns - 10, 60)
    print("\n\n")
    print_boxed("About SGC++ Runner", width, Colors.CYAN + Colors.BOLD)
    print("")
    print_centered("Version 1.2", width)
    print_centered("Cooked up by Squirrel Acorns (5quirre1) :3", width)
    print("")
    print_centered("This program helps you run SGC++ programs on", width)
    print_centered("any device with Python installed!!!!", width)
    print("")
    print_centered("Press Enter to return..", width)
    input()
def main():
    parser = argparse.ArgumentParser(description="Run SGC++ programs.")
    parser.add_argument("sgcx_file", nargs="?", help="path to the sgc++ program!")
    parser.add_argument("--skip-splash", action="store_true", help="skip the splash screen")
    parser.add_argument("--about", action="store_true", help="show about information")
    args = parser.parse_args()
    config = load_config()
    if args.skip_splash:
        config["show_splash"] = False
    if args.about:
        show_about()
        return
    if args.sgcx_file:
        main_py_path = config.get("main_py_path")
        if not main_py_path:
            print(f"{Colors.FAIL}main.py config has not been done, plz do that before run{Colors.ENDC}")
        else:
            print(f"{Colors.BOLD}{'-' * 50}{Colors.ENDC}")
            execute_script(main_py_path, args.sgcx_file)
    else:
        show_splash(config)
        while True:
            choice = show_main_menu(config)
            if choice == "1":
                run_program(config)
            elif choice == "2":
                config = configure_path(config)
            elif choice == "3":
                config = settings_menu(config)
            elif choice == "4":
                show_about()
            elif choice == "5":
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
