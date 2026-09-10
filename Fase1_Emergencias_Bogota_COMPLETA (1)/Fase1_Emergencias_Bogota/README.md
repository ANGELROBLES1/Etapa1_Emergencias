# Fase 1 - Sistema inteligente para rutas de emergencia en Bogota

## Integrantes
- Santiago Parra Acuña
- Sergio Alberto Morales Pirajan
- Angel Robles Araque

## Descripcion
Proyecto de Inteligencia Artificial para la Fase 1 del Corte 1. El sistema modela una red vial simplificada de Bogota mediante un grafo en NetworkX y construye un agente basado en utilidad capaz de seleccionar un centro de atencion de urgencias y una ruta, considerando distancia, tiempo estimado, semaforos, demanda historica por localidad y adecuacion del servicio.

**Importante:** este proyecto no usa TransMilenio. La red se plantea sobre tramos viales, intersecciones y centros de urgencias.

## Fuentes oficiales verificadas
- Secretaria Distrital de Salud - Servicios de Urgencias y Ambulancias, CSV 2026. Actualizacion de datos: 23 de julio de 2026.
- Secretaria Distrital de Salud - Llamadas de Urgencias y Emergencias Linea 123, CSV julio 2026. Actualizacion de datos: 4 de septiembre de 2026.
- Secretaria Distrital de Movilidad - Red Semaforica de Bogota D.C. Fecha del dato: 12 de junio de 2026. Metadato actualizado: 2 de septiembre de 2026.
- IDECA / Datos Abiertos Movilidad - Malla Vial Integral Bogota D.C., usada como fuente oficial para representar los ejes viales de la ciudad.

## Estructura
```text
Fase1_Emergencias_Bogota/
├── data/
│   ├── nodos.csv
│   ├── aristas.csv
│   ├── servicios_urgencias_muestra.csv
│   ├── llamadas123_resumen_localidad_muestra.csv
│   └── fuentes_datos_verificadas.md
├── src/
│   ├── grafo.py
│   ├── agente.py
│   ├── pruebas.py
│   ├── visualizar.py
│   └── main.py
├── figures/
│   ├── grafo_red_emergencias.png
│   ├── ruta_normal.png
│   └── ruta_bloqueo.png
├── output/
│   └── salida_pruebas.txt
├── docs/
│   ├── Fase1_Emergencias_Bogota.docx
│   └── Fase1_Emergencias_Bogota.pdf
└── slides/
    └── Presentacion_Fase1_Emergencias_Bogota.pptx
```

## Instalacion
```bash
pip install -r requirements.txt
```

## Ejecucion
```bash
python src/main.py
```

Para regenerar las figuras:
```bash
python src/visualizar.py
```

## Pruebas incluidas
1. Ruta normal desde una emergencia simulada en Kennedy.
2. Comparacion entre seleccion por distancia y seleccion por utilidad.
3. Recalculo de ruta ante bloqueo dinamico de vias cercanas.

## Nota metodologica
El repositorio incluye un dataset inicial normalizado y reducido para Fase 1. La entrega documenta las fuentes oficiales verificadas para ampliar el proyecto con los datos completos en Fase 2 y Fase 3.
