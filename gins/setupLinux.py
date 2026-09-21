import sys, subprocess, tomllib, os, site
from pathlib import Path
from shutil import rmtree, copy

try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.prompt import Confirm
except ImportError:
    print("Rich package not found. Installing it now...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "--break-system-packages"]) # SYSTEM
    from rich.console import Console
    from rich.theme import Theme

""" ALL PACKAGES SHOULD GIVE GUI OUTPUT VIA A GLOBAL CONSOLE OBJECT!!! """
custom_theme = Theme(
{"info": "bold cyan", "warning": "yellow", "danger": "bold red", "success":"bold green"}
)
cons = Console(theme=custom_theme)
def parse_gpth():
    """ GPTH to dict stuff """
    cons.log("Parsing gpth file...", style="info")
    try:
        with open("../GPTH.toml", "rb") as f:
            parsed=tomllib.load(f)
    except FileNotFoundError:
        cons.log("Can't find the GPTH.toml file. This project is incorrectly set up, please contact the author.", style="danger")
        sys.exit(1)
    except:
        cons.log("Error parsing GPTH.toml file.", style="danger")
        sys.exit(1)
    else:
        cons.log("Successfully parsed GPTH.toml file.", style="success")
        return parsed

def ginstall(package_url):
    """ Get a package from github and GINS it. Best Practice: clone the file and use `subprocess.run(["python",f"../{name_of_package}/setup.py])` to run its setup."""
    cons.log(f"Getting gins package {package_url}...",style="info")
    cons.log("Cloning package...", style="info")
    subprocess.run(["git", "clone", f"https://github.com/{package_url}", "../package"]) # SYSTEM
    cons.log("Package cloned.", style="success")
    try:
        cons.log(f"Running setup.py file for {package_url}...", style="info")
        subprocess.run([sys.executable, "../package/gins/setupLinux.py", sys.argv[1], "-I"]) # SYSTEM
    except Exception as e:
        cons.log(f"An error occurred while running the dependency's setup file that was not caught: {e}",style='danger')
        sys.exit(1)
    else:
        cons.log(f"Installed gins package {package_url}!", style="success")
def pipin(package):
    """ Install a package from Pip """
    cons.log(f"Installing {package} from Pip...", style="info")
    try:
        exit_code=subprocess.run([sys.executable, "-m", "pip", 'install', package, "--break-system-packages"]).returncode # SYSTEM
        if exit_code!=0:
            cons.log(f"Error while Pip installing {package}", style="danger")
            sys.exit(1)
        else:
            if do_we_have_it(package):
                cons.log(f'Successfully installed {package} from Pip', style='success')
            else:
                cons.log(f'Pip installed {package}, but it cannot be found.', style='danger')
                sys.exit(1)
    except Exception as e:
        cons.log(f"Exception while installing {package} from pip: {e}")
        sys.exit(1)

def fix_dependencies(deps):
    """ Run ginstall() or pipin() as per the gins. """
    cons.log("Looking up dependencies...")
    try:
        prefixes=[]
        names=[]
        for i in deps:
            prefixes.append(i.split(":")[0])
            names.append(i.split(":")[1])
        for i in range(len(deps)):
            if prefixes[i]=="pip":
                pipin(names[i])
            else:
                ginstall(names[i])
    except Exception as e:
        cons.log(f"Error while checking and installing dependencies: {e}", style="danger")
        sys.exit(1)
    else:
        cons.log("Successfully looked up and installed dependencies.", style="success")

def do_we_have_it(package):
    """ Do we have it? """
    package = package.lower().replace("-","_")
    try:
        __import__(package)
    except ImportError:
        return False
    return True

def stuff(files, pname): # THIS WHOLE FUNCTION IS SYSTEM
    """Stuffs the package"""
    cons.log("Installing package...", style="info")
    try:
        inst_path=Path.home()/f".gins/{pname}"
        inst_path.mkdir(parents=True, exist_ok=True)
        if do_we_have_it(pname):
            if Confirm.ask(f"{pname} already exists. Reinstall?" , console=cons):
                rmtree(inst_path)
                inst_path.mkdir(parents=True, exist_ok=True)
        for i in files:
            copy(f"../{i}",inst_path / i.split("/")[-1])
    except Exception as e:
        cons.log(f"An error ocurred when installing: {e}", style="danger")
        sys.exit(1)

def edit_config(files, pname):
    """Edits the .pth files"""
    spac=site.getusersitepackages()
    pathpath=os.path.join(spac,"ginspaths.pth")
    ginspath=os.path.abspath(Path.home(),".gins/")
    pacpath=os.path.join(ginspath,pname)
    mode='a' if os.path.exists(pathpath) else 'w'
    with open(pathpath, mode, encoding="utf-8") as f:
        f.write(pacpath+"\n")
    
def main():
    """Run all the functions in order using the gpth"""
    try:
        parsed=parse_gpth()
        for k in parsed.keys():
            if k=="gins":
                # We found it.
                cons.log(f'Project {parsed["gins"]["projectname"]} beginning execution...', style='info')
                fix_dependencies(parsed["gins"]["dependencies"])
                stuff(parsed["gins"]["filenames"],parsed['gins']['projectname'])
                edit_config(parsed["gins"]["filenames"],parsed['gins']['projectname'])
                cons.log(f"Succesfully installed {parsed['gins']['projectname']}", style="success")
                sys.exit()
            else:
                pass
    except Exception as e:
        cons.log(f"Uncaught error during setup execution: {e}", style="danger")
        sys.exit(1)
    # Because there is a sys.exit in the if statement, the code won't get here unless there is no gpth.
    cons.log("Can't find the [gins] header in the gpth file. This project is incorrectly set up, please contact the author.", style="danger")
    sys.exit(1)

# ifname

if __name__ == "__main__":
    main()
