from setuptools import setup

setup(
    name='vaksms',
    version='0.1',
    description='VakSms API library',
    long_description='VakSms API library for interacting with the vak-sms.com service',
    url='https://github.com/Pr0n1xGH/vaksms',
    author='PrOn1x',
    author_email='prosto.nechyvak@yahoo.com',
    license='AGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='vak-sms sms api library',
    packages=['vaksms'],
    install_requires=['requests'],
)