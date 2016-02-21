# encoding: utf8
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
        self.svm_feature_file_path = os.path.join(self.svm_dir, 'svm_feature_id.txt')
        self.fgm_feature_file_path = os.path.join(self.fgm_dir, 'fgm_feature_id.txt')
        self.mln_feature_file_path = os.path.join(self.mln_dir, 'mln_evidence.txt')
        self.mln_predict_file_path = os.path.join('..', 'by_product', 'mln_by_product', 'predict.db')
        self.marked_person_dict_path = os.path.join(self.resource_dir, 'mark', 'marked_person_dict.json')

    def set_up(self):
        print 'Experiment setting up...'
        self.get_marked_person_dict()
        self.get_person_list()
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

    def write_svm_feature_file_from_fgm_feature(self, feature_id):

        def fgm_feature_to_svm_feature(fgm_feature):
            svm_label = str(int(fgm_feature[1]) * 2 - 1)
            svm_feature = svm_label
            feature_num = 0
            for part in fgm_feature.split(' ')[1:]:
                feature_num += 1
                split_pos = part.find(':')
                if split_pos < 0:
                    continue
                svm_feature += ' ' + str(feature_num) + part[split_pos:]
            return svm_feature

        svm_test_list = []
        svm_train_list = []
        fgm_feature_path = self.fgm_feature_file_path.replace('id', str(feature_id))
        with open(fgm_feature_path) as fgm_feature_file:
            fgm_features = fgm_feature_file.readlines()
        for fgm_feature in fgm_features:
            if fgm_feature[0] == '+':
                svm_train_list.append(fgm_feature_to_svm_feature(fgm_feature))
            elif fgm_feature[0] == '?':
                svm_test_list.append(fgm_feature_to_svm_feature(fgm_feature))

        with open('../by_product/svm_by_product/source/svm_file/train_'+str(feature_id)+'.dat', 'w') as train_file:
            for train_feature in svm_train_list:
                train_file.write(train_feature + '\n')
        with open('../by_product/svm_by_product/source/svm_file/test_'+str(feature_id)+'.dat', 'w') as test_file:
            for test_feature in svm_test_list:
                test_file.write(test_feature + '\n')

    def svm_evaluate(self):
        cmd = 'python ' + self.svm_dir + '/svm_script/svm.py'
        os.system(cmd)

    # ----------------------FGM-----------------------------------------

    def write_fgm_feature_file(self, feature_id, is_need_binary):
        fgm_feature_content = ''
        train_pos_num = 0
        train_neg_num = 0
        test_pos_num = 0
        test_neg_num = 0
        for person in self.person_list:
            fgm_feature_list = person.get_fgm_feature_line_list()
            for feature_line in fgm_feature_list:
                if feature_line[0] == '?':
                    if feature_line[1] == '0':
                        test_neg_num += 1
                    else:
                        test_pos_num += 1
                else:
                    if feature_line[1] == '0':
                        train_neg_num += 1
                    else:
                        train_pos_num += 1
                fgm_feature_content += feature_line.replace('!', '')
        print 'test_pos =', test_pos_num
        print 'test_neg =', test_neg_num
        print 'train_pos =', train_pos_num
        print 'train_neg =', train_neg_num

        if is_need_binary:
            for person in self.person_list:
                binary_line_list = person.get_binary_relationship_list()
                for binary_line in binary_line_list:
                    binary_line = str(binary_line)
                    id1 = binary_line[binary_line.find('(') + 1: binary_line.find(',')].replace(' ', '')
                    id2 = binary_line[binary_line.find(',') + 1: binary_line.find(')')].replace(' ', '')
                    feature_name = binary_line[:binary_line.find('(')]
                    binary_line = '#edge ' + id1 + ' ' + id2 + ' ' + feature_name + '\n'
                    fgm_feature_content += binary_line

        with open(self.fgm_feature_file_path.replace('id', str(feature_id)), 'w') as feature_file:
            feature_file.write(fgm_feature_content)
            feature_file.write('#logic same_domain_with_invalid 1 0\n')
            feature_file.write('#logic same_prefix 1 1\n')
            feature_file.write('#logic a_contain_prefix_b 1 1\n')
            feature_file.write('#logic same_addr 1 1\n')

    def write_five_fgm_feature_file(self, is_need_binary):
        for looper in range(5):
            self.write_fgm_feature_file(looper, is_need_binary)
            self.write_svm_feature_file_from_fgm_feature(looper)

    def run_fgm_exp(self, is_need_binary):
        import time
        import subprocess
        pro_list = []
        for looper in range(5):
            print 'Running FGM', looper, '...'
            cmd = os.path.join(self.fgm_dir, 'OpenCRF') + ' -est -niter 2000 -gradientstep 0.01 -trainfile ' + self.fgm_feature_file_path.replace('id', str(looper)) + ' -dstmodel model.txt > ' + os.path.join(self.fgm_dir, 'result'+str(looper)+'.txt')
            pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pro_list.append(pro)
            time.sleep(1)
        for pro in pro_list:
            pro.wait()

    def fgm_evaluate(self):
        print 'FGM running over, evaluating...'
        self.svm_evaluate()
        tot_acc = 0.0
        tot_pre = 0.0
        tot_rec = 0.0
        max_precision = 0.0
        min_precision = 99999.0
        max_recall = 0.0
        min_recall = 99999.0
        max_accuracy = 0.0
        min_accuracy = 99999.0
        for looper in range(5):
            result_file_path = os.path.join(self.fgm_dir, 'result'+str(looper)+'.txt')
            with open(result_file_path) as result_file:
                performance_lines = result_file.readlines()[-5:-1]
                accuracy = float(performance_lines[0][-5: -1])
                precision = float(performance_lines[1][-5: -1])
                recall = float(performance_lines[2][-5: -1])
                tot_acc += accuracy
                tot_pre += precision
                tot_rec += recall
                if precision > max_precision:
                    max_precision = precision
                if precision < min_precision:
                    min_precision = precision
                if recall > max_recall:
                    max_recall = recall
                if recall < min_recall:
                    min_recall = recall
                if accuracy > max_accuracy:
                    max_accuracy = accuracy
                if accuracy < min_accuracy:
                    min_accuracy = accuracy

        accuracy = (tot_acc) / 500.0
        precision = (tot_pre) / 500.0
        recall = (tot_rec) / 500.0
        f1_value = 2 * precision * recall / (precision + recall)

        print '-------------FGM----------------'
        print 'accuracy =', accuracy
        print 'precision =', precision
        print 'recall =', recall
        print 'F1_value =', f1_value
        print '--------------------------------'

        f = open(os.path.join(self.fgm_dir, 'result.txt'), 'w')
        old = sys.stdout
        sys.stdout = f
        print 'accuracy =', accuracy
        print 'precision =', precision
        print 'recall =', recall
        print 'F1_value =', f1_value
        sys.stdout = old

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
        # self.write_mln_feature_file()
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
        accuracy = (1.0 - float(all_error_num + all_miss_num) / float(all_candidate_num)) * 100.0
        precision = float(all_recommend_num - all_error_num) / float(all_recommend_num) * 100.0
        recall = float(all_recommend_num - all_error_num) / float(all_recommend_num - all_error_num + all_miss_num) * 100.0
        print '-------------MLN----------------'
        print 'miss      ', all_miss_num
        print 'error     ', all_error_num
        print 'recommend ', all_recommend_num
        print 'candidate ', all_candidate_num
        print 'accuracy  ', accuracy
        print 'precision ', precision
        print 'recall    ', recall
        print 'F1_VALUE  ', 2 * precision * recall / (precision + recall)

        # print '--------------------------------'

        with open('../performance.txt', 'w') as performance_file:
            performance_file.write('accuracy  ' + str(1.0 - float(all_error_num + all_miss_num) / float(all_candidate_num)) + '\n')
            performance_file.write('recall    ' + str(float(all_recommend_num - all_error_num) / float(all_recommend_num - all_error_num + all_miss_num)) + '\n')
            performance_file.write('precision ' + str(float(all_recommend_num - all_error_num) / float(all_recommend_num)) + '\n')


if __name__ == '__main__':
    mln = MLN()
    # mln.set_up()

    # mln.write_mln_feature_file()
    # mln.run_mln_exp()
    # mln.mln_evaluate()
    #
    # mln.write_five_fgm_feature_file(is_need_binary=True)
    # mln.write_svm_feature_file_from_fgm_feature()
    mln.svm_evaluate()
    # mln.run_fgm_exp(is_need_binary=True)
    # mln.fgm_evaluate()
    # mln.write_svm_feature_file()
    # mln.svm_evaluate()