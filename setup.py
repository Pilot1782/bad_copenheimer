import os
import subprocess

def imports():
  os.system("python3 -m pip install poetry")
  os.system("python3 -m poetry install")
  os.system("python -m pip install poetry")
  os.system("python -m poetry install")

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
    ost = input("\nIs this being run on windows, or linux?")
    if ost.lower() == "windows":
      ost = "\\"
      break
    elif ost.lower() == "linux":
      ost = "/"
      break
    else:
      print("Input failed.")
  
  if ost == "\\":
    inp = input("\nWhat is the directory the folder is stored in? ")
    inp = r"{0}".format(inp)
  else:
    inp = subprocess.check_output("pwd").decode("utf-8")
    inp = inp.split("\n")
    inp = "".join(inp[0])
  inp = inp + ost

  my_file = os.path.exists(f"{inp}setup_done.yay")
  if my_file:
    print("Packages Already Imported, Exiting!")
  else:
    imports()
    with open("setup_done.yay","w") as file:
      pass
  
  print("Updating file paths...")
  print(inp)
  replace_line(f"{inp}stopper.pyw",11,f"settings_path = '{inp}settings.json'\n")
  
  replace_line(f"{inp}dis-bot.pyw",19,f"settings_path = '{inp}settings.json'\n")

if __name__ == "__main__":
  fix_files()
  input("\nSetup is Done!\nPlease change the settings.json file to suit your needs.")