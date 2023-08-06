# -*- coding: UTF-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcsolver",
    version="3.0.2",
    author="Liang Liu",
    author_email="liangliu@main.sdu.edu.cn",
    description="A user friendly program to do Monte Carlo sims for magnetic systems",
    long_description=long_description,
    python_requires='>=3.7',
    install_requires = ['matplotlib','numpy'],
    url="https://github.com/golddoushi/mcsolver",
    packages=["mcsolver"],
    package_data={'mcsolver': ['./*.so']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)