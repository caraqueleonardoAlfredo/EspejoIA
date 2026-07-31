import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from ia_simulada import responder as responder_fallback
from info_service import get_info_data


DEFAULT_MODEL = "gpt-5.6-sol"
OPENAI_TIMEOUT_SECONDS = 8.0

SYSTEM_INSTRUCTIONS = """
Sos el asistente contextual de Dianuby Mirror, un espejo inteligente.
Responde siempre en espanol argentino natural, con voseo cuando corresponda.
Tu respuesta se va a reproducir por voz: usa como maximo dos oraciones breves,
sin Markdown, listas, emojis ni introducciones innecesarias.
Usa los datos del contexto cuando sean relevantes y no inventes datos actuales.
Si un dato figura como no disponible, decilo de manera simple.
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
            "Contexto actual del espejo:\n"
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

        try:
            client = self.client_factory(
                api_key=api_key,
                timeout=OPENAI_TIMEOUT_SECONDS,
                max_retries=0,
            )
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
                reasoning={"effort": "low"},
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


load_dotenv()
AI_SERVICE = ContextualAIService()


def responder_contextual(pregunta: str, modo_actual: str = "IA") -> str:
    return AI_SERVICE.responder(pregunta, modo_actual)
