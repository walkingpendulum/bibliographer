#! /usr/bin/env python3

import fire

from bibliographer.issues_with_non_cyrillic_symbols import main


class CLI:
    def move(self, dir_name):
        main(dir_name)

    def dry_run(self, dir_name):
        main(dir_name, dry_run=True)


if __name__ == '__main__':
    # гугловский фреймворк для создания cli
    # решил попробовать для разнообразия
    fire.Fire(CLI)
