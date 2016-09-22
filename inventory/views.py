from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.dom.minidom import parse, parseString
from .speccy import parse_speccy
from .models import Component
from .models import Computer


# DEPRECATED
# def speccy(request):
#     context = RequestContext(request)
#
#     if 'speccy_xml' in request.FILES.keys():
#         file = request.FILES['speccy_xml']
#         if file.size > 500000:
#             return render_to_response('speccy.html', {'status': 'file is too big'}, context)
#         elif file.content_type != 'text/xml':
#             return render_to_response('speccy.html', {'status': 'file is not xml'}, context)
#         else:
#             xml = file.read()
#     else:
#         return render_to_response('speccy.html', {'status': 'where is file???'}, context)
#
#     computer = parse_speccy(xml)
#     computer.save()
#
#     return render_to_response('speccy.html', {'result': computer}, context)


def grid(request):
    context = RequestContext(request)

    computers = Computer.objects.all()
    processors = Component.objects.filter(sparetype__name='cpu')
    memory = Component.objects.filter(sparetype__name='memory')
    storages = Component.objects.filter(sparetype__name='storage')
    devices = Component.objects.filter(sparetype__name='')  # тут надо както выделить девайся, типа роутеры мониторы принтеры и т.д

    return render_to_response('grid.html', {'computers': computers, 'processors': processors, 'memory': memory, 'storages': storages, 'devices': devices}, context)