# encoding: utf-8
import json
import random
import subprocess

__author__ = 'hong'


def cross_valid(iteration_times, data_file):
    with open(data_file) as data:
        data_lines = data.readlines()
    data.close()
    positive = []
    negative = []
    for line in data_lines:
        line = line.strip('\n')
        tmp = line.split(' ')
        if tmp[0] == '1':
            positive.append(line)
        else:
            negative.append(line)
    random.shuffle(positive)
    random.shuffle(negative)
    n_positive = len(positive)/iteration_times
    print n_positive
    # positive_dataset = tuple(positive[i:i + n] for i in xrange(0, len(positive), n))
    n_negative = len(negative)/iteration_times
    print n_negative
    # negative_dataset = tuple(negative[i:i + n] for i in xrange(0, len(negative), n))
    for i in range(0, iteration_times):
        negative_test_data = negative[i * n_negative: (i + 1) * n_negative]
        negative_train_data = negative[0: i * n_negative] + negative[(i+1) * n_negative:]

        positive_test_data = positive[i*n_positive:(i + 1) * n_positive]
        positive_train_data = positive[0:i*n_positive] + positive[(i+1)*n_positive:]
        result_test = positive_test_data
        result_test.extend(negative_test_data)
        result_train = positive_train_data
        result_train.extend(negative_train_data)
        random.shuffle(result_test)
        random.shuffle(result_train)
        with open('../source/svm_file/test_' + str(i) + '.dat', 'w') as f:
            for case in result_test:
                f.write(case + '\n')
        f.close()
        with open('../source/svm_file/train_' + str(i) + '.dat', 'w') as f:
            for case in result_train:
                f.write(case + '\n')
        f.close()


def svm_train(file_path, flag):
    # train command:
    # ./svm_learn -g 0.5 -c 1 -w1 2 -w-1 0.5 train.dat model
    subprocess.call(["../source/svm_light/svm_learn",
                     file_path + 'train_' + flag + '.dat',
                     file_path + 'model_'+flag])


def svm_prediction(file_path, input_file_name, output_file_name, flag):
    # predict command:
    # ./svm_classify test.dat model predictions
    subprocess.call(['../source/svm_light/svm_classify',
                     file_path + input_file_name,
                     file_path + 'model_' + flag,
                     file_path + output_file_name])


def svm_result_analysis_old(pred_file_path, test_file_path, result_file_path):
    compare_line_list = []
    with open(pred_file_path) as pred_file:
        pred_lines = pred_file.readlines()
    with open(test_file_path) as test_file:
        test_lines = test_file.readlines()
    if len(pred_lines) != len(test_lines):
        print 'Error: prediction line number doesn\'t match test line number'
        return
    unmatch_num = 0
    miss_positive_num = 0
    mistake_judge_num = 0
    for id in range(len(pred_lines)):
        pred_line = pred_lines[id]
        test_line = test_lines[id]
        pred_tag = pred_line.strip('\n')
        test_tag = test_line.split(' ')[0]
        test_tag = int(test_tag)
        if float(pred_tag) < 0.5:
            pred_tag = -1
        else:
            pred_tag = 1
        if pred_tag == test_tag:
            continue
        else:
            unmatch_num += 1
            mistake_judge_num += int(pred_tag == 1)
            miss_positive_num += int(pred_tag == -1)
            compare_line = '[%d/%d] %s' % (pred_tag, test_tag, test_line[test_line.index('#'):])
            compare_line_list.append(compare_line)
            pass
    compare_line_list = sorted(compare_line_list)
    with open(result_file_path, 'w') as compare_file:
        compare_file.write('Accuracy: %f [%d/%d]\n' % (float(len(pred_lines)-unmatch_num)/float(len(pred_lines)), unmatch_num, len(pred_lines)))
        compare_file.write('误判：%d\n' % mistake_judge_num)
        compare_file.write('漏判：%d\n' % miss_positive_num)
        for compare_line in compare_line_list:
            compare_file.write(compare_line)


def svm_result_analysis(pred_file_path, test_file_path, result_file_path):
    compare_line_list = []
    with open(pred_file_path) as pred_file:
        pred_lines = pred_file.readlines()
    with open(test_file_path) as test_file:
        test_lines = test_file.readlines()
    if len(pred_lines) != len(test_lines):
        print 'Error: prediction line number doesn\'t match test line number'
        return
    correct_male = 0
    correct_female = 0
    mistake_male_num = 0
    mistake_female_num = 0  # nv wei nan
    for id in range(len(pred_lines)):
        pred_line = pred_lines[id]
        test_line = test_lines[id]
        pred_tag = pred_line.strip('\n')
        test_tag = test_line.split(' ')[0]
        test_tag = int(test_tag)
        if float(pred_tag) <= 0:
            pred_tag = -1
        else:
            pred_tag = 1


        if pred_tag == 1:
            if pred_tag == test_tag:
                correct_male += 1
            else:
                mistake_female_num += 1
                # compare_line = '[%d/%d] %s' % (pred_tag, test_tag, test_line[test_line.index('#'):])
                # compare_line_list.append(compare_line)
        else:
            if pred_tag == test_tag:
                correct_female += 1
            else:
                mistake_male_num += 1
                # compare_line = '[%d/%d] %s' % (pred_tag, test_tag, test_line[test_line.index('#'):])
                # compare_line_list.append(compare_line)
    # compare_line_list = sorted(compare_line_list)
    accuracy = float(correct_male + correct_female)/float(len(pred_lines))
    accuracy_m = float(correct_male) / (mistake_male_num + correct_male)
    # accuracy_f = float(correct_female) / 58
    print 'Accuracy: %f [%d/%d]' % (float(correct_male+correct_female)/float(len(pred_lines)), correct_male, correct_female)
    print '男判为女：%d' % mistake_male_num
    # print '女判为男：%d' % mistake_female_num
    precision_male = float(correct_male)/(correct_male + mistake_female_num)
    recall_male = float(correct_male)/(correct_male + mistake_male_num)
    # precision_female = float(correct_female)/(correct_female + mistake_male_num)
    # recall_female = float(correct_female)/(correct_female + mistake_female_num)
    print 'male accuracy：%f' % accuracy_m
    print 'male precision：%f' % precision_male
    print 'male recall：%f' % recall_male
    # print 'female accuracy：%f' % accuracy_f
    # print 'female precision：%f' % precision_female
    # print 'female recall：%f\n' % recall_female

    return accuracy, precision_male, recall_male


def prediction_to_result(pred_file_path, test_file_path, original_file_path, result_file_path):

    with open(original_file_path, 'r') as f:
        persons = json.load(f)

    compare_line_list = {}
    with open(pred_file_path) as pred_file:
        pred_lines = pred_file.readlines()
    with open(test_file_path) as test_file:
        test_lines = test_file.readlines()
    if len(pred_lines) != len(test_lines):
        print 'Error: prediction line number doesn\'t match test line number'
        return
    for item_id in range(len(pred_lines)):
        pred_line = pred_lines[item_id]
        test_line = test_lines[item_id]
        pred_tag = pred_line.strip('\n')
        if float(pred_tag) < 0.5:
            pred_tag = 'female'
        else:
            pred_tag = 'male'
        pid = test_line[test_line.index('#')+2:].split(' ')[0].replace('[', '').replace(']', '')
        compare_line_list[pid] = pred_tag
    # persons = json.loads(content_ori)
    for person in persons:
        gender = compare_line_list.get(person.get('id'))
        person['gender'] = gender
    with open(result_file_path, 'w') as compare_file:
        compare_file.write((json.dumps(persons, indent=4)))


if __name__ == '__main__':
    cross_valid(5, '../source/svm_file/svm_feature.txt')
    accuracy_m = 0
    accuracy_f = 0
    precision_male = 0
    recall_male = 0
    precision_female = 0
    recall_female = 0
    for i in range(5):
        svm_train('../source/svm_file/', str(i))
        svm_prediction('../source/svm_file/', 'test_' + str(i) + '.dat', 'predictions_' + str(i) + '.dat', str(i))
        accuracy_male, precision_m, recall_m= svm_result_analysis(
            '../source/svm_file/predictions_' + str(i) + '.dat',
            '../source/svm_file/test_' + str(i) + '.dat',
            '../source/svm_file/result_' + str(i) + '.dat')
        accuracy_m += accuracy_male

        precision_male += precision_m
        recall_male += recall_m
    print accuracy_m/float(5)
    precision_male /= float(5)
    recall_male /= float(5)
    print 'male precision：%f' % precision_male
    print 'male recall：%f' % recall_male
    print 2*precision_male*recall_male/(precision_male + recall_male)
    # prediction_to_result('../source/svm_file/predictions.dat',
    #                     '../source/svm_file/test.dat',
    #                     '../source/input_person_list.json',
    #                     '../source/svm_file/output.json')