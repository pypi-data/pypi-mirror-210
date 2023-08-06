Progress Runner
===============

`progress_runner` is an ncurses display for batch-processing.


Installation:
-------------

```bash
$ pip3 install progress_runner
```


Usage from shell:
-----------------

Create a python file with a `work` function in it. Ex:
```py
async def work(param):
	return True
```

The function must be async, take one parameter, and return bool.

```bash
$ progress_runner test.py test_params.txt
```

When using the shell command, the params file will be parsed as newline-delimited-text, and each line will be passed into your custom `work` function.


Usage in python:
----------------
```py
import progress_runner

async def work(param):
	return True

params = [
	(1,2,3),
	(4,5,6),
	(7,8,9)
]

progress_runner.run(work, params, nthreads=5)

# or:

p = progress_runner.ProgressRunner(work, params, nthreads=5)
p.run()
```
