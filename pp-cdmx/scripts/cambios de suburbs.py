from geographic.models import Suburb


sin_pob = Suburb.objects.filter(pob_2010__isnull=True)
for sub in sin_pob:
    print sub.cve_col

Claves que hay que poner atención.

existían en 2014 o 2015 pero luego desaparecieron

04-057
08-054
08-055
16-020

No existían en 2010 y luego aparecieron:

03-094
12-208
13-031
16-015

