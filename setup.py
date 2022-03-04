import os
import subprocess
import time

def ptime():
  x = time.localtime()
  z = []
  for i in x:
    z.append(str(i))
  z = f"{z[0]} {z[1]}/{z[2]} {z[3]}:{z[4]}:{z[5]}"
  return z
path = ""

def imports():
  try:
    x = subprocess.check_output("python3 --version",shell=True)
  except subprocess.CalledProcessError as err:
    import funcs
    funcs.logerror(err)
  try:
    x = x.split(" ")
    y = x[1].split(".")
    if int(y[1]) >= 6:
      os.system("python3 -m pip install poetry")
      os.system("python3 -m poetry install")
  except Exception as err:
    str(err)
    os.system("python -m pip install poetry")
    os.system("python -m poetry install")
  finally:
    with open(f"{path}log.txt","w") as fp:
      fp.write(f"[{ptime()}] Finished Install Packages and created setup_done.yay file.\n")

def replace_line(file_name, line_num, text): # Yes i know this is a dumb way to solve it but it works
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def fix_files():
  os.system("clear")
  ost = ''
  while ost != "\\" or ost != "/":
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
  print(inp)
  global path
  path = inp

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
  # Replace \ with \\ in inp
  replace_line(f"{inp}.env",1,r'PATH={}settings.json'.format(inp))
  inp = inp.replace("\\","\\\\")
  print(inp)
  replace_line(f"{inp}settings.json",7,r'  "home-dir": "{}",{}'.format(inp,"\n"))

if __name__ == "__main__":
  fix_files()
  input(f"\nSetup is Done at {ptime()}!\nPlease change the settings.json file to suit your needs.")
  with open(f"{path}log.txt","w") as fp:
    fp.write(f"[{ptime()}] Finished Setup with no errors.")