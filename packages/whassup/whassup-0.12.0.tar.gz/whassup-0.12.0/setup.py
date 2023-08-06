import setuptools

setuptools.setup(
    name="whassup",
    version="0.12.0",
    description="Minimalist health-check for stayinalive",
    long_description="TODO",
    long_description_content_type="text/markdown",
    author="Thomas JOUANNOT",
    author_email="mazerty@gmail.com",
    url="https://zebr0.io/projects/whassup",
    download_url="https://gitlab.com/zebr0/whassup",
    packages=["whassup"],
    scripts=["scripts/whassup"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: System"
    ],
    license="MIT",
    install_requires=[
        "requests"
    ]
)
