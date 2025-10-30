"""
Library manager for installing and managing dependencies.
Based on Rokoko Studio Live's library management system.
"""

import importlib
import os
import bpy
import sys
import json
import shutil
import pkgutil
import pathlib
import platform
import ensurepip
import subprocess


class LibraryManager:
    os_name = platform.system()
    system_info = {
        "operating_system": os_name,
    }
    pip_is_updated = False

    def __init__(self, libs_main_dir: pathlib.Path):
        self.libs_main_dir = libs_main_dir
        self.libs_info_file = self.libs_main_dir / ".lib_info"

        python_ver_str = "".join([str(ver) for ver in sys.version_info[:2]])
        self.libs_dir = os.path.join(self.libs_main_dir, f"python{python_ver_str}")

        # Set python path on older Blender versions
        try:
            self.python = bpy.app.binary_path_python
        except AttributeError:
            self.python = sys.executable

        self.check_libs_info()
        self._prepare_libraries()

    # ----------------- Helpers -----------------

    @staticmethod
    def _extract_lib_name(lib: str) -> str:
        """Remove version specifiers from requirement string (e.g. 'numpy>=1.20' -> 'numpy')."""
        for sep in ["=", "<", ">", "~"]:
            lib = lib.split(sep)[0]
        return lib.strip()

    def _prepare_libraries(self):
        # Create main library directory
        os.makedirs(self.libs_main_dir, exist_ok=True)
        # Create python specific library directory
        os.makedirs(self.libs_dir, exist_ok=True)

        # Add the library path to the modules, so they can be loaded from the plugin
        if self.libs_dir not in sys.path:
            sys.path.append(self.libs_dir)

    # ----------------- Library Installation -----------------

    def reset_current_library_installation(self):
        importlib.invalidate_caches()
        if self.libs_info_file.exists():
            print("Resetting current library installation, deleting library info file.")
            self.libs_info_file.unlink()
        try:
            shutil.rmtree(self.libs_dir)
        except PermissionError as e:
            print("Could not fully delete the library directory, please close Blender and try again.")
            print("Error:", e)

    def install_libraries(self, required):
        from . import dependency_check
        
        missing_after_install = []
        missing_libs = []

        # Check which libs are missing
        for lib in required:
            lib_name = self._extract_lib_name(lib)
            import_name = dependency_check.PACKAGE_IMPORT_MAP.get(lib_name, lib_name)
            print(f"Checking if {import_name} exists: ", end='')
            if not pkgutil.find_loader(import_name):
                print(f"not found")
                missing_libs.append(lib)
            else:
                print(f"found")

        if missing_libs:
            self._update_pip()

            print("Installing missing libraries:", missing_libs)
            try:
                command = [
                    self.python, '-m', 'pip', 'install',
                    f"--target={str(self.libs_dir)}", *missing_libs
                ]
                subprocess.check_call(command, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print("PIP Error:", e)
                print("Installing libraries failed.")
                if self.os_name != "Windows":
                    print("Retrying with sudo..")
                    command = ["sudo", self.python, '-m', 'pip', 'install',
                               f"--target={str(self.libs_dir)}", *missing_libs]
                    subprocess.call(command, stdout=subprocess.DEVNULL)
            finally:
                print('\033[39m')  # reset console color
            
            # Invalidate caches so Python can find the new modules
            importlib.invalidate_caches()

            # Verify installation (use import names, not package names)
            missing_after_install = []
            for lib in required:
                lib_name = self._extract_lib_name(lib)
                import_name = dependency_check.PACKAGE_IMPORT_MAP.get(lib_name, lib_name)
                if not pkgutil.find_loader(import_name):
                    missing_after_install.append(lib)
            
            installed_libs = [lib for lib in missing_libs if lib not in missing_after_install]

            if missing_after_install:
                print("WARNING: Could not install the following libraries:", missing_after_install)
            if installed_libs:
                print("Successfully installed missing libraries:", installed_libs)

        print("Finished installing libraries")
        self.create_libs_info()
        return missing_after_install

    # ----------------- Library Info Handling -----------------

    def check_libs_info(self):
        if not os.path.isdir(self.libs_dir):
            return

        if not os.path.isfile(self.libs_info_file):
            print("Library info is missing, deleting library folder.")
            shutil.rmtree(self.libs_main_dir)
            return

        current_data = self.system_info
        with open(self.libs_info_file, 'r', encoding="utf8") as file:
            loaded_data = json.load(file)

        for key, val_current in current_data.items():
            val_loaded = loaded_data.get(key)
            if val_loaded != val_current:
                print("Current info:", current_data)
                print("Loaded info: ", loaded_data)
                print("Library info is not matching, deleting library folder.")
                shutil.rmtree(self.libs_main_dir)
                return

    def create_libs_info(self):
        if not os.path.isdir(self.libs_dir) or os.path.isfile(self.libs_info_file):
            return
        with open(self.libs_info_file, 'w', encoding="utf8") as file:
            json.dump(self.system_info, file)

    # ----------------- Pip Handling -----------------

    def _update_pip(self):
        if self.pip_is_updated:
            return

        print("Ensuring pip")
        try:
            ensurepip.bootstrap()
        except Exception as e:
            print("Ensuring pip failed:", e)

        print("Updating pip")
        try:
            subprocess.check_call([self.python, "-m", "pip", "install", "--upgrade", "pip"])
        except subprocess.CalledProcessError as e:
            print("PIP Error:", e)
            print("Updating pip failed.")
            if self.os_name != "Windows":
                print("Retrying with sudo..")
                subprocess.call(["sudo", self.python, "-m", "pip", "install", "--upgrade", "pip"])
        finally:
            print('\033[39m')

        self.pip_is_updated = True


# Setup library path in the Blender addons directory and start library manager
main_dir = pathlib.Path(os.path.dirname(__file__)).parent
libs_dir = main_dir / "Mocap Libraries"
lib_manager = LibraryManager(libs_dir)
