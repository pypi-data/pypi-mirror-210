from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='FCSAPIAccessSDK',
    version='1.1.1',
    packages=['FCSAPIAccess'],
    url='https://github.com/CPSuperstore/FangCloudServicesAPIAccessSDK',
    license='Apache License 2.0',
    author='CPSuperstore',
    author_email='cpsuperstoreinc@gmail.com',
    description='The SDK for project-level access to your FangCloudServices account',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/CPSuperstore/FangCloudServicesAPIAccessSDK/issues",
    },
    keywords=['FANG', 'CLOUD', 'SERVICES', 'FCS', 'SDK', 'USER', 'MANAGEMENT', 'OAUTH2', 'SECURITY'],
    install_requires=[
        "requests"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'License :: OSI Approved :: Apple Public Source License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: English'
    ]
)
