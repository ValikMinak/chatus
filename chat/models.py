from django.db import models


class Message(models.Model):
    username = models.CharField(max_length=100)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} -- {self.text[:10]}..."
