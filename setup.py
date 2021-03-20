from setuptools import find_packages, setup


def read_file(path):
    with open(path) as f:
        return f.read()


# TODO: I would rather import this as opposed to parsing it, but when
# importing during installation it breaks due to the __init__.py file
# trying to load in other modules.
def parse_version():
    content = read_file('./baseapi/__version__.py')
    return content.split('=')[1].strip()[1:-1]


setup(
    name='baseapi',
    version=parse_version(),
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    description='Easily create maintainable API clients.',
    long_description=read_file('./README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/furious-luke/baseapi',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={'': ['*.txt', '*.js', '*.html', '*.*']},
    install_requires=[
        'requests'
    ],
    extras_require={
    },
    entry_points={
    },
    zip_safe=True
)
