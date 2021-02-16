#Script to hack Katib package as per current API version used

import os
import sys


def _rewrite_helper(input_file, rewrite_rules):
    rules = rewrite_rules or []
    lines = []
    with open(input_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            for rule in rules:
                line = rule(line)
            lines.append(line)
            
    with open(input_file, 'w') as f:
        f.writelines(lines)



def update_python_sdk(file_path):
        # tiny transformers to refine generated codes
        rewrite_rules = [
            lambda l: l.replace('klass = getattr(katib.models, klass)', 'klass = getattr(kubeflow.katib.models, klass)')
        ]
        
        _rewrite_helper(file_path, rewrite_rules)


if __name__ == '__main__':
    update_python_sdk(file_path=sys.argv[1])
