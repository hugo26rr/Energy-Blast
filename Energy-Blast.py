import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QCheckBox, QColorDialog, QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QGroupBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QTabWidget, QMessageBox
import matplotlib.patches as patches
import math

from datetime import datetime
from time import ctime
import ntplib
import os
from cryptography.fernet import Fernet

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Perfiles de vibracion y energia')
        #self.resize(1200, 950)
        self.setFixedSize(1400, 950) 
        # Crear el layout principal
        main_layout = QGridLayout(self)
        #self.setFixedSize(1200, 1000)

        # Crear la barra de menú
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu("Archivo")

        # Añadir la opción de guardar
        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.guardar_imagen)  # Conectar la acción con la función de guardado
        file_menu.addAction(save_action)

        # Añadir la barra de menú al layout principal
        main_layout.setMenuBar(self.menu_bar)

        # Crear el grupo de controles 'Taladro' (sin el campo "Diámetro")
        taladro_group = QGroupBox("Neyman")
        taladro_layout = QGridLayout()
        taladro_group.setFixedSize(250, 200)

        '''
        # Añadir etiquetas y cajas de texto para otras configuraciones
        label_dens_explosivo = QLabel('Densidad Explosivo (Kg/m3):')
        self.input_dens_explosivo = QLineEdit('1320')
        taladro_layout.addWidget(label_dens_explosivo, 0, 0)
        taladro_layout.addWidget(self.input_dens_explosivo, 0, 1)
        '''
        
        label_energia_explosivo = QLabel('Energía Explosivo (kcal/kg):')
        self.input_energia_explosivo = QLineEdit('920')
        taladro_layout.addWidget(label_energia_explosivo, 0, 0)
        taladro_layout.addWidget(self.input_energia_explosivo, 0, 1)
        

        label_dens_roca = QLabel('Densidad Roca (Kg/m3):')
        self.input_dens_roca = QLineEdit('2500')
        taladro_layout.addWidget(label_dens_roca, 1, 0)
        taladro_layout.addWidget(self.input_dens_roca, 1, 1)

        # Añadir botones
        self.calc_button = QPushButton('CALCULAR')
        self.clear_button = QPushButton('LIMPIAR')
        taladro_layout.addWidget(self.calc_button, 2, 0)
        taladro_layout.addWidget(self.clear_button, 2, 1)

        self.calc_button.clicked.connect(self.calculo_neyman)
        self.clear_button.clicked.connect(self.limpiar_canvas)

        taladro_group.setLayout(taladro_layout)

        # Crear el grupo de controles Holmberg
        holmberg_group = QGroupBox("Holmberg and Persson")
        holmberg_layout = QGridLayout()
        holmberg_group.setFixedSize(250, 130)

        '''
        # Añadir etiquetas y cajas de texto para otras configuraciones
        label_factor_k = QLabel('K factor de velocidad:')
        self.input_factor_k = QLineEdit('219')
        holmberg_layout.addWidget(label_factor_k, 0, 0)
        holmberg_layout.addWidget(self.input_factor_k, 0, 1)

        label_factor_alfa = QLabel('α alfa:')
        self.input_factor_alfa = QLineEdit('0.84')
        holmberg_layout.addWidget(label_factor_alfa, 1, 0)
        holmberg_layout.addWidget(self.input_factor_alfa, 1, 1)
        '''

        # Añadir botones
        self.calc_boton = QPushButton('CALCULAR')
        self.clear_boton = QPushButton('LIMPIAR')
        holmberg_layout.addWidget(self.calc_boton, 2, 0)
        holmberg_layout.addWidget(self.clear_boton, 2, 1)

        self.calc_boton.clicked.connect(self.calculo_holmberg)
        self.clear_boton.clicked.connect(self.limpiar_canvas)

        holmberg_group.setLayout(holmberg_layout)

        # Grupo de controles Energia
        dist_energy_group = QGroupBox("Distribucion de Energia")
        dist_energy_layout = QGridLayout()
        dist_energy_group.setFixedSize(250, 70)

        self.calc_energ_boton = QPushButton('CALCULAR')
        # self.clear_boton = QPushButton('LIMPIAR')
        dist_energy_layout.addWidget(self.calc_energ_boton, 0, 0)
        #holmberg_layout.addWidget(self.clear_boton, 2, 1)
        self.calc_energ_boton.clicked.connect(self.calculo_energia)
        dist_energy_group.setLayout(dist_energy_layout)

        # Crear el grupo de configuraciones para los taladros (con el campo "Diámetro" añadido)
        configuracion_group = QGroupBox("Configuraciones de Taladros")
        configuracion_layout = QGridLayout()
        configuracion_group.setFixedSize(500, 250)

        # Encabezados para las columnas (Taladros 1-4)
        configuracion_layout.addWidget(QLabel("Taladro 1"), 0, 1)
        configuracion_layout.addWidget(QLabel("Taladro 2"), 0, 2)
        configuracion_layout.addWidget(QLabel("Taladro 3"), 0, 3)
        configuracion_layout.addWidget(QLabel("Taladro 4"), 0, 4)

        # Añadir "Distancia desde eje x=0 (m)" como primera fila
        configuracion_layout.addWidget(QLabel("Off Set - Toe (m):"), 1, 0)
        self.input_distancia_t1 = QLineEdit('1')
        self.input_distancia_t2 = QLineEdit('5')
        self.input_distancia_t3 = QLineEdit('11')
        self.input_distancia_t4 = QLineEdit('16')
        configuracion_layout.addWidget(self.input_distancia_t1, 1, 1)
        configuracion_layout.addWidget(self.input_distancia_t2, 1, 2)
        configuracion_layout.addWidget(self.input_distancia_t3, 1, 3)
        configuracion_layout.addWidget(self.input_distancia_t4, 1, 4)

        # Añadir "densidad del explosivo" como primera fila
        configuracion_layout.addWidget(QLabel("Densidad Explosivo (kg/m3):"), 2, 0)
        self.input_dens_explosivo_t1 = QLineEdit('1320')
        self.input_dens_explosivo_t2 = QLineEdit('1320')    
        self.input_dens_explosivo_t3 = QLineEdit('1320')
        self.input_dens_explosivo_t4 = QLineEdit('1320')
        configuracion_layout.addWidget(self.input_dens_explosivo_t1, 2, 1)  
        configuracion_layout.addWidget(self.input_dens_explosivo_t2, 2, 2)
        configuracion_layout.addWidget(self.input_dens_explosivo_t3, 2, 3)
        configuracion_layout.addWidget(self.input_dens_explosivo_t4, 2, 4)


        # Añadir "Diámetro" dinámico para cada taladro como segunda fila
        configuracion_layout.addWidget(QLabel("Diámetro (mm):"), 3, 0)
        self.input_diametro_t1 = QLineEdit('165')
        self.input_diametro_t2 = QLineEdit('270')
        self.input_diametro_t3 = QLineEdit('270')
        self.input_diametro_t4 = QLineEdit('270')
        configuracion_layout.addWidget(self.input_diametro_t1, 3, 1)
        configuracion_layout.addWidget(self.input_diametro_t2, 3, 2)
        configuracion_layout.addWidget(self.input_diametro_t3, 3, 3)
        configuracion_layout.addWidget(self.input_diametro_t4, 3, 4)

        # Etiquetas y entradas para las filas de configuraciones
        configuracion_layout.addWidget(QLabel("Taco (m):"), 4, 0)
        self.input_taco_t1 = QLineEdit('5')
        self.input_taco_t2 = QLineEdit('7')
        self.input_taco_t3 = QLineEdit('7')
        self.input_taco_t4 = QLineEdit('7')
        configuracion_layout.addWidget(self.input_taco_t1, 4, 1)
        configuracion_layout.addWidget(self.input_taco_t2, 4, 2)
        configuracion_layout.addWidget(self.input_taco_t3, 4, 3)
        configuracion_layout.addWidget(self.input_taco_t4, 4, 4)

        configuracion_layout.addWidget(QLabel("Longitud de Carga (m):"), 5, 0)
        self.input_carga_t1 = QLineEdit('3')
        self.input_carga_t2 = QLineEdit('8')
        self.input_carga_t3 = QLineEdit('8')
        self.input_carga_t4 = QLineEdit('8')
        configuracion_layout.addWidget(self.input_carga_t1, 5, 1)
        configuracion_layout.addWidget(self.input_carga_t2, 5, 2)
        configuracion_layout.addWidget(self.input_carga_t3, 5, 3)
        configuracion_layout.addWidget(self.input_carga_t4, 5, 4)

        configuracion_layout.addWidget(QLabel("Segundo Taco (m):"), 6, 0)
        self.input_segundo_taco_t1 = QLineEdit('3')
        self.input_segundo_taco_t2 = QLineEdit('0')
        self.input_segundo_taco_t3 = QLineEdit('0')
        self.input_segundo_taco_t4 = QLineEdit('0')
        configuracion_layout.addWidget(self.input_segundo_taco_t1, 6, 1)
        configuracion_layout.addWidget(self.input_segundo_taco_t2, 6, 2)
        configuracion_layout.addWidget(self.input_segundo_taco_t3, 6, 3)
        configuracion_layout.addWidget(self.input_segundo_taco_t4, 6, 4)

        configuracion_layout.addWidget(QLabel("Segunda Carga (m):"), 7, 0)
        self.input_segunda_carga_t1 = QLineEdit('5')
        self.input_segunda_carga_t2 = QLineEdit('0')
        self.input_segunda_carga_t3 = QLineEdit('0')
        self.input_segunda_carga_t4 = QLineEdit('0')
        configuracion_layout.addWidget(self.input_segunda_carga_t1, 7, 1)
        configuracion_layout.addWidget(self.input_segunda_carga_t2, 7, 2)
        configuracion_layout.addWidget(self.input_segunda_carga_t3, 7, 3)
        configuracion_layout.addWidget(self.input_segunda_carga_t4, 7, 4)

        # Añadir  fila de valores de k 
        configuracion_layout.addWidget(QLabel("K:"), 8, 0)
        self.input_k_t1 = QLineEdit('250')
        self.input_k_t2 = QLineEdit('250')
        self.input_k_t3 = QLineEdit('250')
        self.input_k_t4 = QLineEdit('250')
        configuracion_layout.addWidget(self.input_k_t1, 8, 1)
        configuracion_layout.addWidget(self.input_k_t2, 8, 2)
        configuracion_layout.addWidget(self.input_k_t3, 8, 3)
        configuracion_layout.addWidget(self.input_k_t4, 8, 4)
        
        configuracion_layout.addWidget(QLabel("α:"), 9, 0)
        self.input_alpha_t1 = QLineEdit('1.2')
        self.input_alpha_t2 = QLineEdit('1.2')
        self.input_alpha_t3 = QLineEdit('1.2')
        self.input_alpha_t4 = QLineEdit('1.2')
        configuracion_layout.addWidget(self.input_alpha_t1, 9, 1)
        configuracion_layout.addWidget(self.input_alpha_t2, 9, 2)
        configuracion_layout.addWidget(self.input_alpha_t3, 9, 3)   
        configuracion_layout.addWidget(self.input_alpha_t4, 9, 4)

        configuracion_group.setLayout(configuracion_layout)

        ### Crear nuevo grupo de parámetros para el Talud ###
        talud_group = QGroupBox("Configuraciones de Talud")
        talud_layout = QGridLayout()
        talud_group.setFixedSize(250, 200)

        talud_layout.addWidget(QLabel("Altura de banco (m):"), 0, 0)
        self.input_altura_banco = QLineEdit('16')
        talud_layout.addWidget(self.input_altura_banco, 0, 1)

        talud_layout.addWidget(QLabel("Ángulo de cara (°):"), 1, 0)
        self.input_angulo_cara = QLineEdit('80')
        talud_layout.addWidget(self.input_angulo_cara, 1, 1)

        talud_layout.addWidget(QLabel("Ancho de berma (m):"), 2, 0)
        self.input_ancho_berma = QLineEdit('8.8')
        talud_layout.addWidget(self.input_ancho_berma, 2, 1)

        talud_group.setLayout(talud_layout)
        ### Fin del nuevo grupo de Talud ###

        # Crear el grupo para los rangos de colores (ppv)
        rango_colores_group = QGroupBox("Escala PPV")
        rango_colores_layout = QGridLayout()
        rango_colores_group.setFixedSize(250, 350)

        # Colores iniciales y rangos predefinidos
        colores = ['#FFFFFF', '#808080', '#0000FF', '#00FF00', '#FFFF00', '#FFA500', '#FF0000', '#A52A2A']
        rangos = [(0, 50), (50, 150), (150, 350), (350, 800), (800, 1500), (1500, 3000), (3000, 5000), (5000, 10000000000)]

        # Crear los inputs para los rangos y colores
        self.rangos_input = []
        for i, (rango, color) in enumerate(zip(rangos, colores)):
            valor_inicial = QLineEdit(str(rango[0]))

            # Para el último rango, mostrar '<' en lugar de un valor editable
            if i == len(rangos) - 1:  # Último rango
                valor_final = QLabel('<')  # Mostrar '<' en lugar de un campo editable
                valor_final_operacion = 10000000000  # Valor usado internamente para operaciones
            else:
                valor_final = QLineEdit(str(rango[1]))
                valor_final_operacion = float(rango[1])  # Valor usado para operaciones

            color_button = QPushButton()
            color_button.setStyleSheet(f"background-color: {color}")
            color_button.clicked.connect(lambda _, b=color_button: self.seleccionar_color(b))  # Conectar el color picker a cada botón

            # Crear el checkbox y marcarlo por defecto
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Marcar el checkbox por defecto

            # Almacenar los valores iniciales y finales, y el botón de color
            self.rangos_input.append((checkbox, valor_inicial, valor_final, color_button, valor_final_operacion))

            # Añadir los elementos al layout
            rango_colores_layout.addWidget(checkbox, i, 0)  # Añadir el checkbox en lugar de la etiqueta "Rango"
            rango_colores_layout.addWidget(valor_inicial, i, 1)
            rango_colores_layout.addWidget(QLabel("to"), i, 2)
            rango_colores_layout.addWidget(valor_final, i, 3)
            rango_colores_layout.addWidget(color_button, i, 4)
            rango_colores_layout.addWidget(QLabel("mm/s"), i, 5)

        rango_colores_group.setLayout(rango_colores_layout)

        
        # Crear el grupo para los rangos de colores (ppv)
        rango_colores_energ_group = QGroupBox("Escala Energia")
        rango_colores_energ_layout = QGridLayout()
        rango_colores_energ_group.setFixedSize(250, 350)

        # Colores iniciales y rangos predefinidos
        colores_energ = ['#FFFFFF', '#808080', '#0000FF', '#00FF00', '#FFFF00', '#FFA500', '#FF0000', '#A52A2A']
        rangos_energ = [(0, 0.1), (0.1, 0.713), (0.713, 1.325), (1.325, 1.938), (1.938, 2.55), (2.55, 3.16), (3.16, 5), (5, 10000000000)]

        # Crear los inputs para los rangos y colores
        self.rangos_input_energ = []

        for i, (rango, color) in enumerate(zip(rangos_energ, colores)):
            valor_inicial = QLineEdit(str(rango[0]))

            # Para el último rango, mostrar '<' en lugar de un valor editable
            if i == len(rangos) - 1:  # Último rango
                valor_final = QLabel('<')  # Mostrar '<' en lugar de un campo editable
                valor_final_operacion = 10000000000  # Valor usado internamente para operaciones
            else:
                valor_final = QLineEdit(str(rango[1]))
                valor_final_operacion = float(rango[1])  # Valor usado para operaciones

            color_button = QPushButton()
            color_button.setStyleSheet(f"background-color: {color}")
            color_button.clicked.connect(lambda _, b=color_button: self.seleccionar_color(b))  # Conectar el color picker a cada botón

            # Crear el checkbox y marcarlo por defecto
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Marcar el checkbox por defecto

            # Almacenar los valores iniciales y finales, y el botón de color
            self.rangos_input_energ.append((checkbox, valor_inicial, valor_final, color_button, valor_final_operacion))

            # Añadir los elementos al layout
            rango_colores_energ_layout.addWidget(checkbox, i, 0)  # Añadir el checkbox en lugar de la etiqueta "Rango"
            rango_colores_energ_layout.addWidget(valor_inicial, i, 1)
            rango_colores_energ_layout.addWidget(QLabel("to"), i, 2)
            rango_colores_energ_layout.addWidget(valor_final, i, 3)
            rango_colores_energ_layout.addWidget(color_button, i, 4)
            rango_colores_energ_layout.addWidget(QLabel("MJ/t"), i, 5)

        rango_colores_energ_group.setLayout(rango_colores_energ_layout)


        # Crear el área de la gráfica
        self.crear_canvas()

        # Añadir los widgets al layout principal usando la cuadrícula especificada
        main_layout.addWidget(taladro_group, 0, 0, 2, 1)
        main_layout.addWidget(holmberg_group, 0, 1)   
        main_layout.addWidget(dist_energy_group, 1, 1)      
        main_layout.addWidget(configuracion_group, 0, 2, 2, 1)       
        main_layout.addWidget(talud_group, 0, 3, 2 , 1)              
        main_layout.addWidget(self.canvas, 2, 0, 2, 3)         
        main_layout.addWidget(rango_colores_group, 2, 3)
        main_layout.addWidget(rango_colores_energ_group, 3, 3)

        self.setLayout(main_layout)


    def crear_canvas(self):
        """Crea un nuevo canvas y figura."""
        self.fig, self.ax = plt.subplots(figsize=(15, 15))
        self.canvas = FigureCanvas(self.fig)

    def seleccionar_color(self, button):
        """Abrir el diálogo de colores y actualizar el color del botón."""
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}")

    def calculo_neyman(self):
        """Realiza el cálculo y genera la gráfica usando las configuraciones de cada taladro."""
        toe_banco = float(self.input_altura_banco.text())/ np.tan(np.radians(float(self.input_angulo_cara.text())))
        # Recoger los valores de configuración para cada taladro desde las entradas de la interfaz
        distancias = [float(self.input_distancia_t1.text()), float(self.input_distancia_t2.text()), 
                    float(self.input_distancia_t3.text()), float(self.input_distancia_t4.text())] 
        distancias = [dist + toe_banco for dist in distancias]
        tacos = [float(self.input_taco_t1.text()), float(self.input_taco_t2.text()), 
                float(self.input_taco_t3.text()), float(self.input_taco_t4.text())]
        cargas = [float(self.input_carga_t1.text()), float(self.input_carga_t2.text()), 
                float(self.input_carga_t3.text()), float(self.input_carga_t4.text())]
        segundos_tacos = [float(self.input_segundo_taco_t1.text()), float(self.input_segundo_taco_t2.text()), 
                        float(self.input_segundo_taco_t3.text()), float(self.input_segundo_taco_t4.text())]
        segundas_cargas = [float(self.input_segunda_carga_t1.text()), float(self.input_segunda_carga_t2.text()), 
                        float(self.input_segunda_carga_t3.text()), float(self.input_segunda_carga_t4.text())]
        diametros = [float(self.input_diametro_t1.text()) / 1000, float(self.input_diametro_t2.text()) / 1000,  # Convertir de mm a m
                    float(self.input_diametro_t3.text()) / 1000, float(self.input_diametro_t4.text()) / 1000]
        
        # Obtener otros parámetros constantes (por ejemplo: densidad, energía del explosivo)
        den_exps = [float(self.input_dens_explosivo_t1.text()), float(self.input_dens_explosivo_t2.text()),
            float(self.input_dens_explosivo_t3.text()), float(self.input_dens_explosivo_t4.text())]


        q_ex = float(self.input_energia_explosivo.text())  # Energía específica del explosivo [Kcal/kg]
        q_exp = q_ex * 4184  # energía específica del explosivo [m^2/s^2]
        den_rck = float(self.input_dens_roca.text())  # Densidad del macizo rocoso [kg/m^3]

        # Calcular L_bar y vs para las cargas
        L_bar = []
        vs = []
        P =[]
        for i, carga in enumerate(cargas):
            if carga == 0 or diametros[i] == 0:
                print(f"Advertencia: La carga o el diámetro del taladro {i+1} es 0. Se omitirá este taladro.")
                L_bar.append(0)  # O cualquier valor predeterminado
                vs.append(0)
            else:
                L_bar_val = carga / diametros[i]
                L_bar.append(L_bar_val)
                vs_val = np.log((L_bar_val + np.sqrt(1 + L_bar_val**2)) / (-L_bar_val + np.sqrt(1 + L_bar_val**2)))
                vs.append(vs_val)

        for i, v in enumerate(vs):
            if v == 0:
                print(f"Advertencia: El valor de vs del taladro {i+1} es 0. Se omitirá este taladro.")
                P.append(0)  # Asignar 0 para P si el valor de vs es inválido o carga es cero
            else:
                P_val = diametros[i] * np.sqrt((den_exps[i] * q_exp) / (8 * den_rck * v))
                P.append(P_val)
        # Calcular P para cada taladro (ajustando por el diámetro de cada uno
        print(P)
        x = np.linspace(-5, 30, 2000)  # Ampliar rango de x para acomodar todos los taladros
        z = np.linspace(-25, 5, 2000)

        XX, ZZ = np.meshgrid(x, z, indexing='ij')
        YY = 0

        # Inicializamos una lista para almacenar los valores de PPV para cada taladro
        vp_taladros = []

        # Para cada taladro, calcular la PPV en base a sus configuraciones
        for i in range(4):
            taco = tacos[i]
            carga = cargas[i]
            segundo_taco = segundos_tacos[i]
            segunda_carga = segundas_cargas[i]
            distancia = distancias[i]
            den_exp = den_exps[i]
            
            # Coordenadas Z para la primera carga
            z1_primera_carga = -taco - carga
            z2_primera_carga = -taco

            # Cálculo del potencial y componentes de velocidad para la primera carga en el taladro
            vx1 = P[i] * (XX - distancia) * (
                ((z1_primera_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5) * 
                (z1_primera_carga - ZZ + ((z1_primera_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**0.5)**(-1) -
                ((z2_primera_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5) * 
                (z2_primera_carga - ZZ + ((z2_primera_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**0.5)**(-1)
            )
            vz1 = P[i] * (
                ((z2_primera_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5) -
                ((z1_primera_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5)
            )
            vp1 = np.sqrt(vx1**2 + vz1**2)

            # Si el taladro tiene una segunda carga, calcular también para la segunda carga
            if segunda_carga > 0:
                z1_segunda_carga = -(taco + carga + segundo_taco + segunda_carga)
                z2_segunda_carga = -(taco + carga + segundo_taco)

                vx2 = P[i] * (XX - distancia) * (
                    ((z1_segunda_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5) * 
                    (z1_segunda_carga - ZZ + ((z1_segunda_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**0.5)**(-1) -
                    ((z2_segunda_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5) * 
                    (z2_segunda_carga - ZZ + ((z2_segunda_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**0.5)**(-1)
                )
                vz2 = P[i] * (
                    ((z2_segunda_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5) -
                    ((z1_segunda_carga - ZZ)**2 + (XX - distancia)**2 + YY**2)**(-0.5)
                )
                vp2 = np.sqrt(vx2**2 + vz2**2)

                # Tomar el valor máximo entre las dos cargas
                vp_total_taladro = np.maximum(vp1, vp2)
            else:
                # Si no hay segunda carga, solo usar la primera carga
                vp_total_taladro = vp1

            # Agregar el resultado del taladro a la lista
            vp_taladros.append(vp_total_taladro)

        # Combinar los resultados de todos los taladros usando el valor máximo en cada punto
        vp_total = np.maximum.reduce(vp_taladros)*1000
        #vp_total = np.sum(vp_taladros, axis=0)

        # Limpiar la gráfica antes de dibujar
        self.ax.clear()

        ### Actualización de niveles y colores de la gráfica ###
        levels = []
        colors = []

        # Recoger los niveles y colores desde los inputs 
        for i, rango in enumerate(self.rangos_input):
            checkbox, valor_inicial, valor_final, color_button, valor_final_operacion = rango

            if checkbox.isChecked():  # Solo procesar los rangos seleccionados (checkbox marcado)
                valor_inicial = float(valor_inicial.text())

                if i == len(self.rangos_input) - 1:  # Si es el último rango
                    valor_final = 10000000000  # Valor grande usado internamente para operaciones
                else:
                    valor_final = float(valor_final.text())  # Asignar el valor normalmente

                # Solo añadir valores que no se repitan
                if len(levels) == 0 or valor_inicial > levels[-1]: 
                    levels.append(valor_inicial)  # Añadir solo el valor inicial
                if valor_final > levels[-1]:  
                    levels.append(valor_final)

                # Obtener el color actual del botón y añadirlo a la lista de colores
                color = color_button.styleSheet().split(": ")[1]
                colors.append(color)

        cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=len(colors))
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        
        #levels = [3, 10, 20, 50, 150, 10000]
        #cmap = plt.get_cmap('jet')
        #norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        #scatter = self.ax.scatter(XX.flatten(), ZZ.flatten(), c=vp_total.flatten(), cmap=cmap, norm=norm, marker='+', s=0.1)
        #scatter = self.ax.contourf(XX, ZZ, vp_total, levels=levels, cmap=cmap, norm=norm)

        # Dibujar la gráfica
        scatter = self.ax.contourf(XX, ZZ, vp_total, levels=levels, cmap=cmap, norm=norm)

        self.dibujar_taladros()
        self.dibujar_talud()
        # Añadir una nueva barra de color
        #self.colorbar = self.fig.colorbar(scatter, ax=self.ax)
        #self.colorbar.set_label('Velocidad Peak de las Partículas (PPV)')

        # Etiquetas
        self.ax.set_title("Modelo de Neyman")
        #self.ax.set_xlabel('Eje X')
        #self.ax.set_ylabel('Eje Z')
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Establecer los límites de la gráfica según el rango de x y z
        self.ax.set_xlim(x[0], x[-1])  # Limitar el eje X
        self.ax.set_ylim(z[0], z[-1])  # Limitar el eje Z
        self.ax.set_aspect('equal')

        # Redibujar la gráfica
        self.canvas.draw()


    def calculo_holmberg(self):
        """Realiza el cálculo y genera la gráfica usando la ecuación de Holmberg para dos tacos y dos cargas."""
        
        toe_banco = float(self.input_altura_banco.text()) / np.tan(np.radians(float(self.input_angulo_cara.text())))

        # Recoger los valores de configuración para cada taladro desde las entradas de la interfaz
        distancias = [float(self.input_distancia_t1.text()), float(self.input_distancia_t2.text()), 
                    float(self.input_distancia_t3.text()), float(self.input_distancia_t4.text())] 
        distancias = [dist + toe_banco for dist in distancias]
        
        tacos = [float(self.input_taco_t1.text()), float(self.input_taco_t2.text()), 
                float(self.input_taco_t3.text()), float(self.input_taco_t4.text())]
        
        cargas = [float(self.input_carga_t1.text()), float(self.input_carga_t2.text()), 
                float(self.input_carga_t3.text()), float(self.input_carga_t4.text())]
        
        segundos_tacos = [float(self.input_segundo_taco_t1.text()), float(self.input_segundo_taco_t2.text()), 
                        float(self.input_segundo_taco_t3.text()), float(self.input_segundo_taco_t4.text())]
        
        segundas_cargas = [float(self.input_segunda_carga_t1.text()), float(self.input_segunda_carga_t2.text()), 
                        float(self.input_segunda_carga_t3.text()), float(self.input_segunda_carga_t4.text())]
        diametros = [float(self.input_diametro_t1.text()) / 1000, float(self.input_diametro_t2.text()) / 1000,  # Convertir de mm a m
                    float(self.input_diametro_t3.text()) / 1000, float(self.input_diametro_t4.text()) / 1000]
        densidad_explosivo = [float(self.input_dens_explosivo_t1.text()), float(self.input_dens_explosivo_t2.text()),
                            float(self.input_dens_explosivo_t3.text()), float(self.input_dens_explosivo_t4.text())]
        
        ka = [float(self.input_k_t1.text()), float(self.input_k_t2.text()), float(self.input_k_t3.text()), float(self.input_k_t4.text())]
        alphas = [float(self.input_alpha_t1.text()), float(self.input_alpha_t2.text()), float(self.input_alpha_t3.text()), float(self.input_alpha_t4.text())]

        # Parámetros de la ecuación de Holmberg
        #K = float(self.input_factor_k.text())
        #alpha = float(self.input_factor_alfa.text())

        x = np.linspace(-5, 30, 2000)
        z = np.linspace(-25, 5, 2000)
        XX, ZZ = np.meshgrid(x, z, indexing='ij')
        YY = 0

        # Inicializamos una lista para almacenar los valores de PPV para cada taladro
        vp_taladros = []

        # Para cada taladro, calcular el PPV en base a la ecuación de Holmberg
        for i in range(4):
            taco = tacos[i]
            carga = cargas[i]
            segundo_taco = segundos_tacos[i]
            segunda_carga = segundas_cargas[i]
            distancia = distancias[i]
            k = ka[i]
            alpha = alphas[i]

            # Calcular la carga por unidad de longitud (q) para la ecuación de Holmberg
            q = densidad_explosivo[i] * (math.pi * (diametros[i] / 2) ** 2)
            # Longitudes para la ecuación de Holmberg
            H = carga
            Xs = taco

            # **Ro** es la distancia horizontal desde la carga
            Ro = np.abs(XX - distancia)

            # **Xo** es la altura del punto (ZZ), ya que se usa como profundidad en la ecuación
            Xo = -ZZ

            # Cálculo del término de la ecuación de Holmberg para la primera carga
            term1 = np.arctan((H + Xs - Xo) / Ro)
            term2 = np.arctan((-Xs + Xo) / Ro)
            ppv_primera_carga = k * ((q / Ro)*(term1 + term2)) ** (alpha)

            # Si el taladro tiene una segunda carga, calcular el PPV para la segunda carga
            if segunda_carga > 0:
                H2 = segunda_carga
                Xs2 = (taco + carga + segundo_taco)
                term1_segunda_carga = np.arctan((H2 + Xs2 - Xo) / Ro)
                term2_segunda_carga = np.arctan((-Xs2 + Xo) / Ro)
                ppv_segunda_carga = k * ((q / Ro)**(alpha)) * ((term1_segunda_carga + term2_segunda_carga) ** (alpha))

                # Tomar el valor máximo entre la primera y segunda carga
                ppv_holmberg = np.maximum(ppv_primera_carga, ppv_segunda_carga)
            else:
                ppv_holmberg = ppv_primera_carga

            # Guardar los valores de PPV para este taladro
            vp_taladros.append(ppv_holmberg)

        # Combinar los resultados de todos los taladros usando el valor máximo en cada punto
        vp_total = np.maximum.reduce(vp_taladros)

        # Limpiar la gráfica antes de dibujar
        self.ax.clear()

        ### Actualización de niveles y colores de la gráfica ###
        levels = []
        colors = []

        # Recoger los niveles y colores desde los inputs del QGroupBox de rangos de colores
        for i, rango in enumerate(self.rangos_input):
            checkbox, valor_inicial, valor_final, color_button, valor_final_operacion = rango

            if checkbox.isChecked():  # Solo procesar los rangos seleccionados (checkbox marcado)
                valor_inicial = float(valor_inicial.text())

                if i == len(self.rangos_input) - 1:  # Si es el último rango
                    valor_final = 10000000000  # Valor grande usado internamente para operaciones
                else:
                    valor_final = float(valor_final.text())  # Asignar el valor normalmente

                # Solo añadir valores que no se repitan
                if len(levels) == 0 or valor_inicial > levels[-1]:  # Asegurar que el valor inicial es mayor que el anterior
                    levels.append(valor_inicial)  # Añadir solo el valor inicial
                if valor_final > levels[-1]:  # Añadir el valor final solo si es mayor que el último nivel
                    levels.append(valor_final)

                # Obtener el color actual del botón y añadirlo a la lista de colores
                color = color_button.styleSheet().split(": ")[1]
                colors.append(color)

        
        # levels = sorted(set(levels))  # Eliminar duplicados y ordenar

        # Crear el colormap dinámico en base a los colores proporcionados
        cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=len(colors))
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        # Dibujar la gráfica
        scatter = self.ax.contourf(XX, ZZ, vp_total, levels=levels, cmap=cmap, norm=norm)

        self.dibujar_taladros()
        self.dibujar_talud()

        # Añadir una nueva barra de color
        #self.colorbar = self.fig.colorbar(scatter, ax=self.ax)
        #self.colorbar.set_label('Velocidad Peak de las Partículas (PPV)')

        # Etiquetas
        self.ax.set_title("Modelo de Holmberg & Persson")
        #self.ax.set_xlabel('Eje X')
        #self.ax.set_ylabel('Eje Z')
        #self.ax.set_xticks([])
        #self.ax.set_yticks([])
        #self.ax.grid(True)
        # Establecer los límites de la gráfica según el rango de x y z
        self.ax.set_xlim(x[0], x[-1])  # Limitar el eje X
        self.ax.set_ylim(z[0], z[-1])  # Limitar el eje Z
        self.ax.set_aspect('equal')

        # Redibujar la gráfica
        self.canvas.draw()

    def calculo_energia(self):
        """Calcula la distribución de energía en cada punto de la cuadrícula, considerando dos cargas por taladro."""
        toe_banco = float(self.input_altura_banco.text()) / np.tan(np.radians(float(self.input_angulo_cara.text())))

        # Recoger los valores de configuración para cada taladro desde las entradas de la interfaz
        distancias = [float(self.input_distancia_t1.text()), float(self.input_distancia_t2.text()), 
                    float(self.input_distancia_t3.text()), float(self.input_distancia_t4.text())] 
        distancias = [dist + toe_banco for dist in distancias]

        tacos = [float(self.input_taco_t1.text()), float(self.input_taco_t2.text()), 
                float(self.input_taco_t3.text()), float(self.input_taco_t4.text())]
        
        cargas = [float(self.input_carga_t1.text()), float(self.input_carga_t2.text()), 
                float(self.input_carga_t3.text()), float(self.input_carga_t4.text())]
        
        segundos_tacos = [float(self.input_segundo_taco_t1.text()), float(self.input_segundo_taco_t2.text()), 
                        float(self.input_segundo_taco_t3.text()), float(self.input_segundo_taco_t4.text())]
        
        segundas_cargas = [float(self.input_segunda_carga_t1.text()), float(self.input_segunda_carga_t2.text()), 
                        float(self.input_segunda_carga_t3.text()), float(self.input_segunda_carga_t4.text())]
    
        diametros = [float(self.input_diametro_t1.text()), float(self.input_diametro_t2.text()), 
                    float(self.input_diametro_t3.text()), float(self.input_diametro_t4.text())]
    
        dens_expls = [float(self.input_dens_explosivo_t1.text()), float(self.input_dens_explosivo_t2.text()),
                    float(self.input_dens_explosivo_t3.text()), float(self.input_dens_explosivo_t4.text())]
                     
        dens_r = float(self.input_dens_roca.text())  # Densidad de la roca (ρr)

        x = np.linspace(-5, 30, 2000)  
        z = np.linspace(-25, 5, 2000)  
        XX, ZZ = np.meshgrid(x, z, indexing='ij')

        # Inicializar la lista para almacenar las energías de cada taladro
        Energias = []

        # Para cada taladro
        for i in range(4):
            taco = tacos[i]
            carga = cargas[i]
            segundo_taco = segundos_tacos[i]
            segunda_carga = segundas_cargas[i]
            distancia = distancias[i]
            diametro = diametros[i]
            dens_expl = dens_expls[i]

            # Calcular la energía para la primera carga
            h = np.abs(XX - distancia)
            L1 = taco + ZZ
            L2 = (taco + carga) + ZZ 

            # Coordenadas r1 y r2 basadas en la fórmula
            r1 = np.sqrt(h**2 + L1**2)  # Distancia desde el punto P a L1
            r2 = np.sqrt(h**2 + L2**2)  # Distancia desde el punto P a L2 

            # Calcular la energía de la primera carga
            Energy_1 = 187.5 * (dens_expl / dens_r) * ((diametro / 1000)**2) * (1 / h**2) * ((L2 / r2) - (L1 / r1))

            # Si hay segunda carga
            if segunda_carga > 0:
                # Calcular la energía para la segunda carga
                L1_segunda = (taco + carga + segundo_taco) + ZZ
                L2_segunda = (taco + carga + segundo_taco + segunda_carga) + ZZ

                # Coordenadas r1 y r2 para la segunda carga
                r1_segunda = np.sqrt(h**2 + L1_segunda**2)  
                r2_segunda = np.sqrt(h**2 + L2_segunda**2)  

                # Calcular la energía de la segunda carga
                Energy_2 = 187.5 * (dens_expl / dens_r) * ((diametro / 1000)**2) * (1 / h**2) * ((L2_segunda / r2_segunda) - (L1_segunda / r1_segunda))

                # Tomar el máximo entre la primera y segunda carga en cada punto
                Energy_total = Energy_1 + Energy_2
            else:
                # Si no hay segunda carga, usar solo la energía de la primera carga
                Energy_total = Energy_1

            # Almacenar las energías de este taladro
            Energias.append(Energy_total)

        # Combinar los resultados de todos los taladros usando el valor máximo en cada punto
        #Energia_total = np.maximum.reduce(Energias)
        Energia_total = np.sum(Energias, axis=0)

        # Limpiar la gráfica antes de dibujar
        self.ax.clear()

        # Crear el colormap dinámico en base a los colores proporcionados
        levels = []
        colors = []

        # Recoger los niveles y colores desde los inputs del QGroupBox de rangos de colores
        for i, rango in enumerate(self.rangos_input_energ):
            checkbox, valor_inicial, valor_final, color_button, valor_final_operacion = rango

            if checkbox.isChecked():  # Solo procesar los rangos seleccionados (checkbox marcado)
                valor_inicial = float(valor_inicial.text())

                if i == len(self.rangos_input_energ) - 1:  # Si es el último rango
                    valor_final = 10000000000  # Valor grande usado internamente para operaciones
                else:
                    valor_final = float(valor_final.text())  # Asignar el valor normalmente

                # Solo añadir valores que no se repitan
                if len(levels) == 0 or valor_inicial > levels[-1]:  # Asegurar que el valor inicial es mayor que el anterior
                    levels.append(valor_inicial)  # Añadir solo el valor inicial
                if valor_final > levels[-1]:  # Añadir el valor final solo si es mayor que el último nivel
                    levels.append(valor_final)

                # Obtener el color actual del botón y añadirlo a la lista de colores
                color = color_button.styleSheet().split(": ")[1]
                colors.append(color)

        # Crear el colormap dinámico en base a los colores proporcionados
        cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=len(colors))
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        # Dibujar la gráfica de la distribución de energía
        scatter = self.ax.contourf(XX, ZZ, Energia_total, levels=levels, cmap=cmap, norm=norm)

        self.dibujar_taladros()
        self.dibujar_talud()

        # Etiquetas y ajuste de la gráfica
        self.ax.set_title("Distribución de Energía en el plano XZ")
        self.ax.set_xlim(x[0], x[-1])  # Limitar el eje X
        self.ax.set_ylim(z[0], z[-1])  # Limitar el eje Z
        self.ax.set_aspect('equal')

        # Redibujar la gráfica
        self.canvas.draw()


    def limpiar_canvas(self):
        """Limpia completamente el canvas y lo recrea desde cero, incluyendo la barra de colores."""
        # Eliminar el canvas actual del layout
        self.canvas.deleteLater()  # Eliminar el canvas

        # Crear un nuevo canvas
        self.crear_canvas()

        # Redibujar el nuevo canvas
        self.layout().addWidget(self.canvas, 2, 0, 2, 3)

    def dibujar_taladros(self):
        """Dibuja las líneas verticales que representan los taladros con tacos y cargas con fill_between."""

        # Calcular el valor de toe_banco
        toe_banco = float(self.input_altura_banco.text()) / np.tan(np.radians(float(self.input_angulo_cara.text())))

        # Obtener los diámetros de los taladros
        diametros = [float(self.input_diametro_t1.text()), float(self.input_diametro_t2.text()), 
                    float(self.input_diametro_t3.text()), float(self.input_diametro_t4.text())]

        # Colores para las diferentes partes
        color_taco = 'lightgray'  # Color gris claro
        color_carga = 'green'  # Color azul oscuro
        grosor_linea = 0.75  # Ajusta el grosor según lo desees

        # Función para dibujar un taladro con tacos y cargas usando fill_between
        def dibujar_taladro(distancia_taladro, taco1, carga1, taco2, carga2, diametro_taladro):
            # Convertir el diámetro a metros
            diametro_taladro_m = diametro_taladro / 1000  # Convertir de mm a metros
            # Posición X del taladro
            x0 = distancia_taladro + toe_banco

            # Dibujar el primer taco con fill_between (color gris) y borde
            y_taco1 = 0
            self.ax.fill_between([x0 - diametro_taladro_m / 2, x0 + diametro_taladro_m / 2], y_taco1, y_taco1 - taco1, 
                                color=color_taco, edgecolor='black', linewidth=grosor_linea)

            # Dibujar la primera carga con fill_between (color azul oscuro) y borde
            y_carga1 = y_taco1 - taco1
            self.ax.fill_between([x0 - diametro_taladro_m / 2, x0 + diametro_taladro_m / 2], y_carga1, y_carga1 - carga1, 
                                color=color_carga, edgecolor='black', linewidth=grosor_linea)

            # Dibujar el segundo taco con fill_between (color gris) y borde
            y_taco2 = y_carga1 - carga1
            self.ax.fill_between([x0 - diametro_taladro_m / 2, x0 + diametro_taladro_m / 2], y_taco2, y_taco2 - taco2, 
                                color=color_taco, edgecolor='black', linewidth=grosor_linea)

            # Dibujar la segunda carga con fill_between (color azul oscuro) y borde
            y_carga2 = y_taco2 - taco2
            self.ax.fill_between([x0 - diametro_taladro_m / 2, x0 + diametro_taladro_m / 2], y_carga2, y_carga2 - carga2, 
                                color=color_carga, edgecolor='black', linewidth=grosor_linea)

        # Dibujar los taladros 1 a 4 con sus respectivos diámetros y colores
        dibujar_taladro(float(self.input_distancia_t1.text()), float(self.input_taco_t1.text()), float(self.input_carga_t1.text()), 
                        float(self.input_segundo_taco_t1.text()), float(self.input_segunda_carga_t1.text()), diametros[0])
        dibujar_taladro(float(self.input_distancia_t2.text()), float(self.input_taco_t2.text()), float(self.input_carga_t2.text()), 
                        float(self.input_segundo_taco_t2.text()), float(self.input_segunda_carga_t2.text()), diametros[1])
        dibujar_taladro(float(self.input_distancia_t3.text()), float(self.input_taco_t3.text()), float(self.input_carga_t3.text()), 
                        float(self.input_segundo_taco_t3.text()), float(self.input_segunda_carga_t3.text()), diametros[2])
        dibujar_taladro(float(self.input_distancia_t4.text()), float(self.input_taco_t4.text()), float(self.input_carga_t4.text()), 
                        float(self.input_segundo_taco_t4.text()), float(self.input_segunda_carga_t4.text()), diametros[3])

        self.ax.set_aspect('equal', adjustable='box')  # Asegurar que el aspecto del gráfico sea consistente
      

    def dibujar_talud(self):
        """Dibuja el talud basado en los parámetros ingresados por el usuario."""
        
        # Parámetros del talud
        altura_banco = float(self.input_altura_banco.text())
        angulo_cara = float(self.input_angulo_cara.text())
        ancho_berma = float(self.input_ancho_berma.text())

        # Coordenadas para el dibujo del talud
        x0, z0 = 0, 0  # Punto de inicio en la cresta
        
        # Línea negativa (horizontal en el lado izquierdo)
        x_neg = x0 - ancho_berma  # Mismo ancho de berma pero negativo
        z_neg = z0  # Misma altura
        self.ax.plot([x_neg, x0], [z_neg, z0], 'k-', lw=1.5)  # Línea horizontal negativa

        # Coordenadas para la línea inclinada (talud principal)
        x1 = x0 + (altura_banco / np.tan(np.radians(angulo_cara)))  # Coordenada en x para la línea inclinada
        z1 = z0 - altura_banco  # Coordenada en z (descenso) para la línea inclinada

        # Línea inclinada del talud
        self.ax.plot([x0, x1], [z0, z1], 'k-', lw=1.5)  # Línea inclinada

        # Coordenada para la línea horizontal del ancho de la berma
        x2 = x1 + ancho_berma
        z2 = z1  # Misma coordenada z (es horizontal)

        # Línea horizontal de la berma
        self.ax.plot([x1, x2], [z1, z2], 'k-', lw=1.5)  # Línea horizontal (ancho de berma)

        # Línea inclinada final para completar el talud (replica la inclinación original)
        x3 = x2 + (altura_banco / np.tan(np.radians(angulo_cara)))  # Mismo ángulo de inclinación
        z3 = z2 - altura_banco  # Segunda inclinación

        self.ax.plot([x2, x3], [z2, z3], 'k-', lw=1.5)  # Línea inclinada final
    
    def guardar_imagen(self):
        """Abre un diálogo para guardar la figura como imagen."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", options=options)
        if file_path:
            self.fig.savefig(file_path)

if __name__ == '__main__':
    # Crea una instancia de QApplication para la GUI.
    app = QApplication(sys.argv)
    #app.setStyle("Macintosh")

    #app = QApplication([])

    def resource_path(relative_path):
        """Devuelve la ruta absoluta para archivos que están fuera del ejecutable."""
        if getattr(sys, 'frozen', False): 
            base_path = os.path.dirname(sys.executable) 
        else:
            base_path = os.path.abspath(".")  
        
        return os.path.join(base_path, relative_path)

    # Ruta completa al archivo de licencia en la subcarpeta "licence"
    ruta_licencia = resource_path(os.path.join('licence', 'energyKey.dat'))
    ruta_fecha_almacenada = resource_path(os.path.join('licence', 'energyKey00.dat'))


    def leer_archivo_fecha_almacenada():
        try:
            with open(ruta_fecha_almacenada, 'rb') as archivo:
                contenido_f_almacenada = archivo.readlines()
                clave_f_almacenada = contenido_f_almacenada[0].strip()
                fecha_encriptada_f_almacenada = contenido_f_almacenada[1].strip()
        except Exception as e:
            QMessageBox.warning(None, 'Error de Archivo', 'No se pudo leer la licencia. ')
        
        try:
            # desencriptar la fecha almacenada
            f = Fernet(clave_f_almacenada)
            fecha_almacenada_f_almacenada = f.decrypt(fecha_encriptada_f_almacenada).decode()

            # fecha actual del archivo
            fecha_actual_f_almacenada = datetime.strptime(fecha_almacenada_f_almacenada, '%Y-%m-%d')
            
            #mensaje de confirmacion
            #QMessageBox.information(None, 'Fecha Almacenada', f'La fecha almacenada es: {fecha_actual_f_almacenada}, tipo: {type(fecha_actual_f_almacenada)}')
            
            return fecha_actual_f_almacenada
        
        except Exception as e:
            QMessageBox.warning(None, 'Error de Archivo', 'Ocurrió un error con la licencia. ')

    def guardar_en_archivo(llave, fecha_encriptada, nombre_archivo):
        with open(nombre_archivo, 'wb') as archivo:
            archivo.write(llave + b'\n' + fecha_encriptada)

    def almacenar_fecha(fecha_ntp):
        try:
            with open(ruta_fecha_almacenada, 'rb') as archivo:
                contenido_f_almacenada = archivo.readlines()
                clave_f_almacenada = contenido_f_almacenada[0].strip()
                fecha_encriptada_f_almacenada = contenido_f_almacenada[1].strip()
            #mensaje de exito    
            #QMessageBox.warning(None, 'Exito', 'Guardado con exito')
        except Exception as e:
            QMessageBox.warning(None, 'Error de Archivo', 'No se pudo leer la licencia ')
        
        try:
            f = Fernet(clave_f_almacenada)
            fecha_actual_ntp = fecha_ntp.date()
            fecha_actual_ntp = str(fecha_actual_ntp)
            fecha_actual_ntp_encriptada = f.encrypt(fecha_actual_ntp.encode())

            guardar_en_archivo(clave_f_almacenada, fecha_actual_ntp_encriptada, ruta_fecha_almacenada)
        except Exception as e:
            #QMessageBox.warning(None, 'fecha almacenada', f'Hubo un error al gurdar la hora ntp encriptada {e}')
            pass

    # verificar la conexión a internet para obtener la hora NTP
    try:
        # Crear un cliente NTP
        cliente = ntplib.NTPClient()
        respuesta = cliente.request('pool.ntp.org')  # Consulta un servidor NTP
        # Obtener la hora UTC
        utc_time = ctime(respuesta.tx_time)
        # Convertir la cadena utc_time a un objeto datetime
        # El formato que corresponde a "Tue Oct 14 15:30:00 2024" es "%a %b %d %H:%M:%S %Y"
        fecha = datetime.strptime(utc_time, '%a %b %d %H:%M:%S %Y')
        #QMessageBox.critical(None, 'Acceso a Conexión', 'Bienvenido tienes acceso a internet.')
        almacenar_fecha(fecha_ntp=fecha)
    except Exception as e:
        # Mostrar mensaje de error si no se puede obtener la hora NTP
        QMessageBox.critical(None, 'Error de Conexión', 'Por favor, verifique su conexión a internet.')
        fecha = leer_archivo_fecha_almacenada()
        #sys.exit(1)


    try:
        with open(ruta_licencia, 'rb') as archivo:
            contenido = archivo.readlines()
            clave = contenido[0].strip()
            fecha_encriptada = contenido[1].strip()
    except Exception as e:
        QMessageBox.critical(None, 'Error de Licencia', 'No existe archivo con la licencia, contacte con Geoblast.')
        sys.exit(1)


    try:
        # desencriptar la fecha de expiración
        f = Fernet(clave)
        fecha_exp = f.decrypt(fecha_encriptada).decode()

        # convertir las cadenas a objetos datetime
        # Fecha actual
        fecha_actual = fecha.date()
        # fecha expiracion
        fecha_expiracion = datetime.strptime(fecha_exp, '%Y-%m-%d').date()
    except Exception as e:
        QMessageBox.critical(None, 'Error de Licencia', 'Ocurrió un error con las credenciales de la licencia.')
        sys.exit(1)



    # Verificar si la fecha actual es menor o igual a la fecha de expiración
    if fecha_actual <= fecha_expiracion:
        # Calcular la diferencia en días
        dias_restantes = (fecha_expiracion - fecha_actual).days
        # Mostrar mensaje si faltan 5 días o menos
        '''if dias_restantes <= 5:
            if dias_restantes > 0:
                QMessageBox.warning(None, 'Aviso de Licencia', f'Faltan {dias_restantes} días para que expire su licencia.')
            else:
                QMessageBox.warning(None, 'Aviso de Licencia', 'Hoy expira su licencia.')
        '''
        # Crea la ventana principal de la aplicación.
        ventana = MainWindow()
        # Muestra la ventana en la pantalla.
        ventana.show()
        # Inicia el bucle de eventos y cierra la aplicación correctamente.
        sys.exit(app.exec_())

    else:
        QMessageBox.critical(None, 'Licencia Expirada', 'La licencia ha expirado. Por favor contacte a Geoblast para renovar su licencia.')   



