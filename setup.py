from setuptools import setup, find_packages

setup(
    name="meerkatpm",
    version="1.0.0",
    description="Project manager for C/C++",
    author="Ivan Solodovnikov",
    author_email="solodovnikov.ia@phystech.edu",
    install_requires=['pydantic >=1.10.4',
                        'PyYAML >=6.0',
                        'setuptools >=44.0.0',
                        'typing-extensions >=4.4.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'mbpm = meerkatpm:main'
        ]
    },
    packages=find_packages(where='src'),
    package_dir={"":"src"},
    package_data={"":["*"]}
)