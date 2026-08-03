import os
import time
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from ia_simulada import responder as responder_fallback
from info_service import get_info_data
from project_context import PROJECT_CONTEXT


DEFAULT_MODEL = "gpt-5.6-luna"
OPENAI_TIMEOUT_SECONDS = 8.0

SYSTEM_INSTRUCTIONS = f"""
Actuá como embajador de Dianuby Mirror AI. Hablá en español argentino de manera
natural, segura, positiva y fácil de entender. Priorizá los beneficios y la
experiencia del usuario. Respondé normalmente en 1 a 3 oraciones y no superes
las 60 palabras; ampliá sólo si te piden más detalle. Evitá tecnicismos salvo
que la pregunta sea técnica. No uses Markdown, listas, emojis ni introducciones
innecesarias.

Usá la clasificación técnica del contexto de forma interna para mantener la
precisión, pero no menciones espontáneamente «prototipo», «integración
declarada», «limitación», «no validado», «en desarrollo» ni «mejora futura».
No justifiques constantemente el alcance académico. Describí con confianza las
funciones realmente implementadas y explicá límites o trabajo futuro sólo si
te lo preguntan directamente. Para inversores, destacá valor, diferenciación,
escalabilidad y aplicaciones. No inventes funciones, dispositivos, métricas,
resultados ni capacidades. Si desconocés algo, reconocelo brevemente.

No leas código ni nombres de archivos salvo que te lo pidan. No reveles
credenciales, configuración secreta, variables de entorno ni datos sensibles.
También podés responder preguntas generales sin forzar una relación con el
proyecto cuando no corresponda.

Ante «¿qué eres?» o una formulación equivalente, respondé exactamente:
«Soy el asistente inteligente de Dianuby Mirror AI, un espejo interactivo
desarrollado como proyecto final de Ingeniería Electrónica.»

Cuando te pidan presentar el proyecto, prepará una explicación atractiva de
aproximadamente 30 segundos, entre 55 y 70 palabras, enfocada en el valor, la
experiencia y la diferenciación, sin aclarar espontáneamente que es un
prototipo y sin exagerar capacidades.

{PROJECT_CONTEXT}
""".strip()


class ContextualAIService:
    def __init__(
        self,
        client_factory=OpenAI,
        info_provider=get_info_data,
        now_provider=datetime.now,
        fallback=responder_fallback,
    ):
        self.client_factory = client_factory
        self.info_provider = info_provider
        self.now_provider = now_provider
        self.fallback = fallback

    def _fallback(self, pregunta: str, error_type: str) -> str:
        print(f"[AI] Usando fallback: {error_type}")
        return self.fallback(pregunta)

    def _build_input(self, pregunta: str, modo_actual: str) -> str:
        info = self.info_provider()
        ahora = self.now_provider()

        return (
            "Contexto dinámico actual del espejo:\n"
            f"- Fecha y hora local: {ahora.strftime('%d/%m/%Y %H:%M')}\n"
            f"- Modo actual: {modo_actual}\n"
            f"- Clima: {info.get('clima', '--')}\n"
            f"- Temperatura: {info.get('temperatura', '--')}\n"
            f"- Humedad: {info.get('humedad', '--')}\n"
            f"- Dolar blue venta: {info.get('dolar', '--')}\n\n"
            f"Pregunta del usuario: {pregunta}"
        )

    def responder(self, pregunta: str, modo_actual: str = "IA") -> str:
        pregunta = (pregunta or "").strip()
        if not pregunta:
            return self._fallback(pregunta, "EmptyInput")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._fallback(pregunta, "MissingAPIKey")

        started_at = time.perf_counter()

        try:
            client = self.client_factory(
                api_key=api_key,
                timeout=OPENAI_TIMEOUT_SECONDS,
                max_retries=0,
            )
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
                reasoning={"effort": "none"},
                text={"verbosity": "low"},
                instructions=SYSTEM_INSTRUCTIONS,
                input=self._build_input(pregunta, modo_actual),
                max_output_tokens=160,
            )
            answer = " ".join((response.output_text or "").split()).strip()
            if not answer:
                return self._fallback(pregunta, "EmptyResponse")

            print("[AI] Respuesta OpenAI correcta")
            return answer
        except Exception as error:
            return self._fallback(pregunta, type(error).__name__)
        finally:
            elapsed = time.perf_counter() - started_at
            print(f"[AI TIMING] openai={elapsed:.2f}s")


load_dotenv()
AI_SERVICE = ContextualAIService()


def responder_contextual(pregunta: str, modo_actual: str = "IA") -> str:
    return AI_SERVICE.responder(pregunta, modo_actual)
