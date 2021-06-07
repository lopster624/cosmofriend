import re
from urllib.request import urlopen
from PIL import Image, ImageOps
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models


class Friend(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.TextField(blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    date_begin = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Friend, self).save(*args, **kwargs)
        if not self.photo:
            return

        image = Image.open(self.photo.path)
        filename = image.filename
        cropped_image = ImageOps.fit(image, (400, 400), Image.ANTIALIAS)
        try:
            exif = image.info['exif']
            cropped_image.save(filename, quality=40, exif=exif, optimize=True)
        except KeyError:
            cropped_image.save(filename, quality=40, optimize=True)

    def get_remote_image(self, id_user, url):
        img_temp = NamedTemporaryFile()
        img_temp.write(urlopen(url).read())
        img_temp.flush()
        ras = re.search(r'(.jpg|.png|.jpeg|.svg)', str(url).lower())
        self.photo.save(f'{id_user} user picture{ras.group(1)}', File(img_temp))
        self.save()

    class Meta:
        ordering = ['date_begin']

    def __str__(self):
        return self.name


class Event(models.Model):
    class Rating(models.IntegerChoices):
        TERRIBLE = 1, 'Ужасно'
        BAD = 2, 'Плохо'
        NORMAL = 3, 'Удовлетворительно'
        GOOD = 4, 'Хорошо'
        AWESOME = 5, 'Отлично'

    title = models.CharField('Название события', max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField('Дата', blank=True, null=True)
    points = models.IntegerField('Оценка', default=Rating.AWESOME, blank=True, choices=Rating.choices)
    members = models.ManyToManyField(Friend)
    report = models.TextField('Описание', blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Photo(models.Model):
    image = models.ImageField(upload_to='photos/%Y/%m/%d')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
        image = Image.open(self.image.path)
        try:
            exif = image.info['exif']
            image.save(image.filename, quality=40, exif=exif, optimize=True)
        except KeyError:
            image.save(image.filename, quality=40, optimize=True)

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self):
        return self.image.name


class Video(models.Model):
    video = models.FileField(upload_to='videos/%Y/%m/%d')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField('Название видео', max_length=50, blank=True, null=True)

    def __str__(self):
        return self.video.name


class ShareLink(models.Model):
    token = models.CharField('Идентификатор', max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_of_die = models.DateTimeField()
