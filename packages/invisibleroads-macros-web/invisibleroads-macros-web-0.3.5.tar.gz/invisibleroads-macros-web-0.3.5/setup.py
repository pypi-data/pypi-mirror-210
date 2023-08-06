from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = '''
'''
APP_REQUIREMENTS = [
    'invisibleroads-macros-disk>=1.3.0',
    'invisibleroads-macros-process>=0.2.0'],
JINJA_REQUIREMENTS = ['jinja2']
MARKDOWN_REQUIREMENTS = ['markdown2[all]']
STARLETTE_REQUIREMENTS = ['starlette']
TEST_REQUIREMENTS = ['pytest', 'pytest-cov']
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, _)).read().strip() for _ in [
    'README.md', 'CHANGES.md'])


setup(
    name='invisibleroads-macros-web',
    version='0.3.5',
    description='Shortcut functions for web operations',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url=(
        'https://github.com/invisibleroads/'
        'invisibleroads-macros-web'),
    keywords='invisibleroads',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=APP_REQUIREMENTS,
    extras_require={
        'jinja': JINJA_REQUIREMENTS,
        'markdown': MARKDOWN_REQUIREMENTS,
        'starlette': STARLETTE_REQUIREMENTS,
        'test': TEST_REQUIREMENTS},
    entry_points=ENTRY_POINTS)
