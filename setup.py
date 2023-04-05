import logging
import os


from utils import logger

logger = logger.Logger()

def print(*args, **kwargs):
    logger.print(" ".join(args), **kwargs)

def instPyPackage():
    print("\n------------------\nInstalling python packages...")
    # check to make sure that requirements.txt exists
    if not os.path.isfile("requirements.txt"):
        logger.error("requirements.txt not found in current directory.")
        print("requirements.txt not found in current directory.")
    else:
        os.system("pip install -r requirements.txt")


def checkMasscan():
    print("\n------------------\nChecking for masscan (required for scanning)...")
    if os.name != "nt":
        try:
            import masscan

            scanner = masscan.PortScanner()
        except __import__("masscan").PortScannerError:
            print("Masscan not found, installing...")
            gitURL = "https://github.com/adrian154/masscan.git"
            os.system("git clone " + gitURL)
            os.system("sudo apt-get --assume-yes install git make gcc")
            os.chdir("masscan")
            os.system("make")
            os.system("sudo make install")
    else:
        print("Masscan not supported on Windows, please install manually.")


def privVariables():
    print("\n------------------\nCreating privVars.py...")
    if os.name == "nt":
        # create privVars.py
        os.system("echo # Private Variables > privVars.py")
        # add variables
        with open("privVars.py", "a") as f:
            f.write('\nDISCORD_WEBHOOK = ""  # Not usually required\n')
            f.write('TOKEN = ""  # Discord bot token\n')
            f.write('MONGO_URL = ""  # URL from the mongo db setup guide\n')
    elif os.name == "posix":
        # create privVars.py
        os.system("touch privVars.py")
        # add variables
        with open("privVars.py", "a") as f:
            f.write('\nDISCORD_WEBHOOK = "" # Not usually required\n')
            f.write('TOKEN = ""\n')
            f.write('MONGO_URL = ""\n')
    else:
        print("OS not supported, please create privVars.py manually.")


def main():
    instPyPackage()
    checkMasscan()
    privVariables()


if __name__ == "__main__":
    main()
    print("\n------------------\nSetup complete!")
    print(
        "Please edit privVars.py with your variables and run mongoBot.pyw for the discord bot and scanCore.py for the scanner."
    )
    print(
        "Docs can be found here:\nhttps://github.com/Pilot1782/bad_copenheimer/wiki/Installation-(New-Bot)"
    )
