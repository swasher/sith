import django_hstore
from django.contrib import admin
from django.contrib.admin import widgets
from time import gmtime, strftime
from django.contrib import messages
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from inventory.models import Store, Container, Computer
from inventory.models import Component
from inventory.models import SpareType
from inventory.models import Property
from inventory.models import Manufacture


class ContainerMPTTAdmin(MPTTModelAdmin):
    # specify pixel amount for this ModelAdmin only:
    mptt_level_indent = 20
    #list_display = ['name', 'kind']

    def get_queryset(self, request):
        qs = super(ContainerMPTTAdmin, self).get_queryset(request)
        return qs.exclude(kind='PC')
    #inlines = [ComputerInline]


# class AllContainerTree(Container):
#     class Meta:
#         proxy = True
#
# class AllContainerTreeMPTTAdmin(MPTTModelAdmin):
#     list_display_links = ()
#     def has_add_permission(self, request):
#         return False


class ComponentAdminInline(admin.StackedInline):
    model = Component
    fields = ['name']
    readonly_fields = ['name']
    max_num = 1
    extra = 0
    show_change_link = True
    verbose_name = ''
    template = "admin/inventory/component/edit_inline/stacked.html"
    can_delete = True

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

class ComputerMPTTAdmin(admin.ModelAdmin):
    inlines = (ComponentAdminInline, )

    # Начальное значение для имени компьюетра, для случая, если пользователь не загружает speccy
    def get_changeform_initial_data(self, request):
        return {'name': 'New computer, added {}'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))}

    # Эта функция позволяет выводить разные наборы полей для создания и для редактирования объекта Компьютер
    def get_form(self, request, obj=None, **kwargs):
        # Proper kwargs are form, fields, exclude, formfield_callback
        if obj: # obj is not None, so this is a change page
            kwargs['exclude'] = ['kind']
        else: # obj is None, so this is an add page
            kwargs['fields'] = ['name', 'notice', 'parent', 'speccy']
        return super(ComputerMPTTAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if 'speccy' in form.changed_data and Component.objects.filter(container=obj.pk).exists():
            messages.add_message(request, messages.INFO, 'Невозможно объеденить компоненты с уже имеющимися.'
                                                         'Загрузите speccy в чистый компьютер')
            obj.speccy = None
        super(ComputerMPTTAdmin, self).save_model(request, obj, form, change)

class PropertyAdminInline(admin.TabularInline):
    model = Property

class SpareTypeAdmin(admin.ModelAdmin):
    inlines = (PropertyAdminInline, )
    #fields = ['name']

class ComponentAdmin(admin.ModelAdmin):
    #fields = ['name', 'warranty']
    #list_display_fields = ['name', 'warranty', 'description',]
    #list_editable
    pass

admin.site.site_header = 'SITH'

# admin.site.register(AllContainerTree, AllContainerTreeMPTTAdmin)
admin.site.register(Container, ContainerMPTTAdmin)
admin.site.register(Computer, ComputerMPTTAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(SpareType, SpareTypeAdmin)
admin.site.register(Store)
admin.site.register(Manufacture)
