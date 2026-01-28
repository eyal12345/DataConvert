import subprocess
import shutil
import sys
import os

def install_dependencies(project_path) -> None:
    # extract dependencies from requirements document
    with open(f'{project_path}/requirements.txt', 'r') as file:
        dependencies = file.read().split()
    # install each dependency in site packages
    for dependency in dependencies:
        result = subprocess.run(f'pip install {dependency}', shell=True, capture_output=True, text=True)
        print(result.stdout)

def install_application(project_path) -> None:
    if not os.path.exists(f'{project_path}/dist/main.exe'):
        application = f'python -m PyInstaller --noconfirm --onefile --windowed --icon="{project_path}/logo.ico" --add-data="{project_path}/logo.ico;." "{project_path}/main.py"'
        result = subprocess.run(application, shell=True, capture_output=True, text=True)
        print(result.stdout)

def transfer_installations(work_path, save_folder) -> None:
    os.makedirs(f'{save_folder}/dist') if not os.path.exists(f'{save_folder}/dist') else None
    shutil.move(f'{work_path}/dist/main.exe', f'{save_folder}/dist/main.exe')
    shutil.move(f'{work_path}/main.spec', f'{save_folder}/main.spec')
    shutil.rmtree(f'{save_folder}/build') if os.path.exists(f'{save_folder}/build') else None
    shutil.move(f'{work_path}/build', f'{save_folder}')
    shutil.rmtree(f'{work_path}/dist')

# get current project path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# install all dependencies of the application
install_dependencies(project_path)
# install application
install_application(project_path)
# get current working directory
work_path = os.getcwd()
# get user's path location from cli
save_folder = sys.argv[1]
# transfer all installed files to user's path choice
transfer_installations(work_path, save_folder)
