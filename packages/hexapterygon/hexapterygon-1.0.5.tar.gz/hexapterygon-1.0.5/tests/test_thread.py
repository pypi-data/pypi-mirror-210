import threading
from traceback import print_tb
from signal import SIGINT
from os import kill, getpid
from time import sleep


def on_thread_exc(e):
    print_tb(e.exc_traceback)
    kill(getpid(), SIGINT)

def my_thread(): # running "subproccesses" ...
    while True: sleep(1) 
    raise Exception('Oh no a thread exception...')

def my_busy_method(): # running main stuff ...
    raise Exception('Oh no a thread exception...')
    while True: sleep(1) 

def main():
    threading.excepthook = on_thread_exc
    t = threading.Thread(target=my_thread)
    t.daemon = True
    t.start()
    my_busy_method()

if __name__ == "__main__": main()

"""
# Solution for curses
**Extending an [answer](https://stackoverflow.com/a/7099229/11465149) + [comment](https://stackoverflow.com/questions/905189/why-does-sys-exit-not-exit-when-called-inside-a-thread-in-python#comment100748729_7099229) I found:** If you are using the [`uni-curses`](https://github.com/unicurses/unicurses) or [`curses`](https://docs.python.org/3/library/curses.html) module and you are stack **within** a thread wanting to exit ... or if you just want to forcefully but also cleanly exit your program for other reasons, you can also do it like so:

```
import os, signal, sys
# ...

def killAll(self,etype, value, tb):
    print('Exited cleanly!')


def force_exit():
    uc.endwin() # if you are using uni-curses
    sys.excepthook = self.killAll
    os.kill(os.getpid(), signal.SIGINT)

def my_thread():
   # Do stuff here ... and then:
   force_exit()

#...

t = threading.Thread(target=my_thread)
t.daemon = True
t.start()

# ... Here is happening something that prevents exit() like get_ch in a loop
```
```

Exited cleanly!

```
# General Solution
```python
import threading
from traceback import print_tb
from signal import SIGINT
from os import kill, getpid
from time import sleep


def exit_thread(ex):
    traceback.print_tb(ex.exc_traceback)
    kill(getpid(), SIGINT)

def my_thread(): # ...
    raise Exception('Oh no a thread exception... I wonder what will happen now...')

def my_busy_method():
    while True: sleep(1) # ...

def main():
    threading.excepthook = exit_thread
    t = threading.Thread(target=my_thread)
    t.daemon = True
    t.start()
    my_busy_method()

if __name__ == "__main__": main()
```
```
  File "/usr/lib/python3.10/threading.py", line 1016, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.10/threading.py", line 953, in run
    self._target(*self._args, **self._kwargs)
  File ".../test.py", line 16, in my_thread
    raise Exception('Oh no a thread exception... I wonder what will happen now...')
...
```

### References:
 - https://stackoverflow.com/questions/49663124/cause-python-to-exit-if-any-thread-has-an-exception
 - https://stackoverflow.com/questions/905189/why-does-sys-exit-not-exit-when-called-inside-a-thread-in-python#comment100748729_7099229
 - https://stackoverflow.com/questions/37706479/how-do-i-exit-an-application-from-a-thread-in-python

### Outro:
*It might be a low quality answer but it is one that definitely does the trick when it needs to ;)* 
"""
