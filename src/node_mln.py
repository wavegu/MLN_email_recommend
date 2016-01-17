import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class NodeMLN:

    def __init__(self, google_item_dict):
        self.node_name = str(google_item_dict['id'])
        self.email = str(google_item_dict['email_addr']).lower()
        self.person_name = str(google_item_dict['person_name']).lower().replace('-', ' ')
        self.google_title = str(google_item_dict['title']).lower()
        self.google_content = str(google_item_dict['content']).lower()
        self.grounding_file_path = os.path.join('..', 'result', self.person_name, 'MLN.db')

        self.last_name = self.person_name.split(' ')[-1]
        self.first_name = self.person_name.split(' ')[0]
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

    def prefix_contain_last_name(self):
        is_contain_last_name = self.last_name in self.prefix
        return self.grounding_string_unary('prefix_contain_last_name', is_contain_last_name)

    def prefix_contain_first_name(self):
        is_contain_first_name = self.first_name in self.prefix and len(self.first_name) > 2
        return self.grounding_string_unary('prefix_contain_first_name', is_contain_first_name)

    def prefix_is_invalid_keyword(self):
        invalid_keyword_list = ['email', 'info', 'mailto']
        is_invalid_prefix = False
        for invalid_keyword in invalid_keyword_list:
            if self.prefix == invalid_keyword:
                is_invalid_prefix = True
                break
        return self.grounding_string_unary('prefix_is_invalid_keyword', is_invalid_prefix)

    def google_title_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_title
        return self.grounding_string_unary('google_title_contain_last_name', is_contain_last_name)

    def google_title_contain_first_name(self):
        is_contain_first_name = self.first_name in self.google_title
        return self.grounding_string_unary('google_title_contain_first_name', is_contain_first_name)

    def google_content_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_content
        return self.grounding_string_unary('google_content_contain_last_name', is_contain_last_name)

    def google_content_contain_first_name(self):
        is_contain_first_name = self.last_name in self.google_content
        return self.grounding_string_unary('google_content_contain_first_name', is_contain_first_name)

    def prefix_contained_in_last_name(self):
        is_contained_in_last_name = self.prefix in self.last_name
        return self.grounding_string_unary('prefix_contained_in_last_name', is_contained_in_last_name)

    def prefix_contained_in_first_name(self):
        is_contained_in_first_name = self.prefix in self.first_name
        return self.grounding_string_unary('prefix_contained_in_first_name', is_contained_in_first_name)

    def google_content_contain_all_first_char(self):
        all_char = ''
        for name_part in self.person_name.split(' '):
            all_char += name_part[0]
        is_contain_all_first_char = False
        if all_char in self.prefix:
            is_contain_all_first_char = float(len(all_char)) >= float(len(self.prefix)) * 0.75
        return self.grounding_string_unary('google_content_contain_all_first_char', is_contain_all_first_char)

    def prefix_contained_in_name_part_with_first_char(self):
        first_name_with_first_char = self.last_name[0] + self.first_name
        last_name_with_first_char = self.first_name[0] + self.last_name

        last_name_with_all_first_char = ''
        for name_part in self.person_name.split(' ')[:-1]:
            last_name_with_all_first_char += name_part[0]
        last_name_with_all_first_char += self.last_name

        is_prefix_contained = self.prefix in first_name_with_first_char or self.prefix in last_name_with_first_char or self.prefix in last_name_with_all_first_char
        return self.grounding_string_unary('prefix_contained_in_name_part_with_another_first_char', is_prefix_contained)

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

            self.google_content_contain_all_first_char(),
            self.prefix_contained_in_name_part_with_first_char(),

            self.prefix_is_invalid_keyword()
        ]
        return grounding_list