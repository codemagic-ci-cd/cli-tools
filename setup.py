from setuptools import find_packages
from setuptools import setup


def get_version():
    # TODO: implement versioning
    return '0.0.2'


setup(
    name='codemagic-cli-tools',
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
    long_description_content_type='text/markdown',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    scripts=['bin/code_signing_manager.rb'],
    python_requires=">=3.7",
    install_requires=[
        "pyopenssl>=19.0",
    ],
    entry_points={
        "console_scripts": [
            "storage = codemagic_cli_tools.storage:Storage.invoke_cli",
            "grab = codemagic_cli_tools.grab:Grab.invoke_cli",
            "keychain = codemagic_cli_tools.keychain:Keychain.invoke_cli",
            "git-changelog = codemagic_cli_tools.git_changelog:GitChangelog.invoke_cli",
            "universal-apk = codemagic_cli_tools.universal_apk_generator:UniversalApkGenerator.invoke_cli",
        ]
    },
)

