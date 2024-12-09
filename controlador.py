# Aquí va el controlador:
# yoguis
# controlador.py
from modelo import cargar_imagen_dicom, segmentar_imagen, agregar_imagen_dicom, insertar_paciente_en_bd, obtener_imagenes_dicom
from tkinter import messagebox
from datetime import datetime
import sqlite3 
# La librería sqlite3 proporciona una interfaz para interactuar con bases de 
# datos SQLite dentro de tus programas Python. Esto incluye la capacidad de crear bases de datos, 
# realizar consultas SQL, insertar datos, actualizar registros, eliminar registros, y trabajar con transacciones.
import SimpleITK as sitk
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import tkinter as tk

from datetime import datetime
from modelo import insertar_paciente_en_bd  # Suponiendo que tienes una función para insertar en la base de datos
insertar_paciente=[]
def convertir_fecha(fecha):
    # Convertir la fecha de formato MM/DD/YYYY a YYYY-MM-DD
    try:
        fecha_convertida = datetime.strptime(fecha, "%m/%d/%Y").strftime("%Y-%m-%d")
        return fecha_convertida
    except ValueError:
        print("Fecha en formato incorrecto")
        return None

def insertar_paciente_controlador(id_paciente, nombre, fecha_ingreso):
    # Convertimos la fecha al formato adecuado antes de insertarla en la base de datos
    fecha_ingreso_correcta = convertir_fecha(fecha_ingreso)
    
    if fecha_ingreso_correcta:  # Solo insertamos si la fecha es válida
        insertar_paciente(id_paciente, nombre, fecha_ingreso_correcta) # A que funcion esta asociadas
    else:
        print("Error: La fecha es inválida, no se puede insertar el paciente.")


def obtener_conexion(tipo_base_datos="sqlite"):
    """Función para obtener una conexión a la base de datos según el tipo especificado."""
    try:
        # if tipo_base_datos == "sqlite":
        #     return sqlite3.connect('radiomica.db')
        if tipo_base_datos == "mysql":
            return mysql.connector.connect(
                host="localhost", 
                user="root", 
                password="info2024", 
                database="radiomica"
            )
        # Solo se trabaja con mysql
        else:
            raise ValueError("Tipo de base de datos no soportado.")
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {e}")
        return None
# Función para manejar el evento de cargar una imagen
import SimpleITK as sitk
# una de las herramientas más populares en el ámbito de la segmentación y el registro de imágenes médicas
from modelo import agregar_imagen_dicom  # Función para insertar imagen en la base de datos

def manejar_cargar_imagen(archivo_imagen):
    """Función para cargar una imagen DICOM desde el archivo."""
    try:
        imagen = sitk.ReadImage(archivo_imagen)  # Leemos la imagen DICOM con SimpleITK
        print("Imagen cargada exitosamente.")
        # Aquí podrías procesar la imagen si es necesario
        return imagen
    # Se lee la imagen normal, si se tiene tiempo mirar se se puede explocionar 
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar la imagen DICOM: {str(e)}")
        return None
    
def manejar_segmentar_imagen(zona, archivo_imagen):
    """Función para segmentar una imagen DICOM en una zona específica."""
    try:
        imagen = sitk.ReadImage(archivo_imagen)  # Leemos la imagen DICOM
        # Aquí implementas el proceso de segmentación basado en la zona
        imagen_segmentada = segmentar(imagen, zona)  # Asume que tienes una función de segmentación
        return imagen_segmentada
# que es segmentar? Creamos función de segmentar?? esto es para que las imagenes se puedan hallar las características 
    except Exception as e:
        messagebox.showerror("Error", f"Error al segmentar la imagen: {str(e)}")
        return None

 
# Función para agregar la imagen DICOM a la base de datos

def manejar_agregar_imagen_dicom(id_paciente, archivo_imagen):
    """Función para agregar la imagen DICOM a la base de datos."""
    try:
        imagen = sitk.ReadImage(archivo_imagen)  # Leemos la imagen DICOM
        # Aquí agregarías la imagen a la base de datos, tal vez almacenándola como un archivo binario
        agregar_imagen_dicom(id_paciente, imagen)  # Llama a la función del modelo para agregarla
        print("Imagen DICOM agregada a la base de datos correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al agregar la imagen DICOM: {str(e)}")
# Agregar función para guardar imagen en archivo binario


# Función para configurar la base de datos y crear las tablas necesarias
def configurar_base_de_datos(tipo_base_datos="sqlite"):
    """Configura la base de datos y crea las tablas necesarias"""
    try:
        # if tipo_base_datos == "sqlite":
        #     # Conexión a la base de datos SQLite
        #     conn = sqlite3.connect('radiomica.db')  # Nombre de la base de datos SQLite
        #     cursor = conn.cursor()

        #     # Crear tabla 'pacientes' si no existe
        #     cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS pacientes (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         nombre TEXT NOT NULL,
        #         edad INTEGER NOT NULL,
        #         genero TEXT NOT NULL,
        #         historial_medico TEXT NOT NULL,
        #         fecha_ingreso TEXT NOT NULL
        #     )
        #     ''')

        #     # Confirmar los cambios y cerrar la conexión
        #     conn.commit()
        #     conn.close()
        #     messagebox.showinfo("Éxito", "Base de datos SQLite configurada correctamente.")

        if tipo_base_datos == "mysql":
            # Conexión a la base de datos MySQL
            conn = mysql.connector.connect(
                host="localhost",  # Cambia por la IP de tu servidor MySQL si es remoto
                user="root",  # Tu usuario de MySQL
                password="info2024",  # Tu contraseña de MySQL
                database="radiomica"  # La base de datos MySQL que estás usando
            )
            cursor = conn.cursor()

            # Crear tabla 'pacientes' si no existe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255),
                edad INT,
                genero VARCHAR(10),
                historial_medico TEXT,
                fecha_ingreso DATE
            )
            ''')

            # Confirmar los cambios y cerrar la conexión
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Base de datos MySQL configurada correctamente.")

    except Exception as e:
        # Manejo de errores con mensaje de error
        messagebox.showerror("Error", f"No se pudo configurar la base de datos: {e}")
# Se comento la base de datos de sqlite


import mysql.connector

def manejar_insertar_paciente(nombre, edad, genero, historial_medico, fecha_ingreso):
    try:
        # Crear conexión a la base de datos
        conexion = mysql.connector.connect(
            host="localhost",      # Cambia esto según tu configuración
            user="root",        # Cambia esto según tu configuración
            password="info2024", # Cambia esto según tu configuración
            database="radiomica" # Cambia esto según tu configuración
        )
        
        # Crear un cursor a partir de la conexión
        cursor = conexion.cursor()

        # Definir la consulta SQL para insertar los datos
        consulta_sql = "INSERT INTO pacientes (nombre, edad, genero, historial_medico, fecha_ingreso) VALUES (%s, %s, %s, %s, %s)"
        valores = (nombre, edad, genero, historial_medico, fecha_ingreso)
        
        # Ejecutar la consulta
        cursor.execute(consulta_sql, valores)

        # Confirmar la transacción
        conexion.commit()

        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

        # Mensaje de éxito
        messagebox.showinfo("Éxito", "Paciente agregado correctamente.")
    except Exception as e:
        # Si hay un error, mostrarlo
        messagebox.showerror("Error", f"Hubo un error al insertar el paciente: {e}")

def agregar_paciente(paciente_id, nombre, edad, genero):
    conn = sqlite3.connect('radiomica.db')  # Asegúrate de que la base de datos esté bien especificada
    c = conn.cursor()

    # Asegúrate de que la tabla pacientes exista
    c.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            paciente_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            edad INTEGER,
            genero TEXT
        );
    ''')

    # Agrega el nuevo paciente
    c.execute("INSERT INTO pacientes (paciente_id, nombre, edad, genero) VALUES (?, ?, ?, ?)",
              (paciente_id, nombre, edad, genero))

    conn.commit()
    conn.close()
# Se debe crear conexion con sql

def manejar_agregar_paciente(paciente_id, nombre, edad, genero):
    """Función para agregar un nuevo paciente a la base de datos."""
    # Llama a la función del modelo para agregar el paciente a la base de datos
    agregar_paciente(paciente_id, nombre, edad, genero)
    print(f"Paciente {nombre} agregado correctamente.")
# esta función esta en controlador, se agrega al modelo o se hace una nueva ya que en modelo no ha funciones con ese tipo

# Función para ver las imágenes DICOM almacenadas
def manejar_ver_imagenes_dicom():
    """Función para ver las imágenes DICOM almacenadas."""
    # Obtener las imágenes DICOM de la base de datos o directorio
    imagenes = obtener_imagenes_dicom()  # Aquí implementas una función que obtenga las imágenes
    if imagenes:
        # Mostrar la primera imagen, o alguna lógica para elegir una
        imagen = sitk.ReadImage(imagenes[0])  # Suponiendo que la lista tiene rutas de imágenes
        sitk.Show(imagen, "Imagen DICOM")
        messagebox.showinfo("Mostrar Imagen", "Imagen DICOM mostrada correctamente.")
    else:
        messagebox.showwarning("No hay imágenes", "No se encontraron imágenes DICOM.")
# Función se debe llamar en vista o se hace una función llamada show para visualizar


# controlador.py (o donde prefieras definirla)
def manejar_cargar_neuroimagen(id_paciente, archivo_imagen):
    # Aquí va la lógica de lo que quieres hacer con el ID y la imagen
    print(f"Se ha cargado la neuroimagen para el paciente {id_paciente} desde {archivo_imagen}")
    # Aquí podrías agregar la lógica para almacenar la imagen en la base de datos
    # o realizar alguna otra operación relacionada con el paciente.


import numpy as np
import SimpleITK as sitk
from modelo import agregar_caracteristicas_al_paciente, guardar_pacientes_en_csv

# Función para extraer características de la imagen
def extraer_caracteristicas(imagen_numpy):
    # Calcular estadísticas básicas sobre la imagen
    promedio = np.mean(imagen_numpy)
    desviacion_estandar = np.std(imagen_numpy)
    valor_maximo = np.max(imagen_numpy)
    valor_minimo = np.min(imagen_numpy)
    rango = valor_maximo - valor_minimo
    mediana = np.median(imagen_numpy)
    varianza = np.var(imagen_numpy)
    
    # Crear un diccionario con las características extraídas
    caracteristicas = {
        "Promedio": promedio,
        "Desviación Estándar": desviacion_estandar,
        "Valor Máximo": valor_maximo,
        "Valor Mínimo": valor_minimo,
        "Rango": rango,
        "Mediana": mediana,
        "Varianza": varianza
    }
    
    return caracteristicas

# SE REPITIO EL CODIGO BORRAR


from modelo import agregar_caracteristicas_al_paciente, guardar_pacientes_en_csv
import numpy as np
import SimpleITK as sitk
from modelo import agregar_caracteristicas_al_paciente

# Función para extraer características de la imagen
def extraer_caracteristicas(imagen_numpy):
    # Calcular estadísticas básicas sobre la imagen
    promedio = np.mean(imagen_numpy)
    desviacion_estandar = np.std(imagen_numpy)
    valor_maximo = np.max(imagen_numpy)
    valor_minimo = np.min(imagen_numpy)
    rango = valor_maximo - valor_minimo
    mediana = np.median(imagen_numpy)
    varianza = np.var(imagen_numpy)
    
    # Crear un diccionario con las características extraídas
    caracteristicas = {
        "Promedio": promedio,
        "Desviación Estándar": desviacion_estandar,
        "Valor Máximo": valor_maximo,
        "Valor Mínimo": valor_minimo,
        "Rango": rango,
        "Mediana": mediana,
        "Varianza": varianza
    }
    
    return caracteristicas

import numpy as np
import pandas as pd
from tkinter import filedialog
import pydicom
import mysql.connector

def cargar_neuroimagen_y_extraer_caracteristicas(archivo_dicom, id_paciente):
    # Cargar la imagen DICOM
    dicom_data = pydicom.dcmread(archivo_dicom)
    imagen = dicom_data.pixel_array  # Suponiendo que la imagen está en pixel_array
    
    # Extraer características con numpy y pandas (esto es solo un ejemplo)
    media = np.mean(imagen)
    desviacion_estandar = np.std(imagen)
    maximo = np.max(imagen)
    minimo = np.min(imagen)
    
    # Crear un DataFrame de pandas con las características
    caracteristicas = pd.DataFrame({
        'Media': [media],
        'Desviación estándar': [desviacion_estandar],
        'Máximo': [maximo],
        'Mínimo': [minimo]
    })
    
    # Imprimir las características extraídas
    print(caracteristicas)
    
    # Agregar las características al paciente en la base de datos
    # Suponiendo que tienes una función para esto en el modelo
    agregar_caracteristicas_al_paciente(id_paciente, caracteristicas)
# PORQUE ESTA SACASDO LAS CARACTERÍSTICAS DE DICOM E IMAGENES
