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
* gnome3 - keyring, gconf 

If running Ubuntu 11.04::

        sudo apt-get install gir1.2-gtk-3.0 zenity libcanberra-gtk3-0
        sudo apt-add-repository ppa:gnome3-team/gnome3
        sudo apt-get install gtk3-engines 
        # probably you'll need to manualy install gnome3 theme to ~/.config/gtk-3/0

------------
Installation
------------
To install latest version::

        sudo pip install -U git+git://github.com/neubloc/neubloc-timesheet.git#egg=neubloc_timesheet

------
Runing
------
First you need to install icon (needs configured sudo)::

        neubloc_timesheet_install_icons

Then simply run::

        neubloc_timesheet
