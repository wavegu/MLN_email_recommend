import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

with open('old_input_person_list.json') as json_file:
	current_person_list = json.load(json_file)
	print len(current_person_list)

with open('mark/10_thousand_people_list.json') as json_file:
	people_list = json.load(json_file)

count = 0
for person in people_list:
	if person['name'] + '.json' not in os.listdir('google_items'):
		continue
	count += 1
	already_in = False
	for current_person in current_person_list:
		if person['name'] == current_person['name']:
			already_in = True
			break
	if not already_in:
		current_person_list.append(person)

with open('input_person_list.json', 'w') as json_file:
	json_file.write(json.dumps(current_person_list, indent=4))

print len(current_person_list)
print count