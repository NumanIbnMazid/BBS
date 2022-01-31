from django.db import models
from bbs.helpers import get_dynamic_fields
from bbs.utils import autoslugFromUUID


@autoslugFromUUID()
class FAQ(models.Model):
    question_title = models.CharField(
        max_length=255, verbose_name='question title'
    )
    slug = models.SlugField(unique=True, max_length=254)
    answer = models.TextField(
        blank=True, null=True, verbose_name='question answer'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )
    class Meta:
        verbose_name = ("FAQ")
        verbose_name_plural = ("FAQs")
        ordering = ["-created_at"]

    def __str__(self):
        return self.question_title

    def get_fields(self):
        return [get_dynamic_fields(field, self) for field in self.__class__._meta.fields]