# app/core/grados.py

# Diccionario con las llaves normalizadas y su representación legible (opcional para el frontend)
GRADOS = {
    "primaria_primero": "Primero de primaria",
    "primaria_segundo": "Segundo de primaria",
    "primaria_tercero": "Tercero de primaria",
    "primaria_cuarto": "Cuarto de primaria",
    "primaria_quinto": "Quinto de primaria",
    "primaria_sexto": "Sexto de primaria",
}

def es_grado_valido(grado_normalizado: str) -> bool:
    """
    Verifica si el grado (en su formato normalizado ej. 'primaria_primero') 
    existe dentro de las opciones permitidas.
    """
    return grado_normalizado in GRADOS

def normalizar_grado(texto: str) -> str:
    """
    Convierte 'Primero de primaria' -> 'primaria_primero'
    Si ya viene normalizado ('primaria_primero'), lo devuelve tal cual.
    """
    texto_limpio = texto.lower().strip()
    
    # Si ya está en el formato correcto (ej. primaria_primero), lo dejamos pasar
    if texto_limpio in GRADOS:
        return texto_limpio

    partes = texto_limpio.split()
    if len(partes) >= 3 and partes[1] == "de":
        grado = partes[0]       # primero, segundo, tercero...
        nivel = partes[2]       # primaria, secundaria...
        return f"{nivel}_{grado}"
        
    return texto_limpio.replace(" ", "_")