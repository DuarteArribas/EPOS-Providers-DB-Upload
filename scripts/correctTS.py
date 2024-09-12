import os
import sys

def correctName(filename,provider):
  newFilename = os.path.join(os.path.dirname(filename),f"{provider}_{os.path.basename(filename).split('.')[0]}_01D.pos")
  os.rename(filename,newFilename)
  return newFilename
  
def main():
  if sys.argv[1] == "" or sys.argv[2] == "":
    print("Usage: python correctTS.py providerTSDir provider [old_version] [new_version]",file = sys.stderr)
    sys.exit(-1)
  allTS         = os.listdir(sys.argv[1])
  allTSNewNames = []
  for ts in allTS:
    if len(os.path.basename(ts)) == len("ABEP00GBR.pos"):
      allTSNewNames.append([ts,correctName(os.path.join(sys.argv[1],ts),sys.argv[2])])
  
  for new_name in allTSNewNames:
    allTS.remove(new_name[0])
  for ts in allTS:
    currLines = ""
    if "DS_Store" in ts:
      continue
    with open(os.path.join(sys.argv[1],ts),"r") as f:
      currLines = f.readlines()
      currLines = "".join(currLines)
      currLines = currLines.replace("ReleaseNumber","ReleaseVersion")
      #currLines = currLines.replace("Method-url    : ","Method-url    : https://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdf")
      currLines = currLines.replace("https://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdfhttps://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdf","https://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdf")
      currLines = currLines.replace("not_specified","unknown")
      if len(sys.argv) == 5 and sys.argv[3] and sys.argv[4]:
        currLines = currLines.replace(f"ReleaseVersion : {sys.argv[3]}",f"ReleaseVersion : {sys.argv[4]}")
    with open(os.path.join(sys.argv[1],ts),"w") as f:
      f.write(currLines)
      
  for ts in allTSNewNames:
    currLines = ""
    with open(ts[1],"r") as f:
      currLines = f.readlines()
      currLines = "".join(currLines)
      currLines = currLines.replace("ReleaseNumber","ReleaseVersion")
      #currLines = currLines.replace("Method-url    : ","Method-url    : https://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdf")
      currLines = currLines.replace("https://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdfhttps://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdf","https://gnssproducts.epos.ubi.pt/methods/UGA_TS.pdf")
      currLines = currLines.replace("not_specified","unknown")
      if len(sys.argv) == 5 and sys.argv[3] and sys.argv[4]:
        currLines = currLines.replace(f"ReleaseVersion : {sys.argv[3]}",f"ReleaseVersion : {sys.argv[4]}")
    with open(ts[1],"w") as f:
      f.write(currLines)
    
      
if __name__ == "__main__":
  main()