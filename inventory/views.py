from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .models import Component
from .models import Computer


@login_required()
def grid(request):
    context = RequestContext(request)

    computers = Computer.objects.all()
    processors = Component.objects.filter(sparetype__name='cpu')
    memory = Component.objects.filter(sparetype__name='memory')
    storages = Component.objects.filter(sparetype__name='storage')

    q = Component.objects.all()
    q = q.exclude(sparetype__name='cpu')
    q = q.exclude(sparetype__name='memory')
    q = q.exclude(sparetype__name='storage')
    q = q.exclude(sparetype__name='videocard')
    q = q.exclude(sparetype__name='cdrom')
    q = q.exclude(sparetype__name='motherboard')
    devices = q

    return render_to_response('grid.html', {'computers': computers, 'processors': processors, 'memory': memory, 'storages': storages, 'devices': devices}, context)