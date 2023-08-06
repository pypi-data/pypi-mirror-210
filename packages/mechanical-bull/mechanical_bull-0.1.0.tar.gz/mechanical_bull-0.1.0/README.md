# Mechanical Bull

Mechanical Bull is an ActivityPub Client application build based on [bovine](https://codeberg.org/bovine/bovine/). It's main goal is to provide a platform for automating activities undertaking in the FediVerse. Furthermore, it serves as a demonstration how ActivityPub Clients can be build with bovine.

## Installation

One can simply install mechanical_bull with pip via

```bash
pip install mechanical-bull
```

Once can then add a new user by running

```bash
python -m mechanical_bull.add_user [--accept] name hostname
```

This will  then prompt you to add a new did:key to your ActivityPub Actor. This did:key will be used to authenticate mechanical_bull against your server. Once you have added the key, press enter, and mechanical_bull is running. This method of authentication is called Moo-Auth-1 and described [here](https://blog.mymath.rocks/2023-03-15/BIN1_Moo_Authentication_and_Authoriation).

The configuration is saved in `config.toml`. bovine also supports authentication through private keys and HTTP signatures. For the details on how to configure this, please consult bovine. You can add further automations there.

Then you should be able to run mechanical bull via

```bash
python -m mechanical_bull.run
```

## Configuration

First by adding `log_file = "mechanical_bull.log"` to your `config.toml` you can make mechanical_bull write log entries to a file. Second, the config file has the following format

```toml
logfile = "mechanical_bull.log"

[cow]
private_key = "z3u2Yxcowsarethebestcowsarethebestcowsarethebest"
host = "cows.rocks"

[cow.handlers]
"mechanical_bull.actions.reject_follow_request" = true
# "mechanical_bull.actions.accept_follow_request" = true
"mechanical_bull.actions.log_to_file" = { filename = "cow.txt" }
```

The listed handlers are provided by mechanical_bull. They allow to accept / reject follow requests automatically, and the final one logs all traffic on the event source to "cow.txt".

## Writing automations

The examples of `mechanical_bull.actions.accept_follow_request` and `mechanical_bull.actions.log_to_file` should show how to write a new automation. The basic idea is that each file contains a function handle with signature

```python
async def handle(client: BovineClient, data: dict, **kwargs):
    return
```

here the kwargs are the dict given by the definiton in the handler block, i.e.

```toml
[user.handlers]
"my.package" = { arg1 = "value1", arg2 = "value2 }
```

## Contibuting

Please report bugs, etc. to the [issue tracker](https://codeberg.org/bovine/mechanical_bull/issues). Contributings in the form of pull requests are welcome. You can also contact me on the FediVerse at `@helge@mymath.rocks`.

Finally, I plan a multi-user "server" version of this project called __mechanical_herd__. The functionality should be similar, but updating the configuration should not require a restart. One might also think hooking into the redis from [bovine_pubsub](https://codeberg.org/bovine/bovine/src/branch/dev/bovine_pubsub) for this. mechanical_herd will probably be part of the bovine user management interface.
