import setuptools

from pathlib import Path

import glob

# note: build this package with the following command:
# pip wheel --no-deps -w dist .

base_path = Path(__file__).parent
long_description = (base_path / 'README.md').read_text()

setuptools.setup(
    name='minecraft-monitoring-api',
    version='0.1.2',
    author='Xpos587',
    license='MIT',
    description='This is a reverse engineered API wrapper for https://monitoringminecraft.ru/, which allow you automate the process.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7',
    packages=['minecraftmonitoring'],
    # package_dir={
    #     '': 'minecraftmonitoring'
    # },
    include_package_data=True,
    # py_modules=['minecraftmonitoring'],
    install_requires=['requests'],
    url='https://github.com/Xpos587/minecraft-monitoring-api'
)