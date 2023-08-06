def replace_line_in_file(file_path, regex, replacement):
  new_lines = []

  with open(file_path, 'r') as f:
    for line in f:
      if regex.search(line):
        new_lines.append(replacement)
      else:
        new_lines.append(line)
  
  with open(file_path, 'w') as f:
    f.writelines(new_lines)

def add_to_file(file_path, regex, new_line):
  found = False
  with open(file_path, 'r') as file:
    file_lines = file.readlines()
    for line in file_lines:
      if regex.match(line):
        found = True
        break

  if found:
    print("found")
    return 

  with open(file_path, 'a') as f:
    f.write('\n' + new_line + '\n')