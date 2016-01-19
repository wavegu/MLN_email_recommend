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
        self.marked_person_dict = {}
        self.svm_dir = CONSTANT_PATH['svm_by_product_dir']
        self.fgm_dir = CONSTANT_PATH['fgm_by_product_dir']
        self.mln_dir = CONSTANT_PATH['mln_by_product_dir']
        self.result_dir = CONSTANT_PATH['result']
        self.resource_dir = CONSTANT_PATH['resource']

        self.input_person_list_path = os.path.join(self.resource_dir, 'input_person_list.json')
        self.report_path = os.path.join(self.result_dir, 'report.json')
        self.google_item_file_path = os.path.join('..', 'by_product', 'google_item.json')
        self.svm_feature_file_path = os.path.join(self.svm_dir, 'svm_feature.txt')
        self.fgm_feature_file_path = os.path.join(self.fgm_dir, 'fgm_feature.txt')
        self.mln_feature_file_path = os.path.join(self.mln_dir, 'mln_evidence.txt')
        self.mln_predict_file_path = os.path.join('..', 'by_product', 'mln_by_product', 'predict.db')
        self.marked_person_dict_path = os.path.join(self.resource_dir, 'mark', 'marked_person_dict.json')

        self.get_marked_person_dict()
        self.get_person_list()
        # self.add_id_to_google_items()
        self.write_google_item_file()

    def get_marked_person_dict(self):
        with open(self.marked_person_dict_path) as marked_person_file:
            self.marked_person_dict = json.load(marked_person_file)
        return self.marked_person_dict

    def get_person_list(self):
        item_filename_list = os.listdir(CONSTANT_PATH['google_item_dir'])
        invalide_person_file = open('../result/invalid_person_list.txt', 'w')
        for item_filename in item_filename_list:
            person_name = item_filename.replace('.json', '')
            with open(os.path.join('..', 'resource', 'google_items', item_filename)) as item_file:
                item_list = json.load(item_file)
                if not item_list:
                    invalide_person_file.write(person_name + '\n')
                    continue
            if person_name not in self.marked_person_dict:
                print person_name, 'not in marked'
                continue
            marked_email_list = self.marked_person_dict[person_name]['email_list']
            marked_email_list = [email.lower() for email in marked_email_list]
            person = PersonMLN(person_name, item_list, marked_email_list)
            self.person_list.append(person)

    def add_id_to_google_items(self):
        item_id = 0
        for person in self.person_list:
            new_item_list = []
            with open(person.raw_item_file_path) as item_file:
                item_list = json.load(item_file)
                for item_dict in item_list:
                    item_id += 1
                    item_dict['id'] = str(item_id)
                    new_item_list.append(item_dict)
            with open(person.raw_item_file_path, 'w') as item_file:
                item_file.write(json.dumps(new_item_list, indent=4))

    def write_google_item_file(self):
        item_dict_dict = {}
        for person in self.person_list:
            for node in person.node_mln_list:
                item_dict_dict[node.node_name] = node.item_dict
        with open(self.google_item_file_path, 'w') as google_item_file:
            google_item_file.write(json.dumps(item_dict_dict, indent=4))

    # ----------------------SVM-----------------------------------------

    def write_svm_feature_file(self):
        svm_feature_content = ''
        for person in self.person_list:
            for feature_line in person.get_svm_feature_line_list():
                svm_feature_content += feature_line
        with open(self.svm_feature_file_path, 'w') as feature_file:
            feature_file.write(svm_feature_content)

    # ----------------------FGM-----------------------------------------

    def write_fgm_feature_file(self):
        fgm_feature_content = ''
        for person in self.person_list:
            for feature_line in person.get_fgm_feature_line_list():
                fgm_feature_content += feature_line.replace('!', '')
        for person in self.person_list:
            binary_line_list = person.get_binary_relationship_list()
            for binary_line in binary_line_list:
                binary_line = str(binary_line)
                id1 = binary_line[binary_line.find('(') + 1: binary_line.find(',')].replace(' ', '')
                id2 = binary_line[binary_line.find(',') + 1: binary_line.find(')')].replace(' ', '')
                feature_name = binary_line[:binary_line.find('(')]
                binary_line = '#edge ' + id1 + ' ' + id2 + ' ' + feature_name + '\n'
                fgm_feature_content += binary_line

        with open(self.fgm_feature_file_path, 'w') as feature_file:
            feature_file.write(fgm_feature_content)

    # ----------------------MLN-----------------------------------------

    def write_mln_feature_file(self):
        with open(self.mln_feature_file_path, 'w') as feature_file:
            binary_evidence_list = []
            for person in self.person_list:
                # person.write_mln_evidence_file()
                unary_evidence_list = person.get_unary_evidence_list()
                for unary_evidence in unary_evidence_list:
                    feature_file.write(unary_evidence[1])
                binary_evidence_list += person.get_binary_relationship_list()
            for binary_evidence in binary_evidence_list:
                feature_file.write(binary_evidence)

    def run_mln_exp(self):
        # for person in self.person_list:
        #     person.write_mln_evidence_file()
        self.write_mln_feature_file()
        prog_path = os.path.join('..', 'resource', 'tuffy', 'prog.mln')
        query_path = os.path.join('..', 'resource', 'tuffy', 'query.db')
        evidence_path = self.mln_feature_file_path
        cmd = 'java -jar ../resource/tuffy/tuffy.jar -i ' + prog_path + ' -e ' + evidence_path + ' -queryFile ' + query_path + ' -r ' + self.mln_predict_file_path
        os.system(cmd)

    def mln_evaluate(self):

        all_error_num = 0
        all_miss_num = 0

        with open(self.google_item_file_path) as item_file:
            google_item_dict = json.load(item_file)

        pred_ids = []
        with open(self.mln_predict_file_path) as prediction_file:
            lines = prediction_file.readlines()
            for line in lines:
                pred_id = line[line.find('(') + 1: line.find(')')]
                pred_ids.append(pred_id)

        for item_id, item in google_item_dict.items():
            label = item['label']
            if item_id in pred_ids:
                if label == '-1':
                    all_error_num += 1
            else:
                if label == '1':
                    all_miss_num += 1

        all_candidate_num = len(google_item_dict.keys())
        all_recommend_num = len(pred_ids)
        print '---------------------------------'
        print 'miss      ', all_miss_num
        print 'error     ', all_error_num
        print 'recommend ', all_recommend_num
        print 'candidate ', all_candidate_num
        print 'accuracy  ', 1.0 - float(all_error_num + all_miss_num) / float(all_candidate_num)
        print 'recall    ', float(all_recommend_num - all_error_num) / float(all_recommend_num - all_error_num + all_miss_num)
        print 'precision ', float(all_recommend_num - all_error_num) / float(all_recommend_num)

        with open('../performance.txt', 'w') as performance_file:
            performance_file.write('accuracy  ' + str(1.0 - float(all_error_num + all_miss_num) / float(all_candidate_num)) + '\n')
            performance_file.write('recall    ' + str(float(all_recommend_num - all_error_num) / float(all_recommend_num - all_error_num + all_miss_num)) + '\n')
            performance_file.write('precision ' + str(float(all_recommend_num - all_error_num) / float(all_recommend_num)) + '\n')

        # with open(self.report_path, 'w') as report_file:
        #     report_file.write(json.dumps(report_dict, indent=4))


if __name__ == '__main__':
    mln = MLN()
    mln.write_fgm_feature_file()
    mln.write_svm_feature_file()
    # mln.run_mln_exp()
    # mln.mln_evaluate()
    # mln.write_mln_feature_file()
    # print len(mln.person_list)