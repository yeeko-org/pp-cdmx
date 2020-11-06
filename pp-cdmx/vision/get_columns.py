# -*- coding: utf-8 -*-
"""
referencias de google Vision con python
https://cloud.google.com/vision/docs/
    libraries?hl=es-419#client-libraries-install-python
https://googleapis.dev/python/vision/latest/index.html
"""


def block_fy(e):
    return e['fy']


def block_fx(e):
    return e['fx']


def get_vertices(vertices):
    data = []
    for vertice in vertices:
        data.append({
            "x": vertice.x,
            "y": vertice.y
        })
    return data


def get_data_order(path_file):
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()
    with io.open(path_file, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.document_text_detection(image=image)
    blocks = []
    # indice de primera columna
    try:
        page = response.full_text_annotation.pages[0]
    except Exception as e:
        print e
        print "programado solo para pagina por pagina"
        return
    # estimado de la primera columna
    index_fc = page.width / 8
    for block in page.blocks:
        total_text = []
        data_paragraphs = []
        for paragraph in block.paragraphs:
            data_words = []
            for word in paragraph.words:
                word_symbols = []
                symbols_data = []
                detected_break = False
                for symbol in word.symbols:
                    word_symbols.append(symbol.text)

                    symbol_data = {
                        "text": symbol.text,
                        "confidence": symbol.confidence,
                        "vertices": get_vertices(symbol.bounding_box.vertices)
                    }

                    """
                    tipo de quiebre de una palabra
                    http://googleapis.github.io/googleapis/java/
                        grpc-google-cloud-vision-v1/0.1.5/apidocs/
                        com/google/cloud/vision/v1/
                        TextAnnotation.DetectedBreak.BreakType.html
                    UNKNOWN = 0;
                    SPACE = 1;
                    SURE_SPACE = 2;
                    EOL_SURE_SPACE = 3;
                    HYPHEN = 4;
                    LINE_BREAK = 5;
                    """
                    detected_break = symbol.property.detected_break.type
                    if detected_break in [3, 4, 5]:
                        word_symbols.append(u"\n")
                        symbol_data["detected_break"] = detected_break
                    symbols_data.append(symbol_data)
                word_text = u''.join(word_symbols)
                data_words.append({
                    "symbols": symbols_data,
                    "vertices": get_vertices(word.bounding_box.vertices),
                    "word": word_text,
                    "detected_break": detected_break
                })
                try:
                    total_text.append(word_text)
                except Exception as e:
                    pass
            data_paragraphs.append({
                "words": data_words,
                "vertices": get_vertices(paragraph.bounding_box.vertices)
            })
        vertices = get_vertices(block.bounding_box.vertices)
        blocks.append(
            {
                "block": {
                    "paragraphs": data_paragraphs,
                    "vertices": vertices
                },
                "total_text": total_text,
                "vertices": vertices,
                "w": u" ".join(total_text),
                "fx": vertices[0].get("x", 0),
                "fy": vertices[0].get("y", 0)
            })
    blocks.sort(key=block_fx)
    return blocks


def get_words_list(data_order):
    words_list = []
    for block in data_order:
        paragraphs = block.get("block", {}).get("paragraphs", [])
        for paragraph in paragraphs:
            words = paragraph.get("words", [])
            for word in words:
                words_list.append({
                    "vertices": word.get("vertices"),
                    "word": word.get("word"),
                    "detected_break": word.get("detected_break"),
                })
    return words_list


def greater_to_left_column(ordern_blocks, var_px=40, rectification=True):
    if not ordern_blocks:
        return []
    first_block = ordern_blocks[0]
    fxa = first_block.get("vertices")[0].get("x", 0)
    fxb = first_block.get("vertices")[1].get("x", 0)
    fxc = (fxa + fxb) / 2
    columns = []
    index = 0
    # for block in ordern_blocks:
    while not index >= len(ordern_blocks):
        block = ordern_blocks[index]
        vertices = block.get("vertices")
        xa = vertices[0].get("x", 0)
        xb = vertices[1].get("x", 0)
        xc = (xa + xb) / 2
        left_line = (xa > (fxa - var_px) and xa < (fxa + var_px))
        right_line = (xb > (fxb - var_px) and xb < (fxb + var_px))
        center_line = (xc > (fxc - var_px) and xc < (fxc + var_px))
        if left_line or right_line or center_line:
            column = ordern_blocks.pop(index)
            columns.append(column)
        else:
            index += 1
    columns.sort(key=block_fy)
    return columns


def precision_graph(data):
    for column in data:
        print["o" if b else " " for b in column]


def info_data(data):
    for column in data:
        print[b.get("w") for b in column]


def test_all_files(mypath, print_test=True):
    from os import listdir
    from os.path import isfile, join
    pages = []
    onlyfiles = [
        f for f in listdir(mypath) if isfile(
            join(mypath, f)) and (".png" in f or ".jpg" in f)]
    for file in onlyfiles:
        full_file_path = mypath + file
        test = get_data_order(full_file_path)
        data = []
        while test:
            columns = greater_to_left_column(test, var_px=20)
            data.append(columns)
        if print_test:
            print u"test sobre %s, grafica:" % file
            precision_graph(data)
            print
            print "----------------------------------------------------------"
            print
        pages.append({
            "data": data,
            "file_name": file
        })
    return pages


def update(d, u):
    import collections
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def get_year_data(mypath, pp_year=2018, th=False, print_test=True):
    from project.models import FinalProject
    from geographic.models import (TownHall, Suburb)
    from public_account.models import(PublicAccount, PPImage)
    from period.models import PeriodPP
    from os import listdir
    from os.path import isfile, join
    import re
    # Ajustes que no estoy seguro que funcionen:
    all_pdf_files = []
    for page in [1, 2]:
        base_path = "%s%s\\" % (mypath, page)
        for f in listdir(base_path):
            full_file_path = "%s%s" % (base_path, f)
            if isfile(full_file_path) and (".png" in f and "PP-" in f):
                all_pdf_files.append([f, full_file_path])
    try:
        periodpp = PeriodPP.objects.get(year=pp_year)
    except Exception as e:
        raise e
        return
    scraping_simple = {}
    re_vars = re.compile(r'^.*\\p([1-2])\\PP-(\d{4})-(\w{2,3})_(\d{4}).png$')
    for file in all_pdf_files:
        if re_vars.match(file[1]):
            all_vars = re.sub(re_vars, '\\1-\\2-\\3-\\4', file[1])
        else:
            continue
        sub_image, year, short_name, image_name = all_vars.split("-")
        if year != u"%s" % pp_year:
            continue
        if th and th != short_name:
            # Se especificó una alcaldía en específico
            continue
        townhall = TownHall.objects.filter(short_name=short_name).first()
        if not townhall:
            print u"townhall no identificado con el short_name: %s" % short_name
            continue
        print townhall

        vision_data = get_data_order(file[1])
        # copia para mandar y guardar en algun otro momento
        # vision_data_copy=list(vision_data)
        data_in_columns = []
        while vision_data:
            columns = greater_to_left_column(vision_data, var_px=20)
            data_in_columns.append(columns)
        normalize_data_ = normalize_data(data_in_columns)
        if not townhall.short_name in scraping_simple:
            scraping_simple[townhall.short_name] = {
                "townhall": townhall,
                "period": periodpp
            }
        townhall_scraping_data = {
            "images": {
                image_name: {
                    sub_image: {
                        "data": normalize_data_,
                        "file": file[0]
                    }
                }
            }
        }
        scraping_simple[townhall.short_name] = update(
            scraping_simple[townhall.short_name], townhall_scraping_data)
    return scraping_simple


def get_year_data_v2(mypath, pp_year=2018, th=False):
    from project.models import FinalProject
    from geographic.models import (TownHall, Suburb)
    from public_account.models import(PublicAccount, PPImage)
    from period.models import PeriodPP
    from os import listdir
    from os.path import isfile, join
    import re
    import json
    all_pdf_files = []
    for f in listdir(mypath):
        full_file_path = "%s%s" % (mypath, f)
        if isfile(full_file_path) and ("0001.png" in f and "PP-" in f):
            all_pdf_files.append([f, full_file_path])
    print len(all_pdf_files)
    try:
        period_pp = PeriodPP.objects.get(year=pp_year)
    except Exception as e:
        raise e
        return
    scraping_simple = {}
    re_vars = re.compile(r'^.*\\PP-(\d{4})-(\w{2,3})_(\d{4}).png$')
    for file in all_pdf_files:
        print file
        if re_vars.match(file[1]):
            all_vars = re.sub(re_vars, '\\1-\\2-\\3', file[1])
        else:
            continue
        year, short_name, image_name = all_vars.split("-")
        if year != u"%s" % pp_year:
            continue
        if th and th != short_name:
            # Se especificó una alcaldía en específico
            continue
        townhall = TownHall.objects.filter(short_name=short_name).first()
        if not townhall:
            print u"townhall no identificado con el short_name: %s" % short_name
            continue
        public_account, is_created = PublicAccount.objects.get_or_create(
            townhall=townhall,
            period_pp=period_pp)
        ppimage, is_created = PPImage.objects.get_or_create(
            public_account=public_account, path=file[0])
        try:
            variables = json.loads(ppimage.vision_data)
        except Exception as e:
            variables = {}
        vision_data = get_data_order(file[1])
        variables["full"] = vision_data
        ppimage.vision_data = json.dumps(variables)
        ppimage.save()
        print ppimage


def extractDataForLens(path_image, year=2018, th=False):
    from public_account.models import PublicAccount, PPImage
    import json
    data_from_lens = get_year_data(path_image, pp_year=year, th=th)
    # pages = dict.items(data_from_lens)
    for th_sn, th_data in data_from_lens.items():
        import json
        townhall = th_data.get("townhall")
        periodpp = th_data.get("period")
        images_scraping = th_data.get("images")
        public_account, is_created = PublicAccount.objects.get_or_create(
            townhall=townhall, period_pp=periodpp)

        public_account.variables = json.dumps(images_scraping)
        public_account.save()

        for image_name, image_data in images_scraping.items():
            file = None
            for sub_image, sub_image_data in image_data.items():
                file = sub_image_data.get("file")
                if file:
                    break
            pp_image, is_created = PPImage.objects.get_or_create(
                public_account=public_account,
                path=file
            )
            pp_image.json_variables = json.dumps(image_data)
            pp_image.save()


def proces_scraping_simple(scraping_simple):
    for townhall_id, townhall_scraping_data in scraping_simple.items():
        images = townhall_scraping_data.get("images")
        townhall = townhall_scraping_data.get("townhall")
        period = townhall_scraping_data.get("period")
        for image in images:
            image_a = images[image].get("1")
            image_b = images[image].get("2")
            if not (image_b and image_b):
                return
            """
            limite de los valores
            """
            irregular = False
            data_b = image_b.get("data")
            if len(data_b) == 5:
                # informacion regular esperada
                total_datos_esperados = len(data_b[0])
                for colum_b in data_b:
                    if len(colum_b) != total_datos_esperados:
                        irregular = "no todas las columnas tienen el mismo tamaño"
                        break
            else:
                irregular = "informaion irregular, se esperavan 5 columnas para este dato"
            if irregular:
                print "------------------------------------------------------"
                print "informaion irregular, se esperavan 5 columnas para este dato"
                print data_b
                print
                total_datos_esperados = 0
                continue


def normalize_data(data):
    data_n = []
    for colum in data:
        colum_n = []
        for row in colum:
            word = row.get("w")
            if u"\n" in word:
                colum_n += [w.strip() for w in word.split(u"\n") if w.strip()]
            else:
                if not word:
                    return
                colum_n.append(word)
        data_n.append(colum_n)
    return data_n


def normalize_data_db(data, file_name):
    import csv
    if not ".csv" in file_name:
        file_name = "%s.csv" % file_name
    columns_count = len(data)
    large_row = 0
    for column in data:
        x = len(column)
        if x > large_row:
            large_row = x
    with open(file_name, mode='wb') as page_file:
        page_writer = csv.writer(
            page_file,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
        data_csv = []
        for y in range(large_row):
            row = []
            for x in range(columns_count):
                try:
                    row.append(data[x][y].encode("latin-1"))
                except Exception as e:
                    row.append(None)
            data_csv.append(row)
        page_writer.writerows(data_csv)


def page_to_csv(pages, page_id):
    import csv
    page = pages[page_id].get("data")
    file_name = pages[page_id].get("file_name", 'page_%s.csv' % page_id)
    file_name = file_name.replace(".png", ".csv").replace(".jpg", ".csv")
    if not ".csv" in file_name:
        file_name = "%s.csv" % file_name
    columns_count = len(page)
    large_row = 0
    for column in page:
        x = len(column)
        if x > large_row:
            large_row = x
    with open(file_name, mode='wb') as page_file:
        page_writer = csv.writer(
            page_file,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
        data = []
        for y in range(large_row):
            row = []
            for x in range(columns_count):
                try:
                    row.append(page[x][y].get("w").encode("latin-1"))
                except Exception as e:
                    row.append(None)
            data.append(row)
        page_writer.writerows(data)
