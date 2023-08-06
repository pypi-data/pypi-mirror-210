from ShellUtilities import Shell
import os
import logging
from pathlib import Path
import sys
# This contains python functions which basically reimpliment the bash script logic
# They make the same exact calls to the git cli and use the same logical structure

def determine_version_number(repo_path=None, adjust_for_pep_440=True, adjust_for_pypi=False):
    
    # Try to run code from the installed path first
    path = Path(sys.executable)
    root_or_drive = path.root or path.drive
    script_name = "determine_tbd_calver_version_number.sh"
    script_path = os.path.join(root_or_drive, "usr", "local", "bin", script_name)
    
    # if the code is not installed, run it from this directory
    if not os.path.exists(script_path):
        logging.warn("Script does not appear to be installed correctly.")
        logging.debug("Running from local path instead.")  
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not repo_path:
            repo_path = os.getcwd()
        src_root_dir = os.path.dirname(current_dir)
        bash_dir = os.path.join(src_root_dir, "bash", "bin")
        script_path = os.path.join(bash_dir, script_name)
    
    version_number = Shell.execute_shell_command(f"bash {script_path}", cwd=repo_path).Stdout
    
    if not adjust_for_pep_440 and not adjust_for_pypi:
        return version_number
    
    # With PEP 440 version specifier is `<public identifier>[+<local label>]`
    # This means we need to adjsut our version number to use a + rather than a .
    # for the fourth element in the version number
    #
        
    parts = version_number.split(".")
    year = parts[0]
    month = parts[1]
    day = parts[2]
    branch_type = parts[3]
    build_or_commit = parts[4]
    
    if adjust_for_pep_440:
        version_number = f"{year}.{month}.{day}+{branch_type}.{build_or_commit}"
    
    # Note that Pypi does not allow local labels to be used. It is very strict
    # that it is a public package repository meant to serve public packages.
    # As such, the version numbers output by this library will not be compliant
    # with pypi (though they will work with other systems like artifactory).
    # 
    # One of the main issues is that the PEP 440 scheme really only allows numbers
    # which it represents with N:
    #
    #        [N!]N(.N)*[{a|b|rc}N][.postN][.devN]
    #
    # This means that only integration branches can have version numbers because 
    # they are synchronous in nature. Asynchronous branches cannot be assigned 
    # sequential numbers because they are non-sequention by nature.
    
    if adjust_for_pypi:
        if branch_type == "master":
            version_number = f"{year}.{month}.{day}.rc{build_or_commit}"
        elif branch_type == "release":
            version_number = f"{year}.{month}.{day}.{build_or_commit}"
        else:
            raise Exception(f"Unable to determine version number for a branch of type {branch_type} as it is not compliant with pypi's enforcement of PEP 440. See notes in source code for more details.")

    return version_number