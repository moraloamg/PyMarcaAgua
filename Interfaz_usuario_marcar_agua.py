"""
Modulo que contiene la interfaz gráfica de usuario.
"""

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, Label
import fitz  # PyMuPDF para validar PDFs
from PIL import Image,ImageTk
from marcar_agua_pdf import anadir_marca_agua_a_pdf, vista_previa_pdf  # Importamos la función desde el otro fichero

__author__ = "Adrian Mateos"
__copyright__ = "Copyright 2025"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = ""
__email__ = "https://github.com/moraloamg"
__status__ = "Completed"

def seleccionar_pdf_entrada():
    """Abre un diálogo para seleccionar el PDF de entrada y valida que sea un archivo PDF válido."""
    ruta = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    if ruta:
        try:
            fitz.open(ruta).close()  # Intenta abrir el PDF para verificar que no esté corrupto
            entrada_var.set(ruta)
        except Exception:
            messagebox.showerror("Error", "El archivo PDF seleccionado está corrupto o no es válido.")


def seleccionar_imagen():
    """Abre un diálogo para seleccionar una imagen valida."""
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes en jpg, jpeg o png", "*.jpg;*.jpeg;*.png")])
    if ruta:
        try:
            fitz.open(ruta).close()  # Intenta la imagen para ver que no está corrupta
            entrada_imagen_var.set(ruta)
            entrada_texto.config(state="disabled")
            #texto_var.set("")
            entrada_color.config(state="disabled")
            #color_var.set("")
            #color_label.config(bg=root.cget("bg"), text="")
            marco_color.config(state="disabled")
            entrada_mayus.config(state="disabled")
            entrada_minus.config(state="disabled")
        except Exception:
            messagebox.showerror("Error", "La imágen está corrupta o no es válida.")


def quitar_imagen():
    ruta = entrada_imagen_var.get()
    if ruta:
        try:
            entrada_imagen_var.set("Aún no se ha elegido una imagen")
            entrada_texto.config(state="normal")
            entrada_color.config(state="normal")
            marco_color.config(state="normal")
            entrada_mayus.config(state="normal")
            entrada_minus.config(state="normal")
        except Exception:
            messagebox.showerror("Error", "La imágen está corrupta o no es válida.")


def lugar_de_guardado():
    """Abre un diálogo para seleccionar una carpeta donde guardar el PDF de salida y permite nombrarlo."""
    ruta = filedialog.askdirectory()
    if ruta:
        nombre_archivo = nombre_archivo_var.get().strip()
        if not nombre_archivo:
            messagebox.showerror("Error", "Antes de elegir un lugar de guardado debes introducir un nombre para el archivo.")
            return
        salida_var.set(f"{ruta}/{nombre_archivo}.pdf")

def seleccionar_color():
    """Abre un selector de color y convierte la salida en una tupla RGB."""
    color = colorchooser.askcolor()[0]  # Devuelve (R, G, B) o None
    if color:
        color_var.set(f"({int(color[0])}, {int(color[1])}, {int(color[2])})")
        # Actualiza el label del color con un pequeño recuadro de color y elimina la tupla
        marco_color.config(bg=f'#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}', text="")

def validar_longitud_texto(*args):
    """Limita la entrada de texto a 30 caracteres."""
    if len(texto_var.get()) > 20:
        texto_var.set(texto_var.get()[:30])  # Recorta el texto a 30 caracteres


def generar_vista_previa():
    """Genera una vista previa de la marca de agua."""

    mensaje_de_error = "Para usar la vista previa deberás indicar el archivo PDF, el nombre del archivo y lugar de guardado, el texto de la marca de agua y su color, o bien una imagen."

    if not os.path.isabs(entrada_var.get()) or not os.path.isabs(salida_var.get()) or not nombre_archivo_var.get():
        messagebox.showerror("Error", mensaje_de_error)
        return
    if not texto_var.get().strip() and not os.path.isabs(entrada_imagen_var.get()): 
        messagebox.showerror("Error", mensaje_de_error)
        return
    if not color_var.get() and not os.path.isabs(entrada_imagen_var.get()):
        messagebox.showerror("Error", mensaje_de_error)
        return
    
    if os.path.isfile(entrada_imagen_var.get()) and not color_var.get():
        color_var.set((0,0,0))

    try:
        # Generar vista previa
        imagen_previa = vista_previa_pdf(
            ruta_entrada_pdf=entrada_var.get(),
            texto_marca_agua=texto_var.get(),
            tamano_fuente=tamano_var.get(),
            opacidad_texto=opacidad_var.get(),
            texto_mayusculas=mayusculas_var.get(),
            color_texto=eval(color_var.get()),
            blanco_y_negro=bn_var.get(),
            ruta_imagen=entrada_imagen_var.get()
        )

        if imagen_previa:
            imagen_pil = Image.open(imagen_previa)
            imagen_pil.thumbnail((400, 500))
            imagen_tk = ImageTk.PhotoImage(imagen_pil)
            
            if hasattr(marco_imagen, "imagen_label"):
                marco_imagen.imagen_label.config(image=imagen_tk)
                marco_imagen.imagen_label.image = imagen_tk
            else:
                marco_imagen.imagen_label = Label(marco_imagen, image=imagen_tk)
                marco_imagen.imagen_label.image = imagen_tk
                marco_imagen.imagen_label.pack()
    
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error generando la vista previa: {str(e)}")


def ejecutar():
    """Valida los datos y ejecuta la función de marca de agua."""
    try:
        # Validaciones
        if not os.path.isabs(entrada_var.get()) or not os.path.isabs(salida_var.get()) or not nombre_archivo_var.get():
            raise ValueError("Debes seleccionar el archivo PDF y el nombre y carpeta donde guardarlo.")
        if not texto_var.get().strip() and not os.path.isabs(entrada_imagen_var.get()): 
            raise ValueError("Debes introducir un texto o una imagen como marca de agua.")
        if not color_var.get() and not os.path.isabs(entrada_imagen_var.get()):
            raise ValueError("Debes elegir un color para el texto.")
    
        if os.path.isfile(entrada_imagen_var.get()) and not color_var.get():
            color_var.set((0,0,0))

        #Parámetros para la función
        anadir_marca_agua_a_pdf(
            ruta_entrada_pdf=entrada_var.get(),
            ruta_salida_pdf=salida_var.get(),
            texto_marca_agua=texto_var.get(),
            tamano_fuente=tamano_var.get(),
            opacidad_texto=opacidad_var.get(),
            texto_mayusculas=mayusculas_var.get(),
            color_texto=eval(color_var.get()),  # Convierte el string en tupla
            blanco_y_negro=bn_var.get(),
            ruta_imagen=entrada_imagen_var.get()
        )

        messagebox.showinfo("Éxito", f"PDF procesado correctamente.\nEl archivo se ha guardado en:\n{salida_var.get()}")
        nombre_archivo_var.set("")
        salida_var.set("Aún no se ha elegido un lugar de guardado")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}\nPara más información contacte con el desarrollador.")

def reiniciar():
    """Restablece todos los valores de entrada."""
    entrada_var.set("Aún no se ha elegido un archivo PDF")
    entrada_imagen_var.set("Aún no se ha elegido una imagen")
    salida_var.set("Aún no se ha elegido un lugar de guardado")
    texto_var.set("")
    entrada_texto.config(state="normal")
    tamano_var.set(16)
    opacidad_var.set(100)
    mayusculas_var.set(False)
    color_var.set("")
    entrada_color.config(state="normal")
    bn_var.set(False)
    nombre_archivo_var.set("")
    # Restablecer el label del color
    marco_color.config(state="normal")
    marco_color.config(bg=root.cget("bg"), text="")
    entrada_mayus.config(state="normal")
    entrada_minus.config(state="normal")
    #borrar el contenido del marco
    if hasattr(marco_imagen, "imagen_label"):
        marco_imagen.imagen_label.destroy()
        del marco_imagen.imagen_label


# Crear ventana principal
root = tk.Tk()
root.title("Añadir Marca de Agua a PDF. versión 1.0")

# Tamaño fijo para cada frame
ANCHO_FRAME = 450
ALTO_FRAME = 500

# Calcular el ancho total de la ventana para que se ajuste exactamente a los frames
ANCHO_VISIBLE_POR_FRAME = 425  # Ancho visible de cada frame
MARGEN_ENTRE_FRAMES = 45  # Espacio entre los frames (ajustado a 10 píxeles)
PADX_EXTERNO = 15  # Margen externo a cada lado de los frames
ancho_ventana = (ANCHO_VISIBLE_POR_FRAME * 2) + MARGEN_ENTRE_FRAMES + (PADX_EXTERNO * 2) + 18  # +18 para la scrollbar del frame izquierdo
alto_ventana = 740
ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
x_pos = (ancho_pantalla // 2) - (ancho_ventana // 2)
y_pos = (alto_pantalla // 2) - (alto_ventana // 2)
root.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")

root.resizable(False, False)

#-------------------FRAME IZQUIERDO-----------------------------------------

# Crear frame izquierdo con scroll horizontal y vertical
frame_izquierdo = tk.Frame(root, width=ANCHO_FRAME, height=ALTO_FRAME, padx=3, pady=4, relief="solid", bd=1)
frame_izquierdo.pack(side="left", padx=(PADX_EXTERNO, 5), pady=10, fill="y")  # 5 píxeles de separación interna

# Crear Canvas y Scrollbars para frame_izquierdo
canvas_izq = tk.Canvas(frame_izquierdo)
scrollbar_izq_y = tk.Scrollbar(frame_izquierdo, orient="vertical", command=canvas_izq.yview, width=18)
scrollbar_izq_x = tk.Scrollbar(frame_izquierdo, orient="horizontal", command=canvas_izq.xview, width=18)
canvas_izq.configure(yscrollcommand=scrollbar_izq_y.set, xscrollcommand=scrollbar_izq_x.set)

# Colocar el Canvas y Scrollbars en frame_izquierdo
scrollbar_izq_y.pack(side="right", fill="y")
scrollbar_izq_x.pack(side="bottom", fill="x")
canvas_izq.pack(side="left", fill="both", expand=True)

# Crear un frame interno dentro del Canvas
frame_interior_izq = tk.Frame(canvas_izq)
canvas_izq.create_window((0, 0), window=frame_interior_izq, anchor="nw")

#-------------------FRAME DERECHO-----------------------------------------

# Crear frame derecho sin scroll
frame_derecho = tk.Frame(root, width=ANCHO_FRAME, height=ALTO_FRAME, padx=3, pady=4, relief="solid", bd=1)
frame_derecho.pack(side="right", padx=(5, PADX_EXTERNO), pady=10, fill="y")  # 5 píxeles de separación interna

# Crear Canvas para frame_derecho (sin scrollbar)
canvas_der = tk.Canvas(frame_derecho, width=ANCHO_VISIBLE_POR_FRAME)
canvas_der.pack(side="left", fill="both", expand=True)

# Crear un frame interno dentro del Canvas para los widgets de frame_derecho
frame_interior_der = tk.Frame(canvas_der)
canvas_der.create_window((0, 0), window=frame_interior_der, anchor="nw")

#---------------------VARIABLES----------------------------------------
entrada_var = tk.StringVar(value="Aún no se ha elegido un archivo PDF")
entrada_imagen_var =  tk.StringVar(value="Aún no se ha elegido una imagen")
salida_var = tk.StringVar(value="Aún no se ha elegido un lugar de guardado")
texto_var = tk.StringVar()
tamano_var = tk.IntVar(value=16)
opacidad_var = tk.IntVar(value=100)
mayusculas_var = tk.BooleanVar(value=False)
color_var = tk.StringVar()
bn_var = tk.BooleanVar(value=False)
nombre_archivo_var = tk.StringVar()

# Asociar la validación a la variable de texto
texto_var.trace_add("write", validar_longitud_texto)

# --------------------------------WIDGETS FRAME IZQUERDO----------------------------------------
marco_cuadrado_pdf = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_pdf.pack(padx=10, pady=4, fill="x")

tk.Label(marco_cuadrado_pdf, text="Seleccione el archivo PDF", font=("Arial", 9, "bold underline")).pack(anchor="w")
tk.Button(marco_cuadrado_pdf, text="Elegir archivo PDF", command=seleccionar_pdf_entrada).pack(anchor="w", pady=5)
frame_ruta_origen = tk.Frame(marco_cuadrado_pdf)
tk.Label(frame_ruta_origen, text="Ruta origen:", fg="black").pack(side="left")
tk.Label(frame_ruta_origen, textvariable=entrada_var, fg="blue").pack(side="left")
frame_ruta_origen.pack(anchor="w")
#-----------------------------------------------------------------------------------------------

marco_cuadrado_nombre = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_nombre.pack(padx=10, pady=4, fill="x")

tk.Label(marco_cuadrado_nombre, text="Escriba un nombre para el nuevo archivo PDF con la marca de agua:", font=("Arial", 9, "bold underline")).pack(anchor="w")
tk.Entry(marco_cuadrado_nombre, textvariable=nombre_archivo_var, width=35).pack(anchor="w")

tk.Label(marco_cuadrado_nombre, text="Seleccione la carpeta donde quiera guardar el archivo PDF:", font=("Arial", 9, "bold underline")).pack(anchor="w")
tk.Button(marco_cuadrado_nombre, text="Elegir Carpeta", command=lugar_de_guardado).pack(anchor="w")
frame_ruta_destino = tk.Frame(marco_cuadrado_nombre)
tk.Label(frame_ruta_destino, text="Ruta destino:", fg="black").pack(side="left")
tk.Label(frame_ruta_destino, textvariable=salida_var, fg="blue").pack(side="left")
frame_ruta_destino.pack(anchor="w")
#-----------------------------------------------------------------------------------------------

marco_cuadrado_texto = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_texto.pack(padx=10, pady=4, fill="x")

tk.Label(marco_cuadrado_texto, text="Escriba el texto de la marca de agua (máx. 30 caracteres):", font=("Arial", 9, "bold underline")).pack(anchor="w")
entrada_texto = tk.Entry(marco_cuadrado_texto, textvariable=texto_var, width=35)
entrada_texto.pack(anchor="w")

tk.Label(marco_cuadrado_texto, text="O bien, escoja una imagen para usarla como marca de agua:", font=("Arial", 9, "bold underline")).pack(anchor="w")
tk.Label(marco_cuadrado_texto, text="(se bloquearán ciertas opciones)", font=("Arial", 7)).pack(anchor="w")

frame_botones_imagenes = tk.Frame(marco_cuadrado_texto)
tk.Button(frame_botones_imagenes, text="Elegir imagen", command=seleccionar_imagen).pack(side="left", padx=(0, 10))
tk.Button(frame_botones_imagenes, text="Eliminar imagen", command=quitar_imagen).pack(side="left")
frame_botones_imagenes.pack(anchor="w")

frame_ruta_imagen = tk.Frame(marco_cuadrado_texto)
tk.Label(frame_ruta_imagen, text="Ruta imagen:", fg="black").pack(side="left")
tk.Label(frame_ruta_imagen, textvariable=entrada_imagen_var, fg="blue").pack(side="left")
frame_ruta_imagen.pack(anchor="w")

#-----------------------------------------------------------------------------------------------

marco_cuadrado_color = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_color.pack(padx=10, pady=4, fill="x")

# Etiqueta como estaba originalmente
tk.Label(marco_cuadrado_color, text="Color del texto de la marca de agua:", font=("Arial", 9, "bold underline")).pack(anchor="w")

# Frame para los elementos de color
color_frame = tk.Frame(marco_cuadrado_color)
color_frame.pack(anchor="w")  # Mantengo el anchor="w" como en tu código original

# Botón a la izquierda y marco de color a la derecha dentro de color_frame
entrada_color = tk.Button(color_frame, text="Elegir Color", command=seleccionar_color)
entrada_color.pack(side="left", padx=(0, 10))  # Padding para separar del marco_color
marco_color = tk.Label(color_frame, width=2, height=1, relief="flat")
marco_color.pack(side="right")

#-----------------------------------------------------------------------------------------------

marco_cuadrado_tamano = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_tamano.pack(padx=10, pady=4, fill="x")

tk.Label(marco_cuadrado_tamano, text="Seleccione el tamaño de la marca (16-40):", font=("Arial", 9, "bold underline")).pack(anchor="w")
tk.Scale(marco_cuadrado_tamano, from_=16, to=40, variable=tamano_var, orient="horizontal").pack(anchor="w")
#-----------------------------------------------------------------------------------------------

marco_cuadrado_opacidad = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_opacidad.pack(padx=10, pady=4, fill="x")

tk.Label(marco_cuadrado_opacidad, text="Seleccione la transparencia de la marca (0-255):", font=("Arial", 9, "bold underline")).pack(anchor="w")
tk.Scale(marco_cuadrado_opacidad, from_=0, to=255, variable=opacidad_var, orient="horizontal").pack(anchor="w")
#-----------------------------------------------------------------------------------------------

marco_cuadrado_mayus = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_mayus.pack(padx=10, pady=4, fill="x")

frame_mayus = tk.Frame(marco_cuadrado_mayus)
entrada_mayus = tk.Radiobutton(frame_mayus, text="Minúsculas", variable=mayusculas_var, value=False)
entrada_mayus.pack(side="left")
entrada_minus = tk.Radiobutton(frame_mayus, text="Mayúsculas", variable=mayusculas_var, value=True)
entrada_minus.pack(side="left")
frame_mayus.pack(anchor="w")

#-----------------------------------------------------------------------------------------------

marco_cuadrado_bn = tk.Frame(frame_interior_izq, padx=10, pady=10, relief="solid", bd=1)
marco_cuadrado_bn.pack(padx=10, pady=4, fill="x")

tk.Checkbutton(marco_cuadrado_bn, text="¿Desea convertir el pdf a Blanco y Negro?", variable=bn_var).pack(anchor="w")
#-----------------------------------------------------------------------------------------------

button_frame = tk.Frame(frame_interior_izq)
tk.Button(button_frame, text="Ejecutar", command=ejecutar, bg="green", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
tk.Button(button_frame, command=generar_vista_previa, text="Ver vista previa", bg="blue", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
tk.Button(button_frame, text="Empezar de nuevo", command=reiniciar, bg="red", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
button_frame.pack(side="left")
button_frame.pack(pady=10)
#-----------------------------------------------------------------------------------------------
#------------------------WIDGETS FRAME DERECHO---------------------------------------------------

tk.Label(frame_interior_der, text="Visualizador de vista previa", font=("Arial", 9, "underline")).pack(anchor="w")

# Crear marco sin bordes para la imagen (más alta que ancha)
marco_imagen = tk.Frame(frame_interior_der, width=400, height=500, relief="flat", bd=0, bg="white")
marco_imagen.pack(anchor="nw", padx=10, pady=5)

#------------------------------------------------------------------------------------------------------

# Configurar el scroll para el frame izquierdo
def configurar_scroll_izq(event):
    canvas_izq.config(width=ANCHO_VISIBLE_POR_FRAME)
    canvas_izq.configure(scrollregion=canvas_izq.bbox("all"))

frame_interior_izq.bind("<Configure>", configurar_scroll_izq)

# Actualización inicial
root.update_idletasks()
configurar_scroll_izq(None)

# Habilitar desplazamiento con la rueda del ratón (solo para el frame izquierdo)
def _on_mousewheel(event):
    x_canvas_izq, y_canvas_izq = canvas_izq.winfo_pointerxy()
    
    # Verificar si el cursor está sobre el Canvas izquierdo
    if (canvas_izq.winfo_rootx() <= x_canvas_izq <= canvas_izq.winfo_rootx() + canvas_izq.winfo_width() and
        canvas_izq.winfo_rooty() <= y_canvas_izq <= canvas_izq.winfo_rooty() + canvas_izq.winfo_height()):
        if event.state & 0x0001:  # Si Shift está presionado
            canvas_izq.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            canvas_izq.yview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind_all("<MouseWheel>", _on_mousewheel)


def cerrar_programa():
    """Función que se ejecuta al cerrar la ventana para limpiar y salir."""
    print("Cerrando programa...")  #Mensaje opcional
    root.quit()  #Detiene el loop de Tkinter
    root.destroy()  #Cierra la ventana completamente
    exit()  #Asegura que todo el proceso termine

root.protocol("WM_DELETE_WINDOW", cerrar_programa)

if __name__ == "__main__":
    root.mainloop()