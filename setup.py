# Note to self, never change this

import os
from funcs import funcs

path = os.path.dirname(os.path.abspath(__file__))[0].upper() + os.path.dirname(os.path.abspath(__file__))[1:] + "\\" if os.name == "nt" else "/"
os.system('cls' if os.name == 'nt' else 'clear')
fncs = funcs(path) #setup funcs
fncs.dprint(path)

def imports():
    os.system("python -m pip install -r requirements.txt")

    with open(f"{path}log.txt","w") as fp:
        fp.write(f"[{fncs.ptime()}] Finished Install Packages and created setup_done.yay file.\n")


def replace_line(file_name, line_num, text): # Yes i know this is a dumb way to solve it but it works
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def printfl(path):
    with open(path) as fp:
        return path+"\n"+fp.read()


def fix_files():
    os.system("clear")

    global inp
    my_file = os.path.exists(f"{path}setup_done.yay")
    if my_file:
        print("Packages Already Imported, Exiting!")
    else:
        imports()
        with open("setup_done.yay","w") as file:
            pass

    print("Updating file paths...")

    replace_line(f"{path}.env",0,"SET_PATH="+path) if input("Do you want to use enviroment variables? (y/n): ").lower() == "y" else None
    replace_line(f"{path}settings.json",7,r'    "home-dir": "{}",{}'.format(r'{}'.format(path),"\n"))


def verify():
    print("Please verify the following information is correct\n")
    print(printfl(path+".env"),end="\n\n==================================\n\n")
    print(printfl(path+"settings.json"))


if __name__ == "__main__":
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        fix_files()
        verify()

        fncs.log(f"[{fncs.ptime()}] Finished Setup with no errors.\n")
        exit(0)
    except Exception as e:
        fncs.log(f"[{fncs.ptime()}] Finished Setup with errors.\n")
        fncs.log(f"[{fncs.ptime()}] Error: {e}\n")
        print("An error occured, please check the log file for more information.")
        input("Press enter to exit...")
        exit(1)