from setuptools import setup, find_packages

setup(
    name='drf_simplemiddleware_logger',
    version='1.0',
    description='Django middleware for request/response logging',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/your-username/simplemiddleware',
    author='Jai Antony',
    author_email='jaiantony2015@gmail.com',
    packages=find_packages(),
    install_requires=[
        'Django',
        'djangorestframework',
        'djangorestframework-simplejwt'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
