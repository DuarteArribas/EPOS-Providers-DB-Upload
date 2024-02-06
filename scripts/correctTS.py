import os
import sys

def correctName(filename,provider):
  newFilename = os.path.join(os.path.dirname(filename),f"{provider}_{os.path.basename(filename).split('.')[0]}_01D.pos")
  os.rename(filename,newFilename)
  return newFilename
  
def main():
  if len(sys.argv) != 3 or sys.argv[1] == "" or sys.argv[2] == "":
    print("Usage: python correctTS.py providerTSDir provider",file = sys.stderr)
    sys.exit(-1)
  allTS         = os.listdir(sys.argv[1])
  allTSNewNames = []
  for ts in allTS:
    if len(os.path.basename(ts)) == len("ABEP00GBR.pos"):
      allTSNewNames.append(correctName(os.path.join(sys.argv[1],ts),sys.argv[2]))
      allTS.remove(ts)
  
  for ts in allTS:
    currLines = ""
    with open(os.path.join(sys.argv[1],ts),"r") as f:
      currLines = f.readlines()
      currLines = "".join(currLines)
      currLines = currLines.replace("ReleaseNumber","ReleaseVersion")
      currLines = currLines.replace("not_specified","unknown")
    with open(os.path.join(sys.argv[1],ts),"w") as f:
      f.write(currLines)
      
  for ts in allTSNewNames:
    currLines = ""
    with open(ts,"r") as f:
      currLines = f.readlines()
      currLines = "".join(currLines)
      currLines = currLines.replace("ReleaseNumber","ReleaseVersion")
      currLines = currLines.replace("not_specified","unknown")
    with open(ts,"w") as f:
      f.write(currLines)
      
if __name__ == "__main__":
  main()