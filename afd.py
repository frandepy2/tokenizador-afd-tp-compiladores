import re
# Codigo para crear un AFD

# Este afd usa patrones por extensión, es decir, se definen los estados con cada elemento y transiciones
class AFD:
    def __init__(self, estado_inicial, estados_finales):
        self.estado_inicial = estado_inicial #Estado inicial
        self.estados_finales = estados_finales #Diccionario de estados finales
        self.transiciones = {estado_inicial: {}} #Diccionario de transiciones
        self.lexema_ids = {} #Diccionario para guardar los ids de los lexemas
        self.next_id = 1

    def agregar_transicion(self, estado_origen, lexema, estado_destino):
        if estado_origen not in self.transiciones:
            self.transiciones[estado_origen] = {}
        if lexema in self.transiciones[estado_origen]:
            raise Exception("Transicion duplicada")
        self.transiciones[estado_origen][lexema] = estado_destino
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
            'ERROR_LX,': 'q_ERROR_LX,',
        }

        print("Creando AFD")
        afd = AFD(estado_inicial, estado_finales)
        print("AFD creado")
        print(afd.estado_inicial)
        print(afd.estados_finales)
        print(afd.transiciones)
        return afd

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
        self.afd.agregar_transicion("q0", error_lx, "q_ERROR_LX,")
        return self.afd.lexema_ids[error_lx]


    #Recibe un archivo de entrada y crea un diccionario con los lexemas con su posicion en el texto donde la posicion es el numero de lexemas
    # Y va creando un archivo de salida con el siguiente formato: 
    def tokenizador(self, texto):
        #Este separa en lexemas para analizar en el AFD
        lexemas = re.findall(r'\b\w+\b', texto.lower())
        
        #Este obtiene las palabras en su forma original
        palabras = re.findall(r'\b\w+\b', texto)

        #Evaluamos cada lexema
        for lexema in lexemas:
            # el estado es el tipo de lexema, id_lexema es la posicion en el diccionario de lexemas y es_aceptado es si es aceptado o no
            estado, id_lexema, es_aceptado = self.afd.evaluar_lexema(lexema)
            if es_aceptado:
                print(f"Lexema aceptado: {lexema} se detecto como {estado} en la posicion {self.posicion}, posicion en el diccionario: {id_lexema} palabra original: {palabras[self.posicion]}")
                #Agregamos a lista_salida el proceso con el formato TXT#-N donde TXT es una etiqueta fija, # es el id del lexema y N es la posicion en el texto
                #En el caso de Error Lexixo el id de lexema es 0
                self.lista_salida.append(f"TXT{id_lexema}-{self.posicion+1}")
                self.posicion += 1
            else:
                #Si no es aceptado, le preguntamos al usuario si desea agregarlo al diccionario
                print(f"Lexema no aceptado: {lexema}")
                bandera = True
                while bandera:
                    eleccion = input("Eliga entre un token o un error lexico: 1-Articulo, 2-Sustantivo, 3-Verbo, 4-Adjetivo, 5-Adverbio, 6-Error lexico: ")
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
                self.lista_salida.append(f"TXT{id_lexema}-{self.posicion+1}")

                self.posicion += 1

        # retornamos los lexemas, la lista de salida para el analizador sintactico y los ids de los lexemas
        return lexemas, self.lista_salida, self.afd.get_ids()


def main():
    print("Creando tokenizador")
    tokenizador = TokenizadorAFD()

    # abrir archivo de palabras convertir todo a una sola linea y llamar a tokenizador
    with open("in.txt","r", encoding='utf-8') as archivo:
        texto = archivo.read().replace('\n', ' ')
        lexemas, salida_sintaxis, tokens = tokenizador.tokenizador(texto)

        print("Lexemas: ", lexemas)
        print("Salida sintaxis: ", salida_sintaxis)
        print("Tokens: ", tokens)


if __name__ == "__main__":
    main()
