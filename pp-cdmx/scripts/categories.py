#Ejercicio

from public_account.models import PublicAccount, Row
#from project.models import  
#x=PublicAccount.objects.all().first()
x=PublicAccount.objects.filter(id=15).first()
x.column_formatter_v3()
x.calculate_match_v3()


for pa in PublicAccount.objects.all():
    pa.column_formatter_v3()
    pa.calculate_match_v3()


all_rows = Row.objects.filter(
    image__public_account=self,
    formatted_data__isnull=False)\
    .exclude(formatted_data="[]")

all_rows.count()

FinalProject.objects
            .filter(suburb__townhall=self.townhall, period_pp=self.period_pp)


from public_account.models import PPImage
PPImage.objects.filter(table_data__isnull=False).exclude(table_data="[]").count()
for image in PPImage.objects.filter(table_data__isnull=False).exclude(table_data="[]"):
    print image
    image.calculate_table_ref_columns()
    image.calculate_table_data()



from public_account.models import PPImage
PPImage.objects.filter(public_account__id=17,table_data__isnull=False).exclude(table_data="[]").count()
for image in PPImage.objects.filter(table_data__isnull=False).exclude(table_data="[]"):
    print image
    image.calculate_table_ref_columns()
    image.calculate_table_data()    





def flexibleMatchSuburb_v3(row, sub_name, final_projects):
    # from pprint import pprint
    from public_account.models import Row
    from difflib import SequenceMatcher
    # print u"----------------flexibleMatchSuburb_v3--------------------"

    max_conc = 0
    # sub_id = None
    # match_row_idx = -1
    max_fp = None
    for fp in final_projects:
        concordance = SequenceMatcher(None, fp.suburb.short_name,
                                      sub_name).ratio()
        if Row.objects.filter(final_project=fp).exists():
            concordance -= 0.001
        if concordance > 0.8 and concordance > max_conc:
            max_fp = fp
            # match_row_idx = row_idx
            # match_row_idx = row.id
            max_conc = concordance
    if max_fp:
        # match_row = orphan_rows[match_row_idx]
        # sub_id = saveFinalProjSuburb_v3(
        saveFinalProjSuburb_v3(
            max_fp.suburb.id, row, final_projects, max_conc)

from project.models import FinalProject

final_projects = 







import re
from public_account.models import Row
import unidecode


words = {}
sentences = {}
for row in Row.objects.all().values("project_name", "description"):
    project_name = row.get("project_name") or ""
    description = row.get("description") or ""
    #description = u"%s %s" % (
    #    row.get("project_name") or "", row.get("description") or "")
    try:
        pass
        description = unidecode.unidecode(description)
        description = re.sub(ur'[^a-zA-Z\s]', '', description.lower())
        project_name = unidecode.unidecode(project_name)
        project_name = re.sub(ur'[^a-zA-Z\s]', '', project_name.lower())
    except Exception as e:
        print e
    concatenate = " ".join((description, project_name))
    for word in concatenate.split(" "):
        if word in words:
            words[word] += 1
        else:
            words[word] = 1
    if description in sentences:
        sentences[description] += 1
    else:
        sentences[description] = 1
    if project_name in sentences:
        sentences[project_name] += 1
    else:
        sentences[project_name] = 1

final_words = []
final_sentences = []
for word, count in words.items():
    if count > 3 and len(word) > 3:
        final_words.append([count, word])

for sentence, count in sentences.items():
    if count > 3:
        final_sentences.append([count, sentence])

import csv
len(final_words)
len(final_sentences)
with open('final_words.csv', 'wb') as f:
    write = csv.writer(f)
    write.writerows(final_words)

with open('final_sentences.csv', 'wb') as f:
    write = csv.writer(f)
    write.writerows(final_sentences)




accented_string = u'Málaga'
# accented_string is of type 'unicode'
unaccented_string = unidecode.unidecode(accented_string)
# unaccented_string contains 'Malaga'and is of type 'str'
print unaccented_string


import re
import unidecode
description = u"Hola mundó años 987"
description = description.lower()
description = unidecode.unidecode(description)
description = re.sub(ur'[^a-zA-Z\s]', '', description.lower())
print description

