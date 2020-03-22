from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    name = models.CharField('Название группы', max_length=50)
    users = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Friends(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.TextField(blank=True, null=True)
    points = models.IntegerField(default=0, blank=True)
    date_birth = models.DateField(blank=True, null=True)
    date_begin = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True, related_name='peoples')

    class Meta:
        ordering = ['date_begin']

    def __str__(self):
        return self.name


class Events(models.Model):
    event_rating = (
        (1, 'Ужасно'),
        (2, 'Плохо'),
        (3, 'Удовлетворительно'),
        (4, 'Хорошо'),
        (5, 'Отлично'),
    )
    title = models.CharField('Название события', max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField('Дата', blank=True, null=True)
    points = models.IntegerField('Оценка', default=5, choices=event_rating)
    members = models.ManyToManyField(Friends)
    report = models.TextField('Описание', blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Photos(models.Model):
    image = models.ImageField(upload_to='photos/%Y/%m/%d')
    event = models.ForeignKey(Events, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self):
        return self.image.name


class Videos(models.Model):
    video = models.FileField(upload_to='videos/%Y/%m/%d')
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    title = models.CharField('Название события', max_length=50, blank=True, null=True)

    def __str__(self):
        return self.video.name
