from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from relationships.models import Follow
from notifications.models import Notification
from comments.models import Comment, Like as CommentLike
from posts.models import Like as PostLike


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.following,
            text=f"{instance.follower.username} started following you.",
            content_type=ContentType.objects.get_for_model(Follow),
            target_object_id=instance.follower.id
        )

        notification = Notification.objects.filter(
            user=instance.following,
            text=f"{instance.follower.username} unfollowed you.",
            content_type=ContentType.objects.get_for_model(Follow),
            target_object_id=instance.follower.id
        ).first()

        if notification:
            notification.delete()


@receiver(post_delete, sender=Follow)
def create_unfollow_notification(sender, instance, **kwargs):
    Notification.objects.create(
        user=instance.following,
        text=f"{instance.follower.username} unfollowed you.",
        content_type=ContentType.objects.get_for_model(Follow),
        target_object_id=instance.follower.id
    )

    notification = Notification.objects.filter(
        user=instance.following,
        text=f"{instance.follower.username} started following you.",
        content_type=ContentType.objects.get_for_model(Follow),
        target_object_id=instance.follower.id
    ).first()

    if notification:
        notification.delete()


@receiver(post_save, sender=PostLike)
def create_post_like_notification(sender, instance, created, **kwargs):
    notification = Notification.objects.filter(
        user=instance.post.author,
        text=f"{instance.user.username} liked your post.",
        content_type=ContentType.objects.get_for_model(PostLike),
        target_object_id=instance.post.id
    ).first()

    if created and not notification:
        Notification.objects.create(
            user=instance.post.author,
            text=f"{instance.user.username} liked your post.",
            content_type=ContentType.objects.get_for_model(PostLike),
            target_object_id=instance.post.id
        )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.author:
        Notification.objects.create(
            user=instance.post.author,
            text=f"{instance.user.username} commented on your post.",
            content_type=ContentType.objects.get_for_model(Comment),
            target_object_id=instance.post.id
        )


@receiver(post_save, sender=CommentLike)
def create_comment_like_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.comment.user:
        Notification.objects.create(
            user=instance.comment.user,
            text=f"{instance.user.username} liked your comment.",
            content_type=ContentType.objects.get_for_model(CommentLike),
            target_object_id=instance.user.id
        )


@receiver(post_delete, sender=PostLike)
def delete_unnecessary_like_notification(sender, instance, **kwargs):
    notification = Notification.objects.filter(
        user=instance.post.author,
        text=f"{instance.user.username} liked your post.",
        content_type=ContentType.objects.get_for_model(PostLike),
        target_object_id=instance.post.id
    ).first()

    if notification:
        notification.delete()


@receiver(post_delete, sender=CommentLike)
def delete_unnecessary_comment_like_notification(sender, instance, **kwargs):
    notification = Notification.objects.filter(
        user=instance.comment.user,
        text=f"{instance.user.username} liked your comment.",
        content_type=ContentType.objects.get_for_model(CommentLike),
        target_object_id=instance.user.id
    ).first()

    if notification:
        notification.delete()
