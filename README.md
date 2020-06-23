Creates a JSON dump of the [fischertechnik database](https://ft-datenbank.de/)

Just a small project, not necessarily useful for third parties.

Install the requirements via `pip install -r requirements.txt`

Run `python ftdbdump.py` to create JSON file which contains all construction
kits and their parts (everything in category 653 of the database but not
category 661 (fischertip)).

To load the associated images, create a symbolic link "ftdb-dump.json" to 
the file created by `ftdbdump.py`.

Run `python downloadimages.py`.

A directory "images" is created.

To crop the images (remove white space), run `python ftdbcrop.py`. 
The directories "cropped_images" and "thumbnails" are created.

To create the Excel files, run `python ftdbxl.py` after the images have been 
loaded and edited as described above.

Thanks to the [DB team](https://ft-datenbank.de/ticket/4942) for maintaining 
the database.
