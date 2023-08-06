# SeleniumBot

This library provides you tools that will help you create selenium bots.

## Installation

`pip install seleniumbot`

## Actions

Actions are classes that will tell bot what to do. There are two types of actions, `simple` actions
and `navigation` actions.

Actions also have some required properties. Here's the list of them:
- `name` - Action name.
- `coefficient` - The chance that this action will be executed.

### Simple Actions

Simple actions are the actions that do not create other actions.

### Navigation Actions

Navigation actions are the actions that after execution return set of new actions.

## Examples

### Simple Action

This is the example on how to create a simple action. Note, that this action receives the button
that it will click to during it's executing. This button should come from `Navigation` type action.

> `Note`: This action goes into new page, where old actions may be irrelevant. For this type
> of actions we need to set `flush_actions = True`

`click_video.py:`
```python
import time

from selenium.webdriver.remote.webelement import WebElement

from seleniumbot import SeleniumClient, Action


class ClickVideo(Action):
    name = 'ClickVideoAction'
    coefficient = 0.1
    flush_actions = True  
    

    button: WebElement

    def __init__(self, button: WebElement):
        self.button = button

    def _execute(self, client: SeleniumClient, last_action: Action | None):
        self.button.click()

        # YouTube has different page reload logic when clicking on videos,
        # so we need to add some sleep time
        time.sleep(10)

```


### Navigation Action

This is example of a `ScrollAction` which is `Navigation` action type, that produces new actions 
(`ClickVideoAction` in particular).

`scroll.py:`

```python
from selenium.webdriver.common.by import By

from click_video import ClickVideo
from seleniumbot import Action, SeleniumClient


class ScrollAction(Action):
    name = 'ScrollAction'
    coefficient = 0.75

    def _execute(self, client: SeleniumClient, last_action: Action | None) -> list[Action]:
        scroll_min, scroll_max = 400, 1500
        client.scroll(scroll_min, scroll_max)

        click_video_actions = self.__get_click_video_actions(client)

        actions = [*click_video_actions]
        return actions

    @staticmethod
    def __get_click_video_actions(client: SeleniumClient) -> list[ClickVideo]:
        video_id = 'thumbnail'
        videos = client.find_elements(By.ID, video_id)
        click_video_action = [ClickVideo(button=video) for video in videos]

        return click_video_action

```

### StartAction

In order to tell our bot where to start we need to create another `StartAction`.
`StartAction` is a special action that should be executed only once, at the beginning.

`start.py`

```python
from seleniumbot import Action, SeleniumClient


class StartAction(Action):
    name = 'StartAction'
    coefficient = 0  # put any number since this field is ignored for StartAction

    def _execute(self, client: SeleniumClient, last_action: Action | None):
        client.goto('https://www.youtube.com/')

```

### Putting it all together

`main.py:`

```python
from selenium.webdriver.chrome.options import Options

from scroll import ScrollAction
from seleniumbot import SeleniumBot
from start import StartAction


def main():
    # In order to test and see how bot behaves, we need to reassign options
    # that will not use --headless mode.
    options = Options()
    options.add_argument('window-size=1920,1080')
    
    
    bot = SeleniumBot(start_action=StartAction, options=options)
    bot.set_navigation_actions([ScrollAction])
    bot.start()


if __name__ == '__main__':
    main()


```

## Using proxy

In order to use proxy, just pass second type of options to SeleniumBot.

```python
from scroll import ScrollAction
from selenium.webdriver.chrome.options import Options
from start import StartAction

from seleniumbot import SeleniumBot


def main():
    # In order to test and see how bot behaves, we need to reassign options
    # that will not use --headless mode.
    options = Options()
    options.add_argument('window-size=1920,1080')

    seleniumwire_options = {
        'proxy': {
            'https': 'https://user:password@host:port'
        }
    }

    bot = SeleniumBot(start_action=StartAction, options=options, seleniumwire_options=seleniumwire_options)
    bot.set_navigation_actions([ScrollAction])
    bot.start()


if __name__ == '__main__':
    main()

```