# CommonsNotifier

## Setting up

Clone the bot code:

```
git clone https://github.com/MaxSem/CommonsNotifier.git bot
cd bot
```

Set up the dependencies in virtualenv:

```
virtualenv --python=python3 virtualenv
virtualenv/bin/pip install pywikibot mwparserfromhell pymysql
```

Link to the pre-made config. The bot requires `config.json` to be present. Most of the time you want to just link to one of the preexisting configs, `config.dev.json` or `config.prod.json`.

```
ln -s config.<type>.json config.json
```

Currently, the bot uses BotPasswords.

When you register a new bot password, you get a message like
> The new password to log in with **[bot username]@[sub bot name]** is **[some hex string]**. *Please record this for future reference*.

Create `user-password.py` in the bot's directory with the following content:
```
('bot user account', BotPassword('sub bot name', 'that long hex string'))
```

If you're running a clone that isn't using the default username `Community Tech bot`, you also need to change it in `user-config.py`.

### Development environment

### Toolforge
