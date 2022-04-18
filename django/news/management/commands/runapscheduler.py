import logging

from django.conf import settings
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from news.models import Post, Subscriber, Category

logger = logging.getLogger(__name__)


def my_job():
    datestart = datetime.now() - timedelta(days=7)
    categories = Category.objects.all()

    for category in categories:
        posts = Post.objects.filter(
            creationDate__range=[datestart, datetime.now()], category=category)

        if posts:
            print(posts, datestart)

            subscrube_list = Subscriber.objects.all().filter(
                category=category).values_list('user__email', 'user__username')

            for i in subscrube_list:
                if i[0] != '':
                    userEmail = [i[0]]
                    userName = i[1]
                    html_content = render_to_string(
                        'weeklyNewsletter_template.html',
                        {
                            'posts': posts,
                            'username': userName,
                            'category': category.categoryName,
                        }
                    )

                    msg = EmailMultiAlternatives(
                        subject='Еженедельная рассылка',
                        # это то же, что и message
                        body='',
                        from_email='novikov.e.s@yandex.ru',
                        to=userEmail,  # это то же, что и recipients_list
                    )
                    msg.attach_alternative(
                        html_content, "text/html")  # добавляем html

                    msg.send()  # отсылаем


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day="*/7"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
