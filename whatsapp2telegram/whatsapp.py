import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from whatsapp2telegram.telegram_bot import TelegramBot


class WhatsAppClient:
    def __init__(self, telegram_bot: TelegramBot):
        self.telegram_bot = telegram_bot
        self.driver = None
        self.user_data_dir = os.path.join(os.getcwd(), "whatsapp_user_data")

    async def start(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")  # type: ignore
        chrome_options.add_argument("--lang=en")  # type: ignore
        chrome_options.add_argument(f"user-data-dir={self.user_data_dir}")  # type: ignore
        chrome_options.add_argument("--window-size=1920,1080")  # type: ignore
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://web.whatsapp.com")
        if not self._is_authenticated():
            await self._authenticate()

    def stop(self):
        if self.driver:
            self.driver.quit()

    def _is_authenticated(self) -> bool:
        try:
            if self.driver is None:
                raise WebDriverException("WebDriver is not initialized")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[@data-icon="chats-filled"]')
                )
            )
            return True
        except Exception:
            return False

    async def _authenticate(self):
        print("Authenticating...")
        if self.driver is None:
            raise WebDriverException("WebDriver is not initialized")
        qr_canvas_element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//canvas[@aria-label='Scan this QR code to link a device!']",
                )
            )
        )
        print("QR code found on page")

        screenshot = self.driver.get_screenshot_as_png()  # type: ignore
        await self.telegram_bot.send_qr_code(screenshot)
        print("QR code sent to Telegram. Please scan it with your WhatsApp app.")

        print("Waiting for QR code to be scanned")
        WebDriverWait(self.driver, 60).until(EC.staleness_of(qr_canvas_element))
        print("QR code scanned")

        print("Waiting for authentication")
        if self._is_authenticated():
            print("WhatsApp is authenticated successfully")
        else:
            raise Exception("Authentication failed")

    async def get_new_messages(self) -> list[dict[str, str]]:
        print("Getting new whatsapp messages")
        try:
            if self.driver is None:
                raise WebDriverException("WebDriver is not initialized")
            # # Dump the entire page HTML into a file
            # page_source = self.driver.page_source
            # with open("whatsapp_page_dump.html", "w", encoding="utf-8") as f:
            #     f.write(page_source)
            # print("Page HTML has been dumped to 'whatsapp_page_dump.html'")
            unread_chats = (
                self.driver.find_elements(
                    By.XPATH,
                    "//span[contains(@aria-label, 'unread message')]",
                )
                + self.driver.find_elements(
                    By.XPATH,
                    "//span[contains(@aria-label, 'непрочитанное сообщение')]",
                )
                + self.driver.find_elements(
                    By.XPATH,
                    "//span[contains(@aria-label, 'непрочитанных')]",
                )
            )

            unread_chats = unread_chats[1:]
            print(f"Unread chats: {len(unread_chats)}")

            messages: list[dict[str, str]] = []
            requres_refresh = len(unread_chats) > 1

            for chat in unread_chats:
                print(f"chat: {chat.text}")
                unread_count = chat.get_attribute("aria-label")  # type: ignore
                if unread_count:
                    unread_count = unread_count.split()[0]
                print(f"Unread messages count: {unread_count}")
                chat.click()  # type: ignore
                time.sleep(1)
                chat_name = self.driver.find_element(
                    By.XPATH, "//header/div[2]/div/div/div/span"
                ).text
                print(f"Chat name: {chat_name}")
                message_elements = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'copyable-text')]/parent::*"
                )
                # print(f"message_elements: {message_elements}")
                # Get the last unread_count elements from message_elements
                if unread_count and unread_count.isdigit():
                    unread_count_int = int(unread_count)
                    message_elements = message_elements[-unread_count_int:]
                else:
                    print(
                        f"Warning: Invalid unread count '{unread_count}' for chat '{chat_name}'"
                    )
                for element in message_elements:
                    message_text: str = "\n".join(
                        map(
                            lambda x: x.text,
                            element.find_elements(  # type: ignore
                                By.XPATH,
                                ".//span[contains(@class, 'selectable-text') and contains(@class, 'copyable-text')]/span",
                            ),
                        )
                    )
                    print(f"message_text: {message_text}")
                    messages.append(
                        {
                            "chat": chat_name,
                            "text": message_text,
                        }
                    )

            if requres_refresh:
                self.driver.refresh()
            return messages
        except WebDriverException as e:
            print("[get_new_messages] WebDriver connection lost. Restarting...")
            print(e)
            self.stop()
            await self.start()
            return []

    async def send_message(self, chat_name: str, message: str):
        try:
            if self.driver is None:
                raise WebDriverException("WebDriver is not initialized")

            search_box = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true' and @aria-autocomplete='list']",
                    )
                )
            )

            # try:
            #     screenshot_path = f"whatsapp_screenshot_{int(time.time())}.png"
            #     self.driver.save_screenshot(screenshot_path)
            #     print(f"Screenshot saved to {screenshot_path}")
            # except Exception as e:
            #     print(f"Failed to save screenshot: {e}")

            search_box.click()
            time.sleep(1)
            search_box.send_keys(chat_name)
            search_box.send_keys(Keys.ENTER)

            # try:
            #     screenshot_path = f"whatsapp_screenshot_{int(time.time())}.png"
            #     self.driver.save_screenshot(screenshot_path)
            #     print(f"Screenshot saved to {screenshot_path}")
            # except Exception as e:
            #     print(f"Failed to save screenshot: {e}")

            message_box = self.driver.find_element(
                By.XPATH, "//div[@contenteditable='true' and @data-tab='10']"
            )

            # try:
            #     screenshot_path = f"whatsapp_screenshot_{int(time.time())}.png"
            #     self.driver.save_screenshot(screenshot_path)
            #     print(f"Screenshot saved to {screenshot_path}")
            # except Exception as e:
            #     print(f"Failed to save screenshot: {e}")

            message_box.clear()
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            self.driver.refresh()
        except WebDriverException as e:
            print(e)
            print(f"[send_message] WebDriver connection lost. Restarting... {e}")
            self.stop()
            await self.start()
