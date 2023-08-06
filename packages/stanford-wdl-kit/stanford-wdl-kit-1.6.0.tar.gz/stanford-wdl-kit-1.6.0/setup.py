#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'stanford-wdl-kit',
        version = '1.6.0',
        description = 'A WDL toolkit with a focus on ETL and Cloud integration',
        long_description = '# WDL-kit\n## A WDL toolkit with a focus on ETL and Cloud integration\n\nWDL-kit is a collection of dockerized utilities to simplify the creation of ETL-like workflows in the Workflow Definition Language. \n\n## Features\n\n* YAML-to-WDL\n  \n  Converts .yaml files into .wdl tasks. This is primarily a workaround for the WDL language not supporting multi-line strings, which is problematic for SQL ETL workflows. \n\n* Google Cloud\n\n  Wrappers for BigQuery, Google Cloud Storage, etc. \n\n* Slack\n\n  Wrapper for sending Slack messages\n\n* MailGun\n\n  Wrapper for sending mail via MailGun',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: 3',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: OS Independent',
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License'
        ],
        keywords = '',

        author = 'Darren Guan, Joe Mesterhazy, Tyler Tollefson, Smita Limaye, Jay Chen',
        author_email = 'dguan2@stanford.edu, jmesterh@stanford.edu, tjt8712@stanford.edu, slimaye@stanford.edu, jchen313@stanford.edu',
        maintainer = 'Research IT: Technology & Digital Solutions, Stanford Medicine',
        maintainer_email = 'rit-oss-admin@stanford.edu',

        license = 'Apache License, Version 2.0',

        url = 'https://github.com/susom/wdl-kit',
        project_urls = {},

        scripts = [],
        packages = [],
        namespace_packages = [],
        py_modules = [
            'gcp.bigquery',
            'gcp.cloudsql',
            'gcp.gcs',
            'utils.backup',
            'utils.mailer',
            'utils.slacker',
            'utils.yaml2wdl'
        ],
        entry_points = {
            'console_scripts': [
                'wbq = gcp.bigquery:main',
                'wgcs = gcp.gcs:main',
                'csql = gcp.cloudsql:main',
                'wbr = utils.backup:main',
                'yaml2wdl = utils.yaml2wdl:main',
                'slacker = utils.slacker:main',
                'mailer = utils.mailer:main'
            ]
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'miniwdl>=1.5.1',
            'pybuilder>=0.13.7',
            'google-cloud-bigquery==2.32.0',
            'google-cloud-storage==2.1.0',
            'pandas==1.3.5',
            'dataclasses-json==0.5.6',
            'pyarrow==6.0.1',
            'PyYAML==6.0',
            'slack_sdk==3.15.2',
            'boltons==21.0.0',
            'importlib_metadata',
            'bump2version==1.0.1',
            'google-api-python-client==2.63.0',
            'oauth2client==4.1.3',
            'pysftp==0.2.9',
            'aiohttp==3.8.3',
            'cryptography==39.0.2',
            'Requests==2.28.1',
            'google-auth==2.12.0',
            'pg8000==1.29.2',
            'SQLAlchemy==1.4.42',
            'cloud-sql-python-connector==0.9.0',
            'pyOpenSSL==23.0.0'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
