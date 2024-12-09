import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
from tkcalendar import DateEntry
from controlador import ControladorPacientes
import mysql.connector
from datetime import datetime
import mysql.connector
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VistaPacientes:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x800")  # Tamaño de la ventana principal
        self.root.title("Gestión de Pacientes")
        self.root.config(bg="#87CEEB")  # Establecer el color de fondo de la ventana azul

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Crear un Frame dentro de la ventana principal para contener los widgets
        frame = tk.Frame(self.root, bg="#87CEEB")  # El color del fondo del frame es azul
        frame.pack(fill="both", expand=True)  # El Frame ocupa todo el espacio disponible en la ventana

        # Crear una etiqueta dentro del Frame

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Pacientes")
         # Crear un Canvas para la barra de desplazamiento

        # Crear un Canvas para la barra de desplazamiento
        self.canvas = tk.Canvas(self.tab1)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Crear una barra de desplazamiento vertical
        self.scrollbar_y = tk.Scrollbar(self.tab1, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")

        # Configurar la vista del Canvas con la barra de desplazamiento
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        # Crear un Frame dentro del Canvas que contendrá los widgets
        self.frame_tab1 = tk.Frame(self.canvas)

        # Establecer la ventana del canvas en el frame_tab1
        self.canvas.create_window((0, 0), window=self.frame_tab1, anchor="nw")

        # Agregar contenido dentro del frame
        self.lista_tablas_label = tk.Label(self.frame_tab1, text="Selecciona una tabla:")
        self.lista_tablas_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.lista_tablas = ttk.Combobox(self.frame_tab1, values=["pacientes", "caracteristica_paciente"])
        self.lista_tablas.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.cargar_tablas_button = tk.Button(self.frame_tab1, text="Mostrar Tablas", command=self.mostrar_tablas)
        self.cargar_tablas_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.texto_datos = tk.Text(self.frame_tab1, height=15, width=100)
        self.texto_datos.grid(row=2, column=0, columnspan=2, pady=10)

        self.label_id = tk.Label(self.frame_tab1, text="Ingrese ID de Paciente:")
        self.label_id.grid(row=3, column=0, pady=10)

        self.entry_id = tk.Entry(self.frame_tab1)
        self.entry_id.grid(row=3, column=1, pady=10)

        self.boton_ver_graficas = tk.Button(self.frame_tab1, text="Ver Gráficas", command=self.mostrar_graficas)
        self.boton_ver_graficas.grid(row=4, column=0, columnspan=2, pady=10)

        # Actualizar el área visible dentro del canvas
        self.frame_tab1.update_idletasks()  # Para obtener el tamaño real de los widgets dentro del frame

        # Establecer la región de desplazamiento del Canvas
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Asegurarse de que el contenido se expanda con la ventana
        self.tab1.grid_rowconfigure(0, weight=1)  # Hacer que la fila 0 ocupe todo el espacio vertical
        self.tab1.grid_columnconfigure(0, weight=1)


        label = tk.Label(frame, bg="#87CEEB", fg="black")
        label.pack(pady=20)  

        # Crear un notebook (pestañas)
        # Conexión a la base de datos
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
        
        # Controlador que manejará la lógica de las tablas
        self.c = ControladorPacientes(self.conexion_db)
        print("Vista de pacientes inicializada.")

    def obtener_datos(self, ID_entry, nombre_entry, edad_entry, genero_combobox, historial_medico_text, fecha_ingreso_entry):
        ID= ID_entry.get()
        nombre = nombre_entry.get()
        edad = edad_entry.get()
        genero = genero_combobox.get()
        historial_medico = historial_medico_text.get("1.0", "end-1c")
        fecha_ingreso = fecha_ingreso_entry.get()
        self.c.agregar_paciente(ID,nombre, edad, genero, historial_medico, fecha_ingreso)
        return

    def editar_paciente(self):
        # Ventana para editar los datos del paciente
        ventana_editar = tk.Toplevel()
        ventana_editar.title("Editar Paciente")
        ventana_editar.geometry("400x600")
        ventana_editar.config(bg="#f5f5f5")

        # Solicitar el ID del paciente a editar
        label_id = tk.Label(ventana_editar, text="ID del Paciente", font=("Arial", 12),  bg="#87CEEB", fg="black")
        label_id.pack(pady=5)
        entry_id = tk.Entry(ventana_editar)
        entry_id.pack(pady=5, padx=20)

        def cargar_datos_paciente():
            paciente_id = entry_id.get()
            if paciente_id.isdigit():
                paciente_id = int(paciente_id)
                paciente = self.c.obtener_paciente(paciente_id)
                if paciente:
                    # Poblamos los campos con los datos del paciente
                    entry_nombre.delete(0, tk.END)
                    entry_nombre.insert(0, paciente['nombre'])

                    entry_edad.delete(0, tk.END)
                    entry_edad.insert(0, paciente['edad'])

                    entry_genero.set(paciente['genero'])

                    entry_historial.delete(1.0, tk.END)
                    entry_historial.insert(tk.END, paciente['historial_medico'])

                    entry_fecha_ingreso.set_date(paciente['fecha_ingreso'])
                else:
                    messagebox.showerror("Error", "Paciente no encontrado.")
            else:
                messagebox.showwarning("Advertencia", "Por favor ingrese un ID válido.")

        btn_cargar_datos = tk.Button(ventana_editar, text="Cargar Datos", command=cargar_datos_paciente)
        btn_cargar_datos.pack(pady=10)

        label_nombre = tk.Label(ventana_editar, text="Nombre", font=("Arial", 12),  bg="#87CEEB", fg="black")
        label_nombre.pack(pady=5)
        entry_nombre = tk.Entry(ventana_editar)
        entry_nombre.pack(pady=5, padx=20)

        label_edad = tk.Label(ventana_editar, text="Edad", font=("Arial", 12),  bg="#87CEEB", fg="black")
        label_edad.pack(pady=5)
        entry_edad = tk.Entry(ventana_editar)
        entry_edad.pack(pady=5, padx=20)

        label_genero = tk.Label(ventana_editar, text="Género", font=("Arial", 12),  bg="#87CEEB", fg="black")
        label_genero.pack(pady=5)
        entry_genero = ttk.Combobox(ventana_editar, values=["Masculino", "Femenino", "Otro"], state="readonly")
        entry_genero.pack(pady=5, padx=20)

        label_historial = tk.Label(ventana_editar, text="Historial Médico", font=("Arial", 12),  bg="#87CEEB", fg="black")
        label_historial.pack(pady=5)
        entry_historial = tk.Text(ventana_editar, height=5, width=40)
        entry_historial.pack(pady=5, padx=20)

        label_fecha_ingreso = tk.Label(ventana_editar, text="Fecha de Ingreso", font=("Arial", 12),  bg="#87CEEB", fg="black")
        label_fecha_ingreso.pack(pady=5)
        entry_fecha_ingreso = DateEntry(ventana_editar, date_pattern="mm/dd/yyyy")
        entry_fecha_ingreso.pack(pady=5, padx=20)

        def guardar_datos_paciente():
            paciente_id = entry_id.get() 
            nombre = entry_nombre.get()
            edad = entry_edad.get()
            genero = entry_genero.get()
            historial_medico = entry_historial.get("1.0", "end-1c")
            fecha_ingreso = entry_fecha_ingreso.get()
            
            if paciente_id.isdigit():
                paciente_id = int(paciente_id)
                fecha_ingreso = datetime.strptime(fecha_ingreso, '%m/%d/%Y').strftime('%Y-%m-%d')
                self.c.editar_paciente(paciente_id, nombre, edad, genero, historial_medico, fecha_ingreso)
                messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
                ventana_editar.destroy()
            else:
                messagebox.showerror("Error", "Error al actualizar el paciente.")

        # Botón para guardar los cambios
        btn_guardar = tk.Button(ventana_editar, text="Guardar Cambios", command=guardar_datos_paciente)
        btn_guardar.pack(pady=10)


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
        # Abrir cuadro de diálogo para seleccionar el archivo DICOM
        archivo_dicom = filedialog.askopenfilename(
            title="Selecciona la imagen DICOM",
            filetypes=[("Archivos DICOM", "*.dcm")]
        )
    
        if archivo_dicom:
            # Ventana emergente para solicitar el ID del paciente
            ventana_id = tk.Toplevel()
            ventana_id.title("ID del Paciente")

            tk.Label(ventana_id, text="Ingresa el ID del paciente:").pack(pady=10)
            entry_id_paciente = tk.Entry(ventana_id)
            entry_id_paciente.pack(pady=10)

            # Botón para confirmar el ID del paciente
            btn_confirmar = tk.Button(
                ventana_id,
                text="Confirmar",
                command=lambda: self.procesar_imagen_y_guardar(
                    archivo_dicom, entry_id_paciente.get(), ventana_id
                )
            )
            btn_confirmar.pack(pady=10)


    def procesar_imagen_y_guardar(self, archivo_dicom, id_paciente, ventana_id):
        try:
        # Validar que se ingresó un ID
            if not id_paciente.isdigit():
                raise ValueError("El ID del paciente debe ser un número válido.")
        
            id_paciente = int(id_paciente)  # Convertir a entero
            self.c.cargar_neuroimagen_y_extraer_caracteristicas(archivo_dicom, id_paciente)
            tk.messagebox.showinfo("Éxito", "Características extraídas y guardadas correctamente.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al procesar la imagen: {e}")
        finally:
            ventana_id.destroy()  # Cerrar la ventana emergente
    


    def crear_ventana_agregar_paciente(self):
        ventana_agregar = tk.Toplevel()
        ventana_agregar.title("Formulario de Paciente")
        ventana_agregar.geometry("400x600")
        ventana_agregar.config(bg="#F1E6FF")

        # aqui intentamos ponerle color a las ventanas pero este proceso conlleva descargar una nueva libreria
        # y crear un nuevo estilo para modificar como se desee, pero decidimos dejarlo asi 


        titulo = tk.Label(ventana_agregar, text="Formulario de Paciente", font=("Arial", 16), bg="#E6D0FF",  fg="black")
        titulo.pack(pady=20)

        label_ID = tk.Label(ventana_agregar, text="ID", font=("Arial", 12), bg="#87CEEB", fg="black")
        label_ID.pack(pady=5)

        entry_ID = tk.Entry(ventana_agregar)
        entry_ID.pack(pady=5, padx=20) 


        label_nombre = tk.Label(ventana_agregar, text="Nombre", font=("Arial", 12), bg="#87CEEB", fg="black")
        label_nombre.pack(pady=5)
        entry_nombre = tk.Entry(ventana_agregar)
        entry_nombre.pack(pady=5, padx=20)

        label_edad = tk.Label(ventana_agregar, text="Edad", font=("Arial", 12), bg="#87CEEB", fg="black")
        label_edad.pack(pady=5)
        entry_edad = tk.Entry(ventana_agregar)
        entry_edad.pack(pady=5, padx=20)

        label_genero = tk.Label(ventana_agregar, text="Género", font=("Arial", 12), bg="#87CEEB", fg="black")
        label_genero.pack(pady=5)
        entry_genero = ttk.Combobox(ventana_agregar, values=["Masculino", "Femenino", "Otro"], state="readonly")
        entry_genero.pack(pady=5, padx=20)

        label_historial = tk.Label(ventana_agregar, text="Historial Médico", font=("Arial", 12), bg="#87CEEB", fg="black")
        label_historial.pack(pady=5)
        entry_historial = tk.Text(ventana_agregar, height=5, width=40)
        entry_historial.pack(pady=5, padx=20)

        label_fecha_ingreso = tk.Label(ventana_agregar, text="Fecha de Ingreso", font=("Arial", 12), bg="#87CEEB", fg="black")
        label_fecha_ingreso.pack(pady=5)
        entry_fecha_ingreso = DateEntry(ventana_agregar, date_pattern="mm/dd/yyyy")
        entry_fecha_ingreso.pack(pady=5, padx=20)

        agregar_paciente_btn = tk.Button(ventana_agregar, text="Agregar Paciente", command=lambda: self.obtener_datos(
            entry_ID, entry_nombre, entry_edad, entry_genero, entry_historial, entry_fecha_ingreso))
        agregar_paciente_btn.pack(pady=20)
    

    def borrar_paciente(self):
        # Pedir al usuario el ID del paciente a eliminar
        paciente_id = simpledialog.askstring("Eliminar Paciente", "Ingresa el ID del paciente a eliminar:")

        if paciente_id:
            if paciente_id.isdigit():
                paciente_id = int(paciente_id)
                try:
                    # Obtener las imágenes asociadas al paciente
                    paciente = self.c.obtener_paciente(paciente_id)
                
                    if paciente:
                        # Eliminar las características del paciente
                        self.c.eliminar_caracteristicas_paciente(paciente_id)
                    
                        # Obtener las imágenes asociadas
                        imagenes = paciente.get('imagenes')
                    
                        if imagenes:
                            # Si tiene imágenes, eliminarlas
                            for imagen in imagenes.split(','):
                                if os.path.exists(imagen):
                                    os.remove(imagen)  # Eliminar la imagen
                            # Eliminar las imágenes de la base de datos
                    
                        # Eliminar el paciente de la base de datos
                        self.c.eliminar_paciente(paciente_id)
                        messagebox.showinfo("Éxito", "Paciente y sus imágenes eliminados correctamente.")
                    else:
                        messagebox.showerror("Error", "Paciente no encontrado.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar el paciente: {str(e)}")
            else:
                messagebox.showerror("Error", "El ID del paciente es inválido.")


    def obtener_paciente(self, paciente_id):
        # Simulación de obtener un paciente desde la base de datos
        # Aquí debería ir la consulta real a la base de datos
        if paciente_id == 1:  # Ejemplo, si el ID es 1, simula que existe
            return {'imagenes': 'ruta_imagen1.jpg,ruta_imagen2.jpg'}  # Simulamos que tiene imágenes
        elif paciente_id == 2:  # Ejemplo, si el ID es 2, simula que no tiene imágenes
            return {'imagenes': ''}
        else:
            return None

    def eliminar_paciente(self, paciente_id):
        cursor = self.conexion_db.cursor()
        query = "DELETE FROM pacientes WHERE id = %s"
        cursor.execute(query, (paciente_id,))
        self.conexion_db.commit()  # Confirmamos la eliminación del paciente
        cursor.close()
        print(f"Paciente con ID {paciente_id} eliminado de la base de datos.")



    def eliminar_imagenes_de_base_datos(self, paciente_id):
        cursor = self.conexion_db.cursor()
        query = "DELETE FROM caracteristicas_paciente WHERE id_paciente = %s"
        cursor.execute(query, (paciente_id,))
        self.conexion_db.commit()  # Confirmamos la eliminación de las características asociadas
        cursor.close()
        print(f"Características asociadas al paciente con ID {paciente_id} eliminadas de la base de datos.")


    def mostrar_tablas(self):
        # Obtener el nombre de la tabla seleccionada
        tabla = self.lista_tablas.get()

        if tabla == "pacientes":
            self.mostrar_pacientes()
        elif tabla == "caracteristica_paciente":
            self.mostrar_caracteristicas_paciente()

    def mostrar_pacientes(self):
        # Aquí agregas el código para mostrar la tabla de pacientes
        print("Mostrando la tabla de pacientes")
    
        # Ejecutar la consulta SQL
        cursor = self.conexion_db.cursor()
        cursor.execute("SELECT * FROM pacientes")
    
        # Obtener los nombres de las columnas
        column_names = [desc[0] for desc in cursor.description]
    
        # Obtener los datos de la consulta
        datos = cursor.fetchall()
    
        # Limpiar el área de texto
        self.texto_datos.delete(1.0, tk.END)
    
        # Mostrar los nombres de las columnas
        self.texto_datos.insert(tk.END, " | ".join(column_names) + "\n")
        self.texto_datos.insert(tk.END, "-" * 100 + "\n")  # Para separar las columnas de los datos

        # Mostrar los datos de la tabla
        for row in datos:
            self.texto_datos.insert(tk.END, " | ".join(map(str, row)) + "\n")

    def mostrar_caracteristicas_paciente(self):
        # Aquí agregas el código para mostrar la tabla de caracteristicas_paciente
        print("Mostrando la tabla de caracteristicas_paciente")
    
        # Ejecutar la consulta SQL
        cursor = self.conexion_db.cursor()
        cursor.execute("SELECT * FROM caracteristicas_paciente")
    
        # Obtener los nombres de las columnas
        column_names = [desc[0] for desc in cursor.description]
    
        # Obtener los datos de la consulta
        datos = cursor.fetchall()
    
        # Limpiar el área de texto
        self.texto_datos.delete(1.0, tk.END)
    
        # Mostrar los nombres de las columnas
        self.texto_datos.insert(tk.END, " | ".join(column_names) + "\n")
        self.texto_datos.insert(tk.END, "-" * 100 + "\n")  # Para separar las columnas de los datos

        # Mostrar los datos de la tabla
        for row in datos:
            self.texto_datos.insert(tk.END, " | ".join(map(str, row)) + "\n")
    
    def salir(self):
        # Crear un cuadro de diálogo para confirmar si el usuario quiere salir
        respuesta = messagebox.askyesno("Salir", "¿Estás seguro de que deseas salir?")
        if respuesta:  # Si el usuario elige "Sí"
            self.root.quit()  # Salir del programa

        
    def abrir_ventana_principal(self):
        ventana = tk.Tk()
        ventana.title("Gestión de Pacientes")
        ventana.geometry("600x400")

        titulo = tk.Label(ventana, text="Gestión de Pacientes", font=("Arial", 18, "bold"), anchor="center", bg="#E6D0FF",  fg="black")
        titulo.pack(pady=20)

        agregar_paciente_btn = tk.Button(ventana, text="Agregar Paciente", command=self.crear_ventana_agregar_paciente)
        agregar_paciente_btn.pack(pady=20)

        cargar_imagen_btn = tk.Button(ventana, text="Cargar Neuroimagen", command=self.cargar_neuroimagen)
        cargar_imagen_btn.pack(pady=20)

        editar_paciente_btn = tk.Button(ventana, text="Editar Paciente", command=self.editar_paciente)
        editar_paciente_btn.pack(pady=20) 

        btn_borrar = tk.Button(ventana, text="Eliminar Paciente", command=self.borrar_paciente)
        btn_borrar.pack(pady=10) 

        salir_programa_btn = tk.Button(ventana, text="Salir del programa", command=self.salir)
        salir_programa_btn.pack(pady=20) 

        ventana.mainloop()


    def mostrar_graficas(self):
        # Pedir el ID del paciente
        id_paciente = simpledialog.askinteger("ID del Paciente", "Introduce el ID del paciente:", parent=self.root)
        if id_paciente is None:
            return  # Si no se ingresa un ID, no hacer nada

        # Conexión a la base de datos MySQL
        conn = mysql.connector.connect(
            host="localhost",  # Dirección del servidor (puede ser localhost o la IP del servidor)
            user="root",  # Tu usuario de MySQL
            password="info2024",  # Tu contraseña de MySQL
            database="radiomica"  # Nombre de la base de datos
        )

        cursor = conn.cursor()

        # Consulta SQL para obtener los datos del paciente por su id_paciente
        cursor.execute('''
            SELECT media, mediana, moda, desviacion_estandar, varianza, kurtosis, entropia, volumen, area_superficie, elongacion
            FROM caracteristicas_paciente
            WHERE id_paciente = %s;
        ''', (id_paciente,))

        datos = cursor.fetchone()

        if datos is None:
            print(f"No se encontraron datos para el paciente con ID {id_paciente}")
            conn.close()
            return
    # Crear una nueva ventana (Toplevel) para mostrar las gráficas ESTO CHATTTT
        ventana_graficas = tk.Toplevel(self.root) 
        ventana_graficas.title("Gráficas de Pacientes")
        ventana_graficas.geometry("800x600")  # Tamaño de la ventana de gráficas

        # Crear un DataFrame con los datos obtenidos
        columnas = ['media', 'mediana', 'moda', 'desvE', 'varianza', 'kurtosis', 'entropia', 'volumen', 'a.Sup', 'elongacion']
        df = pd.DataFrame([datos], columns=columnas)
        print(datos)

        # columnas = ['media', 'mediana', 'moda', 'desviacion_estandar', 'varianza', 'kurtosis', 'entropia', 'volumen', 'area_superficie', 'elongacion']
        # df = pd.DataFrame([datos], columns=columnas)
        # print(datos)

        # Cerrar la conexión con la base de datos
        conn.close()

        # Crear las gráficas con un tamaño adecuado
        fig, axes = plt.subplots(1,2,figsize=(13.8, 7))  # Tamaño más adecuado para ambas gráficas (más pequeñas)
        fig.tight_layout(pad=2.0)  # Ajustar el espaciado entre las subgráficas

        # Gráfico de Dispersión 3D para correlación entre tres características
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(121, projection='3d')

        # Seleccionamos tres características para mostrar la relación, en este caso 'media', 'volumen' y 'entropia'
        ax.scatter(df['media'], df['volumen'], df['entropia'], color='b', alpha=0.7)
        ax.set_xlabel('Media', fontsize=5)
        ax.set_ylabel('Volumen', fontsize=5)
        ax.set_zlabel('Entropía', fontsize=5)
        ax.set_title("Correlación 3D: Media vs Volumen vs Entropía", fontsize=12)

        ax.tick_params(axis='both', which='major', labelsize=5)  # Reducir tamaño de las etiquetas de los ejes
        ax.set_xlabel('Eje X', fontsize=5)  # Reducir tamaño de la etiqueta del eje X
        ax.set_ylabel('Eje Y', fontsize=5)  # Reducir tamaño de la etiqueta del eje Y
        ax.set_title('VOLUMEN', fontsize=12)  # Reducir tamaño del título
        # Gráfico de barras para mostrar la relación entre las características seleccionadas
        
        axes[1].bar(df.columns, df.iloc[0], color='c', alpha=0.7)
        axes[1].set_title("CARACTERISTICAS", fontsize=12)
        axes[1].set_ylabel("Valor", fontsize=10)
        axes[1].tick_params(axis='x', labelsize=8)  # Reducir tamaño de etiquetas en el eje x
        axes[1].tick_params(axis='y', labelsize=8)  # Reducir tamaño de etiquetas en el eje y

        fig.tight_layout()

        # Mostrar la graficas del GUI en la ventana de Tkinter  
        canvas_graficas = FigureCanvasTkAgg(fig, master=ventana_graficas)  # Ligar el gráfico a la ventana
        canvas_graficas.get_tk_widget().grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        canvas_graficas.draw()
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.2)

        # Asegurarse de que el botón "Ver Gráfica" sea visible
        self.boton_ver_graficas.grid(row=4, column=0, columnspan=2, pady=10)


if __name__ == "__main__":
    root= tk.Tk()
    vista = VistaPacientes(root)  # Aquí se crea la vista con la conexión a la base de datos
    vista.abrir_ventana_principal()
