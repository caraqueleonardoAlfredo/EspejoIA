import os
import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai_service import ContextualAIService, DEFAULT_MODEL, SYSTEM_INSTRUCTIONS
from project_context import PROJECT_CONTEXT


INFO_DATA = {
    "clima": "Parcialmente nublado",
    "temperatura": "19 C",
    "humedad": "70%",
    "dolar": "$1300",
}


class ContextualAIServiceTests(unittest.TestCase):
    def make_service(self, client_factory, fallback=None):
        return ContextualAIService(
            client_factory=client_factory,
            info_provider=lambda: INFO_DATA,
            now_provider=lambda: datetime(2026, 7, 31, 10, 30),
            fallback=fallback or Mock(return_value="Respuesta de respaldo"),
        )

    @patch("ai_service.time.perf_counter", side_effect=[10.0, 11.234])
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_uses_responses_api_with_context_and_default_model(self, _mock_clock):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(
            output_text="  Llevate un abrigo liviano.  "
        )
        client_factory = Mock(return_value=client)
        service = self.make_service(client_factory)

        output = io.StringIO()
        with redirect_stdout(output):
            result = service.responder("Necesito abrigo?", "IA")

        self.assertEqual(result, "Llevate un abrigo liviano.")
        self.assertEqual(
            output.getvalue().strip().splitlines(),
            ["[AI] Respuesta OpenAI correcta", "[AI TIMING] openai=1.23s"],
        )
        client_factory.assert_called_once_with(
            api_key="test-key",
            timeout=8.0,
            max_retries=0,
        )
        request = client.responses.create.call_args.kwargs
        self.assertEqual(request["model"], DEFAULT_MODEL)
        self.assertEqual(request["reasoning"], {"effort": "none"})
        self.assertEqual(request["text"], {"verbosity": "low"})
        self.assertEqual(request["max_output_tokens"], 160)
        self.assertIn(PROJECT_CONTEXT, request["instructions"])
        self.assertIn("Raspberry Pi 5", request["instructions"])
        self.assertIn("31/07/2026 10:30", request["input"])
        self.assertIn("Modo actual: IA", request["input"])
        self.assertIn("Temperatura: 19 C", request["input"])
        self.assertIn("Pregunta del usuario: Necesito abrigo?", request["input"])

    def test_project_context_distinguishes_current_and_future_scope(self):
        self.assertIn("IMPLEMENTADO", PROJECT_CONTEXT)
        self.assertIn("PROTOTIPO", PROJECT_CONTEXT)
        self.assertIn("MEJORAS FUTURAS", PROJECT_CONTEXT)
        self.assertIn("POTENCIAL, NO IMPLEMENTACIÓN ACTUAL", PROJECT_CONTEXT)
        self.assertIn("no deben inventarse", PROJECT_CONTEXT)

    def test_prompt_contains_no_secrets(self):
        prompt = f"{SYSTEM_INSTRUCTIONS}\n{PROJECT_CONTEXT}"

        self.assertNotIn("OPENAI_API_KEY", prompt)
        self.assertNotIn("DECART_API_KEY", prompt)
        self.assertNotIn("dct_", prompt)
        self.assertNotIn("test-key", prompt)

    def test_required_identity_is_in_instructions(self):
        self.assertIn(
            "Soy el asistente inteligente de Dianuby Mirror AI, un espejo "
            "interactivo\ndesarrollado como proyecto final de Ingeniería "
            "Electrónica.",
            SYSTEM_INSTRUCTIONS,
        )

    def test_commercial_response_style_is_in_instructions(self):
        self.assertIn("embajador de Dianuby Mirror AI", SYSTEM_INSTRUCTIONS)
        self.assertIn("1 a 3 oraciones", SYSTEM_INSTRUCTIONS)
        self.assertIn("60 palabras", SYSTEM_INSTRUCTIONS)
        self.assertIn("entre 55 y 70 palabras", SYSTEM_INSTRUCTIONS)
        self.assertIn("valor, diferenciación", SYSTEM_INSTRUCTIONS)
        self.assertIn("No inventes funciones", SYSTEM_INSTRUCTIONS)

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "modelo-demo"},
        clear=True,
    )
    def test_uses_configured_model(self):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output_text="Hola")
        service = self.make_service(Mock(return_value=client))

        service.responder("Hola")

        self.assertEqual(
            client.responses.create.call_args.kwargs["model"],
            "modelo-demo",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_uses_fallback_without_creating_client(self):
        client_factory = Mock()
        fallback = Mock(return_value="Respuesta local")
        service = self.make_service(client_factory, fallback)

        result = service.responder("Que hora es?")

        self.assertEqual(result, "Respuesta local")
        fallback.assert_called_once_with("Que hora es?")
        client_factory.assert_not_called()

    @patch("ai_service.time.perf_counter", side_effect=[20.0, 28.0])
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_api_timeout_uses_fallback(self, _mock_clock):
        client = Mock()
        client.responses.create.side_effect = TimeoutError("simulated timeout")
        fallback = Mock(return_value="Respuesta local")
        service = self.make_service(Mock(return_value=client), fallback)

        output = io.StringIO()
        with redirect_stdout(output):
            result = service.responder("Como esta el clima?")

        self.assertEqual(result, "Respuesta local")
        self.assertEqual(
            output.getvalue().strip().splitlines(),
            ["[AI] Usando fallback: TimeoutError", "[AI TIMING] openai=8.00s"],
        )
        fallback.assert_called_once_with("Como esta el clima?")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_empty_api_response_uses_fallback(self):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output_text="  ")
        fallback = Mock(return_value="Respuesta local")
        service = self.make_service(Mock(return_value=client), fallback)

        result = service.responder("Que podes hacer?")

        self.assertEqual(result, "Respuesta local")
        fallback.assert_called_once_with("Que podes hacer?")


if __name__ == "__main__":
    unittest.main()
