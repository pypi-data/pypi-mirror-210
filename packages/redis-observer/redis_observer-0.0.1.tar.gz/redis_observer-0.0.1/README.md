# Track your python file usage!
Python package to track the usage of any python script / generate events and send them to a redis stream.

# Sample usage in your script

```python

from redis_observer.logstream import logstream
import os

logstream(
    redis_host='redis-15205.c266.us-east-1-3.ec2.cloud.redislabs.com',
    redis_port=15205,
    redis_username='default',
    redis_password='omkarkonnur',
    appname='mycoolscript',
    maxlength=100,
    # Custom parameters
    filename=os.path.basename(__file__),
    email='omkar.konnur@redis.com'
)

```