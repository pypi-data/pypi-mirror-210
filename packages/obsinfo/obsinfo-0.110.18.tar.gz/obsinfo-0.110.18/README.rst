README
===================

*obsinfo* is a system for for creating FDSN-standard data and metadata for
ocean bottom seismometers using standardized, easy-to-read information files 

Current goal
-------------------

To come out with a first version (v1.x) schema for the information files.  We
would like input from seismologists and ocean bottom seismometer
manufacturers/operators about what information/capabilities are missing.  
Existing questions can be found/modified in the gitlab `ISSUES <https://gitlab.com/resif/obsinfo/-/issues>`_


`Documentation <https://obsinfo.readthedocs.io/en/latest/index.html>`_

`Source code <https://gitlab.com/resif/obsinfo>`_


Versioning
----------------

We use standard MAJOR.MINOR.MAINTENANCE version numbering but, while the
system is in prerelease:

- MAJOR==0

- MINOR increments every time the information 
  file structure changes in a **non-backwards-compatible** way

- MAINTENANCE increments when the code changes or the file structure changes
  in a **backwards-compatible** way