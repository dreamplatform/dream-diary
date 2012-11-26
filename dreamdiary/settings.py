
from django.conf import settings

USE_MOCKUP_QUERIES = getattr(settings, 'DREAMDIARY_USE_MOCKUP_QUERIES')
DOMAIN = getattr(settings, 'DREAMDIARY_DOMAIN')
DESKTOP_DOMAIN = getattr(settings, 'DREAMDIARY_DESKTOP_DOMAIN')


#these will be rendered to colorpicker
COLORS = (
    '#1fb91f',
    '#148b14',
    '#65ae65',
    '#22a0e8',
    '#0075c7',
    '#7accff',
    '#ff0000',
    '#e10000',
    '#e86868',
    '#ff8400',
    '#e57700',
    '#f19e46',
    '#f600ff',
    '#c000c7',
    '#ef79f3',
    '#00efd6',
    '#00b8a5',
    '#73e4d8',
)
