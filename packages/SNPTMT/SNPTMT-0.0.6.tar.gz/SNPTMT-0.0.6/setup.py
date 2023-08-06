from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

version = '0.0.6'

setup(
    name='SNPTMT',
    version=version,

    author='FIvER4IK',
    author_email='andrewshatalov3@gmail.com',

    description='Python module for searching for a new popular topics in the message threade',
                 
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='https://github.com/FIvER4IK/snptmt',
    
    download_url=''.format(
        version
    ),

    packages=find_packages(),  # make sure to call find_packages() with parentheses
    
    classifiers=[
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
    ],
    keywords='clusters clustering short text search new popular topics message thread',
    python_requires='>=3.4'
)




































