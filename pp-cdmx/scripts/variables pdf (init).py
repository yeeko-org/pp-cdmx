# -*- coding: utf-8 -*-
from vision.get_columns import extractDataForLens

path = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'

from vision.get_columns import extractDataForLens



def execute_townhall(th , need_lens=False, is_test=True):
    from public_account.models import PPImage, PublicAccount
    from project.models import FinalProject
    if need_lens:
        extractDataForLens(path, th=th)
    public_account=PublicAccount.objects.filter(townhall__short_name=th).first()
    public_account.column_formatter(is_test)
    print print_results(th)

def print_results(th):
    from project.models import FinalProject
    print "*********************"
    print th
    won = FinalProject.objects.filter(approved__isnull=False, 
        suburb__townhall__short_name=th).count()
    no_won = FinalProject.objects.filter(approved__isnull=True,
        suburb__townhall__short_name=th).count()
    print "%s  -->logrados"%won
    print "%s  --> no logrados:"%no_won


def execute_all_townhalls():
    from geographic.models import TownHall
    for th in TownHall.objects.all():
        execute_townhall(th.short_name)

def print_all_results():
    from project.models import FinalProject
    from geographic.models import TownHall
    for th in TownHall.objects.all():
        print_results(th.short_name)
    print "*********************"
    print "RESULTADOS GLOBALES"
    print "logrados:"
    print FinalProject.objects.filter(approved__isnull=False).count()
    print "no logrados:"
    print FinalProject.objects.filter(approved__isnull=True).count()


def lens_th(th):
    execute_townhall(th, True, True)


def extract_only_pages(th, page):
    from public_account.models import PPImage, PublicAccount
    public_account=PublicAccount.objects.filter(townhall__short_name=th).first()
    public_account.column_formatter(True, page)




all_ths = ["CUH", "CUJ", "TLP", "VC", "XO", "AO", "IZT", "AZC", "TLH", "MC", "MH", "COY", "GAM", "BJ", "MIL", "IZP"]


#execute_townhall(all_ths[3])

from geographic.models import Suburb


execute_townhall('VC')


extract_only_pages("VC", 2)

lens_th('VC')
lens_th('IZT')


ref = 'FUENTES DE AZCAPOTZALCOPARQUES DE AZCAPOTZALCO (U HAB)'
con = 'FUENTES DE AZCAPOTZALCO  PARQUES DE'
sin = 'FUENTES DE AZCAPOTZALCO  PARQUES DE AZCAPOTZALCO (U HAB)'

from scripts.data_cleaner import similar
similar(ref, con)
similar(ref, sin)


def input(num):
    print "ya te recibí"
    print num


def mi_preg():
    answer = input("Escribe el ID que te interesa:") 
    if answer == 1: 
        print "Hará algo con 1"
    elif answer == 2: 
        print "Hará algo con 2"
    else: 
        print("Please enter yes or no.") 


def mi_preg2():
    answer = raw_input("Enter yes or no: ") 
    if answer == "yes": 
        print "Hará algo con yes"
    elif answer == "no": 
        print "Hará algo con no"
    else: 
        print("Please enter yes or no.") 


from geographic.models import *
from project.models import FinalProject

salinas = FinalProject.objects.filter(suburb__short_name__icontains="SALINAS", 
    suburb__townhall__short_name="AZC")

specific_text = Suburb.objects.filter(name__icontains="refiere")


Suburb.objects.filter(townhall__short_name='AZC', finalproject__image__isnull=False).count()

FinalProject.objects.filter(image__isnull=False)
FinalProject.objects.filter().update(image=None)
FinalProject.objects.filter(image__isnull=False)


Suburb.objects.filter().update(compact_name=None)

import re
from geographic.models import *

import unidecode
from public_account.models import *
from period.models import *
import numpy
from vision.get_columns import get_year_data
import json

dels = ["CUH", "CUJ", "TLP", "VC", "XO", "AO", "IZT", "AZC", "TLH", "MC", "MH", "COY", "GAM", "BJ", "MIL"]

path_image = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'


data_from_lens = get_year_data(path_image, 2018, dels[0])


data_for_tests = data_from_lens[dels[0]]


##$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\rick_\keys\googlelens.json"

from vision.get_columns import extractDataForLens
path = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'
curr_th = "AZC"
extractDataForLens(path, th=curr_th)






