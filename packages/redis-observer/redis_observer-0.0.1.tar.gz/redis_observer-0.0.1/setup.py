import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='redis_observer',
    version='0.0.1',
    author='Omkar Konnur',
    author_email='omkar.konnur@redis.com',
    description='Track Usage, Log events from any python script into redis streams',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Redislabs-Solution-Architects/redis-observer',
    project_urls = {
        "Bug Tracker": "https://github.com/Redislabs-Solution-Architects/redis-observer/issues"
    },
    license='MIT',
    packages=['redis_observer'],
    install_requires=['redis'],
)