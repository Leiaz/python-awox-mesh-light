from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='awoxmeshlight',
        version='0.1.0',
        description='A package to control Awox Mesh light bulbs.',
        long_description = long_description,
        long_description_content_type="text/markdown",
        url='http://github.com/leiaz/python-awox-mesh-light',
        author='Laetitia Berthelot',
        author_email='leiaz@mailbox.org',
        license='MIT',
        packages=['awoxmeshlight'],
        classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7'
        ],
        install_requires=['bluepy', 'pycryptodome']
        )
