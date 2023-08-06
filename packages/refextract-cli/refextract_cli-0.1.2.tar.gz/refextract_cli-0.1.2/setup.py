from setuptools import setup

setup(
    name='refextract_cli',
    version='0.1.0',
    packages=['refextract_cli'],
    install_requires=[
        "refextract==1.1.4",
         "rich==13.3.4"],
    entry_points={
        'console_scripts': [
            'refex=refextract_cli.cli:main'
        ]
    }
)

