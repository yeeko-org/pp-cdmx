Pasar el formato de la columna avance



# x_left de colonia:
"Unidad Responsable del Gasto"
# x_center de colonia:
"Colonia o Pueblo Originario"
# x_center de proyecto:
"Proyecto"
# x_center de desripción:
"Descripción"
# resto de columnas:
"Avance del"
"Abrobado*"
"Modificado"
"Ejercido"
"Variación %"


PP-{AAAA}-{ID_ALCALDIA}_{PÁGINA}-1.png
PP-{AAAA}-{ID_ALCALDIA}_{PÁGINA}-2.png

{
	"cve_townhall": 4,
	"name": "AZCAPOTZALCO",
	"year": 2008,
	"double_proy_desc": True,
	"sign_over": False,
	"colonia": {
		"initial_col": "AGUILERA", 
		"align_x": "center",
		"align_y": "center",
		"multiple_lines": True,
		"special_format"	: None
	},
	"proy": { 
		"first_record_proy": "TRABAJO UNIDO",
		"second_record_proy": "IMPERMEABILIZACIÓN EN ALDAMA",
		"phrases_width": ["TRABAJO UNIDO", "PARA AGUILERA"],
		"phrases_height": ["TRABAJO UNIDO", "FERROCARRILEROS"],
		"required_proy": True
	},
	"desc": { 
		"first_record_desc": "TRABAJO UNIDO",
		"second_record_desc": "IMPERMEABILIZACIÓN EN ALDAMA",
		"final_x": "PARA AGUILERA",
		"required_desc": False
	},
	"last_5_align_y": "center",
	"ammounts_align_x": "center",
	"avance": {
		"avance_initial": "AGUILERA", 
		"avance_format": "III#",
		"avance_align_x": "center"
	},
	"variation": {
		"variation_initial": "AGUILERA", 
		"variation_format" : "III#",
		"variation_align_x": "center"
	},
}


#Antes que nada, construir función que estandarice los textos, que incluya:
#GUARDADO DE BASE DE DATOS.
#--Espacios + paréntesis. || ( EJEMPLO ) --> (EJEMPLO)
#--Espacios y puntos.  || EJEMPLO . INCREIBLE --> EJEMPLO. INCREIBLE
#--Espacios y comas. || EJEMPLO , INCREIBLE --> EJEMPLO, INCREIBLE
#--Dobles espacios.
#Además, estandarizar con los siguientes criterios
#PARA COMPARAR. (usar slugify)
#--Acentos --> frases sin un solo acento || ÁRBOL --> ARBOL
#--Todo Mayúsculas  
#--comas --> espacios
#--puntos --> espacios
#--ignorar todo lo que no sea espacio o [a-Z, 0-9, ()]
#considerar los siguientes casos:
# SANTA FE (PBLO), SANTA FE (U HAB)
#(U HAB) (U.HAB.) (U. HAB.) --> (U HAB)




##### VARIABLES POR CADA ALCALDÍA:

"font_size" : 12,
"space_between_lines" : 2,
"space_between_columns" : 4,



"suburbs":[
	{
		#Directamente obtenido de la tabla
		"name": "",
		#obtenido si el cruce con la base de datos es exitoso
		"suburb_id": 45,
		"project":{
			"text": "IMPERMEABILIZACIÓN EN ALDANA",
			#Utilizar algún algoritmo de python para verificar grado de coincidencia.
			"coincidence_winer": 0.84,
			"winer_project_id": 4784,
		},
		"description":{
			"text": "IMPERMEABILIZACIÓN EN ALDANA",
		},
		"avance":{
			"raw_text": "1009",
			"value": 100.00,
		},
		#la misma situación para las 5 últimas columnas
		"approved": {
			"raw_text": "487,487.32",
			"value": 487487.32,
		},
		"column":{
			"center_y": 78,
			"start_y_col": 18,
			"end_y_col": 120,
		},
	}
]

#Por cada columna:
"whidth_{{column}}": 154,




##### VARIABLES POR CADA HOJA:

"inclinado": 
"start_x": 
"start_y": 
"center_{{column}}": 548,
"start_{{column}}": 20,
"end_{{column}}": 1130





#pasos:

#1. Analizar la página 1.
#2. Encontrar el grado de inclinación:
	#A partir de la primera y última letra de los encabezados de las columnas 1 y 3.
#Encontrar el centro de cada columna (ajustado según inclinación)
	#Calcular el centro con la primer línea de cada encabezado de columna.
#Calcular el inicio de la primera columna (ajustado):
	#Con la frase "Unidad Responsable del Gasto", ubicar la ubicación de la "U"
#Calcular el ancho real de la columna proyecto (ajustado):
	#Utilizar las variables first_record_proy y second_record_proy
	#Obtener la posición de la primera y la última letra de cada frase
#Calcular lo mismo para la columna descripción.
	
#Obtener una lista de cada colonia:
	#Utilizar los delimitadores del eje x ya construídos
	#Si la línea completa de texto no tiene coincidencias, intentar concatenar 
	#la siguiente línea, siempre y cuando no exista espacio estre ellas
	#y siempre y cuando la siguiente línea por sí misma no tenga coincidencias
#Obtener el centro (y) de cada colonia (ajustado).

#Obtener para cada colonia sus delimitadores (eje y) de la columna proyecto:
	#Obetner top (con la primera línea) y el bottom (usando el center)
	#La siguiente colonia en la lista debe usar el valor bottom previo para 
	#calcular su propio top, pero será ajustado a la posición y que tenga la 
	#primer línea de texto encontrada en su área.
#Obtener los valores de las últimas 5 columnas
	#Usando su centro x y el centro de cada colonia, averiguar qué palabras
	# interceptan dicho punto (con un radio de 6px)










def 

	all_townhalls = TownHall.objects.all() #Cada una de las alcaldías.
	for th in all_townWalls:
		AssignTownHallVars(th)




def AssignTownHallVars(th):






for 


por cada alcaldía:


Primer paso:



for 

