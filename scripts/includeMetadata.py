import os

with open('metadata.txt', 'r') as f:
    metadata = f.readlines()

for filename in os.listdir():
  if filename != 'metadata.txt' and filename.split('.')[-1] != 'py':
    with open(filename,'r') as f:
      lines = f.readlines()

    with open(filename,'w') as f:
      for i,line in enumerate(lines):
        if i == 9:
          f.write('%Begin EPOS metadata\n')
          for meta_line in metadata:
            f.write(meta_line)
          f.write('%End EPOS metadata\n')
        f.write(line)