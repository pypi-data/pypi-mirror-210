# webdrivertools

A Python library providing utility functions for simplifying interactions with Selenium, the popular web testing and automation framework.

webdrivertools exports three core functions:

1. `click_element_area`
2. `find_element`
3. `click`

These functions can be imported using:

```python
from webdrivertools import click_element_area, find_element, click
```

## Requirements

- Python 3.10+
- Selenium

## Installation

To install webdrivertools, simply run:

```shell
pip install webdrivertools
```

## Functions

### click_element_area

```python
click_element_area(driver: WebDriver, element: WebElement) -> None
```

Click on the element area, even if it is covered by an overlay. This function is useful when dealing with elements obstructed by modal overlays or other overlapping elements, which may cause issues when attempting to interact with the intended element using Selenium.

### find_element

```python
find_element(driver: WebDriver, value: str, by: str = By.CSS_SELECTOR, innerText: str | None = None) -> WebElement
```

Find a single HTML element within a webdriver page by attribute or criteria and optional inner text filtering, returning the matched WebElement.

### click

```python
click(driver: WebDriver, value: str, by: str = By.CSS_SELECTOR, innerText: str | None = None, retries: int = 3, sleep_between_retries: float = 1) -> None
```

Click on an element with an optional innerText filter. Number of retries and sleep between retries can be tweaked according to requirements.

## Usage

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdrivertools import click, find_element

# Instantiate a WebDriver instance
driver = webdriver.Chrome()

# Navigate to a webpage
driver.get("https://example.com")

# Find and click a button with a specific CSS selector and innerText
click(driver, ".button-class", By.CSS_SELECTOR, "Submit")

# Find an element using an xpath and optional innerText filtering
element = find_element(driver, '//div[contains(@class, "target-element")]', By.XPATH, "Target Text")

# Click on an area of the element even if it's covered by an overlay
click_element_area(driver, element)

# Close the webdriver instance
driver.quit()
```

## License

MIT License

## Contributing

Contributions are welcome. Please create a new issue or a pull request with your proposed changes.

## Support

If you encounter any issues, please create a new issue on the GitHub repository.
