import pathlib

from setuptools import find_packages
from setuptools import setup

package_meta = {}
exec(pathlib.Path('src/codemagic/__version__.py').read_text(), package_meta)

setup(
    name=package_meta['__title__'],
    version=package_meta['__version__'],
    description=package_meta['__description__'],
    url=package_meta['__url__'],
    project_urls={
        'Documentation': 'https://github.com/codemagic-ci-cd/cli-tools/blob/master/README.md',
        'Code': 'https://github.com/codemagic-ci-cd/cli-tools',
        'Issue tracker': 'https://github.com/codemagic-ci-cd/cli-tools/issues',
    },
    license=package_meta['__licence__'],
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    scripts=['bin/code_signing_manager.rb'],
    python_requires='>=3.7',
    install_requires=[
        'cryptography>=3.3',
        'google-api-python-client>=1.7.12,<2',
        'httplib2>=0.19.0',
        'oauth2client>=4.1.3',
        'PyJWT>=2.0.0,<3',
        'pyopenssl>=19.0',
        'requests>=2.25.1',
    ],
    extras_require={
        'dev': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'app-store-connect = codemagic.tools:AppStoreConnect.invoke_cli',
            'android-app-bundle = codemagic.tools:AndroidAppBundle.invoke_cli',
            'codemagic-cli-tools = codemagic.tools:CodemagicCliTools.invoke_cli',
            'git-changelog = codemagic.tools:GitChangelog.invoke_cli',
            'google-play = codemagic.tools:GooglePlay.invoke_cli',
            'keychain = codemagic.tools:Keychain.invoke_cli',
            'universal-apk = codemagic.tools:UniversalApkGenerator.invoke_cli',
            'xcode-project = codemagic.tools:XcodeProject.invoke_cli',
        ],
    },
)
