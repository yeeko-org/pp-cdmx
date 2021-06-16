# pp-cdmx
Presupuesto Participativo CDMX


### **Manual de procesamiento de datos**

El sistema de procesamiento de datos es muy específico para el formato de presupuesto participativo, pero puede adaptarse a distintas necesidades. Utilizando el sistema de referencias manuales se puede reducir drásticamente el tiempo de búsqueda, análisis y desarrollo de referencias, además de aumentar la precisión en la extracción de datos.

**Requerimientos:**

Se necesita tener una configuracion de autenticación con cloud.google.com, generar el archivo service-account-file.json que tendrá que ser agregado como variable de entorno como lo indica la documentación.

https://cloud.google.com/vision/docs/libraries?hl=es-419#setting_up_authentication

y tener instalado el paquete pip:

    google-cloud-vision


Información de una sola página tipo imagen:

El siguiente script genera una lista de datos que en adelante llamaremos vison_data, la cual contiene toda la información de los bloques  con sus posiciones en formato json

    from vision.get_columns import get_data_order
    vision_data = get_data_order(u"path_completo_del_archivo_local")

con una estructura resultante con la siguiente estructura:

    [
        {
            "fx": 258,
            "fy": 324,
            "vertices": [{"y": 324, "x": 258}, ...],
            "total_text": ["Unidad", "Responsable", ...],
            "w": "Unidad Responsable del Gasto : 02CD16 DELEGACIÓN XOCHIMILCO\n",
            "block":
            {
                "vertices": [{"y": 324, "x": 258}, ...],
                "paragraphs": [
                    {
                        "vertices": [{"y": 324, "x": 258}, ...],
                        "words": [
                            {
                                "symbols": [
                                    {
                                        "text": "U",
                                        "confidence": 0.9900000095367432,
                                        "vertices": [{"y": 324, "x": 258}, ...]
                                    }
                                ],
                                "detected_break": 1,
                                "word": "Unidad",
                                "vertices": [{"y": 324, "x": 258}, ...]
                            }
                        ]
                    }
                ]
            }
        }
    ]

* vertices siempre sera una lista de 4 puntos: superior izq, superior der, inferior der e inferior izq
* las coordenadas x se leen con normalidad de izquierda a derecha, pero las y se leen de arriba a abajo, siendo el top y=0


**Carga de datos masivos por cuenta publica**

El siguiente script escanea todos los archivos, que tengan el formato correcto en su nombre, de una carpeta  y genera los registros en la base de datos, se espera que el formato del nombre del archivo coincida con **r'^.*\\PP-(\d{4})-(\w{2,3})_(\d{4}).png$' **que representa a year, short_name, image_name.

    from vision.get_columns import get_year_data_v2
    get_year_data_v2(path, year, th)

**path**: dirección completa de la carpeta donde deberán estar todas las imágenes
**year**: limita el procesamiento de imágenes a un año especifico
**th**: limita el procesamiento de imágenes a una delegación específica

Este proceso requiere del registro previo de los catálogos de Period y TownHall, y generará los registros de PublicAccount y PPImage, la información resultante vison_data se registrará por cada imagen procesada en PPImage.vision_data

De ser el caso de re procesar por lotes la información, este mismo script no duplica los registros, sólo actualizará PPImage.vision_data si ya existe y creará los registros para los nuevos.

También se pueden procesar lotes incompletos o faltantes apuntando el path a la carpeta con los nuevos archivos y ajustando el year y th a las necesidades, siempre y cuando los archivos tengan el formato correcto en el nombre


**Cálculo vision_data por PPImage:**

Cuando se quiera procesar el vision_data de un registro PPImage ya existente, con un archivo imagen que no cumpla con el formato de el nombre, o un registro nuevo sin el script automatico por lotes, se puede usar el método calculate_vision_data del modelo

    PPimage.calculate_vision_data(path)

El save del modelo PPimage, en caso de que no se tenga vision_data y un path válido como archivo, intentará obtener el vision_data antes de guardarse


Para la creación o actualización de Registros de una PPImage se recurre a 2 opciones, con referencias automáticas o manuales, siendo más precisas las segundas

Para las referencias automáticas, se deben tener configuradas por Perido las variantes adecuadas de las referencias.

Para las referencias manuales se requiere que la primera página de la cuenta pública relacionada también tenga las referencias manuales completas, las consecutivas solo necesitaran los puntos extremos.

    PPImage.get_table_data(recalculate=True)

Este metodo generará los Rows determinando que referencia utilizara.


