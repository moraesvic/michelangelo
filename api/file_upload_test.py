import time, re, random
from typing import List, Tuple, Dict, Callable
from werkzeug.datastructures import FileStorage
from dataclasses import dataclass, field

from file_upload import get_new_name

NUMBER_OF_TESTS = 50
VERBOSE = True

@dataclass
class Test:
    fn: Callable
    args: Tuple = field(default_factory = tuple)
    kwargs: Dict = field(default_factory = dict)
    
    def run(self):
        return self.fn(*self.args, **self.kwargs)


def get_new_name_test() -> bool:
    milliseconds_length = len(str(int(time.time() * 1000)))
    regex = re.compile(r"[0-9]{%d}-[0-9]{9}" % (milliseconds_length))

    for i in range(NUMBER_OF_TESTS):
        time.sleep(random.random() * 0.05)
        new_name = get_new_name()
        if not regex.match(new_name):
            print(f"{new_name} does not correspond to the expected format!")
            return False
        elif VERBOSE:
            print(f"{new_name} : ok")

    return True

def main():
    tests = [
        Test(get_new_name_test)
    ]
    approved = 0
    for test in tests:
        if test.run():
            approved += 1
        else:
            print(f"Test {approved} of {len(tests)} failed!")
            return

    print(f"Success! {approved} tests approved!")

main()