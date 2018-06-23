import glob
import itertools
import os
import shutil
import string
import subprocess
import tempfile

ascii_set = set(string.ascii_lowercase)


def has_non_cyrillic_symbols(file_name, except_letters='ivxlcdm'):
    """Check if there are non-digit and non-cyrillic symbols."""
    bad_letters = [letter for letter in map(str.lower, file_name) if letter.isalpha() and letter not in except_letters]
    return bool(set(bad_letters) & ascii_set)


def base_name_tuple(path): return os.path.basename(path).rsplit('.', 1)


def list_bad_paths(dir_name):
    """Build list with paths for files with non-cyrillic symbols."""
    bad_paths = []
    for path in glob.iglob(os.path.join(dir_name, '**', '*'), recursive=True):
        if not os.path.isfile(path):
            continue

        file_name, _ = base_name_tuple(path)
        if has_non_cyrillic_symbols(file_name):
            bad_paths.append(path)

    return sorted(bad_paths)


def make_rename_task(path, new_file_name):
    """Makes a pair (old path, new path). """
    old_file_name, extension = base_name_tuple(path)
    if old_file_name == new_file_name:
        return

    new_path = os.path.join(os.path.dirname(path), '%s.%s' % (new_file_name, extension))
    return path, new_path


def make_tasks(bad_paths, path_to_num_index):
    """

        составляем файл со списком "плохих" названий, открываем его в редакторе,
        дожидаемся закрытия, парсим результат и возвращаем список пар (старый путь, новый путь)

    """
    tasks = []
    num_to_path_index = {v: k for k, v in path_to_num_index.items()}

    # сортируем, чтобы была детерминированность при идентичных запусках
    sorted_paths = sorted(bad_paths, key=os.path.split)

    # создаем временный файл
    _, temp_file_path = tempfile.mkstemp(suffix='.txt', text=True)
    try:

        # пишем в файл список старых названий с уникальным численным идентификатором
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            for _, group_it in itertools.groupby(sorted_paths, key=lambda t: os.path.split(t)[-2]):
                for path in group_it:
                    file_name, _ = base_name_tuple(path)
                    print('%s %s' % (path_to_num_index[path], file_name), file=f)

                print('', file=f)

        # открываем файл в Sublime Text (сгодится любой редактор, который
        # умеет блокировать поток выполнения до закрытия файла.
        # у sublime для этого есть специальный флаг -w)
        subprocess.Popen(['subl', '-w', temp_file_path]).wait()

        # парсим результат, составляем список пар (старый путь, новый путь)
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
        # убираемся за собой
        os.unlink(temp_file_path)

    return tasks


def main(dir_name, dry_run=False):
    dir_name = os.path.expanduser(dir_name)

    bad_paths = list_bad_paths(dir_name)

    # словарь с уникальным номером для каждого пути.
    # нужен, чтобы изменные названия с их исходными версиями
    path_to_num_index = {path: str(i) for i, path in enumerate(bad_paths)}

    # открываем файл для редактирования пользователю,
    # дожидаемся окончания и матчим измененные названия с их исходными версиями
    tasks = make_tasks(bad_paths, path_to_num_index)

    # выводим пользователю на экран план работы
    for src, dst in tasks:
        print(src, ' --> ', dst)

    if dry_run:
        return

    okay_input = 'y'
    # запрашиваем подтверждение
    answer = input('Type `%s` if everything is ok: ' % okay_input)

    if answer == okay_input:
        # переименовываем файлы
        for src, dst in tasks:
            shutil.move(src, dst)
