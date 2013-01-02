from django.db import models

# Create your models here.
class SpareType(models.Model):
    name = models.CharField(max_length=30)
    longname = models.CharField(max_length=70)
    shortname = models.CharField(max_length=30)
    iscontainer = models.BooleanField()


class Contractor(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)


class Item(models.Model):
    name = models.CharField(max_length=50)
    node = models.IntegerField()
    parentnode = models.ForeignKey('self', null=True, blank=True, related_name='children')
    iscontainer = models.BooleanField()
    type = models.ForeignKey(SpareType)

    purchase_date = models.DateField()
    purchase_contactor = models.ForeignKey(Contractor)
    purchase_warranty = models.IntegerField()
    purchase_price = models.IntegerField()
    purchase_iscash = models.BooleanField()
    purchase_invoice = models.IntegerField()

    part_manufacture = models.CharField(max_length=50)
    part_model = models.CharField(max_length=70)
    part_feature = models.CharField(max_length=2000)
    part_url = models.URLField()


    def __unicode__(self):
        return u'{0} {1} {2}'.format(self.type.shortname, self.part_manufacture, self.part_model)
