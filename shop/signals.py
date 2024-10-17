# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PostComments
from django.core.mail import send_mail


@receiver(post_save, sender=PostComments)
def notify_user_on_comment(sender, instance, created, **kwargs):
    if created:
        # Notify the post author
        post_author = instance.post.author
        comment_author = instance.author
        post_title = instance.post.title

        subject = f"New comment on your post: {instance.post.title}"
        message = f"""
                Hello {post_author.username},\n\n
                {comment_author.username} has commented on your post '{post_title}'.\n\n'
                Comment: {instance.text}\n\n
                View your post: http://localhost:8000/blog/post/{instance.post.slug}/
            """

        send_mail(
            subject,
            message,
            "noreply@example.com",
            [post_author.email],
            fail_silently=False,
        )
