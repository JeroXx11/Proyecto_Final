import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
from tkcalendar import DateEntry
from controlador import ControladorPacientes
import mysql.connector
from datetime import datetime
import mysql.connector


class VistaPacientes:
    def __init__(self):
        # Establece la conexión con la base de datos
        self.conexion_db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="info2024",
            database="radiomica"
        )
        if self.conexion_db.is_connected():
            cursor = self.conexion_db.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"Conectado a la base de datos: {db_name[0]}")
        else:
            print("No se pudo establecer la conexión con la base de datos.")
        
        self.c = ControladorPacientes(self.conexion_db)
        print("Vista de pacientes inicializada.")
        
    def obtener_datos(self, nombre_entry, edad_entry, genero_combobox, historial_medico_text, fecha_ingreso_entry):
        nombre = nombre_entry.get()
        edad = edad_entry.get()
        genero = genero_combobox.get()
        historial_medico = historial_medico_text.get("1.0", "end-1c")
        fecha_ingreso = fecha_ingreso_entry.get()
        self.c.agregar_paciente(nombre, edad, genero, historial_medico, fecha_ingreso)
        return


    def pedir_id_paciente(self, archivo_dicom):
        ventana_entrada = tk.Toplevel()
        ventana_entrada.title("Ingresar ID del Paciente")
        ventana_entrada.geometry("300x150")

        etiqueta = tk.Label(ventana_entrada, text="Por favor, ingresa el ID del paciente:")
        etiqueta.pack(pady=10)

        id_paciente_entry = tk.Entry(ventana_entrada)
        id_paciente_entry.pack(pady=10)

        def obtener_id():
            id_paciente = id_paciente_entry.get()
            if id_paciente:
                ventana_entrada.destroy()
                # Ahora pasa el archivo DICOM y el ID a la lógica de procesamiento
                self.c.cargar_neuroimagen_y_extraer_caracteristicas(archivo_dicom, id_paciente)
            else:
             messagebox.showwarning("Advertencia", "El ID del paciente es obligatorio.")

        boton_aceptar = tk.Button(ventana_entrada, text="Aceptar", command=obtener_id)
        boton_aceptar.pack(pady=10)

        ventana_entrada.transient()
        ventana_entrada.grab_set()
        ventana_entrada.mainloop()


    def cargar_neuroimagen(self):
        archivo_dicom = filedialog.askopenfilename(
            title="Selecciona la imagen DICOM",
            filetypes=[("Archivos DICOM", "*.dcm")]
        )
        if archivo_dicom:
            self.pedir_id_paciente(archivo_dicom)

    def crear_ventana_agregar_paciente(self):
        ventana_agregar = tk.Toplevel()
        ventana_agregar.title("Formulario de Paciente")
        ventana_agregar.geometry("400x400")
        ventana_agregar.config(bg="#f5f5f5")

        titulo = tk.Label(ventana_agregar, text="Formulario de Paciente", font=("Arial", 16), bg="#f5f5f5")
        titulo.pack(pady=20)

        label_nombre = tk.Label(ventana_agregar, text="Nombre", font=("Arial", 12), bg="#f5f5f5")
        label_nombre.pack(pady=5)
        entry_nombre = tk.Entry(ventana_agregar)
        entry_nombre.pack(pady=5, padx=20)

        label_edad = tk.Label(ventana_agregar, text="Edad", font=("Arial", 12), bg="#f5f5f5")
        label_edad.pack(pady=5)
        entry_edad = tk.Entry(ventana_agregar)
        entry_edad.pack(pady=5, padx=20)

        label_genero = tk.Label(ventana_agregar, text="Género", font=("Arial", 12), bg="#f5f5f5")
        label_genero.pack(pady=5)
        entry_genero = ttk.Combobox(ventana_agregar, values=["Masculino", "Femenino", "Otro"], state="readonly")
        entry_genero.pack(pady=5, padx=20)

        label_historial = tk.Label(ventana_agregar, text="Historial Médico", font=("Arial", 12), bg="#f5f5f5")
        label_historial.pack(pady=5)
        entry_historial = tk.Text(ventana_agregar, height=5, width=40)
        entry_historial.pack(pady=5, padx=20)

        label_fecha_ingreso = tk.Label(ventana_agregar, text="Fecha de Ingreso", font=("Arial", 12), bg="#f5f5f5")
        label_fecha_ingreso.pack(pady=5)
        entry_fecha_ingreso = DateEntry(ventana_agregar, date_pattern="mm/dd/yyyy")
        entry_fecha_ingreso.pack(pady=5, padx=20)

        agregar_paciente_btn = tk.Button(ventana_agregar, text="Agregar Paciente", command=lambda: self.obtener_datos(
            entry_nombre, entry_edad, entry_genero, entry_historial, entry_fecha_ingreso))
        agregar_paciente_btn.pack(pady=20)

    def abrir_ventana_principal(self):
        ventana = tk.Tk()
        ventana.title("Gestión de Pacientes")
        ventana.geometry("600x400")
        ventana.config(bg="#f5f5f5")

        titulo = tk.Label(ventana, text="Gestión de Pacientes", font=("Arial", 18, "bold"), anchor="center")
        titulo.pack(pady=20)

        agregar_paciente_btn = tk.Button(ventana, text="Agregar Paciente", command=self.crear_ventana_agregar_paciente)
        agregar_paciente_btn.pack(pady=20)

        cargar_imagen_btn = tk.Button(ventana, text="Cargar Neuroimagen", command=self.cargar_neuroimagen)
        cargar_imagen_btn.pack(pady=20)

        ventana.mainloop()

# Instancia de Vista
if __name__ == "__main__":
    vista = VistaPacientes()  # Aquí se crea la vista con la conexión a la base de datos
    vista.abrir_ventana_principal()
