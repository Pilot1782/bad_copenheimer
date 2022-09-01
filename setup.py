import os
import subprocess
from funcs import funcs
path = ""

# Get system path
ost = ''
while ost != "\\"or ost != "/":
  ost = input("\nIs this being run on windows, or linux? ")
  if ost.lower() == "windows":
    ost = "\\"
    break
  elif ost.lower() == "linux":
    ost = "/"
    break
  else:
    print("Input failed.")
  
inp = os.path.dirname(os.path.abspath(__file__))

os.system('cls' if os.name == 'nt' else 'clear')
inp = inp + ost
inp = inp[0].upper() + inp[1:]
fncs = funcs(inp+"settings.json") #setup funcs

fncs.dprint(inp)
path = inp

def imports():
  try:
    #x = subprocess.check_output("python3 --version",shell=True)
    x = subprocess.check_output("python3.10 --version",shell=True)
  except subprocess.CalledProcessError as err:
    #fncs.log(err)
    pass
  try:
    x = x.split(" ")
    y = x[1].split(".")
    if int(y[1]) >= 6:
      os.system("python3 -m pip install -r requirements.txt")
  except Exception as err:
    str(err)
    os.system("python -m pip install -r requirements.txt")
  finally:
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
  my_file = os.path.exists(f"{inp}setup_done.yay")
  if my_file:
    print("Packages Already Imported, Exiting!")
  else:
    imports()
    with open("setup_done.yay","w") as file:
      pass


  print("Updating file paths...")
  inp = r"{}".format(inp)
  replace_line(f"{inp}.env",0,r'{}PATH={}settings.json{}'.format("\r",inp,"\n"))
  fncs.dprint(inp)
  replace_line(f"{inp}settings.json",7,r'  "home-dir": "{}",{}'.format(inp,"\n"))

def verify():
  print("Please verify the following information is correct")
  print(printfl(inp+".env"),end+"\n==================================\n")
  print(printfl(inp+"settings.json"))


if __name__ == "__main__":
  os.system('cls' if os.name == 'nt' else 'clear')
  fix_files()
  verify()
  
  with open(f"{path}log.txt","w") as fp:
    fp.write(f"[{fncs.ptime()}] Finished Setup with no errors.\n")
