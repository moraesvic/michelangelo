#!/usr/bin/env python3.8
import os, re, subprocess, sys

class colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def rel_path(path, base_dir = ""):
    # This function is also defined elsewhere, but I wanted this to run
    # as standalone (not as a module)
    if not base_dir:
        base_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(base_dir, path)

def run_command(cmd):
    # Will output lines to screen as soon as they are received

    # Clean the command for better presentation
    cmd = re.sub(r"[ ]{2,}", " ", cmd)
    cmd = re.sub(r"[\t]{2,}", " ", cmd)
    cmd = re.sub(r"[\n]+", " ", cmd)

    print(f"\n{colors.YELLOW}$ {cmd}{colors.END}")

    with subprocess.Popen(
        cmd,
        shell = True,
        text = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT
    ) as proc:
        for line in proc.stdout:
            print(line, end="", flush=True)
    if proc.returncode != 0:
        raise Exception(f"Error! Command <{cmd}> exited with non-zero status!")

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

############################################################
# CONSTANTS
############################################################

ROOT_ID = 0
REQUIREMENTS_FILE = rel_path("requirements.txt")
TMP_FILE = rel_path("tmp_file.txt")
ENV_FILE = rel_path(".env")
CLIENT_ENV_FILE = rel_path("client/.env")

############################################################

def get_pip_requirements():
    regex_first_line = re.compile(r"^\$ pip freeze")
    regex_last_line = re.compile(r"^>>> pip")

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

def install_pip_requirements(pip_command):
    print(f"\n{colors.CYAN}We will now install pip requirements.{colors.END}")
    os.chdir(rel_path("."))
    
    # Installing dependencies
    try:
        run_command(f". venv/bin/activate ; {pip_command} install -r {TMP_FILE}")
    except:
        print("\n\n'pip install' exited with error. If you are getting something " +
            """like "ModuleNotFoundError: No module named '_ctypes'" """ + 
            "you might want to install libffi-dev (sudo apt install libffi-dev) " +
            "and perhaps rebuild your python version")
        print("\n\nIf, on the other hand, the error happens when psycopg2 library " +
            "is installing, you might need to install libpq-dev " +
            "(sudo apt-get install libpq-dev)\n")
        raise

    # Removing tmp_file
    os.remove(TMP_FILE)

def change_env(uname, password, database, host, port):
    current_env = read_env(ENV_FILE)

    current_env["POSTGRES_USER"] = uname
    current_env["POSTGRES_PASSWORD"] = password
    current_env["POSTGRES_DATABASE"] = database
    current_env["POSTGRES_HOST"] = host
    current_env["POSTGRES_PORT"] = port
    current_env["APP_NAME"] = "michelangelo"

    write_env(ENV_FILE, current_env)

def install_db():
    print(f"\n{colors.CYAN}We will now install the database.\n{colors.END}")

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
            run_command(f"which {dep}")
        except:
            print(f"It seems like {dep} is not installed in your computer.")
            raise

def install_front_end():
    print(f"\n{colors.CYAN}We will now proceed with the front-end installation{colors.END}")

    os.chdir(rel_path("./client"))

    run_command("npm install")

    dic = {
        "BROWSER": "none",
        "PORT": 7777,
        "BACKEND_PORT": 9999,
        "PUBLIC_URL": "/michelangelo"
    }
    write_env(CLIENT_ENV_FILE, dic)

def install_venv():
    print("\nWe will now install a virtual environment.")

    os.chdir(rel_path("."))

    run_command("python3.8 -m venv venv")

def instructions_nginx():
    print(f"\n{colors.CYAN}INSTRUCTIONS FOR NGINX{colors.END}\n")
    print("This app was made for using in production with Nginx as a reverse proxy.")
    print("We will NOT do this configuration for you, as it might break your existing servers")
    print("We advise you to edit your conf.d file in /etc/nginx and insert the " +
        "following directive in the server block:")
    block = """-----

location = /michelangelo {
    return 302 /michelangelo/;
}

location /michelangelo/ {
    rewrite /michelangelo/(.*) /$1 break;
    proxy_pass http://localhost:7777/michelangelo/;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-For $remote_addr;

}

-----"""
    print(block)

def find_pip():
    # Ugly code, need to improve later
    try:
        subprocess.run(f"which pip", shell=True, check=True)
        return "pip"
    except subprocess.CalledProcessError:
        try:
            subprocess.run(f"which pip3", shell=True, check=True)
            return "pip3"
        except subprocess.CalledProcessError:
            try:
                subprocess.run(f"which pip3.8", shell=True, check=True)
                return "pip3.8"
            except subprocess.CalledProcessError:
                print(f"It seems like pip is not installed in your computer.")
                raise


def create_uploads_dir():
    print(f"\n{colors.CYAN}Creating uploads/ directory{colors.END}")
    os.chdir(rel_path("."))
    os.mkdir("uploads")

def main():
    version = sys.version_info
    if version.major != 3 or version.minor != 8:
        print("Script (and app) must be run with Python3.8")
        print("If you do not have it yet, we recommend building for source:")
        commands = """
cd ~
wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
tar -xf Python-3.8.0.tgz
cd Python-3.8.0
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

# optionally remove installation directory

# cd ..
# rm -r Python-3.8.0
# rm Python-3.8.0.tgz
"""
        print(commands)
        print("The above command might take 5 minutes to execute and will NOT "
            "remove your current Python3 version. " +
            "You can also install Python3.8 with your package manager. " + 
            "Details must be confirmed according to your operating system.")
        return
    
    if os.getuid() != ROOT_ID:
        print("This script must be run as root")
        return

    try:
        check_dependencies(["psql", "npm", "exiftool", "convert", "compare", "nginx"])
    except subprocess.CalledProcessError:
        print(f"{colors.RED}ERROR!{colors.END}")
        print("Install the missing software and run again.")
        print('TIP: "convert" and "compare" can be found in the "imagemagick" package')
        return

    install_venv()

    try:
        pip_command = find_pip()
    except:
        return
    
    try:
        get_pip_requirements()
        install_pip_requirements(pip_command)
        install_db()
        install_front_end()
        instructions_nginx()
        create_uploads_dir()
    except:
        print(f"{colors.RED}Installation cannot continue. Exiting...{colors.END}")
        return

    print(f"\n\n{colors.GREEN}Well done!{colors.END} You are almost ready to go. Now what you have to do is: " + 
    "go to project main folder, activate virtual environment (source ./venv/bin/activate), " + 
    "run the development server (./scripts/run_dev) " +
    "and do the tests (./scripts/run_tests).\n\n" +
    "If everything is ok, go ahead and " +
    "populate the database (python3.8 -m scripts.populate_db). Then, you can finally "
    "run the server in production mode (./scripts/run_prod)\n")

    print(f"{colors.CYAN}TL;DR{colors.END}\n\n" + 
    "\tcd path/to/michelangelo\n" +
    "\tsource ./venv/bin/activate\n" +
    "\t./scripts/run_dev &\n" +
    "\t(^ you will need to let this running in the background)\n\n" +
    "\t./scripts/run_tests\n\n" +
    "\tpython3.8 -m scripts.populate_db\n" +
    "\t(you can now stop the development environment)\n" +
    "\t./scripts/run_prod\n")

    print(f"{colors.CYAN}If anything doesn't work, keep calm and don't panic.{colors.END}")

if __name__ == "__main__":
    main()