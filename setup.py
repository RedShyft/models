from setuptools import setup

setup(
    name="Database models",
    version="0.0.1",
    description="Database models for RedShyft",
    packages=['models'],
    install_requires=['SQLAlchemy', 'passlib', 'PyJWT']
)
