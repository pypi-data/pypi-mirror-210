from setuptools import setup

setup(
    name='prefect_postgres_sensors',
    version='0.6.0',
    author='James-Wachuka',
    author_email='jewachu26@email.com',
    description='Prefect sensors for monitoring PostgreSQL databases',
    packages=['prefect_postgres_sensors'],
    install_requires=[
        'prefect==0.15.2',
        'psycopg2-binary'
    ],
)
