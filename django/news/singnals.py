from pyexpat import model
from unicodedata import category
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.db.models.signals import m2m_changed
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Post, Subscriber, PostCategory, Category


@receiver(m2m_changed, sender=PostCategory)
def send_email(sender, instance, model, action, **kwargs):

    if action == "post_add":

        post = Post.objects.get(pk=instance.id)
        category = PostCategory.objects.get(post=post).category
        subscrube_list = Subscriber.objects.all().filter(
            category=category).values_list('user__email', 'user__username')

        for i in subscrube_list:
            if i[0] != '':
                userEmail = [i[0]]
                userName = i[1]
                html_content = render_to_string(
                    'email_template.html',
                    {
                        'post': post,
                        'username': userName,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=f'{Post.objects.get(pk=instance.id).title}',
                    # это то же, что и message
                    body=f'{Post.objects.get(pk=instance.id).preview()}',
                    from_email='novikov.e.s@yandex.ru',
                    to=userEmail,  # это то же, что и recipients_list
                )
                msg.attach_alternative(
                    html_content, "text/html")  # добавляем html

                msg.send()  # отсылаем


@receiver(user_signed_up, dispatch_uid="some.unique.string.id.for.allauth.user_signed_up")
def user_signed_up_(request, user, **kwargs):
    send_mail(
        subject=f'Регистрация на портале.',
        message=f'Добро пожаловать {user}. Спасибо за регистрацию на портале))',
        from_email='novikov.e.s@yandex.ru',
        recipient_list=[user.email],
    )
