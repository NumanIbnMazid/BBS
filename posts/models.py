from django.db import models
from bbs.helpers import get_dynamic_fields
from bbs.utils import (
    unique_slug_generator
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save


""" 
-------------------------------------------------------------------
                            ** Thread ***
-------------------------------------------------------------------
"""

class Thread(models.Model):
    title = models.CharField(
        max_length=254, unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    weight = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name="thread weight"
    )
    description = models.TextField(
        blank=True, null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("Thread")
        verbose_name_plural = ("Threads")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_fields(self):
        return [get_dynamic_fields(field, self) for field in self.__class__._meta.fields]


# # -------------------------------------------------------------------
# #                             Post
# # -------------------------------------------------------------------

class Post(models.Model):
    title = models.CharField(
        max_length=255
    )
    slug = models.SlugField(
        unique=True
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="post_users"
    )
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="post_threads"
    )
    weight = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name="post weight"
    )
    description = models.TextField(
        blank=True, null=True
    )
    allowed_users = models.ManyToManyField(
        get_user_model(), related_name='allowed_users', null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("Post")
        verbose_name_plural = ("Posts")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'post':
                return (field.name, self.post.title, field.get_internal_type())
            elif field.name == 'user':
                return (field.name, self.user, field.get_internal_type())
            elif field.name == 'thread':
                return (field.name, self.thread, field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())

        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]


# # -------------------------------------------------------------------
# #                           Post Comment
# # -------------------------------------------------------------------

class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_comments', verbose_name='post'
    )
    commented_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_comment', verbose_name='commented by'
    )
    comment = models.TextField(
        blank=True, null=True, verbose_name='comment'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-updated_at']

    def __str__(self):
        return str(self.comment) if len(str(self.comment)) <= 10 else str(self.comment)[:10] + " ..."

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'post':
                return (field.name, self.post.title)
            elif field.name == 'commented_by':
                return (field.name, self.commented_by.username, field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]


# # -------------------------------------------------------------------
# #                           Post CommentReply
# # -------------------------------------------------------------------

class CommentReply(models.Model):
    comment = models.ForeignKey(
            Comment, on_delete=models.CASCADE, related_name='comment_replies', verbose_name='comment'
    )
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_comment_replys', verbose_name='replied by'
    )
    reply = models.TextField(
        blank=True, null=True, verbose_name='reply'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = 'Comment Reply'
        verbose_name_plural = 'Comment Replies'
        ordering = ['-updated_at']

    def __str__(self):
        return str(self.reply) if len(str(self.reply)) <= 10 else str(self.reply)[:10] + " ..."

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'post':
                return (field.name, self.post.title, field.get_internal_type())
            elif field.name == 'replied_by':
                return (field.name, self.replied_by.username, field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]


# # -------------------------------------------------------------------
# #                  Pre-Save Post-Save Configurations
# # -------------------------------------------------------------------


# # Thread

def thread_slug_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance=instance, field=instance.title)


pre_save.connect(thread_slug_pre_save_receiver, sender=Thread)



# # Post

def thread_slug_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance=instance, field=instance.title)


pre_save.connect(thread_slug_pre_save_receiver, sender=Post)