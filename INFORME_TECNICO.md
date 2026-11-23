# NeuroEcosistema: evaluación de agentes neuronales en un ecosistema simulado

**Autor:** Julian Pulido  
**Asignatura:** Electiva I de Profundización – Inteligencia Artificial  
**Universidad Santo Tomás – Seccional Tunja**

> Borrador de estructura. Reemplazar los campos entre corchetes con las decisiones confirmadas y datos de ejecuciones reales antes de entregar. No reportar cifras simuladas o esperadas como resultados.

## 1. Problema y pregunta

Se estudia si agentes controlados por redes neuronales pueden mejorar la búsqueda de alimento, la persecución y la evasión frente a una estrategia aleatoria, bajo distintos recursos y presiones del entorno. La pregunta orientadora es: ¿en qué condiciones el control neuronal mejora el desempeño frente a estrategias sin aprendizaje?

## 2. Diseño del entorno y agentes

El entorno es una cuadrícula de 32 × 32. Las presas consumen energía con el tiempo y recuperan energía al consumir plantas; los depredadores gastan energía y la recuperan al capturar una presa. Un episodio termina al alcanzar el límite de tiempo o cuando no quedan presas vivas. Se incluyen los escenarios de abundancia, escasez y presión (obstáculos y más depredadores).

Las presas reciben diez variables y los depredadores nueve. Cada red tiene dos capas ocultas de 12 y 8 neuronas, activación `tanh` y cinco salidas asociadas con movimientos discretos. Se enmascaran los movimientos fuera del tablero o bloqueados por obstáculos. [Explicar qué información se excluyó y cómo eso limita el comportamiento.]

## 3. Entrenamiento

Se usa neuroevolución elitista: evaluar candidatos, conservar los de mayor aptitud y crear descendientes mediante mutaciones aleatorias de sus pesos. La aptitud de presas combina supervivencia, energía final y alimento consumido; la de depredadores combina capturas y energía final. [Añadir generaciones, tamaño de población, episodios de entrenamiento, tasas de mutación y semillas finales.] Los parámetros del modelo se guardan en JSON.

## 4. Metodología experimental

Para cada escenario se ejecutan [n] repeticiones por configuración, con semillas registradas y condiciones iguales. Las comparaciones son: (1) control aleatorio frente a neuronal; (2) red inicializada frente a red entrenada; (3) configuración [A] frente a [B]. Para cada una, indicar hipótesis, variable independiente, métricas, controles y semillas. Las métricas por episodio se conservan en `results/experimentos.csv`.

## 5. Resultados

Insertar tablas y gráficas calculadas a partir del CSV. Reportar supervivencia media de presas, alimento consumido, capturas, energía final, duración del episodio y dispersión entre semillas cuando corresponda. Indicar número de repeticiones y valores faltantes.

| Escenario | Control | Supervivencia media | Alimento medio | Capturas medias | Energía final | Desviación/variabilidad |
|---|---|---:|---:|---:|---:|---:|
| Abundancia | Aleatorio | [calcular] | [calcular] | [calcular] | [calcular] | [calcular] |
| Abundancia | Neuronal entrenado | [calcular] | [calcular] | [calcular] | [calcular] | [calcular] |
| Escasez | Aleatorio | [calcular] | [calcular] | [calcular] | [calcular] | [calcular] |
| Escasez | Neuronal entrenado | [calcular] | [calcular] | [calcular] | [calcular] | [calcular] |
| Presión | Aleatorio | [calcular] | [calcular] | [calcular] | [calcular] | [calcular] |
| Presión | Neuronal entrenado | [calcular] | [calcular] | [calcular] | [calcular] | [calcular] |

## 6. Discusión, fallos y limitaciones

Interpretar patrones y variabilidad con base en las ejecuciones. Indicar resultados que contradigan las hipótesis. La aptitud optimizada es una función de recompensa diseñada por el equipo, por lo que puede favorecer atajos o conductas no deseadas. El alcance actual usa información del agente más cercano y movimientos en cuadrícula; estos supuestos limitan la complejidad ecológica. [Añadir fallos observados y evidencia concreta.]

## 7. Recomendaciones

Proponer cambios priorizados y justificar cada uno con una métrica o comportamiento observado, por ejemplo ampliar observaciones, ajustar la recompensa o evaluar otra arquitectura. No afirmar mejoras hasta ejecutar una comparación controlada.

## 8. Uso de herramientas de IA generativa

Se utilizó ChatGPT para apoyar la planificación, la estructura inicial del código y la documentación. El equipo debe revisar, comprender, ejecutar y adaptar el material; registrar qué sugerencias aceptó o descartó y las validaciones realizadas. [Describir la participación y validación real de cada integrante.]

## Referencias

[Añadir fuentes consultadas sobre redes neuronales, neuroevolución y metodología experimental, en el estilo solicitado por el docente.]
