import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

# Codigo para crear un AFD

# Este afd usa patrones por extensión, es decir, se definen los estados con cada elemento y transiciones
class AFD:
    def __init__(self, estado_inicial, estados_finales, contador_documentos, contador_por_token):
        self.estado_inicial = estado_inicial #Estado inicial
        self.estados_finales = estados_finales #Diccionario de estados finales
        self.transiciones = {estado_inicial: {}} #Diccionario de transiciones
        self.lexema_ids = {} #Diccionario para guardar los ids de los lexemas
        self.next_id = 1
        self.contador_documentos = contador_documentos
        self.contador_por_token = contador_por_token

    def agregar_transicion(self, estado_origen, lexema, estado_destino):
        if estado_origen not in self.transiciones:
            self.transiciones[estado_origen] = {}
        if lexema in self.transiciones[estado_origen]:
            raise Exception("Transicion duplicada")
        self.transiciones[estado_origen][lexema] = estado_destino
        self.contador_por_token[estado_destino] = self.contador_por_token.get(estado_destino, 0) + 1
        if lexema not in self.lexema_ids:
            self.lexema_ids[lexema] = self.next_id
            self.next_id += 1
        #devolvemos el id del lexema para poder guardarlo en el diccionario de tokens
        return self.lexema_ids[lexema]

    #Algoritmo de simulacion de AFD para evaluar un lexema
    def evaluar_lexema(self, lexema):
        estado_actual = self.estado_inicial
        id_lexema = 0
        if lexema in self.transiciones[estado_actual]:
            estado_actual = self.transiciones[estado_actual][lexema]
            id_lexema = self.lexema_ids[lexema]
        else:
            return estado_actual, id_lexema, False

        return (estado_actual, id_lexema, True) if estado_actual in self.estados_finales.values() else ("NOT_FOUND",id_lexema, False)
    
    # Devuelve cada lexema con su id
    def get_ids(self):
        return self.lexema_ids
    
    # Devuelve el AFD en formato JSON
    def guardar_en_json(self, filename):
        data = {
            'estado_inicial': self.estado_inicial,
            'estados_finales': self.estados_finales,
            'transiciones': self.transiciones,
            'lexema_ids': self.lexema_ids,
            'next_id': self.next_id,
            'contador_documentos': self.contador_documentos,
            'contador_por_token': self.contador_por_token
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def cargar_de_json(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.estado_inicial = data['estado_inicial']
        self.estados_finales = data['estados_finales']
        self.transiciones = data['transiciones']
        self.lexema_ids = data['lexema_ids']
        self.next_id = data['next_id']
        self.contador_documentos = data.get('contador_documentos', 0)
        self.contador_por_token = data.get('contador_por_token', {})

    def cantidad_lexemas_por_token(self, token):
        return self.contador_por_token.get(token, 0)

class TokenizadorAFD:
    def __init__(self):
        self.diccionario = {}
        self.afd = self.construir_afd()
        self.posicion = 0

    lista_salida = []

    def construir_afd(self):
        estado_inicial =  "q0"
        estado_finales = {
            'ARTICULO': 'q_ARTICULO',
            'SUSTANTIVO': 'q_SUSTANTIVO',
            'VERBO': 'q_VERBO',
            'ADJETIVO': 'q_ADJETIVO',
            'ADVERBIO': 'q_ADVERBIO',
            'ERROR_LX': 'q_ERROR_LX',
        }

        contador_por_token = {
            'q_ARTICULO': 0,
            'q_SUSTANTIVO': 0,
            'q_VERBO': 0,
            'q_ADJETIVO': 0,
            'q_ADVERBIO': 0,
            'q_ERROR_LX': 0,
        }

        print("Creando AFD")
        afd = AFD(estado_inicial, estado_finales, 0, contador_por_token)
        print("AFD creado")
        return afd

    def get_cantidad_lexemas_por_token(self, token):
        return self.afd.cantidad_lexemas_por_token(token)

    def agregar_articulo(self, articulo):
        self.afd.agregar_transicion("q0", articulo, "q_ARTICULO")
        return self.afd.lexema_ids[articulo]

    def agregar_sustantivo(self, sustantivo):
        self.afd.agregar_transicion("q0", sustantivo, "q_SUSTANTIVO")
        return self.afd.lexema_ids[sustantivo]
    
    def agregar_verbo(self, verbo):
        self.afd.agregar_transicion("q0", verbo, "q_VERBO")
        return self.afd.lexema_ids[verbo]
    
    def agregar_adjetivo(self, adjetivo):
        self.afd.agregar_transicion("q0", adjetivo, "q_ADJETIVO")
        return self.afd.lexema_ids[adjetivo]
    
    def agregar_adverbio(self, adverbio):
        self.afd.agregar_transicion("q0", adverbio, "q_ADVERBIO")
        return self.afd.lexema_ids[adverbio]
    
    def agregar_error_lexico(self, error_lx):
        self.afd.agregar_transicion("q0", error_lx, "q_ERROR_LX")
        return self.afd.lexema_ids[error_lx]


    def obtener_cantidad_lexemas_por_token(self, token):
        return self.afd.cantidad_lexemas_por_token(token)

        
    def guardar_afd(self, filename):
        self.afd.guardar_en_json(filename)

    def cargar_afd(self, filename):
        self.afd.cargar_de_json(filename)

    #Recibe un archivo de entrada y crea un diccionario con los lexemas con su posicion en el texto donde la posicion es el numero de lexemas
    # Y va creando un archivo de salida con el siguiente formato: 
    def tokenizador(self, texto):
        #Este separa en lexemas para analizar en el AFD
        lexemas = re.findall(r'\b\w+\b', texto.lower())
        #Este obtiene las palabras en su forma original
        palabras = re.findall(r'\b\w+\b', texto)

        # Obtenemos la cantidad de lexemas 
        cantidad_lexemas = len(lexemas)
        contador_lexemas_procesados = 0
        contador_lexemas_no_procesados = 0
        
        #Evaluamos cada lexema
        for lexema in lexemas:
            # el estado es el tipo de lexema, id_lexema es la posicion en el diccionario de lexemas y es_aceptado es si es aceptado o no
            estado, id_lexema, es_aceptado = self.afd.evaluar_lexema(lexema)
            if es_aceptado:
                print(f"Lexema aceptado: {lexema} se detecto como {estado}")
                #Agregamos a lista_salida el proceso con el formato TXT#-N donde TXT es una etiqueta fija, # es el id del lexema y N es la posicion en el texto
                #En el caso de Error Lexixo el id de lexema es 0
                self.lista_salida.append(f"TXT{self.afd.contador_documentos}-{self.afd.lexema_ids[lexema]}")
                self.posicion += 1
                contador_lexemas_procesados += 1
            else:
                #Si no es aceptado, le preguntamos al usuario si desea agregarlo al diccionario
                print(f"Lexema no aceptado: {lexema}")
                eleccion = elegir_categoria(lexema, self)

                if eleccion == "1":
                    id_lexema = self.agregar_articulo(lexema)
                    bandera = False
                elif eleccion == "2":
                    id_lexema = self.agregar_sustantivo(lexema)
                    bandera = False
                elif eleccion == "3":
                    id_lexema = self.agregar_verbo(lexema)
                    bandera = False
                elif eleccion == "4":
                    id_lexema = self.agregar_adjetivo(lexema)
                    bandera = False
                elif eleccion == "5":
                    id_lexema = self.agregar_adverbio(lexema)
                    bandera = False
                elif eleccion == "6":
                    id_lexema = self.agregar_error_lexico(lexema)
                    bandera = False
                else:
                    print("Opcion invalida")

                #Agregamos a lista_salida el proceso con el formato TXT#-N donde TXT es una etiqueta fija, # es el id del lexema y N es la posicion en el texto
                #En el caso de Error Lexixo el id de lexema es 0
                self.lista_salida.append(f"TXT{self.afd.contador_documentos}-{self.afd.lexema_ids[lexema]}")
                self.posicion += 1
                contador_lexemas_no_procesados += 1

        # retornamos los lexemas, la lista de salida para el analizador sintactico y los ids de los lexemas
        return lexemas, self.lista_salida, self.afd.get_ids(), contador_lexemas_procesados, contador_lexemas_no_procesados, cantidad_lexemas


def elegir_categoria(lexema, tokenizador):
    def seleccion(eleccion):
        opciones = {
            "1": lambda: tokenizador.agregar_articulo(lexema),
            "2": lambda: tokenizador.agregar_sustantivo(lexema),
            "3": lambda: tokenizador.agregar_verbo(lexema),
            "4": lambda: tokenizador.agregar_adjetivo(lexema),
            "5": lambda: tokenizador.agregar_adverbio(lexema),
            "6": lambda: tokenizador.agregar_error_lexico(lexema),
        }
        if eleccion in opciones:
            id_lexema = opciones[eleccion]()
            top.destroy()
            return id_lexema
        else:
            messagebox.showerror("Error", "Opción inválida")

    top = tk.Toplevel()
    top.title("Seleccionar categoría del lexema")
    msg = tk.Label(top, text=f"Lexema no aceptado: {lexema}\nElige una categoría:")
    msg.pack()

    opciones = ["1-Artículo", "2-Sustantivo", "3-Verbo", "4-Adjetivo", "5-Adverbio", "6-Error léxico"]
    for opcion in opciones:
        btn = tk.Button(top, text=opcion, command=lambda op=opcion.split('-')[0]: seleccion(op))
        btn.pack()

    top.wait_window()

def main():
    def cargar_archivo():
        archivo = filedialog.askopenfilename(title="Seleccionar archivo de entrada", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            with open("in.txt","r", encoding='utf-8') as archivo:

                estadisticas_antes()

                texto = archivo.read().replace('\n', ' ')
                lexemas, salida_sintaxis, tokens, contador_lexemas_procesados, contador_lexemas_no_procesados, cantidad_lexemas = tokenizador.tokenizador(texto)

                porcentaje_lexemas_procesados = contador_lexemas_procesados / cantidad_lexemas * 100
                porcentaje_lexemas_no_procesados = contador_lexemas_no_procesados / cantidad_lexemas * 100

                porcentaje.set(f"Se procesaron {contador_lexemas_procesados} lexemas de {cantidad_lexemas} ({porcentaje_lexemas_procesados}%)\n"
                              f"No se procesaron {contador_lexemas_no_procesados} lexemas de {cantidad_lexemas} ({porcentaje_lexemas_no_procesados}%)")


                now = datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                output_filename = f"out_{timestamp}.txt"
                with open(output_filename, "w") as archivo:
                    archivo.write(" ".join(salida_sintaxis))


                tokenizador.guardar_afd('afd_persist.json')
                actualizar_estadisticas()
                messagebox.showinfo("Proceso completado", f"Se guardó el archivo de salida en {output_filename}")

    def estadisticas_antes():
        cant_articulos = tokenizador.get_cantidad_lexemas_por_token("q_ARTICULO")
        cant_sustantivos = tokenizador.get_cantidad_lexemas_por_token("q_SUSTANTIVO")
        cant_verbos = tokenizador.get_cantidad_lexemas_por_token("q_VERBO")
        cant_adjetivos = tokenizador.get_cantidad_lexemas_por_token("q_ADJETIVO")
        cant_adverbios = tokenizador.get_cantidad_lexemas_por_token("q_ADVERBIO")
        cant_errores = tokenizador.get_cantidad_lexemas_por_token("q_ERROR_LX")

        res_antes.set(  "Resultados luego del proceso del texto\n"
                        f"Articulo: {cant_articulos}\n"
                        f"Sustantivo: {cant_sustantivos}\n"
                        f"Verbo: {cant_verbos}\n"
                        f"Adjetivo: {cant_adjetivos}\n"
                        f"Adverbio: {cant_adverbios}\n"
                        f"Errores lexicos: {cant_errores}")
        

    def actualizar_estadisticas():
        cant_articulos = tokenizador.get_cantidad_lexemas_por_token("q_ARTICULO")
        cant_sustantivos = tokenizador.get_cantidad_lexemas_por_token("q_SUSTANTIVO")
        cant_verbos = tokenizador.get_cantidad_lexemas_por_token("q_VERBO")
        cant_adjetivos = tokenizador.get_cantidad_lexemas_por_token("q_ADJETIVO")
        cant_adverbios = tokenizador.get_cantidad_lexemas_por_token("q_ADVERBIO")
        cant_errores = tokenizador.get_cantidad_lexemas_por_token("q_ERROR_LX")

        resultado.set(  "Resultados luego del proceso del texto\n"
                        f"Articulo: {cant_articulos}\n"
                        f"Sustantivo: {cant_sustantivos}\n"
                        f"Verbo: {cant_verbos}\n"
                        f"Adjetivo: {cant_adjetivos}\n"
                        f"Adverbio: {cant_adverbios}\n"
                        f"Errores lexicos: {cant_errores}")
        

    print("Creando tokenizador")
    tokenizador = TokenizadorAFD()

    if os.path.exists('afd_persist.json'):
        print("Cargando AFD desde JSON existente")
        tokenizador.cargar_afd('afd_persist.json')
    else:
        print("No se encontró archivo JSON, se creará uno nuevo")

    # Incrementar el contador de documentos
    tokenizador.afd.contador_documentos += 1
    
    # Crear la interfaz gráfica
    root = tk.Tk()
    root.title("Tokenizador AFD")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    cargar_button = tk.Button(frame, text="Cargar archivo de texto", command=cargar_archivo)
    cargar_button.pack(pady=5)

    porcentaje = tk.StringVar()
    porcentaje_label = tk.Label(frame, textvariable=porcentaje, justify="left")
    porcentaje_label.pack(pady=5)

    # Variables de estadísticas
    stats_text = tk.StringVar()
    stats_label = tk.Label(frame, textvariable=stats_text, justify="left")
    stats_label.pack(pady=5)
    
    res_antes = tk.StringVar()
    res_antes_label = tk.Label(frame, textvariable=res_antes, justify="left")
    res_antes_label.pack(pady=5)

    resultado = tk.StringVar()
    resultado_label = tk.Label(frame, textvariable=resultado, justify="left")
    resultado_label.pack(pady=5)


    root.mainloop()


if __name__ == "__main__":
    main()


