import itertools
import getpass
import random
import sys
import os
from Crypto.Cipher import AES

def deterministicSequence(seed):
  """Deterministic sequence for generating folders

  Parameters
  ----------
  seed : int
    The sequence's seed

  Yields
  ------
  int
    The next value of the sequence
  """
  a = 1103515245
  c = 12345
  m = 2 ** 31 - 1
  x = seed
  while True:
    x = (a * x + c) % m
    yield x % 2

def createDirectories(baseDir,numDirs,levels,ciphertext):
  """Create directories

  Parameters
  ----------
  baseDir    : str
    The base directory to start creating the directories
  numDirs    : str
    The number of directories to create at each level
  levels     : int
    The number of levels
  ciphertext : bytes
    The ciphertext to save
  """
  if levels == 0:
    return
  for i in range(numDirs):
    dir_name = os.path.join(baseDir,str(i))
    os.makedirs(dir_name)
    for j in range(10):
      with open(f"{dir_name}/f{random.randint(0,50)}","w") as f:
        f.write(str(random.randint(0,int("9" * len(str(ciphertext))))))
    createDirectories(dir_name, numDirs, levels-1,ciphertext)

def obfuscatedSequence(password,dir):
  """Create a sequence of obfuscating folders to hide the password

  Parameters
  ----------
  password : str
    The password to hide
  dir     : str
    The base directory
  """
  key = b'Strong pwd GNSS.'
  cipher = AES.new(key,AES.MODE_EAX)
  nonce = cipher.nonce
  ciphertext,tag = cipher.encrypt_and_digest(password.encode())
  seq = deterministicSequence(172)
  createDirectories(dir,2,7,ciphertext)
  with open(f"{dir}/{next(seq)}/{next(seq)}/{next(seq)}/{next(seq)}/{next(seq)}/f40","w") as f:
    f.write(str(ciphertext))
  print("Password hidden successfully!")
  
def main():
  if len(sys.argv) != 2 or sys.argv[1] == "":
    print("Usage: python obfuscatePassword.py baseDir",file = sys.stderr)
    sys.exit(-1)
  password = getpass.getpass("Enter your password: ")
  obfuscatedSequence(password,sys.argv[1])

if __name__ == "__main__":
  main()