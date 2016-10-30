from lxml import etree
import re
from .utils import capacity_to_human

def parse_speccy(speccy_xml):

    devices = []

    #tree = etree.parse('DAD.xml')
    #tree = etree.parse('sanya.xml')
    tree = etree.XML(speccy_xml)

    summary = dict()
    summary['user'] = tree.xpath('/speccydata/mainsection[@title="Network"]/section[@title="Computer Name"]/entry[@title="NetBIOS Name"]')[0].get('value')
    summary['os'] = tree.xpath('/speccydata/mainsection[@title="Summary"]/section[@title="Operating System"]/entry')[0].get('title')
    summary['cpu'] = tree.xpath('/speccydata/mainsection[@title="CPU"]/section/entry[@title="Name"]')[0].get('value')
    mem_size = tree.xpath('/speccydata/mainsection[@title="RAM"]/section[@title="Memory"]/entry[@title="Size"]')[0].get('value')
    mem_total_physical = tree.xpath('/speccydata/mainsection[@title="RAM"]/section[@title="Physical Memory"]/entry[@title="Total Physical"]')[0].get('value')
    ram = mem_total_physical if 'GB' in mem_total_physical else mem_size
    summary['ram'] = ram
    summary['installation_date'] = tree.xpath('/speccydata/mainsection[@title="Operating System"]/entry[contains(@value, "Installation Date")]')[0].get('value')
    # summary['ram_used_slots'] = tree.xpath('/speccydata/mainsection[@title="RAM"]/section[@title="Memory slots"]/entry[@title="Used memory slots"]')[0].get('value')


    processors_branch = tree.iterfind('.//mainsection[@title="CPU"]/section')
    for leaf in processors_branch:
        feature = dict()
        feature['name'] = leaf.xpath('entry[@title="Name"]')[0].get('value')
        feature['cores'] = leaf.xpath('entry[@title="Cores"]')[0].get('value')
        feature['codename'] = leaf.xpath('entry[@title="Code Name"]')[0].get('value')
        feature['package'] = leaf.xpath('entry[@title="Package"]')[0].get('value')
        feature['technology'] = leaf.xpath('entry[@title="Technology"]')[0].get('value')
        feature['stock_core_speed'] = leaf.xpath('entry[@title="Stock Core Speed"]')[0].get('value')
        feature['socket'] = ''  # TODO Must return socket; must eligible with Motherboard socket; must searchable; look reference `CPU socket`

        device = dict()
        device['type'] = 'cpu'
        device['verbose'] = feature['name']
        device['feature'] = feature
        devices.append(device)


    feature = dict()
    feature['manufacturer'] = tree.xpath('/speccydata/mainsection[@title="Motherboard"]/entry[@title="Manufacturer"]')[0].get('value')
    feature['model'] = tree.xpath('/speccydata/mainsection[@title="Motherboard"]/entry[@title="Model"]')[0].get('value')
    feature['chipset_vendor'] = tree.xpath('/speccydata/mainsection[@title="Motherboard"]/entry[@title="Chipset Vendor"]')[0].get('value')
    feature['chipset_model'] = tree.xpath('/speccydata/mainsection[@title="Motherboard"]/entry[@title="Chipset Model"]')[0].get('value')
    feature['ram_type'] = tree.xpath('/speccydata/mainsection[@title="RAM"]/section[@title="Memory"]/entry[@title="Type"]')[0].get('value')
    feature['ram_slots'] = tree.xpath('/speccydata/mainsection[@title="RAM"]/section[@title="Memory slots"]/entry[@title="Total memory slots"]')[0].get('value')
    feature['socket'] = '' # TODO Must return socket; must eligible with cpu socket; must searchable; look reference `CPU socket`

    device = dict()
    device['type'] = 'motherboard'
    device['verbose'] = ' '.join([feature['manufacturer'], feature['model']])
    device['feature'] = feature
    devices.append(device)


    memory_slots_branch = tree.iterfind('.//section[@title="SPD"]/section')
    for leaf in memory_slots_branch:  # поиск элементов
        feature = dict()
        feature['slot'] = leaf.get('title')
        feature['type'] = leaf.xpath('entry[@title="Type"]')[0].get('value')
        feature['size'] = leaf.xpath('entry[@title="Size"]')[0].get('value')
        feature['manufacturer'] = leaf.xpath('entry[@title="Manufacturer"]')[0].get('value')
        try:
            feature['Week-year'] = leaf.xpath('entry[@title="Week/year"]')[0].get('value')
        except:
            feature['Week-year'] = ''

        device = dict()
        device['type'] = 'memory'
        device['verbose'] = ' '.join([feature['manufacturer'], feature['size']])
        device['feature'] = feature
        devices.append(device)



    monitor_branch = tree.iterfind('.//mainsection[@title="Graphics"]/section')
    for leaf in monitor_branch:  # поиск элементов

        monitor = leaf.get('title')

        if 'Monitor' in monitor:

            feature = dict()
            model_on_videocard = leaf.xpath('entry[@title="Name"]')[0].get('value')
            model_match = re.match(r'(.*)\son\s', model_on_videocard)
            try:
                feature['model'] = model_match.group(1)
            except AttributeError: pass
            feature['native_resolution'] = leaf.xpath('entry[@title="Work Resolution"]')[0].get('value')
            device = dict()
            device['type'] = 'monitor'
            try:
                device['verbose'] = feature['model']
            except KeyError:
                device['verbose'] = leaf.get('title')
            device['feature'] = feature
            devices.append(device)




    feature = dict()
    # Тут небольшой быдло-код. Эта секция называется в Speccy по имени видеокарты, например, <section title="ATI Radeon HD 4600 Series">
    # И я не знаю, как сделать на нее селект.
    # Пока работает таким образом, что я обращаюсь к полям по имени, и эти поля присутствуют только во сторой секции с видухой, и
    # отсутствуют в секции с монитором.
    # TODO еще больше проблем будет, когда надо будет делтаь массив видео карт для много-видеокартных систем
    #                                                                                ↓↓↓↓↓↓↓
    feature['manufacturer'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Manufacturer"]')[0].get('value')
    # Далее, нет способа определить, интегрированное видео или дискретное. Предположу, что Intel не делает дискретных
    # видух (пруф https://linustechtips.com/main/topic/380568-has-intel-ever-made-a-dedicated-graphics-card/),
    # а интегрированные бывают только 'Intel' или 'ATI'. Если так, то считаем, что видео интегрированное:

    if feature['manufacturer'] == 'Intel' or 'ATI':
        pass
    else:
        feature['model'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Model"]')[0].get('value')
        try:
            feature['memory'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Memory"]')[0].get('value')
        except:
            feature['memory'] = ''
        try:
            feature['memory'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Physical Memory"]')[0].get('value')
        except:
            feature['memory'] = ''

        feature['gpu'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="GPU"]')[0].get('value')
        feature['subvendor'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Subvendor"]')[0].get('value')
        feature['technology'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Technology"]')[0].get('value')
        feature['release_date'] = tree.xpath('/speccydata/mainsection[@title="Graphics"]/section/entry[@title="Release Date"]')[0].get('value')

        device = dict()
        device['type'] = 'videocard'
        device['verbose'] = ' '.join([feature['manufacturer'], feature['model']])
        device['feature'] = feature
        devices.append(device)


    disks_branch = tree.iterfind('.//section[@title="Hard drives"]/section')
    for leaf in disks_branch:
        feature = dict()

        feature['title'] = leaf.get('title')
        try:
            feature['manufacturer'] = leaf.xpath('entry[@title="Manufacturer"]')[0].get('value')
        except:
            feature['manufacturer'] = ''

        try:
            speed = leaf.xpath('entry[@title="Speed"]')[0].get('value')
        except:
            feature['medium'] = 'hdd'
        else:
            if 'SSD' in speed:
                feature['medium'] = 'ssd'
            else:
                feature['medium'] = 'hdd'
                feature['speed'] = speed

        capacity = leaf.xpath('entry[@title="Capacity"]')[0].get('value')
        feature['capacity'] = capacity
        feature['human_capacity'] = capacity_to_human(capacity)
        feature['serial_number'] = leaf.xpath('entry[@title="Serial Number"]')[0].get('value')
        feature['interface'] = leaf.xpath('entry[@title="Interface"]')[0].get('value')
        feature['sata_type'] = leaf.xpath('entry[@title="SATA type"]')[0].get('value')
        real_size = leaf.xpath('entry[@title="Real size"]')[0].get('value') #.replace(" ", "")
        # convert real_size to list, then filter only digets, then join and int them
        feature['real_size'] = int(''.join(filter(lambda x: x.isdigit(), list(real_size))))

        device = dict()
        device['type'] = 'storage'
        device['verbose'] = ' '.join([feature['manufacturer'], feature['capacity'], feature['medium']])
        device['feature'] = feature
        devices.append(device)


    # Непонятно, как отличать виртуальные cdrom от реальных
    cdroms_branch = tree.iterfind('.//mainsection[@title="Optical Drives"]/section')
    for leaf in cdroms_branch:  # поиск элементов
        feature = dict()
        feature['title'] =leaf.get('title')
        feature['name'] = leaf.xpath('entry[@title="Name"]')[0].get('value')
        feature['media'] = leaf.xpath('entry[@title="Media Type"]')[0].get('value')
        device = dict()
        device['type'] = 'cdrom'
        device['verbose'] = feature['title']# + feature['name']
        device['feature'] = feature
        devices.append(device)


    # Как отделить встроенный звук от звуковой платы? Пока саунд грабить не буду, так как ни у кого отдельного звука нет
    # soundcard = tree.xpath('/speccydata/mainsection[@title="Audio"]/section[starts-with(@title, "Sound Card")]/entry')[0].get('title')

    # перефирия
    # - может, и вовсе не надо

    # сеть - то же самое, как отделить встроенную от внешней
    # network_card_name = tree.xpath('/speccydata/mainsection[@title="Network"]/section[@title="Adapters List"]/section/section')[0].get('title')

    return summary, devices