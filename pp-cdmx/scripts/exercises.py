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

def print_results(th):
    from project.models import FinalProject
    print "*********************"
    print th
    won = FinalProject.objects.filter(inserted_data=True, 
        suburb__townhall__short_name=th).count()
    no_won = FinalProject.objects.filter(inserted_data=False,
        suburb__townhall__short_name=th).count()
    won_sub = FinalProject.objects.filter(image__isnull=False, 
        suburb__townhall__short_name=th).count()
    no_won_sub = FinalProject.objects.filter(image__isnull=True,
        suburb__townhall__short_name=th).count()
    print "%s  --> logrados"%won
    print "%s  --> no logrados:"%no_won
    print "%s  --> con suburb"%won_sub
    print "%s  --> sin suburb:"%no_won_sub


def execute_all_townhalls(reset_images=False):
    from geographic.models import TownHall
    for th in TownHall.objects.all():
        execute_townhall(th.short_name, False, reset_images)

def print_all_results():
    from project.models import FinalProject
    from geographic.models import TownHall
    for th in TownHall.objects.all():
        print_results(th.short_name)
    print "*********************"
    print "RESULTADOS GLOBALES"
    print "logrados:"
    print FinalProject.objects.filter(inserted_data=True).count()
    print "no logrados:"
    print FinalProject.objects.filter(inserted_data=False).count()


def lens_th(th):
    execute_townhall(th, True, True)


def extract_only_pages(th, page_number):
    from public_account.models import PPImage, PublicAccount
    public_account=PublicAccount.objects.filter(townhall__short_name=th).first()
    public_account.column_formatter(False, page_number)
