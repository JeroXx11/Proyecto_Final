import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk  # Importamos el módulo ttk para usar Notebook (pestañas)
from datetime import datetime
import mysql.connector
import SimpleITK as sitk
import pandas as pd

# Clase ConexionBaseDatos (tal como la tienes en tu código)
class ConexionBaseDatos:
    def __init__(self, host="localhost", user="root", password="info2024", database="radiomica"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexion = None

    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conexion.is_connected():
                print("Conexión exitosa a la base de datos")
        except mysql.connector.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.conexion = None
        return self.conexion

    def cerrar_conexion(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("Conexión cerrada.")

# Clase GestorDICOM (tal como la tienes en tu código)
class GestorDICOM:
    @staticmethod
    def cargar_imagen_dicom():
        archivo = filedialog.askopenfilename(filetypes=[("DICOM", "*.dcm")])
        if archivo:
            imagen = sitk.ReadImage(archivo)
            print("Imagen cargada exitosamente.")
            sitk.Show(imagen, "Imagen DICOM")
            return imagen, archivo
        return None, None

    @staticmethod
    def agregar_imagen_dicom(id_paciente, imagen, conexion):
        try:
            imagen_binaria = sitk.GetArrayFromImage(imagen).tobytes()
            cursor = conexion.cursor()
            consulta = "INSERT INTO imagenes_dicom (id_paciente, imagen_dicom) VALUES (%s, %s)"
            cursor.execute(consulta, (id_paciente, imagen_binaria))
            conexion.commit()
            print("Imagen DICOM agregada correctamente.")
        except Exception as e:
            print(f"Error al agregar imagen DICOM: {e}")
        finally:
            cursor.close()

    @staticmethod
    def obtener_imagenes_dicom(conexion):
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ruta_imagen FROM imagenes_dicom")
            imagenes = cursor.fetchall()
            return [imagen[0] for imagen in imagenes]
        except mysql.connector.Error as err:
            print(f"Error al obtener imágenes DICOM: {err}")
            return []


# Clase GestorPacientes (tal como la tienes en tu código)
class GestorPacientes:
    @staticmethod
    def crear_tabla_pacientes(conexion):
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100),
                    edad INT,
                    genero VARCHAR(10),
                    historial_medico TEXT,
                    fecha_ingreso DATE
                );
            """)
            print("Tabla 'pacientes' creada o ya existente.")
        except mysql.connector.Error as err:
            print(f"Error al crear la tabla 'pacientes': {err}")
        finally:
            cursor.close()

    @staticmethod
    def insertar_paciente( ID, nombre, edad, genero, historial_medico, fecha_ingreso, conexion):
        try:
            cursor = conexion.cursor()
            fecha_formateada = datetime.strptime(fecha_ingreso, '%m/%d/%Y').strftime('%Y-%m-%d')
            consulta = """
                INSERT INTO pacientes (nombre, edad, genero, historial_medico, fecha_ingreso)
                VALUES (%s, %s, %s, %s, %s.%s)
            """
            cursor.execute(consulta, (ID, nombre, edad, genero, historial_medico, fecha_formateada))
            conexion.commit()
            print(f"Paciente {nombre} agregado correctamente.")
        except mysql.connector.Error as e:
            print(f"Error al insertar paciente: {e}")
        finally:
            cursor.close()

    @staticmethod
    def guardar_pacientes_csv(pacientes, nombre_archivo='pacientes.csv'):
        df = pd.DataFrame([paciente.__dict__ for paciente in pacientes])
        df.to_csv(nombre_archivo, index=False)
        print(f"Datos guardados en {nombre_archivo}")

    @staticmethod
    def editar_paciente(id_paciente, nombre, edad, genero, historial_medico, fecha_ingreso, conexion):
        try:
            cursor = conexion.cursor()
            fecha_formateada = datetime.strptime(fecha_ingreso, '%m/%d/%Y').strftime('%Y-%m-%d')
            consulta = """
                UPDATE pacientes
                SET nombre = %s, edad = %s, genero = %s, historial_medico = %s, fecha_ingreso = %s
                WHERE id = %s
            """
            cursor.execute(consulta, (nombre, edad, genero, historial_medico, fecha_formateada, id_paciente))
            conexion.commit()
            print(f"Paciente {nombre} actualizado correctamente.")
        except mysql.connector.Error as e:
            print(f"Error al actualizar paciente: {e}")
        finally:
            cursor.close()

    def obtener_datos_caracteristicas_paciente(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT media, mediana, moda, desviacion_estandar, varianza, kurtois, entropia, volumen, diagnostico_alzheimer FROM caracteristicas_paciente")
        datos = cursor.fetchall()

        # Crear un DataFrame de Pandas para facilitar la manipulación
        df = pd.DataFrame(datos, columns=["media", "mediana", "moda", "desviacion_estandar", "varianza", "kurtois", "entropia", "volumen", "diagnostico_alzheimer"])

        return df
