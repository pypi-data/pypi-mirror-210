**NAME**

::

 opd - operator daemon


**SYNOPSIS**


::

 python3 -m opd <cmd> [key=val] [key==val]
 python3 -m opd [-c] [-d] [-v]


**DESCRIPTION**


**opd** is intended to be programmable, it provides object persistence, an
event handler and some basic code to load modules that can provide additional
functionality.

**opd** uses object programming, object oriented programming without the
oriented. Object programming is programming where the methods are seperated
out into functions that use the object as the first argument of that funcion.
This gives base class definitions a clean namespace to inherit from and to load
json data into the object's __dict__. A clean namespace prevents a json loaded
attribute to overwrite any methods.

**opd** stores it's data on disk where objects are time versioned and the
last version saved on disk is served to the user layer. Files are JSON dumps
and paths carry the type in the path name what makes reconstruction from
filename easier then reading type from the object.


*INSTALL**


download the tarball from https://github.com/nopaths/opd/releases/


**USAGE**


use an alias for easier typing::

 $ alias opd="python3 -m opd"

list of commands::

 $ opd cmd
 cmd,err,flt,sts,thr,upt

start a console::

 $ opd -c
 >

start additional modules::

 $ opd mod=<mod1,mod2> -c
 >

list of modules::

 $ opd mod
 cmd,err,flt,fnd,irc,log,mod,rss,sts,tdo,thr,upt


**CONFIGURATION**


*irc*

:: 

 $ opd cfg server=<server>
 $ opd cfg channel=<channel>
 $ opd cfg nick=<nick>
  

*sasl*

::

 $ opd pwd <nsvnick> <nspass>
 $ opd cfg password=<frompwd>


*rss*

::

 $ opd rss <url>
 $ opd dpl <str_in_url> <i1,i2>
 $ opd rem <str_in_url>
 $ opd nme <str_in_url< <name>
    

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

 opd is placed in the Public Domain.
