# pyrosexmod
A monkeypatcher add-on for Pyrosex

## Introduction
pyrosexmod is a compilation of utils i developed for extend my personal use of Pyrosex. Then i started to use it and more bots and now i published it to make it easier to be installed in new projects.
It works *together* with pyrosex, this is *not* a fork nor modded version. It does monkey patching to add features to Pyrosex classes.

IMPORTANT: you should have installed asyncio pyrosex.

## Usage
Import `pyrosexmod` at least one time in your script, so you'll be able to use modified pyrosex in all files of the same proccess. Example:
```python
# config.py
import pyrosexmod.listen
from pyrosex import Client

app = Client('my_session')
```
```python
# any other .py
from config import app
# no need to import pyrosexmod again, pyrosex is already monkeypatched globally (at the same proccess)
```

I separated the patches between packages to allow you to import only what you want. The `__init__.py` of each package does the monkeypatch automatically as soon as they are imported (except for `pyrosexmod.helpers`, which provides classes and functions that should be explicitely imported).

### `pyrosexmod.listen`
Just import it, it will automatically do the monkeypatch and you'll get these new methods:
- `await pyrosex.Client.listen(chat_id, filters=None, timeout=30)`
Awaits for a new message in the specified chat and returns it
You can pass Update Filters to the filters parameter just like you do for the update handlers. e.g. `filters=filters.photo & filters.bot`

- `await pyrosex.Client.ask(text, chat_id, filters=None, timeout=30)`
Same of `.listen()` above, but sends a message before awaiting
You can pass custom parameters to its send_message() call. Check the example below.

- The bound methods `Chat.listen`, `User.listen`, `Chat.ask` and `User.ask`

Example:
```python
from pyrosexmod import listen # or import pyrosexmod.listen
from pyrosex import Client
client = Client(...)
...
    answer = await client.ask(chat_id, '*Send me your name:*', parse_mode='Markdown')
    await client.send_message(chat_id, f'Your name is: {answer.text}')    
```

### `pyrosexmod.filters`
Import it and the following Update Filters will be monkeypatched to `pyrosex.filters`:

- `filters.dice`
A dice message.

### Copyright & License
This project may include snippets of Pyrosex code
- Pyrosex - Telegram MTProto API Client Library for Python. Copyright (C) 2017-2020 Dan <<https://github.com/OTHFamily>>

Licensed under the terms of the [GNU Lesser General Public License v3 or later (LGPLv3+)](COPYING.lesser)
