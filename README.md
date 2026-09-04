#BrocoliLOGSvERIFIMATOR
## 🛡️ SENTINEL - Analizador de Logs y Auditor de Seguridad en Red

**SENTINEL** es una herramienta de consola escrita en Python diseñada para la **auditoría de seguridad básica, análisis de logs y reconocimiento de red**. Permite a administradores de sistemas y entusiastas de la ciberseguridad inspeccionar la salud del sistema, evaluar archivos de registro, identificar puertos expuestos y mapear la red local.

---

## 📌 Introducción

En el ámbito de la ciberseguridad y la administración de redes, la visibilidad es fundamental. **SENTINEL** centraliza varias tareas esenciales de diagnóstico en una sola interfaz interactiva por consola. 

Con esta herramienta puedes procesar rápidamente archivos de registros (logs) para detectar anomalías, auditar qué servicios locales están escuchando conexiones externas, identificar riesgos potenciales de exposición y mapear qué dispositivos están conectados a la red local (LAN).

---

## 🧠 Lo que Esperas Aprender con este Proyecto

Desarrollar y trabajar con **SENTINEL** te permite adquirir y reforzar habilidades clave en **Python, Redes y Ciberseguridad**:

1. **Análisis de Logs y Tratamiento de Archivos:**
   - Procesamiento eficiente de archivos de texto con el módulo `pathlib`.
   - Clasificación de niveles de severidad (`INFO`, `WARNING`, `ERROR`, `CRITICAL`, etc.) mediante agregación de datos (`collections.Counter`).

2. **Auditoría de Sistemas y Redes:**
   - Inspección de interfaces de red, IP local, gateway y servidores DNS configurados.
   - Identificación de procesos del sistema y sockets en estado de escucha (*listening ports*).

3. **Análisis de Riesgos y Seguridad:**
   - Evaluación heurística de servicios locales para clasificar el nivel de riesgo según su puerto, proceso y grado de exposición a la red.
   - Diferenciación entre servicios conocidos y no identificados.

4. **Reconocimiento de Red (LAN Scanning):**
   - Escaneo activo de segmentos de red para descubrir direcciones IP, direcciones MAC y fabricantes de dispositivos (*OUI lookup*).

5. **Generación de Reportes e Integración de Módulos:**
   - Arquitectura modular en Python (separación en `analizador`, `network_scanner`, `security_analyzer`, `sistema`, `report_generator`).
   - Exportación de hallazgos para documentación de auditorías.

---

## 🛠️ Funcionalidades Principales

- 📑 **Análisis de Logs:** Carga de archivos `.log` con conteo automático por niveles de severidad.
- 💻 **Auditoría de Sistema:** Muestra SO, arquitectura, hostname, IPs y servicios activos escuchando puertos.
- ⚠️ **Evaluación de Hallazgos:** Asigna niveles de riesgo y exposición a los servicios locales detectados.
- 🌐 **Escáner LAN:** Descubre dispositivos activos en la red local con su respectiva MAC y fabricante.
- 📊 **Generación de Reportes:** Exporta el resumen del análisis a un archivo consolidado.

---

## 🏗️ Estructura del Proyecto

```text
jubilant-broccoli/
├── main.py               # Menú interactivo y punto de entrada principal
├── analizador.py         # Lectura y detección de niveles en archivos de log
├── sistema.py            # Recopilación de métricas e información del SO/red
├── security_analyzer.py  # Evaluación de hallazgos y riesgos de seguridad
├── network_scanner.py   # Mapeo y escaneo de dispositivos en la LAN
└── report_generator.py  # Módulo encargado de consolidar y guardar reportes
