import os
import sys


def replace_any_len(s, what_to_replace, what_replace_to):
    if s.count(what_to_replace) % 2:
        replaced = s.replace(what_to_replace * 2, '').replace(what_to_replace, what_replace_to)
    else:
        replaced = what_replace_to.join([x for x in s.split(what_to_replace * 2) if x])

    return replaced


def format_name(name):
    cond = any([
        ' -' in name,
        '- ' in name,
        '--' in name,
    ])
    if not cond:
        return

    space_normalized = replace_any_len(name, ' ', ' ')
    dash_normalized = replace_any_len(space_normalized, '-', '-')
    long_dash = chr(8212)
    formatted_name = ' {} '.format(long_dash).join(dash_normalized.replace(' -', '$-').replace('- ', '-$').split('$-$'))

    return formatted_name


def do_replace_dashes(path, file, dry_run):
    if not format_name(file):
        return

    names = [os.path.join(path, t) for t in [file, format_name(file)]]
    if dry_run:
        print('%s --> %s' % tuple(names))
    else:
        os.rename(*names)


def replace_dashes_in_path(path_to_dir, dry_run):
    answer = input('Requested renaming for directory "{}", is it correct? y/[n]\n'.format(path_to_dir))
    if answer != 'y':
        print('Aborting')
        sys.exit(1)

    for path, _, files in os.walk(path_to_dir):
        for file in files:
            file = file.strip()
            if not file or file.startswith('.'):
                continue

            do_replace_dashes(path, file, dry_run)
