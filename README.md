# NeuroEcosistema: depredadores y presas

**Autor:** Julian Pulido  
**Asignatura:** Electiva I de Profundización – Inteligencia Artificial  
**Universidad Santo Tomás – Seccional Tunja**

Simulación 2D de presas y depredadores controlados por perceptrones multicapa. El código usa Python 3 y la biblioteca estándar: no requiere instalar paquetes externos. La ventana gráfica usa Tkinter (incluido en muchas distribuciones de Python).

## Requisitos

- Python 3.10 o posterior recomendado.
- Tkinter para el comando de visualización.

## Ejecución

Desde la carpeta del proyecto:

```powershell
python main.py visualizar
```

Si todavía no existen modelos, la simulación usa redes inicializadas al azar. Entrena las redes de ambas especies antes de abrir la visualización:

```powershell
python main.py entrenar --generaciones 8 --poblacion 10 --episodios 2 --semilla 71
python main.py visualizar --escenario abundancia --semilla 42
```

Modelos guardados en `models/`. Haz clic en un agente para consultar las entradas, salidas de red y acción seleccionada. Para observar la línea base aleatoria:

```powershell
python main.py visualizar --escenario escasez --aleatorio
```

## Experimentos

Para comparar también dos arquitecturas, entrena la configuración alternativa y luego ejecuta los experimentos:

```powershell
python main.py entrenar --generaciones 8 --poblacion 10 --episodios 2 --semilla 171 --arquitectura 8,4 --directorio-modelos models/alternativa
python main.py experimentos --repeticiones 10 --semilla 2026
```

El comando ejecuta los tres escenarios definidos (abundancia, escasez y presión) con línea base aleatoria, redes iniciales, redes entrenadas y, si existe, la arquitectura alternativa. Escribe cada episodio en `results/experimentos.csv`; las comparaciones usan la misma semilla de entorno para cada repetición. Entrena primero para que se usen los modelos evolucionados. Registra los parámetros y semillas si cambias las opciones.

## Diseño de la red

- Presa: 10 entradas, dos capas ocultas de 12 y 8 neuronas, cinco salidas.
- Depredador: 9 entradas, dos capas ocultas de 12 y 8 neuronas, cinco salidas.
- Activación: `tanh` en las capas ocultas y de salida. La salida de mayor valor entre los movimientos legales determina la acción.
- Entradas: posición normalizada, dirección y distancia al objetivo/amenaza más cercano, energía, abundancia local/global y proximidad para captura.
- Aprendizaje: neuroevolución elitista. Se evalúan poblaciones de vectores de pesos en episodios con semillas reproducibles; se conservan los mejores y se generan descendientes mutando pesos.

## Archivos

- `neuroecosistema.py`: mundo, agentes, red neuronal, neuroevolución y exportación de resultados.
- `main.py`: entrenamiento, experimentación y ventana Tkinter.
- `INSTRUCCIONES_PROYECTO.md`: requisitos extraídos de la propuesta y plan.
- `BITACORA_DECISIONES.md`: decisiones iniciales y espacio para evidencia.
- `INFORME_TECNICO.md`: estructura para el informe final.

Los resultados deben obtenerse ejecutando el código. Cada JSON de modelo conserva aptitud por generación y el número de parámetros distintos frente al primer candidato inicial. La tendencia de aptitud durante el entrenamiento no demuestra por sí sola que haya aprendizaje generalizable; compara con semillas no usadas durante la selección y examina las métricas del CSV.

