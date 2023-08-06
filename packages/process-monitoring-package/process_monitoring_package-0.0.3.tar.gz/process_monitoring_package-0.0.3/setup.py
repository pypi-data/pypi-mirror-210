from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

setup(
    name='process_monitoring_package',
    version='0.0.3',
    description='A package to monitor a process and send email notifications',
    long_description=LONG_DESCRIPTION, 
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="Chengran",
    license="MIT",
    install_requires=[
        'psutil',
        'requests',
        'tqdm'
    ],
)