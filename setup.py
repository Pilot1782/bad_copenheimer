# Note to self, never change this

import os
from funcs import funcs

path = (os.path.dirname(os.path.abspath(__file__))[0].upper() + os.path.dirname(os.path.abspath(__file__))[1:] + "\\" if os.name == "nt" else "/").replace("\\", "\\\\")

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

    global inp
    my_file = os.path.exists(f"{path}setup_done.yay")
    if my_file:
        print("Packages Already Imported, Exiting!")
    else:
        imports()
        with open("setup_done.yay","w") as file:
            pass

    my_file = os.path.exists(f"{path}privVars.py")
    if my_file:
        print("Variable file found, Exiting!")
    else:
        imports()
        with open("privVars.py","w") as file:
            file.write('MONGO_URL = "mongodb+srv://..."\nTOKEN = "..."\n')

    print("Updating file paths...")

    replace_line(f"{path}.env",0,"SET_PATH="+path) if input("Do you want to use enviroment variables (legacy)? (y/n): ").lower() == "y" else None
    replace_line(f"{path}settings.json",7,f'  "home-dir": "{path}",\n')


def verify():
    print("Verifying files...\n\n==================================\n\n")
    print(printfl(path+".env"),end="\n\n==================================\n\n")
    print(printfl(path+"settings.json"))
    print("\n\n==================================\n\n")
    print("Please verify the following information is correct\n")


if __name__ == "__main__":
    try:
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
