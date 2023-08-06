## PyIMCLSTS

This tool reads the IMC schema from a XML file, locally creates files containing the messages and connects (imports) the main global machinery.

See `/example` to check an example implementation of the Follow Reference maneuver.

### Quickstart
- Fancying a virtual env? (Not needed. Just in case you want to isolate it from your python setup)
```shell
$ sudo apt install python3.8-venv
$ python3 -m venv tutorial_env
$ source tutorial_env/bin/activate
```
- To use:
```shell
$ pip3 install pyimclsts
$ # or, if you are cloning the repo, from the folder pyproject.toml is located:
$ pip3 install .
$ # If already installed, update it, with (might need to run it more than once):
$ pip3 install -U pyimclsts
```
- Choose a folder and have a version of the IMC schema. Otherwise, the following command will fetch the latest IMC version from the LSTS git repository. Extract messages locally, with:
```shell
$ python3 -m pyimclsts.extract
```
Check how to provide a black- or whitelist using:
```shell
$ python3 -m pyimclsts.extract --help
```
This is unnecessary in most scenarios, but can be useful if you really have constrained resources. Use it with caution, because it may crash if, for example, you receive an inlined message that has been blacklisted.

This will locally extract the IMC.xml as python classes. You will see a folder called `pyimc_generated` which contains base messages, bitfields and enumerations from the IMC.xml file. They can be locally loaded using, for example:
```python
import pyimc_generated as pg
```
In the top-level module, you will find some functions to allow you to connect to a vehicle and subscribe to messages, namely, a subscriber class.
```python
import pyimclsts.network as n

conn = n.tcp_interface('localhost', 6006)
sub = n.subscriber(conn)

# for example:
sub.subscribe_async(myfunction1, msg_id =pg.messages.Temperature, src='lauv-noptilus-1', src_ent='AHRS')
sub.subscribe_async(myfunction2, msg_id =pg.messages.EstimatedState, src='lauv-noptilus-1', src_ent=None)
```

In most cases, you can find the embedded documentation (docstrings) by hovering the mouse or using `help()` on interactive mode.

Check `/example` for further details.
    
