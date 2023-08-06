smb3-video-autosplitter
==============

.. image:: https://badge.fury.io/py/smb3-video-autosplitter.png
    :target: https://badge.fury.io/py/smb3-video-autosplitter

.. image:: https://ci.appveyor.com/api/projects/status/github/narfman0/smb3-video-autosplitter?branch=main
    :target: https://ci.appveyor.com/project/narfman0/smb3-video-autosplitter

Ingest video data from a capture card to autosplit in livesplit

Installation
------------

Make sure livesplit is running whenever you run the app!

Navigate to the most recent versioned release here:

https://github.com/narfman0/smb3-video-autosplitter/releases

Download the zip and extract to your favorite directory.

We need to update the trigger frame and region.
First, open `config.yml` and set `show_capture_video: true`,
then run the tool. Take a screen cap of princess peach's letter or similar, then
crop her face and take note of coordinates and width/height. Replace the `.png`
in the `data/` directory, and set the region (x,y,width,height) of the cropped
image relative to the original image.
Note1: Each nes, upscalar, everything has slightly different colors, thus we need to
replace all the pngs in the data directory.
Note2: Read it like "whenever you see the trigger (peachs face) at the given position
in the screen cap, split"

License
-------

Copyright (c) 2023 narfman0

See LICENSE for details
