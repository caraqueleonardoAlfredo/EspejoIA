PROJECT_CONTEXT = """
DIANUBY MIRROR AI — CONTEXTO VERIFICADO Y ALCANCE

PROPÓSITO: proyecto final de Ingeniería Electrónica que convierte un espejo en
una interfaz ambiental para consultar información, acceder a domótica y usar
asistencia por voz y experiencias visuales. Su propuesta de valor es concentrar
servicios cotidianos en una superficie familiar, manos libres o táctil.

IMPLEMENTADO: una Raspberry Pi 5 actúa como unidad central y ejecuta una
aplicación local Python/Flask con interfaz web. El estado mantiene tres modos:
INFO muestra hora, clima, temperatura, humedad y dólar; DOMÓTICA incorpora el
panel local de Home Assistant; IA ofrece un menú con asistente y Outfit AR.
Sensores GPIO detectan presencia y gestos: la presencia enciende la interfaz y
el gesto selecciona INFO, DOMÓTICA o IA. El hardware declarado adapta señales
de sensores de 12 V a GPIO mediante optoacopladores PC817; el software recibe
esas entradas como señales digitales activas en bajo.

INTEGRACIÓN FÍSICA DECLARADA: la instalación usa pantalla táctil, micrófono y
salida de audio. Home Assistant centraliza la domótica; se declara el uso de
Zigbee2MQTT y dispositivos reales, pero este repositorio no documenta sus
modelos, cantidad ni automatizaciones, por lo que no deben inventarse.

VOZ IMPLEMENTADA: push-to-talk en el navegador, conversión del audio con
FFmpeg, transcripción mediante el servicio de reconocimiento de Google,
respuesta contextual con OpenAI Responses API, síntesis con Edge TTS y
reproducción local por parlante. La transcripción no la realiza OpenAI.

OUTFIT AR — PROTOTIPO: usa cámara y el SDK de Decart con Lucy VTON para aplicar
una referencia visual de vestimenta al video en tiempo real. Es una experiencia
demostrativa dependiente del servicio remoto; no garantiza talle, ajuste físico
ni una recomendación comercial exacta.

SEGURIDAD Y CONECTIVIDAD: la aplicación y el estado principal funcionan
localmente en la Raspberry Pi; Home Assistant se abre en la red local. Las
claves del backend se cargan desde variables de entorno. Clima, dólar,
transcripción, OpenAI, Edge TTS y Decart necesitan Internet. La autenticación
cliente de Decart y el servidor Flask de desarrollo son aspectos a reforzar
antes de un despliegue productivo.

LIMITACIONES ACTUALES: estado en memoria, dependencia de servicios externos,
panel domótico embebido sin control conversacional directo, fallback de voz
limitado y ausencia de validación productiva a escala. MEJORAS FUTURAS: tokens
efímeros, integración segura con la API de Home Assistant, más funciones
offline, persistencia, monitoreo y pruebas de hardware y experiencia de usuario.

POTENCIAL, NO IMPLEMENTACIÓN ACTUAL: la interfaz podría adaptarse a hogares,
hoteles, comercios, salud y asistencia para información contextual, domótica y
accesibilidad. Son oportunidades futuras, no despliegues ni resultados validados.
""".strip()
