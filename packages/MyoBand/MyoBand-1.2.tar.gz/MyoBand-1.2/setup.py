from setuptools import setup, find_packages

setup(
    name='MyoBand',
    packages=find_packages(),
    version='1.2',
    url='https://github.com/hjsheehy/MyoBand',
    author="Henry Joseph Sheehy",
    author_email='henryjsheehy@gmail.com',
    license=open('LICENSE').read(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['numpy','scipy','matplotlib','mycolorpy','shapely','skikit-image'],
)
