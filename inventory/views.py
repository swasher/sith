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

    from itertools import chain
    todo_computers = Computer.objects.filter(notice__icontains='TODO:')
    todo_components = Component.objects.filter(description__icontains='TODO:')
    todo_items = chain(todo_computers, todo_components)

    # TODO все выводится, но неправильно формируется линк на Компьюетер - он формируется как на Компонент

    return render_to_response('grid.html', {'computers': computers,
                                            'processors': processors,
                                            'memory': memory,
                                            'storages': storages,
                                            'devices': devices,
                                            'todo': todo_items,
                                            },
                              context)