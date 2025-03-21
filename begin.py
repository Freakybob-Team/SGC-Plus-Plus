import os
from pathlib import Path
print("Welcome to SGC++! (aka SigmaGreg Code++, sgcx)")
print("We'd like to thank you for updating or beginning to use SigmaGreg Code++ :)! We really apperciate it.")
print("Please input the FULL path to main.bat (excluding the actual main.bat part) excluding quotation marks!")
pathtobat = input()
p = Path(pathtobat)
p_no_path = pathtobat
print(p)
os.system('start "Setup SGCX" cmd /k "cd ' + p_no_path + '& .\main.bat"')