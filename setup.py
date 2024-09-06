from setuptools import setup, find_packages

setup(
    name='signalfixer',
    version='0.1.0',
    description='Timestamp treatment, time-shift finder and more.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BernatNicolau/signalfixer',
    author='Bernat Nicolau',
    author_email='bernatnicolaujorda@gmail.com',
    license='MIT',
    install_requires=['pandas'],
    extras_require={
        'dev': [
            'pytest',
            'sphinx',

        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',

)
