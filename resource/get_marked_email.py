import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')


person_name_list = [filename.replace('.json', '') for filename in os.listdir('google_items')]
marked_person_dict_list = json.load(open('citation_top_1000_with_affwords.json'))
result_person_dict_dict = {}
for person_dict in marked_person_dict_list:
	person_name = person_dict['name']
	if person_name in person_name_list:
		print person_name
		result_person_dict = {}
		# result_person_dict['name'] = person_name
		if 'email' not in person_dict['contact'] or not person_dict['contact']['email']:
			result_person_dict['email_list'] = []
		else:
			result_person_dict['email_list'] = person_dict['contact']['email'].replace(' ', '').replace('\r\n', '').split(',')
		result_person_dict_dict[person_name.decode('utf8')] = result_person_dict
result_json = json.dumps(result_person_dict_dict, indent=4)
with open('marked_person_dict.json', 'w') as marked_file:
	marked_file.write(result_json)