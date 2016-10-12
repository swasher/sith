from django import forms
from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.dispatch import receiver
from django.template import Template
from django.utils.safestring import mark_safe
from mptt.models import MPTTModel, TreeForeignKey, TreeOneToOneField
from django_hstore import hstore
from django.core.exceptions import ObjectDoesNotExist
from .speccy import parse_speccy
import cloudinary
from cloudinary.models import CloudinaryField
#from cloudinary.api import resource
from .get_cpu_data import cpu_data
from .widgets import AdminCloudinaryWidget

DATATYPE_CHOICES = (
('IntegerField', 'IntegerField'),
('FloatField', 'FloatField'),
('DecimalField', 'DecimalField'),
('BooleanField', 'BooleanField'),
('CharField', 'CharField'),
('TextField', 'TextField'),
('DateField', 'DateField'),
('DateTimeField', 'DateTimeField'),
('EmailField', 'EmailField'),
('GenericIPAddressField', 'GenericIPAddressField'),
('URLField', 'URLField'),
)

KIND_CHOICES = (
    ('ORG', 'Организация'),
    ('ROOM', 'Помещение'),
    ('BOX', 'Бокс'),
    ('TBL', 'Рабочее место'),
    ('PC', 'Компьютер'),
)


class Container(MPTTModel):
    """
    Эта модель содержит древовидную структуру, в которой узлами являются помещения (или контейнеры типа шкафа) или
    компьютеры, которые, в свою очередь, являются контейнерами для комплетующих.
    """
    name = models.CharField(max_length=50, unique=True)
    kind = models.CharField(max_length=4, choices=KIND_CHOICES, null=True)
    notice = models.TextField(max_length=300, default='', blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'

    def __str__(self):
        return self.name


class Computer(Container):
    os = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=20, blank=True) # TODO может это надо сделать integer для поиска
    installation_date = models.CharField(max_length=40, blank=True, null=True) # TODO это надо сделать датой
    speccy = models.FileField(upload_to='', blank=True)

    class Meta:
        verbose_name = 'Компьютер'
        verbose_name_plural = 'Компьютеры'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.speccy._file:
            # if Component.objects.filter(container=self.pk):
            #     messages.add_message(request, messages.INFO, 'Car has been sold')
            xml = self.speccy.read()
            summary, devices = parse_speccy(xml)
            self.os = summary['os']
            self.cpu = summary['cpu']
            self.ram = summary['ram']
            self.installation_date = summary['installation_date']
            self.kind = 'PC'
            self.name = '{} on {} with {}'.format(summary['user'], self.cpu, self.ram)
            self.speccy = None
            super(Computer, self).save(*args, **kwargs)

            for device in devices:
                c = Component()
                c.name = device['verbose']
                c.container = self
                debug_var = device['type']
                c.sparetype = SpareType.objects.get(name=device['type'])
                c.data = device['feature']
                c.save()
        else:
            self.kind = 'PC'
            self.speccy = None
            super(Computer, self).save(*args, **kwargs)

    def get_ancestors_list(self):
        ancestors = self.get_ancestors()
        return '->'.join([i.name for i in ancestors])


class SpareType(models.Model):
    name = models.CharField(max_length=32, help_text='Это ключ, пишется английскими буквами, должен соответсвовать значению, возвращаемому парсером.')
    name_verbose = models.CharField(max_length=32, verbose_name='Human-like название')

    class Meta:
        verbose_name = 'Тип железа'
        verbose_name_plural = 'Тип железа'
        ordering = ['name_verbose']

    def __str__(self):
        return self.name_verbose


class Property(models.Model):
    name = models.CharField(max_length=32)
    sparetype = models.ForeignKey(SpareType)

    class Meta:
        verbose_name = 'Свойство'
        verbose_name_plural = 'Свойства'

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name


class Manufacture(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ['name']
        verbose_name = 'Вендор'
        verbose_name_plural = 'Вендоры'

    def __str__(self):
        return self.name


class Component(models.Model):

    name = models.CharField(max_length=64)
    container = TreeForeignKey(Container)
    sparetype = models.ForeignKey(SpareType)

    manufacture = models.ForeignKey(Manufacture, blank=True, null=True)  # TODO сделать автокомплит
    model = models.CharField(max_length=100, blank=True, null=True)

    purchase_date = models.DateField(blank=True, null=True)
    store = models.ForeignKey(Store, blank=True, null=True)
    warranty = models.SmallIntegerField(blank=True, null=True) # TODO гарантиый талон как отсканированный файл
    serialnumber = models.CharField(max_length=128, blank=True, null=True, verbose_name='Serial')
    description = models.TextField(blank=True)
    price_uah = models.IntegerField(help_text='Стоимость в грн', blank=True, null=True)
    price_usd = models.IntegerField(help_text='Ориентировачная стоимость в USD на момент покупки', blank=True, null=True)
    iscash = models.BooleanField(help_text='Оплачено наличными', default=False)
    invoice = models.CharField(max_length=16, help_text='Номер счета', blank=True)
    product_page = models.URLField(blank=True, help_text='url to pruduct page')

    data = hstore.DictionaryField(blank=True)  # can pass attributes like null, blank, etc.

    def load_properties(self):
        properties  = Property.objects.filter(sparetype__pk=self.sparetype_id)

        data = dict()
        for prop in properties:
            data[prop.name] = ''
        self.data=data
        self.save()

    def load_cpu_data(self):
        import sys
        if self.product_page:
            info = cpu_data(self.product_page)
            if info:
                #self.data = info
                for key, value in info.items():
                    print(sys.stderr, key)
                    self.data[key] = value
                self.save()
        else:
            pass

    class Meta:
        verbose_name = 'Комплектующие и устройства'
        verbose_name_plural = 'Комплектующие и устройства'

    def __str__(self):
        return self.name


class MyCloudinaryField(CloudinaryField):
    def upload_options(self, model_instance):
       return {'folder': 'inventory',
               'tags': [model_instance.component.name],
               'context': {'caption': model_instance.component.name, 'alt': 'место для доп. информации'}
               }


class Image(models.Model):

    component = models.ForeignKey(Component)
    picture = MyCloudinaryField('', blank=True, null=True)

    @property
    def metatag(self):
        try:
            resource = cloudinary.api.resource(self.picture.public_id)
        except cloudinary.api.NotFound:
            return {'tag':'', 'caption':'', 'alt':''}

        try:
            tag = resource['tags'][0]
        except:
            tag = ''

        try:
            alt = resource['context']['custom']['alt']
        except:
            alt = ''

        try:
            caption = resource['context']['custom']['caption']
        except:
            caption = ''

        return {'tag':tag, 'caption':caption, 'alt':alt}

    def metatag_caption(self):
        try:
            resource = cloudinary.api.resource(self.picture.public_id)
            caption = resource['context']['custom']['caption']
        except cloudinary.api.NotFound:
            caption = ''

        return caption

    def __str__(self):
        try:
            public_id = self.picture.public_id
        except AttributeError:
            public_id = ''
        return "{} with Public_id: {}".format(self.component.name, public_id)