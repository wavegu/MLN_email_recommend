import os

def run_tuffy(prog_path, evidence_path, query_path, out_path):
    cmd = 'java -jar tuffy.jar -i ' + prog_path + ' -e ' + evidence_path + ' -queryFile ' + query_path + ' -r ' + out_path
    print cmd
    os.system(cmd)


item_filename_list = os.listdir('../google_items')
for item_filename in item_filename_list:
    person_name = item_filename.replace('.json', '')

    person_dir = os.path.join('../../result', person_name.replace(' ', '_'))
    prog_path = os.path.join('..', 'prog.mln')
    query_path = os.path.join('..', 'query.db')
    evidence_path = os.path.join(person_dir, 'evidence.db')
    out_path = os.path.join(person_dir, 'result.db')
    run_tuffy(prog_path, evidence_path, query_path, out_path)
    break