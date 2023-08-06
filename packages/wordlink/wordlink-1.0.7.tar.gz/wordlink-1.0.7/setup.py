from setuptools import setup

setup(
    name='wordlink',
    version='1.0.7',
    author='Trevor Bloomfield',
    author_email='bloomfieldtm@gmail.com',
    description='Word Link Generator',
    py_modules=['wordlink'],
    url = 'https://github.com/psibir/wordlink',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/psibir/wordlink/archive/v_01.tar.gz',    # I explain this later on
    keywords = ['word', 'link', 'html', 'console'],   # Keywords that define your package best

    install_requires=[
        'fuzzysearch',
        'prettytable'
    ],
    entry_points={
        'console_scripts': [
            'wordlink=wordlink:main'
        ]
    },
)
