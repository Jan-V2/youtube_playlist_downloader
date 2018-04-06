import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def get_imagefree_driver(is_headless):
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
    ## get the Firefox profile object
    firefoxProfile = FirefoxProfile()
    ## Disable CSS
    # disabling css breaks ajax
    # maybe fiddling around with permissions might help
    # firefoxProfile.set_preference('permissions.default.stylesheet', 2)

    ## Disable images
    firefoxProfile.set_preference('permissions.default.image', 2)
    ## Disable Flash
    firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    ## Set the modified profile while creating the browser object
    if is_headless:
        os.environ['MOZ_HEADLESS'] = '1'
    return webdriver.Firefox(firefoxProfile)