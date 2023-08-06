from __future__ import annotations

from time import sleep

from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def click(
    driver: WebDriver,
    value: str,
    by: str = By.CSS_SELECTOR,
    innerText: str | None = None,
    retries: int = 3,
    sleep_between_retries: float = 1,
) -> None:
    """
    Click on an element with optional innerText filter.

    :param driver: WebDriver instance to interact with the browser.
    :param value: Value of the attribute to locate the target element.
    :param by: Attribute type to locate the target element, default is By.CSS_SELECTOR.
    :param innerText: Optional innerText filter to find the target element.
    :param retries: Number of retries to find the element before raising an exception, default is 3.
    :param sleep_between_retries: Time in seconds to wait between retries, default is 1 second.

    :raises ValueError: If the target element is not found after retries.
    """
    # Try to find and click the target element, retrying up to `retries` times, with a
    # `sleep_between_retries` delay between retries
    for _ in range(retries):
        try:
            element = find_element(driver, value, by, innerText)
            break
        except ValueError:
            sleep(sleep_between_retries)
            pass
    else:
        raise ValueError(f"Element not found: {value} (innerText: {innerText})")

    # Scroll the page so that the element is in view
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    # Click the element
    click_element_area(driver, element)


def find_element(
    driver: WebDriver,
    value: str,
    by: str = By.CSS_SELECTOR,
    innerText: str | None = None,
) -> WebElement:
    """
    Find a single HTML element within a webdriver page by attribute or criteria and optional
    inner text filtering and return the matched WebElement.

    :param driver: A WebDriver instance used to navigate and interact with the page
    :param value: The attribute value (e.g., CSS selector, xpath, etc.) to use in element search
    :param by: The attribute type used to search for the element (default: By.CSS_SELECTOR)
    :param innerText: Optional, the innerText to filter the elements by (if provided, only elements
                      with matching innerText will be returned)
    :return: WebElement that matches the search criteria and innerText (if provided)
    :raises ValueError: If the specified element is not found on the page
    """

    # Iterate over elements found by the specified attribute and value
    elements = driver.find_elements(by=by, value=value)
    for element in elements:
        # Check if the innerText of the element matches the specified innerText (if provided)
        if innerText is None or element.get_attribute("innerText").lower() == innerText.lower():
            break
    else:
        # Raise error if no matching element found
        raise ValueError(f"Element not found: {value} (innerText: {innerText})")
    return element


def click_element_area(driver: WebDriver, element: WebElement) -> None:
    """
    Click on the element area, even if it is covered by an overlay. This function
    is useful when dealing with elements obstructed by modal overlays or other
    overlapping elements, which may cause issues when attempting to interact
    with the intended element using Selenium.

    :param driver: A WebDriver instance used to interact with the webpage.
    :param element: A WebElement instance representing the element to be clicked.
    """
    # Get the Rect object of the element, containing its position and dimensions
    rect = element.rect

    # Use JavaScript to find the topmost element at the center of the given element
    overlayElement = driver.execute_script(
        "return document.elementFromPoint(arguments[0], arguments[1]);",
        rect["x"] + rect["width"] // 2,
        rect["y"] + rect["height"] // 2,
    )

    # If an overlay element is found
    if overlayElement is not None:
        try:
            # If the overlay element is clickable, click on it
            overlayElement.click()
        except ElementNotInteractableException:
            # Ignore exceptions related to unclickable overlay elements
            pass
        else:
            # If the click on the overlay element succeeds, stop execution
            return

    # If there's no overlay element, or the overlayElemet is not clickable, click on the given element
    element.click()
