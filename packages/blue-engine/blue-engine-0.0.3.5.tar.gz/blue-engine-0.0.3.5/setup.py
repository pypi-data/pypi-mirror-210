from setuptools import setup

def readme():
    with open('readme.md') as f:
        README = f.read()
    return README


setup(
    name='blue-engine',
    version='0.0.3.5',
    description='',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/MrBlueBlobGuy/Blue-Engine',
    author='Debojyoti Ganguly',
    author_email='debojyotiganguly70@gmail.com',
    license='Zlib',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=['blueEngine'],
    include_package_data=True,
    install_requires=['pygame', 'moderngl', 'pyglm', 'numpy', 'noise', 'lupa'],
    zip_safe=False
)
    