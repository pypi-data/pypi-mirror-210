import os
import re
import json
import errno
import shutil
from os.path import expanduser

import jinja2


def get_home_dir():
    return expanduser('~')


def create_dir_if_not_exists(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def read_file_content(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def read_file_as_list(file_path):
    res = []
    with open(file_path, 'r') as f:
        for line in f:
            if line[-1] == os.linesep:
                line = line[:-1]
            res.append(line)
    return res


# not include files in subdirectories
def get_files_from_dir(dir_path):
    result = []
    for (_dir, dir_names, filenames) in os.walk(dir_path):
        if not os.path.samefile(_dir, dir_path):
            break
        for filename in filenames:
            result.append(os.path.join(_dir, filename))
    return result


def get_file_name(full_path):
    file_name = full_path.split('/')[-1]
    if '.' not in file_name:
        return file_name

    file_name = file_name.split('.')[0]
    return file_name


def load_json_from_file(file_path):
    with open(file_path) as f:
        return json.loads(f.read())


def get_re_group_n(pattern, _str, n):
    p = re.compile(pattern)
    m = p.match(_str)
    return m.group(n)


def match_re(pattern, _str):
    return bool(re.match(pattern, _str))


def render_jinja2_template_file(tpl_dir, file_name, **kwargs):
    template_loader = jinja2.FileSystemLoader(searchpath=tpl_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template_file = file_name
    template = template_env.get_template(template_file)
    output_text = template.render(**kwargs)
    return output_text


def render_jinja2_template_str(_str, **kwargs):
    template = jinja2.Template(_str)
    output_text = template.render(**kwargs)
    return output_text


def print_error(text):
    cred = '\033[91m'
    cend = '\033[0m'
    print(cred + text + cend)


if __name__ == '__main__':
    for l in get_files_from_dir('/Users/clpsz/.bke/db_configs'):
        print(l)
