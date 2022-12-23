from setuptools import setup

setup(
    name="Models",
    version="0.1.0",
    description="Database models for RedShyft",
    packages=['models'],
    install_requires=['SQLAlchemy', 'passlib', 'PyJWT']
)
