# Webscapy: Selenium Configured for Webscraping

## Introduction

Webscapy is a Python package that extends the capabilities of the Selenium framework, originally designed for web testing, to perform web scraping tasks. It provides a convenient and easy-to-use interface for automating browser interactions, navigating through web pages, and extracting data from websites. By combining the power of Selenium with the flexibility of web scraping, Webscapy enables you to extract structured data from dynamic websites efficiently.

## Features

1. <b>Automated Browser Interaction:</b> Webscapy enables you to automate browser actions, such as clicking buttons, filling forms, scrolling, and navigating between web pages. With a user-friendly interface, you can easily simulate human-like interactions with the target website.

2. <b>Undetected Mode:</b> Webscapy includes built-in mechanisms to bypass anti-bot measures, including Cloudflare protection. It provides an undetected mode that reduces the chances of detection and allows for seamless scraping even from websites with strict security measures.

3. <b>Headless Browsers:</b> Webscapy supports headless browser operations, allowing you to scrape websites without displaying the browser window. This feature is useful for running scraping tasks in the background or on headless servers.

4. <b>Element Load Waiting:</b> The package offers flexible options for waiting until specific elements are loaded on the web page. You can wait for elements to appear, disappear, or become interactable before performing further actions. This ensures that your scraping script synchronizes with the dynamic behavior of websites.

5. <b>Execute JavaScript Code:</b> Webscapy allows you to execute custom JavaScript code within the browser. This feature enables you to interact with JavaScript-based functionalities on web pages, manipulate the DOM, or extract data that is not easily accessible through traditional scraping techniques.

## Installation

You can install Webscapy using pip, the Python package manager. Open your command-line interface and execute the following command:

```python
pip install webscapy
```

## Getting Started

Following are the ways to create a driver

1. Simple Driver (headless)

```python
from webscapy import Webscapy

driver = Webscapy()

driver.get("https://google.com")
```

2. Turn off headless

```python
from webscapy import Webscapy

driver = Webscapy(headless=False)

driver.get("https://google.com")
```

3. Make the driver undetectable

```python
from webscapy import Webscapy

driver = Webscapy(headless=False, undetectable=True)

driver.get("https://google.com")
```

4. Connect to a remote browser

```python
from webscapy import Webscapy

REMOTE_URL = "..."
driver = Webscapy(remote_url=REMOTE_URL)

driver.get("https://google.com")
```

## Element Interaction

Following are the ways to interact with DOM Element

1. Load for the element to load

```python
ELEMENT_XPATH = "..."

driver.load_wait(ELEMENT_XPATH)
```

2. Load the element

```python
ELEMENT_XPATH = "..."

element = driver.load_element(ELEMENT_XPATH)
```

3. Interact / Click the element

```python
ELEMENT_XPATH = "..."

element = driver.load_element(ELEMENT_XPATH)
element.click()
```

## Network Activity Data

You can get network activity data after waiting for a while using commands like `time.sleep(...)`

```python
network_data = driver.get_network_data()

print(network_data)
```

## Close the driver

Always close the driver after using it to save memory, or avoid memory leaks

```python
driver.close()
```
