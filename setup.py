from setuptools import setup

setup(name='awoxmeshlight',
        version='0.1',
        description='A package to control Awox Mesh light bulbs.',
        url='http://github.com/leiaz/python-awox-mesh-light',
        author='Laetitia Berthelot',
        author_email='leiaz@free.fr',
        license='MIT',
        packages=['awoxmeshlight'],
        classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
        ],
        install_requires=['bluepy', 'pycryptodome']
        )
