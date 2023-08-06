"""
Framework Constants
"""


class Constants:
    FRAMEWORK = "SeleNew"

    CHROME = 'chrome'
    FIREFOX = 'firefox'
    EDGE = 'edge'

    SUPPORTED_BROWSERS = [CHROME, FIREFOX, EDGE]

    SINGLE_VISIBLE = "single_visible"
    MULTIPLE_VISIBLE = "multiple_visible"
    INVISIBLE = "invisible"
    CLICKABLE = "clickable"

    SUPPORTED_ELEMENT_STATES = [SINGLE_VISIBLE, MULTIPLE_VISIBLE, INVISIBLE, CLICKABLE]
