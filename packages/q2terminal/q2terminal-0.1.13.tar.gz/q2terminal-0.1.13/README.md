[![Python application](https://github.com/AndreiPuchko/q2terminal/actions/workflows/main.yml/badge.svg)](https://github.com/AndreiPuchko/q2terminal/actions/workflows/main.yml)
# Interaction with a terminal session

```python
from q2terminal.q2terminal import Q2Terminal
import sys

t = Q2Terminal()
t.run("programm", echo=True)
assert t.exit_code != 0

assert t.run("$q2 = 123") == []
assert t.run("echo $q2") == ["123"]


if "win32" in sys.platform:
    t.run("notepad")
    assert t.exit_code == 0
```
