---
stylesheet: style.css
pdf_options:
  format: A4
  margin: 20mm
---

# 🚀 Taller de Innovación Nestlé: Propuesta de Valor AeroStock OS

Este documento sintetiza la información operativa de Nestlé, las proyecciones tecnológicas y los entregables requeridos para la ronda final de pitch.

---

## 1. Análisis del Problema y Expectativas (Claves de Nestlé)

### 🔴 El Problema Actual (Dolores / Pain Points)
- **Inventario Manual e Inseguro:** El almacén cuenta con **24,000+ posiciones** a **12 metros de altura**. Al tener **~0% de automatización**, la auditoría exige elevar operarios en canastas de montacargas, generando un **alto riesgo de accidentes**.
- **Trazabilidad Lenta y Desconectada:** El WMS se actualiza de forma manual (post-ingreso). Esta falta de sincronización en tiempo real con SAP genera altas tasas de error, lotes cruzados y desajustes físicos.
- **Cuellos de Botella Constantes:** La dependencia intensiva de los montacargas manuales crea bloqueos al final de la línea. Esto fuerza paros no planificados que reducen el **OEE (Overall Equipment Effectiveness)** de la planta 24/7.

### 🟢 El Desafío (Expectativas de la Solución)
- **Capacidad:** Mover y auditar un flujo de **215 pallets por turno** en un tramo de **20 metros**.
- **Continuidad:** Operación **24/7** con **cero interrupciones** no planificadas.
- **Integración:** Sincronización instantánea de WMS y SAP.
- **KPIs Objetivo:** Reducción a 0 incidentes de seguridad, minimización de tiempos de ciclo y maximización de exactitud del inventario.

---

## 2. Formato: Contexto + Pregunta + Resultado

*(Basado en la estructura del "caso Xpress/motos")*

> **🔍 (Contexto con cuantificación):**  
> Actualmente en el almacén, auditar manualmente racks de hasta 12 metros de altura expone a los operarios a riesgos fatales y consume extensas jornadas exclusivas al conteo. Esto perpetúa un nivel de automatización del ~0% y retrasa el flujo crítico de 215 pallets por turno (dependientes de montacargas manuales). Estos paros no planificados terminan impactando gravemente el OEE y la capacidad productiva de la planta.

> **❓ (Pregunta Reto):**  
> ¿Cómo podríamos automatizar la búsqueda y validación de productos en posiciones de gran altura, de tal manera que reduzcamos drásticamente el tiempo de conteo, eliminemos al 100% el riesgo humano y sincronicemos la trazabilidad en tiempo real con SAP y WMS?

> **🎯 (Resultado Esperado):**  
> Reducir los ciclos de inventario a rutinas diarias automatizadas que alcancen un 99.9% de exactitud en los datos, erradicando por completo la necesidad de realizar trabajo humano en alturas peligrosas.

---

## 3. Formato: Diseño de Propuesta de Valor

*(Plantilla: Nuestro [X] ayuda a [Y] que quieren [Z] para [A] y [B] a diferencia de [C])*

* **NUESTRO(S):** AeroStock OS (Sistema ASRS visual integrado con Drones)
* **AYUDA(N):** A los jefes de bodega y operarios logísticos de Nestlé.
* **QUE QUIEREN:** Mantener un flujo ininterrumpido de 215 pallets por turno (24/7) y tener control total sobre sus inventarios.
* **PARA (Analgésico):** Eliminar la accidentabilidad por caídas de altura (12m) y reducir los frustrantes cuellos de botella y discrepancias en los registros.
* **Y (Creador de Valor):** Aumentar la exactitud del inventario por encima del 99% mediante auditorías visuales (Lectura LPN y detección de caducidades) sincronizadas instantáneamente con el WMS/SAP.
* **A DIFERENCIA DE:** Los métodos tradicionales manuales, donde el personal debe trepar en canastas de montacargas sin validación inmediata de los datos escaneados.

---

## 4. Cuantificación y Estimación de Mejora (Benchmarking)

Proyecciones de impacto del prototipo AeroStock frente al proceso manual actual:

1. ⏱️ **Eficiencia (Reducción de Tiempo)**  
   * **Actual:** Un operador tarda 2 a 3 minutos por cada pallet a gran altura (maniobra de montacargas + escaneo manual).  
   * **Proyección (Dron ASRS):** Vuelo y escaneo automatizado en 2 a 4 segundos por pallet.  
   * **Impacto:** **Reducción del 85% al 90%** en tiempos de captura de inventario.

2. 🛡️ **Seguridad (Cero Riesgo de Altura)**  
   * **Actual:** El 100% de las posiciones superiores a 2 metros exigen el uso de maquinaria para elevar personas.  
   * **Impacto:** **100% de eliminación** de horas-hombre en trabajo riesgoso de altura.

3. 📊 **Calidad (Trazabilidad y Precisión)**  
   * **Actual:** Tasa de error humano y tipeos tardíos entre el 3% y 5%.  
   * **Impacto:** Visión artificial + códigos CODE-128 garantizan una exactitud del **99.9%** con alertas directas por discrepancias de LPN o caducidad.

---

## 5. Estructura de Pitches

### 🎤 Pitch Preliminar (Elevator Pitch - 1 minuto)
"Hola, somos el equipo AeroStock. Actualmente en Nestlé operamos con más de 24,000 posiciones a 12 metros de altura y el control de inventario es 100% manual. Esto obliga a personas a subir en canastas de montacargas, poniendo en riesgo sus vidas, y causando cuellos de botella que frenan una planta que opera 24/7, generando pérdidas por mermas y falta de trazabilidad.
Para solucionarlo, hemos creado **AeroStock OS**, un sistema inteligente de visión artificial que utiliza drones autónomos para auditar la bodega. Nuestro software escanea códigos LPN en vuelo y usa Inteligencia Artificial para detectar caducidades en tiempo real, validándolo contra el WMS. Con esto, eliminamos el 100% del riesgo en alturas, logramos un 99.9% de exactitud y aseguramos que el flujo de 215 pallets por turno nunca se detenga. Gracias."

### 🎙️ Pitch Final (Estructura de 3 minutos - Una idea por diapo)

**Diapo 1: El Dolor y el Impacto (30 seg)**
> "¿Sabían que la falta de automatización en logística está afectando el OEE (Efectividad Total) de nuestra planta productiva? Hoy controlamos 24,000 posiciones de forma completamente manual. Obligamos a operarios a subir a 12 metros de altura en montacargas para auditar, lo que es un riesgo de vida latente y, además, genera cuellos de botella que interrumpen a una producción que no se detiene nunca (24/7)."

**Diapo 2: Contexto y Pregunta Reto (30 seg)**
> "Nuestro registro es tardío y no habla con SAP en tiempo real. La gran pregunta que nos hicimos fue: ¿Cómo podemos auditar a 12 metros, reducir drásticamente los tiempos y sincronizar los datos en segundos sin arriesgar a una sola persona?"

**Diapo 3: La Solución - AeroStock OS (60 seg)**
> "Les presentamos AeroStock OS. Un cerebro de Inteligencia Artificial que recibe video de drones exploradores. Mientras el dron recorre el pasillo y se orienta espacialmente mediante marcadores AprilTags, sus cámaras leen los códigos de barra LPNs y clasifican el producto usando redes neuronales. Si el dron encuentra un pallet de Cereal vencido o mal ubicado, AeroStock emite una alerta crítica a nuestra interfaz web y se integra vía API directamente al WMS. Cero intervención humana, validación 100% digital."

**Diapo 4: Propuesta de Valor y Resultados Cuantificados (45 seg)**
> "Nuestra propuesta de valor transforma un proceso lento y peligroso en una auditoría continua. 
> * **En Seguridad:** Pasamos de un riesgo inminente a CERO riesgo en altura.
> * **En Eficiencia:** Reducimos el tiempo de inventario en más de un 85%.
> * **En Trazabilidad:** Llegamos a una exactitud del 99.9%. Aseguramos que el flujo mínimo de 215 pallets por turno no sufra bloqueos, lo que protege el OEE de la planta y genera ahorros medibles inmediatos."

**Diapo 5: Cierre y Visión (15 seg)**
> "Con AeroStock OS, el almacén deja de ser un cuello de botella y se convierte en una ventaja competitiva ágil, rentable y sobre todo, segura. Muchas gracias."
