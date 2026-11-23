# Bitácora de decisiones técnicas

**Autor:** Julian Pulido  
**Proyecto:** NeuroEcosistema – Depredadores y presas

Las siguientes son decisiones iniciales de diseño. La evidencia experimental está pendiente de ejecución; se debe completar la última columna con resultados reales y cambiar la decisión si los datos lo justifican.

| N.º | Decisión | Alternativas consideradas | Criterio de selección | Evidencia disponible / pendiente |
|---|---|---|---|---|
| 1 | Representar el espacio como cuadrícula 32 × 32 | Espacio continuo; cuadrícula de distinto tamaño | Facilita reproducir posiciones, detectar colisiones y comparar semillas | Decisión de alcance para mantener el simulador pequeño; pendiente medir efecto del tamaño |
| 2 | Observar solo posición propia, objetivo/amenaza más cercano y energía | Dar el estado completo del mundo; usar solo coordenadas absolutas | Entradas compactas y relevantes para búsqueda, persecución y evasión | Supuesto de diseño; revisar si agentes se atascan o ignoran objetivos |
| 3 | Usar cinco acciones discretas: quieto y cuatro direcciones | Movimiento continuo o ocho direcciones | Salida neuronal interpretable y simple de inspeccionar | Definición del controlador; comparar frecuencia de movimiento y desempeño |
| 4 | Usar perceptrones multicapa `10/9 → 12 → 8 → 5` | Una capa oculta; más capas o neuronas | Cumple dos capas ocultas y mantiene el vector de pesos manejable | Cumplimiento arquitectónico verificable; comparación de arquitecturas pendiente |
| 5 | Usar `tanh` en capas ocultas y salida | ReLU, sigmoide, softmax | Salidas acotadas; selección del mayor valor entre acciones legales | Hipótesis técnica; comparar con otra activación/configuración si el tiempo lo permite |
| 6 | Entrenar por neuroevolución elitista | Aprendizaje supervisado; gradiente con recompensa | No exige etiquetar cada acción y permite evaluar comportamiento por episodios | Los genes guardados permiten demostrar cambio de parámetros; pendiente evaluación antes/después |
| 7 | Mantener control aleatorio como línea base | Solo reglas manuales; no presentar referencia | Fácil de reproducir y no incorpora aprendizaje | Comparación directa por semillas y escenarios; completar medias y dispersión desde CSV |
| 8 | Registrar semillas y métricas por episodio en CSV | Solo promedios agregados | Permite auditar repeticiones, variabilidad y detectar resultados atípicos | `results/experimentos.csv`; completar luego de ejecutar el comando experimental |

## Registro posterior a la ejecución

Para cada cambio, añadir fecha, configuración exacta, hipótesis, semillas utilizadas, resultados observados, decisión tomada y explicación. No borrar resultados que contradigan la hipótesis inicial.

