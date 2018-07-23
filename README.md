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
virtualenv/bin/pip install -r requirements.txt
```

Make the database credentials available to the bot. The bot will search for `replica.my.cnf` or `my.cnf` in home directory or the bot's root directory. For uniformity, copy `~/replica.my.cnf` to `bot/my.cnf` and add host/database information to it. For Toolforge deployment, that would be something like:
```
[client]
password = ****
user = s53689
host = tools.db.svc.eqiad.wmflabs
database = s53689__commonsbot
```
For development, you want to either point this to your local MySQL instance. Alternatively, you can use port forwarding to connect to the tools database:
```
ssh -L 33061:tools.db.svc.eqiad.wmflabs:3306 <your labs username>@login.tools.wmflabs.org
```
In such case, the configuration would be:
```
[client]
password = ****
user = s53689
host = localhost
port = 33061
database = s53689__commonsbot
```

Set up wiki credentials. Currently, the bot uses BotPasswords. When you register a new bot password, you get a message like
> The new password to log in with **[bot username]@[sub bot name]** is **[some hex string]**. *Please record this for future reference*.

Create `user-password.py` in the bot's directory with the following content:
```
('bot user account', BotPassword('sub bot name', 'that long hex string'))
```

If you're running a clone that isn't using the default username `Community Tech bot`, you also need to change it in `user-config.py`.

Before running the bot for the first time, **be sure to run the first-run script** or the bot will post several thousands of notifications about the files nominated before the first run:

```
bin/first-run
```

### Toolforge
Set up cron jobs (with `crontab -e`):
```
# Run the bot's main script every 15 minutes
5,20,35,50 * * * * jsub -once -N commtech-commons ${HOME}/bot/bin/cronjob

# Clean up old logfiles and DB entries daily
0 3 * * * jsub -once -N commtech-commons-cleanup ${HOME}/bot/bin/cleanup
```

## Running the bot
Python 3.4+ is required.

### Stopping the bot
To kill a job that's currently running on Toolforge:
```
jstop commtech-commons
```

In most cases, you don't want to completely stop the bot if it misbehaves. Dry run mode is sufficient. In this mode, the bot does everything other than actually posting the messages on-wiki, which allows it to maintain its database in a consistent state, as well as generate logs with any error/debug messages that might help with development. To switch it on, change `"dry-run": false"` to `true` in `config.json`.

If a complete stop is required, comment it out in the crontab. **WARNING**: a complete stop means `bin/first-run` is required before a restart.

### Debug information
Toolforge automatically saves the bot's stdout to `commtech-commons.out` and stderr to `commtech-commons.err` - these contain lots of useful information.

To add some extra verbose debug output, set `verbose_output` to `True` in `user-config.py`.

Old listfiles are saved to `logs/{discussion|speedy}.txt.<timestamp>`.

## Adding a new wiki
Add its dbname to `wikis-enabled` in Git and make sure that all messages are localized.

## Configration
All settings are kept in `config.json`:
* `dry-run` - whether dry run mode os on, see "Stopping the bot" above.

## Development

### Overview

The bot's main operation consists of two scripts:
* `make-list.py` creates lists of files that have been around for long enough to be notified about.
* `post-notifs.py` runs off these files to determine which pages need updating and post the messages.

### Testing
The repository has a makefile, so just run
```
make
```
from the bot's root directory to run the tests.
