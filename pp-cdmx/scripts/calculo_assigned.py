from project.models import *
from geographic.models import *
from public_account.models import *
from django.db.models import Q, Count, Min, Max

falt_fp = FinalProject.objects.filter(
     approved__isnull=True,
     executed__isnull=False)

for proj in falt_fp:
    proj.image
    proj.suburb
    proj.suburb.townhall


for pa in PublicAccount.objects.all():
    final_projs = FinalProject.objects.filter(period_pp=pa.period_pp,
        suburb__townhall=pa.townhall, approved__isnull=False)
    print "%s - %s"%(pa.townhall, pa.period_pp)
    calcs= final_projs.aggregate(min=Min('approved'), max=Max('approved'))
    print calcs["min"]
    print calcs["max"]



">2.5%" > 102.5
"similar" 97.5 - 102.5
"<2.5%" 90 - 97.5
"<10%" 0 - 90
"not_executed" 0





