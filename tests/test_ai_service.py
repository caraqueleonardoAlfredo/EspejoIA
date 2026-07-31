import os
import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai_service import ContextualAIService, DEFAULT_MODEL


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

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_uses_responses_api_with_context_and_default_model(self):
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
        self.assertEqual(output.getvalue().strip(), "[AI] Respuesta OpenAI correcta")
        client_factory.assert_called_once_with(
            api_key="test-key",
            timeout=8.0,
            max_retries=0,
        )
        request = client.responses.create.call_args.kwargs
        self.assertEqual(request["model"], DEFAULT_MODEL)
        self.assertIn("31/07/2026 10:30", request["input"])
        self.assertIn("Modo actual: IA", request["input"])
        self.assertIn("Temperatura: 19 C", request["input"])
        self.assertIn("Pregunta del usuario: Necesito abrigo?", request["input"])

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

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_api_timeout_uses_fallback(self):
        client = Mock()
        client.responses.create.side_effect = TimeoutError("simulated timeout")
        fallback = Mock(return_value="Respuesta local")
        service = self.make_service(Mock(return_value=client), fallback)

        output = io.StringIO()
        with redirect_stdout(output):
            result = service.responder("Como esta el clima?")

        self.assertEqual(result, "Respuesta local")
        self.assertEqual(output.getvalue().strip(), "[AI] Usando fallback: TimeoutError")
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
