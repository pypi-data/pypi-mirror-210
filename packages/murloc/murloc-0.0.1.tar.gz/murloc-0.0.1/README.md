# Murloc
Extensible api server

## Example usage
```
import murloc

# Define server methods here.
# Must have (self, args) as params.
def hello(self, args):
    self.log("hello, world!")
    return f"args={args}"


# Include method routes in this dict like so.
methods = {
    "hello": hello,
}


# Main.
# -- Include methods in murloc.init() like so.
if __name__ == "__main__":
    m = murloc.init(methods=methods)
    m.listen()
```
