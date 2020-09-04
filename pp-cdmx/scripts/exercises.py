# -*- coding: utf-8 -*-
from vision.get_columns import extractDataForLens

path = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'

from vision.get_columns import extractDataForLens



def execute_townhall(th , need_lens=False, reset_images=False):
    from public_account.models import PPImage, PublicAccount
    from project.models import FinalProject
    if need_lens:
        extractDataForLens(path, th=th)
    public_account=PublicAccount.objects.filter(townhall__short_name=th).first()
    public_account.column_formatter(need_lens or reset_images)
    print print_results(th)

def print_results(th=None):
    from project.models import FinalProject
    print "*********************"
    print th or 'RESULTADOS GLOBALES'
    won = FinalProject.objects.filter(inserted_data=True) 
    no_won = FinalProject.objects.filter(inserted_data=False)
    won_sub = FinalProject.objects.filter(image__isnull=False) 
    no_won_sub = FinalProject.objects.filter(image__isnull=True)
    if th:
        won.filter(suburb__townhall__short_name=th)
        no_won.filter(suburb__townhall__short_name=th)
        won_sub.filter(suburb__townhall__short_name=th)
        no_won_sub.filter(suburb__townhall__short_name=th)
    print "%s  --> logrados"%won.count()
    print "%s  --> no logrados"%no_won.count()
    print "%s  --> con suburb"%won_sub.count()
    print "%s  --> sin suburb"%no_won_sub.count()


def execute_all_townhalls(reset_images=False):
    from geographic.models import TownHall
    for th in TownHall.objects.all():
        execute_townhall(th.short_name, False, reset_images)

def print_all_results():
    from project.models import FinalProject
    from geographic.models import TownHall
    for th in TownHall.objects.all():
        print_results(th.short_name)
    print_results()

def lens_th(th):
    execute_townhall(th, True, True)


def extract_only_pages(th, page_number):
    from public_account.models import PPImage, PublicAccount
    public_account=PublicAccount.objects.filter(townhall__short_name=th).first()
    public_account.column_formatter(False, page_number)
