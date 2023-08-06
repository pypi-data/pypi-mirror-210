from setuptools import setup

setup(
    name='VBW',
    version='0.0.0a4',
    author='itrufat',
    description='A wrapper to run VBS from Python.',
    long_description='A Wrapper to run VBS from Python.',
    long_description_content_type='text/markdown',
    url='https://github.com/itruffat/VBW',
    packages=['VBW', 'VBW.VBCore', 'VBW.VBWrappers'],
    package_dir={'': 'src'},
    package_data={
        'VBW.VBCore': ['interactive_interpreter.vbs']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
