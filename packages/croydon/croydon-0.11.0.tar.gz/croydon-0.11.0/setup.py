from setuptools import setup, find_packages


setup(
    name="croydon",
    version="0.11.0",
    description="a micro webframework based on fastapi and motor",
    url="https://gitlab.com/viert/croydon",
    author="Pavel Vorobyov",
    author_email="aquavitale@yandex.ru",
    license="MIT",
    packages=[pkg for pkg in find_packages() if pkg.startswith("croydon")],
    include_package_data=True,
    package_data={"croydon": ["*.txt", "*.py", "*.tmpl"]},
    python_requires=">=3.11",
    install_requires=[
        "fastapi[all]",
        "uvicorn",
        "pymongo",
        "motor",
        "mongomock-motor",
        "aiomcache",
        "pydantic",
        "ipython",
        "requests",
        "bcrypt",
        "deprecation"
    ],
    entry_points={"console_scripts": ["croydon=croydon.command:main"]},
)
