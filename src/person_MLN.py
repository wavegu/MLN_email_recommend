# encoding: utf8
import os
import sys
import json
from util import create_dir_if_not_exist
from node_mln import NodeMLN
from constants import CONSTANT_PATH
reload(sys)
sys.setdefaultencoding('utf8')


class PersonMLN:

    def __init__(self, name):
        self.name = name
        self.result_dir = os.path.join('..', 'result', name.replace(' ', '_'))
        self.grounding_file_path = os.path.join(self.result_dir, 'evidence.db')
        self.raw_item_file_path = os.path.join(CONSTANT_PATH['google_item_dir'], self.name + '.json')
        self.processed_item_file_path = os.path.join(self.result_dir, 'google_item_list.json')
        self.person_dir = os.path.join(CONSTANT_PATH['result_dir'], self.name.replace(' ', '_'))
        self.valid_email_json_path = os.path.join(self.person_dir, 'valid_email.json')

        create_dir_if_not_exist(self.result_dir)

    # 预处理google_item文件，将item中多个email地址的情况拆分成多个item，item中加上id
    def write_processed_google_item_file(self):

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
            item_id = -1
            for google_item_dict in processed_google_item_list:
                item_id += 1
                google_item_dict['id'] = str(item_id)

        # 将 processed_google_item_list 写入文件
        with open(self.processed_item_file_path, 'w') as output_item_file:
            output_item_file.write(json.dumps(processed_google_item_list, indent=4, ensure_ascii=False))

    def write_mln_evidence_file(self):

        # 得到处理过的items文件，其中每个item是一个MLN节点
        self.write_processed_google_item_file()

        # 根据 item_list 得到对应的 MLN节点list
        with open(self.processed_item_file_path) as processed_item_file:
            item_list = json.load(processed_item_file)
        node_mln_list = [NodeMLN(item_dict) for item_dict in item_list]

        # 每个节点写对应的 MLN data 文件
        with open(self.grounding_file_path, 'w') as grounding_file:
            for node in node_mln_list:
                # 写单节点evidence
                node_grounding_list = node.get_unary_groundings()
                for node_grounding in node_grounding_list:
                    grounding_file.write(node_grounding)
                # 写连边evidence
                for another_node in node_mln_list:
                    if node.node_name == another_node.node_name:
                        continue
                    if node.prefix == another_node.prefix:
                        grounding_file.write(node.grounding_string_binary('same_prefix', another_node.node_name))
                    if node.domain == another_node.domain:
                        grounding_file.write(node.grounding_string_binary('same_domain', another_node.node_name))
                    if node.prefix == another_node.prefix and node.domain == another_node.domain:
                        grounding_file.write(node.grounding_string_binary('same_address', another_node.node_name))
                grounding_file.write('\n')

    def run_tuffy(self):
        prog_path = os.path.join('..', 'resource', 'tuffy', 'prog.mln')
        query_path = os.path.join('..', 'resource', 'tuffy', 'query.db')
        evidence_path = os.path.join(self.person_dir, 'evidence.db')
        predict_path = os.path.join(self.person_dir, 'predict.db')
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

    def get_report_dict(self, marked_email_list):
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
            if email in marked_email_list:
                miss_email_list.append(email)
        for email in recommend_email_list:
            if email not in marked_email_list:
                error_email_list.append(email)
        person_report_dict['MISS '] = miss_email_list
        person_report_dict['ERROR'] = error_email_list

        return person_report_dict

























