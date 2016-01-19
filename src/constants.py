import os
from util import create_dir_if_not_exist

CONSTANT_PATH = {
    'google_item_dir': os.path.join('..', 'resource', 'google_items'),
    'result': os.path.join('..', 'result'),
    'resource': os.path.join('..', 'resource'),
    'by_product_dir': os.path.join('..', 'by_product'),
    'mln_by_product_dir': os.path.join('..', 'by_product', 'mln_by_product'),
    'svm_by_product_dir': os.path.join('..', 'by_product', 'svm_by_product'),
    'fgm_by_product_dir': os.path.join('..', 'by_product', 'fgm_by_product'),
}

for key, value in CONSTANT_PATH.items():
    create_dir_if_not_exist(value)