from django.db import models
from django.utils.six import python_2_unicode_compatible
# Create your models here.


@python_2_unicode_compatible
class Comment(models.Model):
    email = models.EmailField(max_length=255)
    text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:20]
