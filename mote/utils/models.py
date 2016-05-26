from __future__ import unicode_literals

import time

from django.db import models
from django.utils.timezone import now


# In seconds.
DEFAULT_LOCK_EXPIRY_TIME = 300


class TaskLock(models.Model):
    name = models.CharField(max_length=255, unique=True)
    creator = models.CharField(max_length=255)
    created_on = models.DateTimeField()
    expire_in = models.PositiveIntegerField()

    @staticmethod
    def _get_time_limited_bucket(timestamp, expire_time):
        seconds_to_previous_bucket = timestamp % expire_time
        return timestamp - seconds_to_previous_bucket

    @classmethod
    def acquire(cls, creator, expire=DEFAULT_LOCK_EXPIRY_TIME):
        # Convert to an int as we don't need millisecond precision.
        created_on = now()
        ts = int(time.time())
        bucket = cls._get_time_limited_bucket(ts, expire)

        name = "{creator}-{bucket}".format(
            creator=creator,
            bucket=bucket
        )
        lock, created = cls.objects.get_or_create(
            name=name,
            defaults={
                "creator": creator,
                "created_on": created_on,
                "expire_in": expire
            }
        )
        if created:
            return lock

        # We got an instance instead of creating which means this lock has
        # already been acquired elsewhere.
        return None

    def release(self):
        self.delete()
