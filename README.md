# Sharinator

This software is a django project designed to provide a platform to organize the sharing of equipment
(and other stuff) with your coterie[TM].

## Non python packages
The python packages required to run the project are listed inside `requirements.txt`.
However there are a couple of non python software pices that are required (by `PIL`).
These are the following (listed as FreeBSD Ports):
 * jpeg
 * tiff
 * webp
 * lcms2
 * freetype2

## Tests
When running the automated tests the following packages (which aren't listed in requirements.txt)
are also required:
 * django-nose>=1.4.0
 * coverage>=5.0

Additionally you're expected to invoce `python3 manage.py test` from the top level folder
in order to make sure that some of the tests can find their corresponding test data.
