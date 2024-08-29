import os
import json
from functools import cache

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))



@cache
def get_db():
    with open(os.path.join(SCRIPT_DIR, '..', 'tools', '_optim_db-minified.json')) as f:
        return json.load(f)


def main():
    from installer import main_test_deps
    db = get_db()
    for package_name in db.keys():
        try:
            main_test_deps(package_name)
        except SystemExit:
            print("Err with", package_name)
        except:
            print("Other err", package_name)

if __name__ == "__main__":
    main()