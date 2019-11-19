from setuptools import find_packages
from setuptools import setup


def get_version():
    # TODO: implement versioning
    return '0.0.1'


setup(
    name='codemagic',
    version=get_version(),
    url='https://github.com/codemagic-ci-cd/cli-tools',
    project_urls={
        "Documentation": "https://github.com/codemagic-ci-cd/cli-tools/README.md",
        "Code": "https://github.com/codemagic-ci-cd/cli-tools",
        "Issue tracker": "https://github.com/codemagic-ci-cd/cli-tools/issues",
    },
    license='GNU General Public License v3.0',
    description="CLI tools used in Codemagic builds",
    long_description=open('README.md').read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "pyopenssl>=19.0",
    ],
    entry_points={
        "console_scripts": [
            "cm-keychain = codemagic.keychain:main"
        ]
    },
)
