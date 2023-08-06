# SeleNew
SeleNew is a framework over Selenium to simplify UI Test Automation. \
SeleNew is a beautified and simplified approach to make your work easy and much faster. 
Why SeleNew? There is a list of advantages that will help you to implement UI Test Automation in a very simplified way. 

* You don't need to worry about killing the browser. SeleNew will do it for you. This will happen automatically as soon as work with the browser is completed and browser no longer needed. 
* You don't need to worry about the locator search strategy. Whether it's CSS_SELECTOR, XPATH, ID or something else, it doesn't matter, rest assured SeleNew will find the element if there is one on the page.
* We have the possibility of a `go_around` in SeleNew. What does it mean? So, it is not a secret and known fact that some elements may be flaky and will not be found for some reason, while they are on the page. SeleNew will go around as long as needed to find it. This option can be easily customized by you. You just need to change the value of the `go_around` parameter
* You don't need to worry about waits and struggle with explicit and implicit waits. SeleNew will do it on your behalf. It will wait for the element if the element exists on the page. This option can be easily customized by you. You just need to change the value of the `timeout` parameter.
* SeleNew provides clear and beautiful logging and exceptions. It will make your debugging much more easy

# Pre-requisites

Python >= 3.8

# Getting started

## Installation

First install SeleNew by below command
```
pip install selenew==<version>
```

To start work using SeleNew please import required components. Example below:
```
from selenew.base.base_object import Selenew
```

## Let's do it as simple as possible

Use below simplified approach from SeleNew
```
selenew.send_keys(".search", "search object")
```

Instead of below complicated approach from Selenium
```
WebDriverWait(self.driver, 2).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, ".search"))
        ).send_keys("search object")
```

## SeleNew Built-in functionalities
All `go_around`, `timeout` and `element_state` parameters can be customized as shown below

### `go_around` functionality
Define as many attempts as you like or use the default one. Default value: 3
```
selenew = SeleNew(browser, go_around=5)
```

### `timeout` functionality
Define as many times as you like, or use the default one. Default value: 3
```
selenew.click(".login-button", timeout=5)
```

### `element_state` functionality
Use one of supported states. Default value: "single_visible" \
All supported states:
* "single_visible"
* "clickable"
* "multiple_visible"
* "invisible"
```
selenew.click(".login-button", element_state="clickable")
```

# Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# License
This project is licensed under the MIT License.

# Author
© 2023 [Toghrul Mirzayev](https://github.com/ToghrulMirzayev)