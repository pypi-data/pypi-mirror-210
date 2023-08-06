from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='authpy',
    version='2.1.1',
    description='Authentication system in Python made easy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='TheUnkownHacker',
    author_email='jhamb.aarav@gmail.com',
    packages=['authpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
