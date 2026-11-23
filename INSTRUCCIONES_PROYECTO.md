# Lectura de la propuesta y plan de ejecución

## Instrucciones que provienen del documento adjunto

El documento de la asignatura solicita un ecosistema 2D de presas y depredadores con consumo de energía, alimento, movimiento, captura y episodios. Las decisiones de los agentes deben proceder de redes neuronales multicapa, con al menos dos capas ocultas por especie. También exige entrenamiento real, comparación contra una referencia aleatoria o basada en reglas, estadísticas consultables y ejecución reproducible.

La evaluación experimental debe incluir tres escenarios: abundancia de recursos y pocos depredadores; escasez de alimento; y mayor presión de depredación u obstáculos. Se requieren varias repeticiones con semillas registradas, comparación antes/después del entrenamiento, entre dos configuraciones y frente a una línea base. Deben informarse métricas pertinentes y acompañarse con hipótesis, controles, resultados y conclusiones basadas en los datos observados.

Los productos solicitados son: repositorio con instrucciones y dependencias, aplicación funcional y forma de reproducir el entrenamiento, informe técnico de máximo diez páginas (sin anexos), bitácora con al menos seis decisiones, evidencia experimental y sustentación. Se permite IA generativa, pero el equipo debe verificar y comprender el código e informar cómo la utilizó.

## Plan de trabajo sugerido

1. **Especificación:** cerrar observaciones, acciones, dinámica de energía y fin de episodio.
2. **Simulación:** construir reglas comunes y agentes aleatorios/de referencia.
3. **Redes y entrenamiento:** implementar redes diferenciadas con dos capas ocultas y neuroevolución; verificar que los pesos cambian.
4. **Visualización y registro:** mostrar agentes y métricas, guardar configuraciones, semillas y resultados en CSV.
5. **Experimentos:** ejecutar los tres escenarios y las comparaciones obligatorias con controles y repeticiones.
6. **Entrega académica:** completar bitácora, informe, gráficos y guía para la demostración.

## Criterio de honestidad experimental

Este archivo resume requisitos de la propuesta; no constituye evidencia de que el sistema ya se haya implementado ni de que alguna estrategia haya mejorado. Las tablas, cifras y conclusiones del informe deben salir de ejecuciones reales del programa.

