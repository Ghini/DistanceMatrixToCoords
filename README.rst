GhiniTreePositioner
======================

what is this
-------------
This plugin solves the problem of estimating accurate positions for trees under a thick canopy, or for locations where high resolution aereal photos are not available.

how does it work
------------------

Points need a 'id' property, and the reference system needs be in the same units as the measured mutual distances. Mutual distances are given in the form of a comma separated file, first two columns are the 'id' of to points, third column their distance, in the same measurement unit as the one in the layer.

Points already in the layer will be used as reference, Points referred to in the mutual distances file, but not in the layer, they will be added to the layer, as precisely as possible

does it really work
----------------------

This plugin is at a very experimental stage. I will be enhancing it as I need that, or as reaction to user feedback.

It would be highly useful if you could provide me with example data, for which, I'm quite sure, the plugin does not yet work.

show me an example
---------------------

we are in Colombia, a small area near La Macarena, I have a GeoTiff for the area and we're looking at it, and 5 reference points:
![Alt text](/doc-resources/pic-case01-01.png?raw=true "Optional Title")

the points have an 'id' field and they are called, clockwise, junction, corner, entrance, source-2, and source.

we do not own a GPS machine, or maybe the battery was down, and we observed two trees in the middle of this area, and we could measure, with the approximation of 0.5m, the distances of point A to source-2, source, corner and junction, and of point B to source, junction, and A.

we put this information in a csv file, like this:

A,source2,70
A,corner,79,
A,source,157
A,junction,154
B,A,58
B,source,148.5
B,junction,98.5

then we invoke the plugin, specifying the name of the layer, and the csv file holding the distances

and we get the result in the same layer.

