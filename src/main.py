"""
SGC++ Main

The main file for the SGC++ language. Idk what else really but yea it's just main.
"""
import sys
import sgc

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sgc = sgc.interpreter()
        sgc.run_file(sys.argv[1])
        exit_code = sgc.variables.get('exit_code', 0)

        color = "\033[32m" if exit_code == 0 else "\033[31m"
        reset = "\033[0m"

        print("-" * 50)
        input(f"Exited with code: {color}{exit_code}{reset}. Press enter to exit...")
        exit(exit_code)
    else:
        print("\033[33m[WARNING] No file provided. Use: python main.py filename.sgcx\033[0m")
        print("\n" + "-" * 50)
        input("Press enter to exit...")
