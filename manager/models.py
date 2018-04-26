from django.db import models


class Query(models.Model):
    query = models.TextField(blank=False)
    date = models.DateTimeField(auto_now=True)