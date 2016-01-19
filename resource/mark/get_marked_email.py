import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# person_name_list = [filename.replace('.json', '') for filename in os.listdir('google_items')]
# marked_person_dict_list = json.load(open('citation_top_1000_with_affwords.json'))
# result_person_dict_dict = {}
# for person_dict in marked_person_dict_list:
# 	person_name = person_dict['name']
# 	if person_name in person_name_list:
# 		print person_name
# 		result_person_dict = {}
# 		# result_person_dict['name'] = person_name
# 		if 'email' not in person_dict['contact'] or not person_dict['contact']['email']:
# 			result_person_dict['email_list'] = []
# 		else:
# 			email_addr = person_dict['contact']['email'].replace(' at ', '@').replace('\r\n', '').replace(' ', '').lower()
# 			result_person_dict['email_list'] = email_addr.split(',')
# 		result_person_dict_dict[person_name.decode('utf8')] = result_person_dict

with open('marked_person_dict.json') as json_file:
	result_person_dict_dict = json.load(json_file)

with open('label.json') as label_file:
	already_in = 0
	label_person_dict = json.load(label_file)
	for person_name, person_dict in label_person_dict.items():
		labeled_email_list = person_dict['email_list']
		if not labeled_email_list:
			continue
		if person_name in result_person_dict_dict:
			already_in += 1
			print 'already in'
			continue
		result_person_dict_dict[person_name] = person_dict


result_json = json.dumps(result_person_dict_dict, indent=4)
with open('marked_person_dict.json', 'w') as marked_file:
	marked_file.write(result_json)

print already_in
print len(sorted(result_person_dict_dict))