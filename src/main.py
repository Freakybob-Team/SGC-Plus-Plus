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
        print("----------------------------------------------")
        input("Press enter to exit..")
    else:
        print("\033[33m[WARNING] Uhh so no file, use like: python main.py filename.sgc\033[0m")
