import subprocess
import shutil
import sys
import os

def install_dependencies() -> None:
    # extract dependencies from requirements document
    with open('requirements.txt', 'r') as file:
        dependencies = file.read().split()
    # install each dependency in site packages
    for dependency in dependencies:
        result = subprocess.run(f'pip install {dependency}', shell=True, capture_output=True, text=True)
        print(result.stdout)

def install_application(current_path) -> None:
    if not os.path.exists('dist/main.exe'):
        application = f'pyinstaller --noconfirm --onefile --windowed --icon={current_path}/logo.ico --add-data {current_path}/logo.ico;. {current_path}/main.py'
        result = subprocess.run(application, shell=True, capture_output=True, text=True)
        print(result.stdout)

def transfer_installations(current_path, save_folder) -> None:
    os.makedirs(f'{save_folder}/dist') if not os.path.exists(f'{save_folder}/dist') else None
    shutil.move(f'{current_path}/dist/main.exe', f'{save_folder}/dist/main.exe')
    shutil.move(f'{current_path}/main.spec', f'{save_folder}/main.spec')
    shutil.rmtree(f'{save_folder}/build') if os.path.exists(f'{save_folder}/build') else None
    shutil.move(f'{current_path}/build', f'{save_folder}')
    shutil.rmtree(f'{current_path}/dist')

# install all dependencies of the application
install_dependencies()
# install application in the path project
current_path = os.getcwd()
install_application(current_path)
# get user's path location from cli
save_folder = sys.argv[1]
# transfer all installed files to user's path choice
transfer_installations(current_path, save_folder)
