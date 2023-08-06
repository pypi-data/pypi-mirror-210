"""
Custom exceptions
"""


class Exceptions:
    ElementNotFound = "[SeleNew] Element {} not found after {} number of attempts"
    BrowserNotFound = "[SeleNew] Failed to call unsupported browser {}"
    DriverNotInitialized = "[SeleNew] Failed to initialized {}"
    StateNotFound = "[SeleNew]: Failed to use unsupported {} state"
