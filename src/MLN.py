import os
from util import *
from constants import CONSTANT_PATH
from person_MLN import PersonMLN

import sys
reload(sys)
sys.setdefaultencoding('utf8')


class MLN:

    def __init__(self):
        self.person_list = []
        self.report_path = os.path.join('..', 'report.json')
        self.marked_person_dict_path = os.path.join('..', 'resource', 'marked_person_dict.json')
        create_dir_if_not_exist(CONSTANT_PATH['result_dir'])
        self.get_person_list()

    def get_person_list(self):
        item_filename_list = os.listdir(CONSTANT_PATH['google_item_dir'])
        invalide_person_file = open('../result/invalid_person_list.txt', 'w')
        for item_filename in item_filename_list:
            person_name = item_filename.replace('.json', '')
            with open(os.path.join('..', 'resource', 'google_items', item_filename)) as item_file:
                if not json.load(item_file):
                    invalide_person_file.write(person_name + '\n')
                    continue
            person = PersonMLN(person_name)
            self.person_list.append(person)

    def run_exp(self, exp_person_num):
        for person in self.person_list:
            person.write_mln_evidence_file()
            person.run_tuffy()
            exp_person_num -= 1
            if exp_person_num == 0:
                break

    def evaluate(self):
        report_dict = {}

        with open(self.marked_person_dict_path) as marked_person_file:
            marked_person_dict = json.load(marked_person_file)

        for person in self.person_list:
            person_name = person.name
            if person_name not in marked_person_dict:
                print person_name, 'not in marked'
                continue
            report_dict[person_name] = person.get_report_dict(marked_person_dict[person_name]['email_list'])

        all_error_num = 0
        all_miss_num = 0
        all_marked_num = 0
        all_recommend_num = 0
        all_abandoned_num = 0
        for person_name in marked_person_dict:
            all_marked_num += len(marked_person_dict[person_name]['email_list'])
        for person_name, person_report_dict in report_dict.items():
            all_error_num += len(person_report_dict['ERROR'])
            all_miss_num += len(person_report_dict['MISS '])
            all_recommend_num += len(person_report_dict['recommend_email_list'])
            all_abandoned_num += len(person_report_dict['abandoned_email_list'])
        all_candidate_num = all_recommend_num + all_abandoned_num
        print '---------------------------------'
        print 'candidate ', all_candidate_num
        print 'miss      ', all_miss_num
        print 'error     ', all_error_num
        print 'marked    ', all_marked_num
        print 'recommend ', all_recommend_num
        print 'accuracy  ', 1.0 - float(all_error_num + all_miss_num) / float(all_candidate_num)
        print 'recall    ', float(all_recommend_num - all_error_num) / float(all_recommend_num - all_error_num + all_miss_num)
        print 'precision ', float(all_recommend_num - all_error_num) / float(all_recommend_num)

        with open('../performance.txt', 'w') as performance_file:
            performance_file.write('accuracy  ' + str(1.0 - float(all_error_num + all_miss_num) / float(all_candidate_num)) + '\n')
            performance_file.write('recall    ' + str(float(all_recommend_num - all_error_num) / float(all_recommend_num - all_error_num + all_miss_num)) + '\n')
            performance_file.write('precision ' + str(float(all_recommend_num - all_error_num) / float(all_recommend_num)) + '\n')

        with open(self.report_path, 'w') as report_file:
            report_file.write(json.dumps(report_dict, indent=4))


if __name__ == '__main__':
    mln = MLN()
    mln.run_exp(1000)
    mln.evaluate()