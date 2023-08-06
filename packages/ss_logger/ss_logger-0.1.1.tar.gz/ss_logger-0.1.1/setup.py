from setuptools import setup, find_packages

setup(
    name='ss_logger',
    version='0.1.1',
    author='amitskidrow',
    author_email='amitskidrow@gmail.com',
    description='Custom Logger For My Tele Application',
    packages=find_packages(),
    install_requires=[
        'snakecase',
    ]
)
