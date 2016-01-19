# encoding: utf8
import os
import sys
import json
from util import create_dir_if_not_exist
from node_mln import NodeMLN
from constants import CONSTANT_PATH
reload(sys)
sys.setdefaultencoding('utf8')

global_node_id = 0


class PersonMLN:

    def __init__(self, name, item_list, marked_email_list):
        self.name = name
        self.google_item_list = item_list
        self.marked_email_list = marked_email_list
        self.node_mln_list = []
        self.aff_word_list = []
        self.resource_dir = CONSTANT_PATH['resource']
        self.input_person_list_path = os.path.join(self.resource_dir, 'input_person_list.json')
        self.person_mln_dir = os.path.join(CONSTANT_PATH['mln_by_product_dir'], self.name.replace(' ', '_'))
        self.grounding_file_path = os.path.join(self.person_mln_dir, 'evidence.db')
        self.raw_item_file_path = os.path.join(CONSTANT_PATH['google_item_dir'], self.name + '.json')
        self.processed_item_file_path = os.path.join(self.person_mln_dir, 'google_item_list.json')
        self.valid_email_json_path = os.path.join(self.person_mln_dir, 'valid_email.json')

        create_dir_if_not_exist(self.person_mln_dir)
        self.get_aff_word_list()
        self.get_node_mln_list()

    def get_aff_word_list(self):
        with open(self.input_person_list_path) as input_file:
            person_list = json.load(input_file)
        for person_dict in person_list:
            if person_dict['name'] == self.name:
                if 'affiliation_words' in person_dict:
                    self.aff_word_list = person_dict['affiliation_words']
                break

    # 预处理google_item文件，将item中多个email地址的情况拆分成多个item，item中加上id
    def get_processed_google_item_list(self):

        # 输入是一个google_item_dict，输出是一个item_dict_list
        def item_to_item_list(google_item_dict):
            import copy
            new_item_list = []
            email_addr_list = google_item_dict['email_addr_list']
            for email in email_addr_list:
                new_item_dict = copy.copy(google_item_dict)
                new_item_dict.pop('email_addr_list')
                new_item_dict['email_addr'] = email
                new_item_dict['person_name'] = self.name
                new_item_list.append(new_item_dict)
            return new_item_list

        processed_google_item_list = []

        # 读原始的items文件，得到 processed_google_item_list
        with open(self.raw_item_file_path) as item_file:
            google_item_list = json.load(item_file)
            for google_item_dict in google_item_list:
                processed_google_item_list += item_to_item_list(google_item_dict)

        # 在所有item中加上'label'域
        for google_item_dict in processed_google_item_list:
            email_addr = google_item_dict['email_addr'].lower()
            email_label = False
            for marked_email in self.marked_email_list:
                if email_addr == marked_email:
                    email_label = True
                    break
            google_item_dict['label'] = str(int(email_label)*2-1)

        return processed_google_item_list

    def get_node_mln_list(self):
        global global_node_id
        self.node_mln_list = []
        processed_item_list = self.get_processed_google_item_list()
        for item_dict in processed_item_list:
            global_node_id += 1
            item_dict['id'] = global_node_id
            self.node_mln_list.append(NodeMLN(item_dict, self.aff_word_list))
        return self.node_mln_list

    def get_unary_evidence_list(self):
        unary_evidence_list = []
        for node in self.node_mln_list:
            unary_evidence_list += node.get_unary_groundings()
        return unary_evidence_list

    def get_binary_relationship_list(self):
        binary_relationship_list = []
        for node_looper in range(len(self.node_mln_list)):
            node = self.node_mln_list[node_looper]
            for another_node_looper in range(node_looper+1, len(self.node_mln_list)):
                another_node = self.node_mln_list[another_node_looper]
                if node.node_name == another_node.node_name:
                    continue
                if node.prefix == another_node.prefix and node.domain != another_node.domain:
                    binary_relationship_list.append(node.grounding_string_binary('same_prefix', another_node.node_name))
                if node.domain == another_node.domain and node.prefix != another_node.prefix:
                    binary_relationship_list.append(node.grounding_string_binary('same_domain', another_node.node_name))
                if node.prefix == another_node.prefix and node.domain == another_node.domain:
                    binary_relationship_list.append(node.grounding_string_binary('same_address', another_node.node_name))
        return binary_relationship_list

    def get_svm_feature_line_list(self):
        svm_feature_line_list = []
        node_mln_list = self.get_node_mln_list()
        for node in node_mln_list:
            svm_feature_line_list.append(node.get_svm_feature_line())
        return svm_feature_line_list

    def get_fgm_feature_line_list(self):
        fgm_feature_line_list = []
        for node in self.node_mln_list:
            fgm_feature_line_list.append(node.get_fgm_feature_line())

        import random
        r = random.randint(1, 10)
        if r < 4:
            fgm_feature_line_list = [feature_line.replace('+', '?') for feature_line in fgm_feature_line_list]

        return fgm_feature_line_list

    def write_mln_evidence_file(self):
        # 每个节点写对应的 MLN data 文件
        with open(self.grounding_file_path, 'w') as grounding_file:
            unary_grounding_list = self.get_unary_evidence_list()
            for node_grounding in unary_grounding_list:
                grounding_file.write(node_grounding[1])
            # 写连边evidence
            binary_relationship_list = self.get_binary_relationship_list()
            for binary_relationship_line in binary_relationship_list:
                grounding_file.write(binary_relationship_line)
            grounding_file.write('\n')

    def run_tuffy(self):
        prog_path = os.path.join('..', 'resource', 'tuffy', 'prog.mln')
        query_path = os.path.join('..', 'resource', 'tuffy', 'query.db')
        evidence_path = os.path.join(self.person_mln_dir, 'evidence.db')
        predict_path = os.path.join(self.person_mln_dir, 'predict.db')
        cmd = 'java -jar ../resource/tuffy/tuffy.jar -i ' + prog_path + ' -e ' + evidence_path + ' -queryFile ' + query_path + ' -r ' + predict_path
        os.system(cmd)

        valid_email_id_list = []
        recommend_email_list = []
        abandoned_email_list = []

        with open(predict_path) as predict_file:
            predict_lines = predict_file.readlines()
            for predict_line in predict_lines:
                left_pos = predict_line.find('(')
                right_pos = predict_line.find(')')
                valid_item_id = predict_line[left_pos+1: right_pos]
                valid_email_id_list.append(valid_item_id)

        with open(self.processed_item_file_path) as item_file:
            item_list = json.load(item_file)
            for item in item_list:
                item_id = item['id']
                item_email = item['email_addr']
                if item_id not in valid_email_id_list and item_email not in abandoned_email_list:
                    abandoned_email_list.append(item['email_addr'])
                elif item_id in valid_email_id_list and item_email not in recommend_email_list:
                    recommend_email_list.append(item['email_addr'])

        person_result_dict = {
            'abandoned_email_list': abandoned_email_list,
            'recommend_email_list': recommend_email_list
        }
        with open(self.valid_email_json_path, 'w') as valid_email_file:
            valid_email_file.write(json.dumps(person_result_dict, indent=4))

    def get_report_dict(self):
        person_report_dict = {}
        with open(self.valid_email_json_path) as valid_email_json_file:
            email_dict = json.load(valid_email_json_file)
            abandoned_email_list = email_dict['abandoned_email_list']
            recommend_email_list = email_dict['recommend_email_list']
        person_report_dict['abandoned_email_list'] = abandoned_email_list
        person_report_dict['recommend_email_list'] = recommend_email_list

        miss_email_list = []
        error_email_list = []
        for email in abandoned_email_list:
            if email in self.marked_email_list:
                miss_email_list.append(email)
        for email in recommend_email_list:
            if email not in self.marked_email_list:
                error_email_list.append(email)
        person_report_dict['MISS '] = miss_email_list
        person_report_dict['ERROR'] = error_email_list

        return person_report_dict

























