import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class NodeMLN:

    def __init__(self, google_item_dict, aff_word_list):
        self.aff_word_list = aff_word_list
        self.item_dict = google_item_dict
        self.label = str(google_item_dict['label'])
        self.node_name = str(google_item_dict['id'])
        self.email = str(google_item_dict['email_addr']).lower()
        self.person_name = str(google_item_dict['person_name']).lower().replace('.', '')
        self.google_title = str(google_item_dict['title']).lower().replace('.', '')
        self.google_content = str(google_item_dict['content']).lower().replace('.', '')
        self.grounding_file_path = os.path.join('..', 'result', self.person_name, 'MLN.db')

        self.last_name = self.person_name.replace('-', ' ').split(' ')[-1]
        self.first_name = self.person_name.replace('-', ' ').split(' ')[0]
        self.domain = self.email[self.email.find('@')+1:]
        self.prefix = self.email[:self.email.find('@')]
        self.prefix = re.sub(r'([\d]+)', '', self.prefix)

    def grounding_string_unary(self, grounding_name, is_true):
        grounding_str = str(grounding_name) + '(' + str(self.node_name) + ')\n'
        if not is_true:
            return '!' + grounding_str
        return grounding_str

    def grounding_string_binary(self, grounding_name, another_node_name):
        grounding_str = str(grounding_name) + '(' + str(self.node_name) + ', ' + str(another_node_name) + ')\n'
        return grounding_str

    def google_title_contain_aff_word(self):
        contain_aff_word = False
        for aff_word in self.aff_word_list:
            if aff_word in self.google_title.split(' '):
                contain_aff_word = True
                break
        return contain_aff_word, self.grounding_string_unary('google_title_contain_aff_word', contain_aff_word)

    def google_content_contain_aff_word(self):
        contain_aff_word = False
        for aff_word in self.aff_word_list:
            if aff_word in self.google_content.split(' '):
                contain_aff_word = True
                break
        return contain_aff_word, self.grounding_string_unary('google_content_contain_aff_word', contain_aff_word)

    def prefix_contain_last_name(self):
        is_contain_last_name = self.last_name in self.prefix
        return is_contain_last_name, self.grounding_string_unary('prefix_contain_last_name', is_contain_last_name)

    def prefix_contain_first_name(self):
        is_contain_first_name = self.first_name in self.prefix and len(self.first_name) > 2
        return is_contain_first_name, self.grounding_string_unary('prefix_contain_first_name', is_contain_first_name)

    def prefix_is_invalid_keyword(self):
        invalid_keyword_list = ['email', 'info', 'mailto']
        is_invalid_prefix = False
        for invalid_keyword in invalid_keyword_list:
            if self.prefix == invalid_keyword:
                is_invalid_prefix = True
                break
        return is_invalid_prefix, self.grounding_string_unary('prefix_is_invalid_keyword', is_invalid_prefix)

    def google_title_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_title
        return is_contain_last_name, self.grounding_string_unary('google_title_contain_last_name', is_contain_last_name)

    def google_title_contain_first_name(self):
        is_contain_first_name = self.first_name in self.google_title
        return is_contain_first_name, self.grounding_string_unary('google_title_contain_first_name', is_contain_first_name)

    def google_content_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_content
        return is_contain_last_name, self.grounding_string_unary('google_content_contain_last_name', is_contain_last_name)

    def google_content_contain_first_name(self):
        is_contain_first_name = self.last_name in self.google_content
        return is_contain_first_name, self.grounding_string_unary('google_content_contain_first_name', is_contain_first_name)

    def prefix_contained_in_last_name(self):
        is_contained_in_last_name = self.prefix in self.last_name
        return is_contained_in_last_name, self.grounding_string_unary('prefix_contained_in_last_name', is_contained_in_last_name)

    def prefix_contained_in_first_name(self):
        is_contained_in_first_name = self.prefix in self.first_name
        return is_contained_in_first_name, self.grounding_string_unary('prefix_contained_in_first_name', is_contained_in_first_name)

    def prefix_contain_all_first_char(self):
        all_char = ''
        for name_part in self.person_name.split(' '):
            all_char += name_part[0]
        is_contain_all_first_char = False
        if all_char in self.prefix:
            is_contain_all_first_char = float(len(all_char)) >= float(len(self.prefix)) * 0.75
        return is_contain_all_first_char, self.grounding_string_unary('prefix_contain_all_first_char', is_contain_all_first_char)

    def prefix_contained_in_name_part_with_first_char(self):
        first_name_with_first_char = self.last_name[0] + self.first_name
        last_name_with_first_char = self.first_name[0] + self.last_name

        last_name_with_all_first_char = ''
        for name_part in self.person_name.split(' ')[:-1]:
            last_name_with_all_first_char += name_part[0]
        last_name_with_all_first_char += self.last_name

        is_prefix_contained = self.prefix in first_name_with_first_char or self.prefix in last_name_with_first_char or self.prefix in last_name_with_all_first_char
        return is_prefix_contained, self.grounding_string_unary('prefix_contained_in_name_part_with_another_first_char', is_prefix_contained)

    def google_title_contain_name(self):
        is_contain_name = self.person_name in self.google_title
        return is_contain_name, self.grounding_string_unary('google_title_contain_name', is_contain_name)

    def google_content_contain_name(self):
        is_contain_name = self.person_name in self.google_content
        return is_contain_name, self.grounding_string_unary('google_content_contain_name', is_contain_name)

    def get_unary_groundings(self):
        grounding_list = [
            self.prefix_contain_last_name(),
            self.prefix_contain_first_name(),

            self.prefix_contained_in_last_name(),
            self.prefix_contained_in_first_name(),

            self.google_title_contain_last_name(),
            self.google_title_contain_first_name(),

            self.google_content_contain_last_name(),
            self.google_content_contain_first_name(),

            self.google_title_contain_name(),
            # self.google_content_contain_name(),

            self.prefix_contain_all_first_char(),
            # self.prefix_contained_in_name_part_with_first_char(),

            self.google_title_contain_aff_word(),
            self.google_content_contain_aff_word(),

            self.prefix_is_invalid_keyword()
        ]
        return grounding_list

    def get_svm_feature_line(self):
        unary_groundings = self.get_unary_groundings()
        feature_list = [flag_grounding[0] for flag_grounding in unary_groundings]
        feature_line = self.label + ' '
        for looper in range(len(feature_list)):
            feature_id = str(looper + 1)
            feature_line += feature_id + ':' + str(int(feature_list[looper])) + ' '
        feature_line += '#' + self.person_name + '[' + self.email + ']' + '\n'
        return feature_line

    def get_fgm_feature_line(self):
        unary_groundings = self.get_unary_groundings()
        feature_name_list = [flag_grounding[1][:flag_grounding[1].find('(')] for flag_grounding in unary_groundings]
        feature_value_list = [flag_grounding[0] for flag_grounding in unary_groundings]

        fgm_token = '+'

        fgm_label = fgm_token + str((int(self.label) + 1) / 2)
        feature_line = fgm_label + ' '
        for looper in range(len(feature_name_list)):
            feature_name = feature_name_list[looper]
            feature_line += feature_name + ':' + str(int(feature_value_list[looper])) + ' '
        feature_line += '\n'
        return feature_line


