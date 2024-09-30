import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException
from whatsapp2telegram.whatsapp import WhatsAppClient
from whatsapp2telegram.telegram_bot import TelegramBot
from selenium.webdriver.common.keys import Keys


@pytest.fixture
def mock_telegram_bot():
    return AsyncMock(spec=TelegramBot)


@pytest.fixture
def whatsapp_client(mock_telegram_bot: TelegramBot):
    return WhatsAppClient(mock_telegram_bot)


@pytest.mark.asyncio
async def test_start(whatsapp_client: WhatsAppClient):
    with patch("whatsapp2telegram.whatsapp.webdriver.Chrome") as mock_chrome:
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        whatsapp_client._is_authenticated = MagicMock(return_value=True)  # type: ignore

        await whatsapp_client.start()

        mock_chrome.assert_called_once()
        mock_driver.get.assert_called_once_with("https://web.whatsapp.com")
        assert whatsapp_client.driver == mock_driver


@pytest.mark.asyncio
async def test_start_with_authentication(whatsapp_client: WhatsAppClient):
    with patch("whatsapp2telegram.whatsapp.webdriver.Chrome") as mock_chrome:
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        whatsapp_client._is_authenticated = MagicMock(side_effect=[False, True])  # type: ignore
        whatsapp_client._authenticate = AsyncMock()  # type: ignore

        await whatsapp_client.start()

        mock_chrome.assert_called_once()
        mock_driver.get.assert_called_once_with("https://web.whatsapp.com")
        whatsapp_client._authenticate.assert_called_once()  # type: ignore


def test_stop(whatsapp_client: WhatsAppClient):
    mock_driver = MagicMock()
    whatsapp_client.driver = mock_driver

    whatsapp_client.stop()

    mock_driver.quit.assert_called_once()


def test_is_authenticated(whatsapp_client: WhatsAppClient):
    mock_driver = MagicMock()
    whatsapp_client.driver = mock_driver

    mock_element = MagicMock()
    mock_driver.find_element.return_value = mock_element

    assert whatsapp_client._is_authenticated() == True  # type: ignore

    mock_driver.find_element.side_effect = WebDriverException()
    assert whatsapp_client._is_authenticated() == False  # type: ignore


# @pytest.mark.asyncio
# async def test_authenticate(
#     whatsapp_client: WhatsAppClient, mock_telegram_bot: TelegramBot
# ):
#     mock_driver = MagicMock()
#     whatsapp_client.driver = mock_driver

#     mock_qr_element = MagicMock()
#     mock_driver.find_element.return_value = mock_qr_element
#     mock_driver.get_screenshot_as_png.return_value = b"fake_screenshot"

#     whatsapp_client._is_authenticated = MagicMock(return_value=True)  # type: ignore

#     await whatsapp_client._authenticate()  # type: ignore

#     mock_telegram_bot.send_qr_code.assert_called_once_with(b"fake_screenshot")  # type: ignore


# @pytest.mark.asyncio
# async def test_get_new_messages(whatsapp_client: WhatsAppClient):
#     mock_driver = MagicMock()
#     whatsapp_client.driver = mock_driver

#     mock_chat = MagicMock(spec=WebElement)
#     mock_chat.get_attribute.return_value = "1 unread message"
#     mock_driver.find_elements.return_value = [mock_chat]

#     mock_chat_name = MagicMock()
#     mock_chat_name.text = "Test Chat"
#     mock_driver.find_element.return_value = mock_chat_name

#     mock_message = MagicMock(spec=WebElement)
#     mock_message_span = MagicMock()
#     mock_message_span.text = "Test Message"
#     mock_message.find_elements.return_value = [mock_message_span]
#     mock_driver.find_elements.return_value = [mock_message]

#     messages = await whatsapp_client.get_new_messages()

#     assert len(messages) == 1
#     assert messages[0] == {"chat": "Test Chat", "text": "Test Message"}


@pytest.mark.asyncio
async def test_send_message(whatsapp_client: WhatsAppClient):
    mock_driver = MagicMock()
    whatsapp_client.driver = mock_driver

    mock_search_box = MagicMock(spec=WebElement)
    mock_message_box = MagicMock(spec=WebElement)
    mock_driver.find_element.side_effect = [mock_search_box, mock_message_box]

    await whatsapp_client.send_message("Test Chat", "Hello, World!")

    mock_search_box.send_keys.assert_any_call("Test Chat")
    mock_search_box.send_keys.assert_any_call(Keys.ENTER)
    mock_message_box.send_keys.assert_any_call("Hello, World!")
    mock_message_box.send_keys.assert_any_call(Keys.ENTER)
