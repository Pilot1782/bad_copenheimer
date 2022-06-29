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

os.system("clear")
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
    os.system("clear")
  print("Updating file paths...")
  inp = r"{}".format(inp)
  replace_line(f"{inp}.env",0,r'{}PATH={}settings.json{}'.format("\r",inp,"\n"))
  fncs.dprint(inp)
  replace_line(f"{inp}settings.json",7,r'  "home-dir": "{}",{}'.format(inp,"\n"))

def settings():
  with open(f"{path}settings.json","r") as fp:
    settings = fp.read()
    settings = settings.split("\n")
    arr = []
    c = 0
    for i in settings:
      if i != "" and i != "{" and i != "}":
        i = i.split('":')
        i[0] = i[0] + '"'
        inp = input(f"{i[0]}:")
        if inp != "":
          i[1] = inp
          if c == 9 or c == 11 or c == 13:
            if i[1].lower().startswith("f"):
              i[1] = "false,"
            elif i[1].lower().startswith("t"):
              i[1] = "true,"
          elif c == 14:
            if i[1].lower().startswith("f"):
              i[1] = "false"
            elif i[1].lower().startswith("t"):
              i[1] = "true"
          else:
            i[1] = f'"{i[1]}"'
        i = ":".join(i)
      print(i)
      arr.append(i)
      c += 1

  text = "\n".join(arr)
  if input(f"{text}\n\nSave? (Y/N)").lower() == "y":
    with open(f"{path}settings.json","w") as fp:
      fp.write("\r"+text+"\n")

if __name__ == "__main__":
  fix_files()
  inp2 = input(f"\nSetup is Done at {fncs.ptime()}!\nPlease change the settings.json file to suit your needs or type 'y' to start editing it now.")
  if inp2 != "":
    settings()
  
  with open(f"{path}log.txt","w") as fp:
    fp.write(f"[{fncs.ptime()}] Finished Setup with no errors.\n")
  os.system("clear")