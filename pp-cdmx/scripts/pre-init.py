# -*- coding: utf-8 -*-
#Todas estas funciones son necesarias ejecutarlas antes de iniciar los ejercicios
from scripts.data_cleaner import cleanSuburbName
from geographic.models import Suburb

#Esta función estandariza los nombres de las Colonias y las guarda en el
#campo short_name, el cual nos ayudará a estandarizar nombres
def buildSuburbComparename():
    all_suburbs = Suburb.objects.all()
    for sub in all_suburbs:
        sub.short_name=cleanSuburbName(sub.name)
        sub.save()
