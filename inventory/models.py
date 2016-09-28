from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import HStoreField
from mptt.models import MPTTModel, TreeForeignKey, TreeOneToOneField
from django_hstore import hstore
from django.core.exceptions import ObjectDoesNotExist
from .speccy import parse_speccy

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

    # для чего это было в примере в офф мануале?
    # objects = hstore.HStoreManager()

    # DEPRECATED
    # TODO Может сделать отдельную кнопку, типа сгенерить нужные поля?
    # Функция рабочая, но мешает загрузку данных из speccy, так как оверрайдит save
    # def save(self, *args, **kwargs):
    #     """
    #     Эта функция заполняет hstore пустыми полями в соответствии с введенным типом Компонента.
    #     Поля берутся из таблицы SpareType
    #     """
    #     try:
    #         # check if this Part already exist and just edited, or it newly created
    #         _ = Component.objects.get(id=self.id)
    #     except ObjectDoesNotExist:
    #         # if raise exception, it means that record is newly created,
    #         # - and now is time to create properties
    #         if getattr(self, 'unit_type', True):
    #             # получаем тип юнита self.description = self.unit_type.name
    #             # получаем объект kind = Kind.objects.get(id=self.id)
    #             # получаем объект property  = Property.objects.get(kind=self.id)
    #             properties  = Property.objects.filter(sparetype__pk=self.unit_type_id)
    #
    #             data = dict()
    #             for prop in properties:
    #                 data[prop.name] = ''
    #             self.data = data
    #     else:
    #         # TODO как быть, если юзер хочет сменить ТИП юнита?
    #         # Можно либо ДОБАВИТЬ новые поля поля, создав кашу,
    #         # либо стереть старые поля вместе с данными и добавить новые поля
    #         pass
    #     super(Component, self).save(*args, **kwargs)

    # DEPRECATED
    # def load_properties(self, *args, **kwargs):
    #     """
    #       Эта функция заменяет метод save модели, сохраняя поля Комплектующего, которые заполнил пользователь,
    #       затем стирет все текущие поля и их значения hstore и создает новые, согласно Типу Комплектующего
    #       из таблицы SpareType
    #     """
    #     if getattr(self, 'unit_type', True):
    #         # получаем тип юнита self.description = self.unit_type.name
    #         # получаем объект kind = Kind.objects.get(id=self.id)
    #         # получаем объект property  = Property.objects.get(kind=self.id)
    #         properties  = Property.objects.filter(sparetype__pk=self.unit_type_id)
    #
    #         data = dict()
    #         for prop in properties:
    #             data[prop.name] = ''
    #         self.data = data
    #     super(Component, self).save(*args, **kwargs)


    class Meta:
        verbose_name = 'Комплектующие и устройства'
        verbose_name_plural = 'Комплектующие и устройства'

    def __str__(self):
        return self.name



