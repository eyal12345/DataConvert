interpreter requirement:
- the project run on python 3.10 or 3.11

recommended command:
- python -m pip install --upgrade pip

dependencies for install application:
- python -m pip install pyinstaller

dependencies for running application:
- python -m pip install requests
- python -m pip install openpyxl
- python -m pip install pyyaml

dependencies from text file (optional):
- python -m pip install -r requirements.txt

usage on cli running:
- python <user_path>/DataConvert/main.py -r "root" -d "depth" -f "format"

Create exe file through 'exe_install/create_exe_file.py' script:
- python install/exe_install.py <path_to_install>/<name_folder_app>

Example to input arguments command in cli:
- python main.py -r "https://www.python.org" -d 2 -f "yml"

Discard all local changes (be careful, this is irreversible):
- git reset --hard HEAD
