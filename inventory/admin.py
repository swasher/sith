import django_hstore
from django.contrib import admin
from django.contrib.admin import widgets
from time import gmtime, strftime
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters, register
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from inventory.models import Store, Container, Computer
from inventory.models import Component
from inventory.models import SpareType
from inventory.models import Property
from inventory.models import Manufacture
from inventory.models import Image


# class ComputerProxy(Container):
#     class Meta:
#         proxy = True
#         verbose_name = "Компьютер"
#         verbose_name_plural = "Компьютеры"

class ComputerAdminInline(admin.StackedInline):
    model = Container
    fields = ['name']
    template = "admin/inventory/component/edit_inline/stacked.html"
    max_num = 1
    extra = 0
    show_change_link = True
    verbose_name = "Компьютер"
    verbose_name_plural = "Компьютеры"

    def get_queryset(self, request):
        qs = super(ComputerAdminInline, self).get_queryset(request)
        return qs.filter(kind='PC')

class ComponentAdminInline(admin.StackedInline):
    model = Component
    fields = ['name']
    template = "admin/inventory/component/edit_inline/stacked.html"
    max_num = 1
    extra = 0
    show_change_link = True
    #can_delete = True
    verbose_name = "Устройство"
    verbose_name_plural = "Устройства"

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

class ContainerMPTTAdmin(MPTTModelAdmin):
    # specify pixel amount for this ModelAdmin only:
    mptt_level_indent = 20
    #list_display = ['name', 'kind']

    def get_queryset(self, request):
        qs = super(ContainerMPTTAdmin, self).get_queryset(request)
        return qs.exclude(kind='PC')

    inlines = [ComputerAdminInline, ComponentAdminInline]

# class AllContainerTree(Container):
#     class Meta:
#         proxy = True
#
# class AllContainerTreeMPTTAdmin(MPTTModelAdmin):
#     list_display_links = ()
#     def has_add_permission(self, request):
#         return False


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


class ImagesAdminInline(admin.TabularInline):
    model = Image
    max_num = 1
    #fields = ( 'image_tag', )
    #readonly_fields = ('image_tag',)


class ComponentAdmin(admin.ModelAdmin):

    def response_change(self, request, obj):
        """
        Эта функция выполняется при нажатии на  кнопку LOAD PROPERTIES в форме редактирования комплектующего.
        Заполняет поле hstore согласно типу комплектующего.
        Если поле hstore что-то содержало, то содержимое удаляется.
        """

        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)

        def return_url():
            redirect_url = reverse('admin:%s_%s_change' %
                               (opts.app_label, opts.model_name),
                               args=(pk_value,),
                               current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        if "_load_component_properties" in request.POST:
            obj.load_properties()
            return return_url()
        elif "_load_cpu_data" in request.POST:
            obj.load_cpu_data()
            return return_url()
        else:
            return super(ComponentAdmin, self).response_change(request, obj)



    def link_to_parent_computer(self, instance):
        from django.utils.html import format_html
        ancestor = instance.container.id
        url = reverse("admin:inventory_computer_change", args=[ancestor])
        computer = instance.container.name
        return format_html("<a href='{}'>{}</a>", url, computer)

    #link_to_parent_computer.short_description = "Link to parent computer"

    list_display=['name', 'sparetype', 'container']  # это поля в виде списка
    fields = ['link_to_parent_computer', 'name', 'container', 'sparetype', 'manufacture', 'model', 'purchase_date',
              'store', 'warranty', 'serialnumber', 'description', 'price_uah', 'price_usd', 'iscash', 'invoice',
              'product_page', 'data'] # это поля для формы редактирования. Перечисление всех полей необходимо для того,
                                      # чтобы поле link_to_parent_computer было в начале списка.

    readonly_fields  = ['link_to_parent_computer']
    ordering = ['sparetype']
    inlines = [ImagesAdminInline]


#from django.contrib.admin.templatetags.admin_modify import submit_row




admin.site.site_header = 'SITH'

# admin.site.register(AllContainerTree, AllContainerTreeMPTTAdmin)
admin.site.register(Container, ContainerMPTTAdmin)
admin.site.register(Computer, ComputerMPTTAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(SpareType, SpareTypeAdmin)
admin.site.register(Store)
admin.site.register(Manufacture)
