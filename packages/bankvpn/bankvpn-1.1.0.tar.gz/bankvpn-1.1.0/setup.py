import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bankvpn",
    version="1.1.0",
    author="jiagui.lin",
    author_email="jiagui.lin@shopee.com",
    description="A Tool to connect vpn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts': [
            'bankvpn = bankvpn.bke_vpn:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'certifi==2023.5.7',
        'charset-normalizer==3.1.0',
        'click==8.1.3',
        'idna==3.4',
        'importlib-metadata==6.6.0',
        'jaraco.classes==3.2.3',
        'Jinja2==3.1.2',
        'keyring==23.13.1',
        'MarkupSafe==2.1.2',
        'more-itertools==9.1.0',
        'pexpect==4.8.0',
        'ptyprocess==0.7.0',
        'PyYAML==6.0',
        'requests==2.31.0',
        'urllib3==2.0.2',
        'zipp==3.15.0'
    ],
)