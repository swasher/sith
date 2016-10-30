import re


def capacity_to_human(capacity):

    regex = r"(\d+)\s*([a-zA-Z]+)"
    matches = re.findall(regex, capacity)[0]

    GB = 1024*1024*1024/1000/1000/1000

    if len(matches)==2:
        if matches[1] in ['GB', 'Gigabytes']:
            human_value = round(int(matches[0]) * GB)
            human_unit = 'GB'
            human = '{}{}'.format(human_value, human_unit)
        else:
            human = 'Unpredictable unit'
    else:
        human =  ''

    return human