########################################################################################################################
# IMPORTS

import logging

import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class SeleniumInterface:

    def __init__(self, chrome_options):
        options = uc.ChromeOptions()
        for option in chrome_options:
            options.add_argument(option)

        self.driver = uc.Chrome(options=options)

    def wait(self, css_selector, timeout=30):
        logger.info(f"waiting for {css_selector}...")
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(("css selector", css_selector)))

    def wait_and_click(self, css_selector, timeout=30):
        logger.info(f"clicking on {css_selector}...")
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(("css selector", css_selector))).click()

    def wait_and_fill(self, css_selector, text_to_fill, timeout=30):
        logger.info(f"sending text to {css_selector}...")
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(("css selector", css_selector))).send_keys(text_to_fill)

    def scroll_to_element(self, css_selector):
        logger.info(f"scrolling to {css_selector}")
        self.driver.execute_script("arguments[0].scrollIntoView();",
                                   self.driver.find_element("css selector", css_selector))

    def quit(self):
        logger.info("closing connections...")
        self.driver.quit()
