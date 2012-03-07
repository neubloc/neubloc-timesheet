-----
About
-----

Neubloc Timesheet controlling app

------------
External requirements
------------

* python2-gobject
* python2-gconf
* zenity

If running in Ubuntu 11.04::

        sudo apt-get install gir1.2-gtk-3.0 zenity libcanberra-gtk3-0

        sudo apt-add-repository ppa:gnome3-team/gnome3
        sudo apt-get install gtk3-engines 

------------
Installation
------------
To install latest version::

        sudo pip install -eU git+git://github.com/neubloc/neubloc-timesheet.git#egg=neubloc_timesheet
        or
        sudo pip install -U git+git://github.com/neubloc/neubloc-timesheet.git
