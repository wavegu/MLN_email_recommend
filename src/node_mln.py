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
        self.email_prefix = self.email[:self.email.find('@')]

    def grounding_string_unary(self, grounding_name, is_true):
        grounding_str = str(grounding_name) + '(' + str(self.node_name) + ')\n'
        if not is_true:
            return '!' + grounding_str
        return grounding_str

    def get_grounding_email_prefix_contain_last_name(self):
        is_contain_last_name = self.last_name in self.email_prefix
        return self.grounding_string_unary('email_prefix_contain_last_name', is_contain_last_name)

    def get_grounding_email_prefix_contain_first_name(self):
        is_contain_first_name = self.first_name in self.email_prefix and len(self.first_name) > 2
        return self.grounding_string_unary('email_prefix_contain_first_name', is_contain_first_name)

    def get_grounding_google_title_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_title
        return self.grounding_string_unary('google_title_contain_last_name', is_contain_last_name)

    def get_grounding_google_title_contain_first_name(self):
        is_contain_first_name = self.first_name in self.google_title
        return self.grounding_string_unary('google_title_contain_last_name', is_contain_first_name)

    def get_grounding_google_content_contain_last_name(self):
        is_contain_last_name = self.last_name in self.google_content
        return self.grounding_string_unary('google_content_contain_last_name', is_contain_last_name)

    def get_grounding_google_content_contain_all_first_char(self):
        all_char = ''
        for name_part in self.person_name.split(' '):
            all_char += name_part[0]
        is_contain_all_first_char = False
        if all_char in self.email_prefix:
            is_contain_all_first_char = float(len(all_char)) >= float(len(self.email_prefix)) * 0.6
        return self.grounding_string_unary('google_content_contain_all_first_char', is_contain_all_first_char)

    def get_groundings(self):
        grounding_list = [
            self.get_grounding_email_prefix_contain_last_name(),
            self.get_grounding_email_prefix_contain_first_name(),
            self.get_grounding_google_title_contain_last_name(),
            self.get_grounding_google_title_contain_first_name(),
            self.get_grounding_google_content_contain_last_name(),
            self.get_grounding_google_content_contain_all_first_char()
        ]
        return grounding_list