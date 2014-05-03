import json
with open('data.txt', 'w') as outfile:
  for eachcourse in allofcourses:
  	outfile.write(json.dumps(eachcourse)+'\n')
