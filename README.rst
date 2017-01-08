GhiniTreePositioner
----------------------

This plugin solves the problem of estimating accurate positions for trees under a thick canopy, or for locations where high resolution aereal photos are not available.

Points need a 'id' property, and the reference system needs be in the same units as the measured mutual distances. Mutual distances are given in the form of a comma separated file, first two columns are the 'id' of to points, third column their distance, in the same measurement unit as the one in the layer.

Points already in the layer will be used as reference, Points referred to in the mutual distances file, but not in the layer, they will be added to the layer, as precisely as possible. 

This plugin is at a very experimental stage. I will be enhancing it as I need that, or as reaction to user feedback.

It would be highly useful if you could provide me with example data, for which, I'm quite sure, the plugin does not yet work.
