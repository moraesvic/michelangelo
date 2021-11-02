#!/usr/bin/env python3.8
import os, re, subprocess, sys

def rel_path(path, base_dir = ""):
    # This function is also defined elsewhere, but I wanted this to run
    # as standalone (not as a module)
    if not base_dir:
        base_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(base_dir, path)

def run_command(cmd):
    # Will output lines to screen as soon as they are received
    with subprocess.Popen(
        cmd,
        shell = True,
        text = True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ) as proc:
        for line in proc.stdout:
            print(line, end="", flush=True)

def read_env(path):
    f = open(path, "r")
    dic = dict()
    regex = re.compile(r"^(.+)=(.+)$")

    line = f.readline()
    while line:
        match = regex.search(line)
        if match:
            dic[match.groups()[0]] = match.groups()[1]
        line = f.readline()

    f.close()
    return dic

def write_env(path, dic):
    f = open(path, "w")
    for key, value in dic.items():
        f.write(f"{key}={value}\n")
    f.close()


ROOT_ID = 0
REQUIREMENTS_FILE = rel_path("requirements.txt")
TMP_FILE = rel_path("tmp_file.txt")
ENV_FILE = rel_path(".env")
CLIENT_ENV_FILE = rel_path("client/.env")

def get_pip_requirements():
    regex_first_line = re.compile(r"^\$ pip freeze")
    regex_last_line = re.compile(r"^>>> PostgreSQL")

    req_file = open(REQUIREMENTS_FILE, "r")

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
    print("\n\nWe will now install pip requirements.\n")
    os.chdir(rel_path("."))

    # Source from virtual environment
    run_command(". venv/bin/activate")
    
    # Installing dependencies
    run_command(f"pip install -r {TMP_FILE}")

    # Removing tmp_file
    os.remove(TMP_FILE)

def change_env(uname, password, database, host, port):
    current_env = read_env(ENV_FILE)

    print(current_env)
    current_env["POSTGRES_USER"] = uname
    current_env["POSTGRES_PASSWORD"] = password
    current_env["POSTGRES_DATABASE"] = database
    current_env["POSTGRES_HOST"] = host
    current_env["POSTGRES_PORT"] = port
    current_env["APP_NAME"] = "michelangelo"

    print(current_env)
    write_env(ENV_FILE, current_env)

def install_db():
    print("\n\nWe will now install the database.\n")

    uname = input("Please type in the username.  ")
    password = input("Now type in the password. (Sorry, we will echo it to screen, please make sure nobody is looking ¯\_(ツ)_/¯)  ")
    database = input("Type the name of the new database.  ")
    command = f"""\
sudo -i -u postgres \
    psql                                                                    \
        -c "CREATE USER {uname} WITH ENCRYPTED PASSWORD '{password}'; "     \
        -c "CREATE DATABASE {database}; "                                   \
        -c "GRANT ALL PRIVILEGES ON DATABASE {database} TO {uname}; "       \
"""
    run_command(command)

    host="localhost"
    port=5432
    
    files = subprocess.check_output("""\
        find ./sql      \
        -maxdepth 1     \
        -type f         \
    """,
        shell = True,
        text = True
        ).strip().split("\n")

    files.sort()

    for file in files:
        print(f"Installing file {file}")
        import_command = f"""       \
PGPASSWORD="{password}" \
psql -U "{uname}"       \
    -h "{host}"         \
    -d "{database}"     \
    -p "{port}"         \
    -f "{file}"         \
"""
        run_command(import_command)

    change_env(uname, password, database, host, port)

def check_dependencies(dependencies):
    for dep in dependencies:
        try:
            subprocess.run(f"which {dep}", shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"It seems like {dep} is not installed in your computer.")
            raise

def install_front_end():
    print("We will now proceed with the front-end installation")

    os.chdir(rel_path("./client"))

    run_command("npm install")
    run_command("npm audit fix")

    dic = {
        "BROWSER": "none",
        "PORT": 7777,
        "BACKEND_PORT": 9999,
        "PUBLIC_URL": "/michelangelo"
    }
    write_env(CLIENT_ENV_FILE, dic)
    BROWSER=none
    PORT=7777
    BACKEND_PORT=9999
    PUBLIC_URL=/michelangelo

def main():
    version = sys.version_info
    if version.major != 3 or version.minor != 8:
        print("Script (and app) must be run with Python3.8")
        return
    
    if os.getuid() != ROOT_ID:
        print("This script must be run as root")
        return

    try:
        check_dependencies(["psql", "npm"])
    except subprocess.CalledProcessError:
        print("Install the missing software and run again.")
        return

    get_pip_requirements()
    install_pip_requirements()
    install_db()
    install_front_end()

    print("\n\nWell done! You are almost ready to go. Now what you have to do is: " + 
    "go to project main folder, run the development server (./scripts/run_dev) " +
    "and do the tests (./scripts/run_tests). If everything is ok, go ahead and " +
    "populate the database (./scripts/populate_db.py). Then, you can finally "
    "run the server in production mode (./scripts/run_prod)\n")

    print("TL;DR\n\n" + 
    "cd path/to/michelangelo\n" +
    "./scripts/run_dev &\n" +
    "(^ you will need to let this running in the background)\n\n" +
    "./scripts/run_tests\n\n" +
    "(you can now stop the development environment)\n" +
    "./scripts/run_prod\n")

    print("If anything doesn't work, keep calm and don't panic.")

if __name__ == "__main__":
    main()