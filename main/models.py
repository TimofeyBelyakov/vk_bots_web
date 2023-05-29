from django.db import models
import os


class ModelFile(models.Model):
    file = models.FileField('Модель', upload_to='models/', max_length=100)
    description = models.TextField('Описание', blank=True, null=True)
    draft = models.BooleanField('Не использовать', default=False)
    datetime = models.DateTimeField('Дата', auto_now=False, auto_now_add=True)

    def __str__(self):
        return f'{os.path.basename(self.file.name)}'

    def get_filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        ordering = ['id']
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class MinMaxFile(models.Model):
    file = models.FileField('Файл', upload_to='min_max/', max_length=100,
                            help_text='Файл .csv с мин. и макс. значениями по столбцам')
    description = models.TextField('Описание', blank=True, null=True)
    datetime = models.DateTimeField('Дата', auto_now=False, auto_now_add=True)

    def __str__(self):
        return f'{os.path.basename(self.file.name)}'

    def get_filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        ordering = ['id']
        verbose_name = 'Файл с мин. и макс.'
        verbose_name_plural = 'Файлы с мин. и макс.'
