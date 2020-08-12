def block_fy(e):
    return e['fy']


def block_fx(e):
    return e['fx']


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
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                word_text = u''.join([
                    symbol.text for symbol in word.symbols
                ])
                try:
                    total_text.append(word_text)
                except Exception as e:
                    pass
        vertices = block.bounding_box.vertices
        blocks.append(
            {
                "raw": block,
                "total_text": total_text,
                "vertices": vertices,
                "w": u" ".join(total_text),
                "fx": vertices[0].x,
                "fy": vertices[0].y
            })
    blocks.sort(key=block_fx)
    return blocks


def greater_to_left_column(ordern_blocks, var_px=40, rectification=True):
    if not ordern_blocks:
        return []
    first_block = ordern_blocks[0]
    fxa = first_block.get("vertices")[0].x
    fxb = first_block.get("vertices")[1].x
    fxc = (fxa + fxb) / 2
    columns = []
    index = 0
    # for block in ordern_blocks:
    while not index >= len(ordern_blocks):
        block = ordern_blocks[index]
        vertices = block.get("vertices")
        xa = vertices[0].x
        xb = vertices[1].x
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


# estructura de objeto
#     {
#         "total_text": total_text,
#         "vertices": vertices,
#         "w": u" ".join(total_text),
#         "fx": vertices[0].x,
#         "fy": vertices[0].y
#     }
pages = test_all_files(
    u"C:\\git\\Cuenta pública (PDF´s 2018)\\recortados\\",
    print_test=False)


for page_id in range(len(pages)):
    page_to_csv(pages, page_id)
