#! /usr/bin/env python3
# coding: utf-8
import glob
import itertools
import os
import string
import subprocess
import sys
import tempfile
import shutil
import fire


ascii_set = set(string.ascii_lowercase)


def nearly_non_cyrillic(file_name, except_letters='ivxlcdm'):
    letters = set(letter.lower() for letter in file_name if letter.isalpha() and letter.lower() not in except_letters)
    return bool(set(letters) & ascii_set)


def base_name_tuple(path):
    return os.path.basename(path).rsplit('.', 1)


def list_bad_paths(dir_name):
    bad_paths = []
    for path in glob.iglob(os.path.join(dir_name, '**', '*'), recursive=True):
        if not os.path.isfile(path):
            continue

        file_name, _ = base_name_tuple(path)
        if nearly_non_cyrillic(file_name):
            bad_paths.append(path)

    return sorted(bad_paths)


def make_rename_task(path, new_file_name):
    old_file_name, extension = base_name_tuple(path)
    if old_file_name == new_file_name:
        return

    new_path = os.path.join(os.path.dirname(path), '%s.%s' % (new_file_name, extension))
    return path, new_path


def make_tasks(bad_paths, path_to_num_index):
    tasks = []
    num_to_path_index = {v: k for k, v in path_to_num_index.items()}

    sorted_paths = sorted(bad_paths, key=os.path.split)
    _, temp_file_path = tempfile.mkstemp(suffix='.txt', text=True)
    try:
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            for _, group_it in itertools.groupby(sorted_paths, key=lambda t: os.path.split(t)[-2]):
                for path in group_it:
                    file_name, _ = base_name_tuple(path)
                    print('%s %s' % (path_to_num_index[path], file_name), file=f)

                print('', file=f)

        subprocess.Popen(['subl', '-w', temp_file_path]).wait()

        with open(temp_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line or line == '\n':
                    continue

                num, new_file_name = line.strip().split(' ', 1)
                path = num_to_path_index[num]

                task = make_rename_task(path, new_file_name)
                if task:
                    tasks.append(task)

    finally:
        os.unlink(temp_file_path)

    return tasks


def main(dir_name, dry_run=False):
    dir_name = os.path.expanduser(dir_name)

    bad_paths = list_bad_paths(dir_name)
    path_to_num_index = {path: str(i) for i, path in enumerate(bad_paths)}

    tasks = make_tasks(bad_paths, path_to_num_index)
    for src, dst in tasks:
        print(src, ' --> ', dst)

    if dry_run:
        return

    okay_input = 'y'
    answer = input('Type `%s` if everything is ok: ' % okay_input)
    if answer == okay_input:
        for src, dst in tasks:
            shutil.move(src, dst)


class CLI:
    def move(self, dir_name):
        main(dir_name)

    def dry_run(self, dir_name):
        main(dir_name, dry_run=True)


if __name__ == '__main__':
    fire.Fire(CLI)
