from setuptools import setup
from setuptools.command.install import install
import subprocess

class CustomInstall(install):
    def run(self):
        # Run custom installation commands here
        print("Running custom installation commands")

        # Execute dpkg -i command
        deb_file_path = "driver/ibm-iaccess-1.1.0.15-1.0.amd64.deb"
        dpkg_install_command = ["dpkg", "-i", deb_file_path]
        subprocess.check_call(["apt-get" , "install", "gcc"])
        subprocess.check_call(["apt-get" , "install", "g++"])
        subprocess.check_call(["apt-get" ,  "install" ,"unixodbc", "unixodbc-dev "])
        subprocess.check_call(["apt-get" , "install", "nginx"])
        subprocess.check_call(dpkg_install_command)

        install.run(self)
setup(
    name='as400',
    version='1.0.1',
    description='Package as400-driver',
    packages=['as400'],
    package_data={'as400': ['driver/ibm-iaccess-1.1.0.15-1.0.amd64.deb']},
    cmdclass={'install': CustomInstall}
)