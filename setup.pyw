import os

def imports():
  os.system("python3 -m pip install poetry")
  os.system("python3 -m poetry lock")
  os.system("python -m pip install poetry")
  os.system("python -m poetry lock")

if __name__ == "__main__":
  imports()