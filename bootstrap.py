import os
import subprocess


def check_and_activate_env():
    if "VIRTUAL_ENV" not in os.environ:
        print("Virtual environment is not activated. Running env.bat...")
        subprocess.call(["env.bat"])


def install_src():
    print("Installing src using uv pip install -e...")
    subprocess.call(["uv", "pip", "install", "-e", "./"])


def main():
    check_and_activate_env()
    install_src()


if __name__ == "__main__":
    main()
