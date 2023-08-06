import curses
import time
import asyncio
import argparse
import importlib.util
import sys

def make_color(num, color):
    curses.init_pair(num, color, curses.COLOR_BLACK)
    return curses.color_pair(num)


class ProgressRunner():
    def __init__(self, fn, params, nthreads=10):
        
        self.fn = fn
        self.params = params
        self.nthreads = nthreads
        self.loglines = []
        self.nerrors = 0
        self.nsuccess = 0

    def init_curses(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        def run_inner(stdscr):
            self.stdscr = stdscr
            asyncio.run(self.run_display_and_tasks())
            p.teardown_curses()

        curses.wrapper(run_inner)

    def teardown_curses(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    async def display_main(self):
        self.stdscr.clear()

        ERROR_COLOR = make_color(1, curses.COLOR_RED)
        COPYTEXT_COLOR = make_color(2, curses.COLOR_BLUE)
        LOG_COLOR = make_color(3, curses.COLOR_YELLOW)
        MEASURE_COLOR = make_color(4, curses.COLOR_GREEN)
        PROGRESS_COLOR = make_color(5, curses.COLOR_WHITE)

        oldheight, oldwidth = (0,0)
        for i in range(1,10000):
            height, width = self.stdscr.getmaxyx()
            if oldheight != height or oldwidth != width:
                # this is a resize event
                self.stdscr.clear()
                curses.resizeterm(height, width)
                oldheight, oldwidth = (height, width)

            nloglines = height-5
            offset = 2
            for line in self.loglines[-nloglines:]:
                trimmedline = line[0:width-2]
                self.stdscr.addstr(offset,1,trimmedline,LOG_COLOR)
                offset += 1
            
            self.stdscr.addstr(0,1,f"Errors: {self.nerrors}", ERROR_COLOR)
            self.stdscr.addstr(1,1,"Current Requests: ", COPYTEXT_COLOR)

            progressstr = "Total Progress: ="
            self.stdscr.addstr(height-3,1,progressstr, COPYTEXT_COLOR)
            prog = (self.nsuccess+self.nerrors)/(self.nsuccess+self.nerrors+len(self.params))
            progwidth = width - 1 - len(progressstr) - 4
            progstr = "="*int(progwidth*prog) + "_"*int(progwidth*(1-prog))
            self.stdscr.addstr(height-3,len(progressstr), progstr, PROGRESS_COLOR)
            self.stdscr.addstr(height-3,len(progressstr)+progwidth+1, f"{int(100*prog)}%", MEASURE_COLOR)

            successstr = "Data successfully saved for requests up to"
            successstr = successstr[0:width-10]
            successpct = int(100*self.nsuccess/(self.nsuccess+self.nerrors+len(self.params)))
            self.stdscr.addstr(height-1,1,successstr +": ", COPYTEXT_COLOR)
            self.stdscr.addstr(height-1,len(successstr)+3, f"{successpct}%", MEASURE_COLOR)

            self.stdscr.refresh()
            await asyncio.sleep(0.1)


    async def worker(self):
        while len(self.params) > 0:
            p = self.params.pop()
            self.loglines.append(str(p))
            ret = await self.fn(*p)
            if ret:
                self.nsuccess += 1
            else:
                self.nerrors += 1

    async def run_tasks(self):
        workers = [ ]
        for i in range(self.nthreads):
            workers.append(self.worker())

        await asyncio.gather(*workers)


    async def run_display_and_tasks(self):
        await asyncio.gather(self.display_main(), self.run_tasks())

    def run(self):
        self.init_curses()


def run(fn, params, nthreads=5):
    p = ProgressRunner(fn, params)
    p.init_curses()


def main():
    parser = argparse.ArgumentParser(
        prog="progress_runner",
        description="ncurses progress runner for python script.",
        epilog=""
    )

    parser.add_argument('py_filepath')
    parser.add_argument('param_filepath')
    parser.add_argument('--nthreads', '-n', action='store_true', required=False)

    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("module.name", args.py_filepath)
    foo = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = foo
    spec.loader.exec_module(foo)

    async def inner_fn(param):
        return await foo.work(param)

    with open(args.param_filepath) as f:
        params = f.read().splitlines()

    nthreads = int(args.nthreads) if args.nthreads else 5

    run(foo.work, params, nthreads)


if __name__ == "__main__":
    main()