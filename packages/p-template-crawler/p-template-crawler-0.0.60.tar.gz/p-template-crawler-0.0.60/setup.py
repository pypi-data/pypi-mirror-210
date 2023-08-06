import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="p-template-crawler",
    version="0.0.60",
    author="pengjun",
    author_email="mr_lonely@foxmail.com",
    description="template tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=[],
    install_requires=[
        'requests',
        'oss2',
        'Image',
        'Pillow',
        'fake_useragent',
        'lxml',
        'UserAgent',
        'urlparser',
        'p-template-generator>=0.1.62',
        'p-template-res>=0.1.28',
        'yt-dlp==2023.3.4',
    ],
    dependency_links=[],
    entry_points={
        'console_scripts':[
            'crawler = mecord_crawler.main:main'
        ]
    },
    python_requires='>=3.7',
)