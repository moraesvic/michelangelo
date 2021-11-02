import os, re, subprocess

def rel_path(path, base_dir = ""):
    # This function is also defined elsewhere, but I wanted this to run
    # as standalone (not as a module)
    if not base_dir:
        base_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(base_dir, path)

ROOT_ID = 1000 # later change to 0
TMP_FILE = rel_path("tmp_file.txt")

def get_pip_requirements():
    regex_first_line = re.compile(r"^\$ pip freeze")
    regex_last_line = re.compile(r"^>>> PostgreSQL")

    req_file = open(rel_path("requirements.txt"), "r")

    # Search for beginning of pip requirements
    line = req_file.readline()
    while not regex_first_line.search(line):
        line = req_file.readline()

    # Start reading
    buffer = ""
    line = req_file.readline()
    while not regex_last_line.search(line):
        buffer += line
        line = req_file.readline()

    req_file.close()

    buffer = buffer.strip()
    tmp_file = open(TMP_FILE, "w")
    tmp_file.write(buffer)
    tmp_file.close()

def install_pip_requirements():
    os.chdir(rel_path("."))

    # Source from virtual environment
    subprocess.check_output(
        ". venv/bin/activate",
        shell = True)
    
    subprocess.check_output(
        f"pip install -r {TMP_FILE}",
        shell = True,
        text = True
    )

    # os.remove(TMP_FILE)


def main():
    if os.getuid() != ROOT_ID:
        print("This script must be run as root")
        return

    get_pip_requirements()
    install_pip_requirements()

if __name__ == "__main__":
    main()