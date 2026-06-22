"""
AI服务测试 - 测试 AIManager、各 Provider 与便捷函数
"""
import pytest
from unittest.mock import MagicMock, patch

from app.services.ai_service import (
    ChatMessage,
    ChatResponse,
    ModelInfo,
    BaseAIProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleGeminiProvider,
    OllamaProvider,
    AIManager,
    ai_manager,
    ai_chat,
)


class TestChatMessage:
    """ChatMessage 数据类测试"""

    def test_create_with_required_fields(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None

    def test_create_with_name(self):
        msg = ChatMessage(role="assistant", content="Hi", name="bot")
        assert msg.name == "bot"

    def test_system_role(self):
        msg = ChatMessage(role="system", content="You are helpful")
        assert msg.role == "system"


class TestChatResponse:
    """ChatResponse 数据类测试"""

    def test_create_minimal(self):
        resp = ChatResponse(content="answer", model="gpt-4o", provider="openai")
        assert resp.content == "answer"
        assert resp.usage == {}
        assert resp.finish_reason is None
        assert resp.raw_response is None

    def test_create_with_usage(self):
        resp = ChatResponse(
            content="answer",
            model="gpt-4o",
            provider="openai",
            usage={"total_tokens": 100},
            finish_reason="stop",
        )
        assert resp.usage["total_tokens"] == 100
        assert resp.finish_reason == "stop"


class TestModelInfo:
    """ModelInfo 数据类测试"""

    def test_defaults(self):
        info = ModelInfo(name="gpt-4o", provider="openai")
        assert info.max_tokens == 4096
        assert info.supports_streaming is True
        assert info.supports_vision is False
        assert info.cost_per_1k_input == 0.0

    def test_custom_values(self):
        info = ModelInfo(
            name="claude",
            provider="anthropic",
            max_tokens=200000,
            supports_vision=True,
            cost_per_1k_input=0.003,
        )
        assert info.max_tokens == 200000
        assert info.supports_vision is True
        assert info.cost_per_1k_input == 0.003


class TestOpenAIProvider:
    """OpenAI Provider 测试"""

    def test_is_available_without_key(self):
        provider = OpenAIProvider(api_key=None)
        # api_key 来自 settings，可能为空字符串
        assert provider.is_available() == bool(provider.api_key)

    def test_is_available_with_key(self):
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.is_available() is True

    def test_get_available_models(self):
        provider = OpenAIProvider(api_key="sk-test")
        models = provider.get_available_models()
        assert len(models) > 0
        assert all(isinstance(m, ModelInfo) for m in models)
        assert all(m.provider == "openai" for m in models)

    def test_chat_completion_with_mock(self):
        provider = OpenAIProvider(api_key="sk-test")
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello back"
        mock_choice.finish_reason = "stop"
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        mock_resp.usage.prompt_tokens = 5
        mock_resp.usage.completion_tokens = 3
        mock_resp.usage.total_tokens = 8
        mock_client.chat.completions.create.return_value = mock_resp
        provider._client = mock_client

        messages = [ChatMessage(role="user", content="Hi")]
        resp = provider.chat_completion(messages, model="gpt-4o")
        assert isinstance(resp, ChatResponse)
        assert resp.content == "Hello back"
        assert resp.provider == "openai"
        assert resp.usage["total_tokens"] == 8

    def test_chat_completion_stream_with_mock(self):
        provider = OpenAIProvider(api_key="sk-test")
        mock_client = MagicMock()

        def make_chunk(text):
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = text
            return chunk

        mock_client.chat.completions.create.return_value = iter(
            [make_chunk("Hello "), make_chunk("world")]
        )
        provider._client = mock_client

        messages = [ChatMessage(role="user", content="Hi")]
        chunks = list(provider.chat_completion_stream(messages, model="gpt-4o"))
        assert "".join(chunks) == "Hello world"


class TestAnthropicProvider:
    """Anthropic Provider 测试"""

    def test_is_available_with_key(self):
        provider = AnthropicProvider(api_key="sk-ant-test")
        assert provider.is_available() is True

    def test_get_available_models(self):
        provider = AnthropicProvider(api_key="sk-ant-test")
        models = provider.get_available_models()
        assert len(models) > 0
        assert all(m.provider == "anthropic" for m in models)

    def test_chat_completion_with_mock(self):
        provider = AnthropicProvider(api_key="sk-ant-test")
        mock_client = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "Claude reply"
        mock_resp = MagicMock()
        mock_resp.content = [mock_block]
        mock_resp.stop_reason = "end_turn"
        mock_resp.usage.input_tokens = 10
        mock_resp.usage.output_tokens = 5
        mock_client.messages.create.return_value = mock_resp
        provider._client = mock_client

        messages = [
            ChatMessage(role="system", content="Be nice"),
            ChatMessage(role="user", content="Hi"),
        ]
        resp = provider.chat_completion(messages, model="claude-3")
        assert resp.content == "Claude reply"
        assert resp.provider == "anthropic"
        assert resp.usage["total_tokens"] == 15


class TestGoogleGeminiProvider:
    """Google Gemini Provider 测试"""

    def test_is_available_with_key(self):
        provider = GoogleGeminiProvider(api_key="gemini-key")
        assert provider.is_available() is True

    def test_get_available_models(self):
        provider = GoogleGeminiProvider(api_key="gemini-key")
        models = provider.get_available_models()
        assert len(models) > 0
        assert any(m.supports_vision for m in models)


class TestOllamaProvider:
    """Ollama Provider 测试"""

    def test_get_available_models_returns_defaults_on_error(self):
        provider = OllamaProvider(base_url="http://localhost:11434")
        # _get_client 会尝试创建 httpx 客户端，但 get_available_models 出错时返回默认
        models = provider.get_available_models()
        assert len(models) > 0
        assert all(m.provider == "ollama" for m in models)

    def test_is_available_returns_bool(self):
        provider = OllamaProvider(base_url="http://localhost:99999")
        # 连不上时返回 False
        assert isinstance(provider.is_available(), bool)


class TestAIManager:
    """AIManager 测试"""

    def test_singleton_instance(self):
        from app.services.ai_service import ai_manager as m1
        assert m1 is ai_manager

    def test_init_providers(self):
        manager = AIManager()
        assert "openai" in manager.providers
        assert "anthropic" in manager.providers
        assert "google" in manager.providers
        assert "ollama" in manager.providers

    def test_fallback_chain(self):
        manager = AIManager()
        assert len(manager.fallback_chain) >= 4
        assert manager.fallback_chain[0] == "openai"

    def test_get_provider(self):
        manager = AIManager()
        provider = manager.get_provider("openai")
        assert provider is not None
        assert isinstance(provider, OpenAIProvider)

    def test_get_provider_unknown(self):
        manager = AIManager()
        assert manager.get_provider("unknown") is None

    def test_add_and_get_api_key(self):
        manager = AIManager()
        manager.add_api_key("openai", "key-1")
        manager.add_api_key("openai", "key-2")
        k1 = manager.get_next_api_key("openai")
        k2 = manager.get_next_api_key("openai")
        k3 = manager.get_next_api_key("openai")
        assert k1 == "key-1"
        assert k2 == "key-2"
        # 轮询回到第一个
        assert k3 == "key-1"

    def test_get_next_api_key_empty(self):
        manager = AIManager()
        assert manager.get_next_api_key("nonexistent") is None

    def test_get_available_providers(self):
        manager = AIManager()
        # 直接设置 provider 的 api_key 让其可用
        manager.get_provider("openai").api_key = "sk-test"
        providers = manager.get_available_providers()
        assert isinstance(providers, list)
        assert "openai" in providers

    def test_get_provider_models(self):
        manager = AIManager()
        models = manager.get_provider_models("openai")
        assert len(models) > 0

    def test_get_provider_models_unknown(self):
        manager = AIManager()
        assert manager.get_provider_models("unknown") == []

    def test_get_all_models(self):
        manager = AIManager()
        # 直接设置 provider 的 api_key 让其可用
        manager.get_provider("openai").api_key = "sk-test"
        models = manager.get_all_models()
        assert len(models) > 0

    def test_chat_with_mock_provider(self):
        manager = AIManager()
        mock_provider = MagicMock(spec=BaseAIProvider)
        mock_provider.is_available.return_value = True
        mock_provider.chat_completion.return_value = ChatResponse(
            content="mocked", model="gpt-4o", provider="openai"
        )
        manager.providers["openai"] = mock_provider
        manager.fallback_chain = ["openai"]

        messages = [ChatMessage(role="user", content="Hi")]
        resp = manager.chat(messages, provider="openai", auto_fallback=False)
        assert resp.content == "mocked"
        mock_provider.chat_completion.assert_called_once()

    def test_chat_fallback_when_provider_unavailable(self):
        manager = AIManager()
        unavailable = MagicMock(spec=BaseAIProvider)
        unavailable.is_available.return_value = False
        available = MagicMock(spec=BaseAIProvider)
        available.is_available.return_value = True
        available.chat_completion.return_value = ChatResponse(
            content="fallback", model="claude", provider="anthropic"
        )
        manager.providers["openai"] = unavailable
        manager.providers["anthropic"] = available
        manager.fallback_chain = ["openai", "anthropic"]

        messages = [ChatMessage(role="user", content="Hi")]
        resp = manager.chat(messages, provider="openai", auto_fallback=True)
        assert resp.content == "fallback"
        assert resp.provider == "anthropic"

    def test_chat_all_providers_fail(self):
        manager = AIManager()
        unavailable = MagicMock(spec=BaseAIProvider)
        unavailable.is_available.return_value = False
        manager.providers["openai"] = unavailable
        manager.fallback_chain = ["openai"]

        messages = [ChatMessage(role="user", content="Hi")]
        with pytest.raises(Exception, match="All AI providers failed"):
            manager.chat(messages, provider="openai", auto_fallback=True)

    def test_chat_unknown_provider_raises(self):
        manager = AIManager()
        messages = [ChatMessage(role="user", content="Hi")]
        with pytest.raises(Exception):
            manager.chat(messages, provider="unknown", auto_fallback=False)


class TestAIChatFunction:
    """ai_chat 便捷函数测试"""

    def test_ai_chat_with_mock(self):
        with patch.object(ai_manager, "chat") as mock_chat:
            mock_chat.return_value = ChatResponse(
                content="hello world", model="gpt-4o", provider="openai"
            )
            result = ai_chat("Hi")
            assert result == "hello world"
            mock_chat.assert_called_once()
            args, kwargs = mock_chat.call_args
            assert kwargs["messages"][0].role == "user"
            assert kwargs["messages"][0].content == "Hi"

    def test_ai_chat_with_system_prompt(self):
        with patch.object(ai_manager, "chat") as mock_chat:
            mock_chat.return_value = ChatResponse(
                content="ok", model="gpt-4o", provider="openai"
            )
            result = ai_chat("Hi", system_prompt="Be nice")
            assert result == "ok"
            args, kwargs = mock_chat.call_args
            messages = kwargs["messages"]
            assert messages[0].role == "system"
            assert messages[0].content == "Be nice"
            assert messages[1].role == "user"
