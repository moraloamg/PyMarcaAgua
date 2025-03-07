"""
Modulo que contiene funciones para añadir una marca de agua en un pdf.
"""

import os
import fitz
from PIL import Image, ImageDraw, ImageFont
import io

__author__ = "Adrian Mateos"
__copyright__ = "Copyright 2025"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = ""
__email__ = "https://github.com/moraloamg"
__status__ = "Completed"


def _crear_marca_agua(texto:str,
                    tamano_fuente_texto:int,
                    opacidad:int = 100,
                    mayusculas: bool = False,
                    color: tuple[int, int, int] = (255, 0, 0)):
    
    """
    Función que crea un recuadro con la marca de agua dentro en diagonal. 
    El codigo generará un recuadro cuyo tamaño se verá influido por el tamaño de la
    fuente dispuesta en los parámetros. A mayor tamaño de fuente, más grande será el recuadro.
    Dentro de dicho recuadro se añadirá el texto, con la fuente, el tamaño y la opacidad indicadas
    abajo.
    El recuadro se adapta automáticamente al tamaño del recuadro. Los tamaños de la fuente recomendados
    son: mínimo 16 y máximo 40.

    Parameters:
    ----------
    - texto (str): Texto de la marca de agua.
    - tamano_fuente_texto (int): Tamaño de la fuente (recomentado ente 16 y 40).
    - opacidad (int): Opacidad del texto (recomendado en 100).
    - mayusculas (bool): Poner el texto en minúsculas con False o mayúsculas con True. False por defecto.
    - color (tuple[int,int,int]): tupla que indica el color en tres dígitos. Rojo por defecto.

    Returns:
    --------
    - recuadro (PIL.Image): recuadro de la marca de agua con el texto centrado y rotado.
    """

    #Se intenta cargar la fuente 'arial.ttf', si falla, usa la fuente predeterminada de PIL
    try:
        fuente = ImageFont.truetype("arial.ttf", tamano_fuente_texto)
    except IOError:
        fuente = ImageFont.load_default()

    #Aplicamos mayúsculas o minúsculas según el parámetro
    texto = texto.upper() if mayusculas else texto.lower()

    #Obtenemos las dimensiones del texto
    ancho_texto, alto_texto = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), texto, font=fuente)[2:4]

    #Calculamos el margen automáticamente según el tamaño de la fuente
    margen_x = tamano_fuente_texto // 2  #Margen horizontal basado en el tamaño de la fuente
    margen_y = tamano_fuente_texto // 3  #Margen vertical más pequeño para evitar espacio extra innecesario

    #Ajustamos el tamaño de el recuadro sumando el margen
    ancho = ancho_texto + 2 * margen_x
    alto = alto_texto + 2 * margen_y

    #Creamos el recuadro con fondo transparente (el ultimo cero indica la transparencia)
    recuadro = Image.new("RGBA", (ancho, alto), (255, 255, 255, 0))
    dibujo = ImageDraw.Draw(recuadro)

    #Calculamos la posición centrada
    x = (ancho - ancho_texto) / 2
    y = (alto - alto_texto) / 2

    #Dibujarmos el texto en el recuadro. "fill" indica el color y el ultimo digito la transparencia.
    dibujo.text((x, y), texto, fill=(*color, opacidad), font=fuente)

    #Rotamos el recuadro 45° y expandir para evitar recortes
    recuadro = recuadro.rotate(45, expand=1)

    return recuadro


def _crear_marca_agua_imagen(ruta_imagen: str = None, tamano: int = 20, opacidad: int = 100):
    """
    Función que crea una marca de agua a partir de una imagen, permitiendo ajustar su tamaño y opacidad.

    Parameters:
    ----------
    - ruta_imagen (str): Ruta de la imagen que se usará como marca de agua.
    - tamano (int): Tamaño de la imagen en porcentaje respecto al original (recomendado entre 16 y 100).
    - opacidad (int): Opacidad de la imagen (recomendado entre 0 y 255, donde 255 es completamente opaco).

    Returns:
    --------
    - imagen (PIL.Image): Imagen de la marca de agua ajustada.
    """

    #Cargamos la imagen aseguramos el canal alfa
    imagen = Image.open(ruta_imagen).convert("RGBA")
    
    #Ajustamos el tamaño de la imagen en función del porcentaje especificado
    ancho_original, alto_original = imagen.size
    nuevo_ancho = int(ancho_original * (tamano / 100))
    nuevo_alto = int(alto_original * (tamano / 100))
    imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

    #Aplicamos la opacidad modificando el canal alfa
    r, g, b, a = imagen.split()
    a = a.point(lambda p: p * (opacidad / 100))  # Ajustar la opacidad en base al porcentaje
    imagen = Image.merge("RGBA", (r, g, b, a))

    #Rotamos la imagen 45° y expandimos para evitar recortes
    imagen = imagen.rotate(45, expand=True)

    return imagen



def vista_previa_pdf(
        ruta_entrada_pdf: str,
        texto_marca_agua: str,
        tamano_fuente: int,
        opacidad_texto: int,
        texto_mayusculas: bool = False,
        color_texto: tuple[int, int, int] = (255, 0, 0),
        blanco_y_negro: bool = False,
        ruta_imagen: str = None):
    
    """
    Función que genera una vista previa del pdf. Hace una captura de la primera página y añade la marca
    de agua, para luego ser enviada a la interfaz gráfica.
    Si hay una ruta de una imagen en su respectiva variable, se devolverá una marca de agua con dicha imagen,
    en caso contrario, se devolverá una marca de agua con un texto.

    Parameters:
    ----------
    - ruta_entrada_pdf (str): Ruta del pdf a marcar.
    - texto_marca_agua (str): Texto saldrá en la marca de agua.
    - ruta_imagen (str): Ruta de la imagen de la marca de agua.
    - tamano_fuente (int): Tamaño de la fuente (recomentado ente 16 y 40).
    - opacidad_texto (int): Opacidad del texto (recomendado en 100).
    - texto_mayusculas (bool): Poner el texto en minúsculas con False o mayúsculas con True. False por defecto.
    - color_texto (tuple[int,int,int]): tupla que indica el color en tres dígitos. Rojo por defecto.
    - blanco_y_negro (bool): True convierte el pdf a blanco y negro, False lo deja como está. False por defecto.
    - ruta_imagen (str): Ruta de la imagen. Si hay una ruta, se pondrá la marca de agua con la imagen y no con el texto.

    Returns:
    --------
    - buffer_imagen (BytesIO): Imagen guardada en memoria.
    """
    
    #Seleccionamos la primera página del pdf
    documento = fitz.open(ruta_entrada_pdf)
    pagina = documento[0]

    #Convertimos la primera página a imagen a una imagen
    pix = pagina.get_pixmap()
    imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    #Convertimos la imagen a blanco y negro si está la correspondiente opción activada
    if blanco_y_negro:
        #Convertimos solo la imagen del PDF a escala de grises antes de aplicar la marca de agua
        imagen = imagen.convert("L").convert("RGB")  #"L" convierte a gris, luego "RGB" para mantener el formato

    #Si hay una marca de agua, la añadimos, si no, añadimos texto
    if not os.path.isfile(ruta_imagen): 
        #Creamos la marca de agua de texto en color
        marca_agua = _crear_marca_agua(texto_marca_agua, tamano_fuente, opacidad_texto, texto_mayusculas, color_texto)
    else:
        #Creamos la marca de agua con imagen si hay imagen
        marca_agua = _crear_marca_agua_imagen(ruta_imagen, tamano_fuente, opacidad_texto)

    #Aplicamos la marca de agua en la imagen
    for x in range(0, imagen.width, marca_agua.width + 10):
        for y in range(0, imagen.height, marca_agua.height + 1):
            imagen.paste(marca_agua, (x, y), marca_agua)

    #Guardamos la imagen final en un buffer
    buffer_imagen = io.BytesIO()
    imagen.save(buffer_imagen, format="JPEG", quality=50)
    buffer_imagen.seek(0)

    #cerramos el documento y retornamos la imagen guardada en memoria
    documento.close()
    return buffer_imagen


def anadir_marca_agua_a_pdf(
        ruta_entrada_pdf:str,
        ruta_salida_pdf:str,
        texto_marca_agua:str,
        tamano_fuente:int,
        opacidad_texto:int,
        texto_mayusculas:bool = False,
        color_texto: tuple[int, int, int] = (255, 0, 0),
        blanco_y_negro: bool = False,
        ruta_imagen:str = None,
        espaciado_ancho:int = 10,
        espaciado_alto:int = 1):
    
    """
    Función que repite una marca de agua en mosaico a cada página de un PDF.
    La cantidad de teselas del mosaico puede verse afectada por la separación horizontal o vertical.
    Si hay una ruta de una imagen en su respectiva variable, se devolverá una marca de agua con dicha imagen,
    en caso contrario, se devolverá una marca de agua con un texto.

    Parameters:
    ----------
    - ruta_entrada_pdf (str): Ruta del pdf a marcar.
    - ruta_salida_pdf (str): Ruta donde queremos guardar el pdf una vez modificado.
    - texto_marca_agua (str): Texto saldrá en la marca de agua.
    - tamano_fuente (int): Tamaño de la fuente (recomentado ente 16 y 40).
    - opacidad_texto (int): Opacidad del texto (recomendado en 100).
    - texto_mayusculas (bool): Poner el texto en minúsculas con False o mayúsculas con True. False por defecto.
    - color_texto (tuple[int,int,int]): tupla que indica el color en tres dígitos. Rojo por defecto.
    - blanco_y_negro (bool): True convierte el pdf a blanco y negro, False lo deja como está. False por defecto.
    - ruta_imagen (str): Ruta de la imagen. Si hay una ruta, se pondrá la marca de agua con la imagen y no con el texto.
    - espaciado_ancho (int): Separación horizontal del texto dispuesto en la marca de agua.
    - espaciado_alto (int): Separación vertical del texto dispuesto en la marca de agua.

    Returns:
    --------
    - pdf con la marca de agua.
    """

    #Abre el PDF de entrada con PyMuPDF
    documento = fitz.open(ruta_entrada_pdf)
    #Crea la imagen de la marca de agua
    if not os.path.isfile(ruta_imagen):
        imagen_marca_agua = _crear_marca_agua(texto_marca_agua, tamano_fuente, opacidad_texto, texto_mayusculas, color_texto)
    else:
        imagen_marca_agua = _crear_marca_agua_imagen(ruta_imagen,tamano_fuente, opacidad_texto)
    #Crea un buffer en memoria para almacenar la imagen
    bytes_imagen = io.BytesIO()
    #Guarda la imagen en el buffer como PNG
    imagen_marca_agua.save(bytes_imagen, format="PNG")
    #Vuelve al inicio del buffer para su lectura
    bytes_imagen.seek(0)
    #Convierte la imagen en un Pixmap de PyMuPDF
    pix = fitz.Pixmap(bytes_imagen.read())
    
    
    #Itera sobre cada página del PDF
    for pagina in documento:

        # Si el parámetro blanco_y_negro es True, convierte la página a escala de grises
        if blanco_y_negro:
            pix_gris = pagina.get_pixmap(colorspace=fitz.csGRAY)  # Convertir a escala de grises
            img_gris = fitz.Pixmap(pix_gris, 0)  # Crear un nuevo Pixmap en gris
            pagina.insert_image(pagina.rect, pixmap=img_gris, overlay=True)  # Sobrescribir en gris

        #Obtiene dimensiones de la página
        ancho_pagina, alto_pagina = pagina.rect.width, pagina.rect.height
        #Obtiene dimensiones de la imagen de la marca de agua
        ancho_imagen, alto_imagen = imagen_marca_agua.size
        
        #Itera sobre la página y posicionar la marca de agua en mosaico
        #Bucle horizontal
        for x in range(0, int(ancho_pagina), ancho_imagen + espaciado_ancho):
            #Bucle vertical 
            for y in range(0, int(alto_pagina), alto_imagen + espaciado_alto):
                #Crea un rectángulo en la posición deseada
                rect = fitz.Rect(x, y, x + ancho_imagen, y + alto_imagen)
                #Inserta la imagen en la página
                pagina.insert_image(rect, pixmap=pix, overlay=True)
    

    #Guarda el PDF modificado con la marca de agua
    documento.save(ruta_salida_pdf)
    #Cierra el documentoumento
    documento.close()
    #Mensaje de confirmación
    print(f"Marca de agua añadida a {ruta_salida_pdf}")

#------------------------------- FIN DEL CODIGO ---------------------------------------



