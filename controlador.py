# controlador_mysql.py
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox, filedialog
import SimpleITK as sitk
import numpy as np
from datetime import datetime
import numpy as np
from scipy.stats import kurtosis, entropy
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# la libreria dicom se encuentra en una funcion llamada procesar_imagen_dicom, sirve para visualizar y extraer la informacion de los archivos dicom 


class BaseDatosMySQL:
    print("control 1")
    def __init__(self, host="localhost", user="root", password="info2024", database="radiomica"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexion = self.obtener_conexion()

    def obtener_conexion(self):
        conexion = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
            )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos MySQL.")
            return conexion
        else:
            print("Error de conexión No se pudo conectar a la base de datos")
            return None

    def configurar_base_datos(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute('''  # Crear las tablas si no existen
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255),
                    edad INT,
                    genero VARCHAR(10),
                    historial_medico TEXT,
                    fecha_ingreso DATE
                )
            ''')
            cursor.execute('''  # Crear la tabla de características
                CREATE TABLE IF NOT EXISTS caracteristicas_imagen (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_paciente INT,
                    promedio FLOAT,
                    desviacion_estandar FLOAT,
                    valor_maximo FLOAT,
                    valor_minimo FLOAT,
                    rango FLOAT,
                    mediana FLOAT,
                    varianza FLOAT,
                    FOREIGN KEY (id_paciente) REFERENCES pacientes(id)
                )
            ''')
            self.conexion.commit()
            print("Tablas configuradas correctamente.")
        except Error as e:
            messagebox.showerror("Error", f"No se pudo configurar la base de datos: {e}")


    def insertar_paciente(self, ID, nombre, edad, genero, historial_medico, fecha_ingreso):
        cursor = self.conexion.cursor()
        fecha_ingreso = datetime.strptime(fecha_ingreso, '%m/%d/%Y').strftime('%Y-%m-%d')
        consulta = '''
            INSERT INTO pacientes (ID, nombre, edad, genero, historial_medico, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s,%s)
        '''
        print(f"Paciente {nombre} de {edad} años, género {genero}, ingresado el {fecha_ingreso} ha sido agregado correctamente.")
        # Ejecutando la consulta
        valores = (ID, nombre, edad, genero, historial_medico, fecha_ingreso)
        cursor.execute(consulta, valores)
        # Confirmando la transacción
        self.conexion.commit()
        cursor.close()



class ControladorPacientes:
    def __init__(self, conexion_db):
        self.conexion_db = conexion_db  # Aquí pasas la conexión a la base de datos
        print("Controlador de pacientes inicializado.")

    def crear_tabla_caracteristicas(self):
        cursor = None
        try:
            cursor = self.conexion_db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS caracteristicas_paciente (
                    id_caracteristica INT AUTO_INCREMENT PRIMARY KEY,
                    id_paciente INT NOT NULL,
                    media FLOAT NOT NULL,
                    mediana FLOAT NOT NULL,
                    moda FLOAT NOT NULL,
                    desviacion_estandar FLOAT NOT NULL,
                    varianza FLOAT NOT NULL,
                    kurtosis FLOAT NOT NULL,
                    entropia FLOAT NOT NULL,
                    volumen FLOAT NOT NULL,
                    area_superficie FLOAT NOT NULL,
                    elongacion FLOAT NOT NULL,
                    FOREIGN KEY (id_paciente) REFERENCES pacientes(id)
                );
            """)
            self.conexion_db.commit()
            print("Tabla 'caracteristicas_paciente' creada o ya existe.")
        except mysql.connector.Error as err:
            print(f"Error al crear la tabla 'caracteristicas_paciente': {err}")
        finally:
            if cursor:
                cursor.close()

    def cargar_neuroimagen_y_extraer_caracteristicas(self, archivo_dicom, id_paciente):
        cursor= None
        try:
            self.crear_tabla_caracteristicas()
            # Validar que el ID del paciente existe en la tabla `pacientes`
            cursor = self.conexion_db.cursor()
            cursor.execute("SELECT COUNT(*) FROM pacientes WHERE id = %s", (id_paciente,))
            if cursor.fetchone()[0] == 0:
                raise ValueError(f"El paciente con ID {id_paciente} no existe.")

            # Procesar la imagen DICOM
            imagen_dicom = self.procesar_imagen_dicom(archivo_dicom)

            # Extraer características
            media = np.mean(imagen_dicom)
            mediana = np.median(imagen_dicom)
            moda = float(np.bincount(imagen_dicom.flatten().astype(int)).argmax())
            desviacion_estandar = np.std(imagen_dicom)
            varianza = np.var(imagen_dicom)
            kurtosis_val = kurtosis(imagen_dicom.flatten())
            entropia_val = entropy(np.histogram(imagen_dicom, bins=256)[0])
            volumen = np.sum(imagen_dicom > 0)  # Suponiendo que es volumen de píxeles no nulos
            area_superficie = np.sum(imagen_dicom > 0)  # Placeholder
            elongacion = 0.0  # Calcula la elongación según tu criterio

            media = float(np.mean(imagen_dicom))
            mediana = float(np.median(imagen_dicom))
            moda = float(np.bincount(imagen_dicom.flatten().astype(int)).argmax())
            desviacion_estandar = float(np.std(imagen_dicom))
            varianza = float(np.var(imagen_dicom))
            kurtosis_val = float(kurtosis(imagen_dicom.flatten()))
            entropia_val = float(entropy(np.histogram(imagen_dicom, bins=256)[0]))
            volumen = int(np.sum(imagen_dicom > 0))
            area_superficie = int(np.sum(imagen_dicom > 0))  # Placeholder
            elongacion = float(0.0)  # Calcula la elongación según tu criterio


            # Insertar características en la tabla `caracteristicas_paciente`
            cursor.execute("""
                INSERT INTO caracteristicas_paciente (
                    id_paciente, media, mediana, moda, desviacion_estandar, 
                    varianza, kurtosis, entropia, volumen, area_superficie, elongacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_paciente, media, mediana, moda, desviacion_estandar, varianza, kurtosis_val,
                  entropia_val, volumen, area_superficie, elongacion))
            self.conexion_db.commit()
            print(f"Características de la imagen del paciente {id_paciente} guardadas correctamente.")
        except Exception as e:
            print(f"Error al cargar y procesar la neuroimagen: {e}")
        finally:
            if cursor:
                cursor.close()

    def obtener_paciente(self, paciente_id):
        cursor = self.conexion_db.cursor(dictionary=True)
        query = "SELECT * FROM pacientes WHERE id = %s"
        cursor.execute(query, (paciente_id,))
        paciente = cursor.fetchone()
        return paciente

    def procesar_imagen_dicom(self, archivo_dicom):
        """
        Función para cargar y procesar una imagen DICOM.
        Retorna la imagen como un arreglo NumPy.
        """
        import pydicom
        ds = pydicom.dcmread(archivo_dicom)
        return ds.pixel_array
    
    def agregar_paciente(self, ID, nombre, edad, genero, historial_medico, fecha_ingreso):
        # Conectando con la base de datos
        cursor = self.conexion_db.cursor()

        fecha_ingreso = datetime.strptime(fecha_ingreso, '%m/%d/%Y').strftime('%Y-%m-%d')
        # Preparando la consulta SQL de inserción
        consulta = """INSERT INTO pacientes (ID, nombre, edad, genero, historial_medico, fecha_ingreso) 
                    VALUES (%s, %s, %s, %s, %s,%s)"""
                    
        valores = (ID, nombre, edad, genero, historial_medico, fecha_ingreso)
        print("control")
        try:
            # Ejecutando la consulta
            cursor.execute(consulta, valores)
            # Confirmando la transacción
            self.conexion_db.commit()
            print(f"Paciente {nombre} de {edad} años, género {genero}, ingresado el {fecha_ingreso} ha sido agregado correctamente.")
        except mysql.connector.Error as err:
            print(f"Error al insertar el paciente: {err}")
        finally:
            # Cerramos el cursor
            cursor.close()

    def editar_paciente(self, id_paciente, nombre, edad, genero, historial_medico, fecha_ingreso):
        cursor = self.conexion_db.cursor()
        query = """
        UPDATE pacientes
        SET nombre = %s, edad = %s, genero = %s, historial_medico = %s, fecha_ingreso = %s
        WHERE id = %s
        """
        cursor.execute(query, (nombre, edad, genero, historial_medico, fecha_ingreso, id_paciente))
        self.conexion_db.commit() 

    def obtener_paciente(self, paciente_id):
        # Realiza la consulta SQL para obtener el paciente
        cursor = self.conexion_db.cursor()
        query = "SELECT * FROM pacientes WHERE id = %s"
        cursor.execute(query, (paciente_id,))
    
        # Obtenemos la descripción de las columnas
        columns = [desc[0] for desc in cursor.description]
    
        # Obtenemos una fila como tupla y la convertimos a diccionario
        paciente = cursor.fetchone()
        if paciente:
            paciente_dict = dict(zip(columns, paciente))  # Convertir la tupla en diccionario
        else:
            paciente_dict = None
    
        cursor.close()
        return paciente_dict


    def eliminar_paciente(self, paciente_id):
        try:
            cursor = self.conexion_db.cursor()
        
            # Primero eliminar todas las referencias en otras tablas que dependen del paciente (por ejemplo, características o imágenes)
            query = "DELETE FROM caracteristicas_paciente WHERE id_paciente = %s"
            cursor.execute(query, (paciente_id,))
        
            # Eliminar el paciente de la tabla principal
            query = "DELETE FROM pacientes WHERE id = %s"
            cursor.execute(query, (paciente_id,))
        
            # Confirmar los cambios en la base de datos
            self.conexion_db.commit()
            cursor.close()

        except Exception as e:
            self.conexion_db.rollback()  # Hacer rollback si ocurre un error
            cursor.close()
            raise Exception(f"Error al eliminar el paciente: {str(e)}")  # Lanza el error hacia arriba

    def eliminar_caracteristicas_paciente(self, paciente_id):
        try:
            cursor = self.conexion_db.cursor()
            # Eliminar las características del paciente
            query = "DELETE FROM caracteristicas_paciente WHERE id_paciente = %s"
            cursor.execute(query, (paciente_id,))
        
            # Confirmar los cambios en la base de datos
            self.conexion_db.commit()
            cursor.close()

        except Exception as e:
            self.conexion_db.rollback()  # Hacer rollback si ocurre un error
            cursor.close()
            raise Exception(f"Error al eliminar las características del paciente: {str(e)}")  # Lanza el error hacia arriba
    
    