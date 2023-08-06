**NAME**

::

    nopaths - there are no paths

**SYNOPSIS**

::

    python3 -m nopaths <cmd> [key=val] [key==val]
    python3 -m nopaths [-c] [-d] [-v]

**DESCRIPTION**

``nopaths`` is a python3 bot, it connects to irc and provides a select sets of
commands. It doesn't use os.popen, does no external imports, can be run in client
or daemon mode and has batteries included. 

``nopaths`` is intended to be programmable, it provides object persistence, an
event handler and some basic code to load modules that can provide additional
functionality.

``nopaths`` uses object programming, programming where the methods are seperated
out into functions that use the object as the first argument of that funcion.
This gives base class definitions a clean namespace to inherit from and to load
json data into the object's __dict__. A clean namespace prevents a json loaded
attribute to overwrite any methods.

``nopaths`` stores it's data on disk where objects are time versioned and the
last version saved on disk is served to the user layer. Files are JSON dumps
and paths carry the type in the path name what makes reconstruction from
filename easier then reading type from the object.

``nopaths`` has some functionality builtin, it can take notes, add todo, maintain a
shopping list and display rss feeds. 


**INSTALL**

install from pypi::

    $ sudo python3 -m pip install nopaths

or download the tarball from https://github.com/nopaths/nopaths/releases/

**USAGE**

use an alias for easier typing::

    $ alias np="python3 -m nopaths"

list of commands::

    $ np cmd
    cmd,err,flt,sts,thr,upt

start a console::

    $ np -c
    >

start additional modules::

    $ np mod=<mod1,mod2> -c
    >

list of modules::

    $ np mod
    cmd,err,flt,fnd,irc,log,mod,rss,sts,tdo,thr,upt

start as daemon::

    $ np -d
    $ 

**CONFIGURATION**

*irc*


::

    $ np cfg server=<server>
    $ np cfg channel=<channel>
    $ np cfg nick=<nick>

*sasl*

::

    $ np pwd <nsvnick> <nspass>
    $ np cfg password=<frompwd>

*rss*

::

    $ np rss <url>
    $ np dpl <str_in_url> <i1,i2>
    $ np rem <str_in_url>
    $ np nme <str_in_url< <name>

**COMMANDS**

::

    cmd - commands
    cfg - irc configuration
    dlt - remove a user
    dpl - sets display items
    ftc - runs a fetching batch
    fnd - find objects 
    flt - instances registered
    log - log some text
    mdl - genocide model
    met - add a user
    mre - displays cached output
    nck - changes nick on irc
    now - genocide stats
    pwd - sasl nickserv name/pass
    rem - removes a rss feed
    req - reconsider
    rss - add a feed
    slg - slogan
    thr - show the running threads
    tpc - genocide stats into topic

**AUTHOR**

::

    No Paths <nopaths@proton.me>

**COPYRIGHT**

::

    nopaths is placed in the Public Domain.
