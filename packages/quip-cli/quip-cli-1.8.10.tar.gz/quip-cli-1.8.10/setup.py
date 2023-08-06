from setuptools import setup, find_packages
from quip import __version__
version = __version__

def main():
    with open('README.md', 'r') as readme:
        long_description = readme.read()
    setup(
        name='quip-cli',
        version=version,
        author_email="huseyin.gomleksizoglu@stonebranch.com",
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            "colorama >= 0.4.4",
            "setuptools >= 44.1.1",
            "Pillow",
            "uip-cli >= 1.3.0",
            "pyyaml",
            "python-gitlab",
            "python-jenkins",
            "keyring"
        ],
        author='Stonebranch',
        description='Tool for creating/updating new universal integrations',
        entry_points={
            'console_scripts': [
                'quip=quip.quip:run'
            ]
        },
        python_requires='>=3.7',
        classifiers=[
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python :: 3'
        ],
        long_description=long_description,
        long_description_content_type="text/markdown"
    )


if __name__ == '__main__':
    main()
