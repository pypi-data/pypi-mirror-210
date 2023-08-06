# Murloc
Extensible api server

## Example usage
```python
import murloc

# First, define the methods you want murloc to handle.
# They must have (self, params) as the function signature.
# `params` will be a `dict` containing the json request params.
def hello(self, params):
    print("hello, world!")
    return f"params={params}"

def command_set(self, params):
    return '{"err":0,"data":"configuration successful"}'


# Then add the methods to murloc using a `dict` like so.
myroutes = {
    "hello": hello,
    "set": command_set,
}
m = murloc.init(methods=myroutes)

# And start the server.
m.listen()
```

## Syntax
Murloc uses the following api conventions.

### Request format
```javascript
{
    "method": string,
    "params": {
        // any valid json
    }
}
```

### Success response
```javascript
{
    "err": 0,
    "data": // any valid json
}
```

### Error response
```javascript
{
    "err": 1,
    "data": // any valid json
}
```

## Examples
```bash
hero@azeroth:~$ cat hero.py
import murloc

def new_character(self, params):
    self.log(f"setting class to {params['class']}")
    self.log(f"equiping weapons: {params['weapons']}")
    return '{"err":0,"data":null}'

methods = {
    "new": new_character,
}
m = murloc.init(methods=methods)

m.listen()
hero@azeroth:~$ python3 hero.py
[2023-05-27 20:35:19] [3139]
     ___
    /\  \
   /::\  \       murloc 1.0.0
  /:/\:\  \
 /:/  \:\  \
/:/__/ \:\__\    Running in default mode
\:\  \ /:/  /    Port: 8048
 \:\  /:/  /     PID:  3139
  \:\/:/  /
   \::/  /             Aaaaaughibbrgubugbugrguburgle!
    \/__/

[2023-05-27 20:35:19] [3139] Listening at 127.0.0.1:8048
[2023-05-27 20:35:33] [3142] Connection from ('127.0.0.1', 43668)
[2023-05-27 20:35:47] [3146] Connection from ('127.0.0.1', 45626)
[2023-05-27 20:35:47] [3146] setting class to warrior
[2023-05-27 20:35:47] [3146] equiping weapons: ['worn shortsword', 'worn buckler']
```

```bash
hero@azeroth:~$ echo '{"method":"new","params":{"class":"warrior","weapons":["worn shortsword","worn buckler"]}}' | nc -q 0 localhost 8048
{"err":0,"data":null}
hero@azeroth:~$ echo '{"method":"dwarf","params":{"variable":"class","value":"warrior"}}' | nc -q 0 localhost 8048
{"err":1,"data":"method not defined"}
hero@azeroth:~$ echo '{"params":{"variable":"class","value":"warrior"}}' | nc -q 0 localhost 8048
{"err":1,"data":"request lacks method"}
hero@azeroth:~$ echo '{"method":"dwarf"}' | nc -q 0 localhost 8048
{"err":1,"data":"request lacks params"}
hero@azeroth:~$
```

## Customizing murloc
The following default parameters can be changed by setting them in the murloc `init()` function.
```python
    version="1.0.0",
    host="127.0.0.1",
    port=8048,
    name="murloc",
    mode="default",
    url="Aaaaaughibbrgubugbugrguburgle!",
    methods=dict(),
    logfile=None,
```
