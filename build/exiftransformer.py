#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -*- coding: utf-8 -*-
#
# Florian Roth

import os
import traceback
import fractions
import scandir
import random
import math
from pyexiv2 import *

class Fraction(fractions.Fraction):
    """Only create Fractions from floats.

    >>> Fraction(0.3)
    Fraction(3, 10)
    >>> Fraction(1.1)
    Fraction(11, 10)
    """

    def __new__(cls, value, ignore=None):
        """Should be compatible with Python 2.6, though untested."""
        return fractions.Fraction.from_float(value).limit_denominator(99999)

def dms_to_decimal(degrees, minutes, seconds, sign=' '):
    """Convert degrees, minutes, seconds into decimal degrees.

    >>> dms_to_decimal(10, 10, 10)
    10.169444444444444
    >>> dms_to_decimal(8, 9, 10, 'S')
    -8.152777777777779
    """
    return (-1 if sign[0] in 'SWsw' else 1) * (
        float(degrees)        +
        float(minutes) / 60   +
        float(seconds) / 3600
    )


def decimal_to_dms(decimal):
    """Convert decimal degrees into degrees, minutes, seconds.

    >>> decimal_to_dms(50.445891)
    [Fraction(50, 1), Fraction(26, 1), Fraction(113019, 2500)]
    >>> decimal_to_dms(-125.976893)
    [Fraction(125, 1), Fraction(58, 1), Fraction(92037, 2500)]
    """
    remainder, degrees = math.modf(abs(decimal))
    remainder, minutes = math.modf(remainder * 60)
    return [Fraction(n) for n in (degrees, minutes, remainder * 60)]


class EXIFTransformer(object):

    file_target = False
    dir_target = False
    target = ""
    HIGH_PROFILE_LOCS = { "Fort Meade": { "lon": -76.7717974, "lat": 39.1079717 },
                          "Pentagon": { "lon": -77.0561619, "lat": 38.8707991 },
                          "Keith Alexanders Mansion": { "lon": -77.0389819, "lat": 38.90054 } }

    def __init__(self, transform_target, locations, root):

        self.target = transform_target
        self.root = root
        self.locations = locations

        # File or Directory
        if os.path.isfile(transform_target):
            self.file_target = True
        if os.path.isdir(transform_target):
            self.dir_target = True

        # Errors
        if not self.file_target and not self.dir_target:
            self.root.log("Target is not a file and not a directory")
        if not os.path.exists(transform_target):
            self.root.log("Target does not exist.")

    def execute(self):
        if self.file_target:
            self.transform(self.target)
        if self.dir_target:
            for root, directories, files in scandir.walk(self.target, followlinks=False):
                try:
                    # Files scan
                    for filename in files:
                        # Generate composed var
                        filePath = os.path.join(root, filename)
                        extension = os.path.splitext(filePath)[1]

                        if extension.lower() == ".jpg":
                            self.transform(filePath)

                except Exception, e:
                    self.root.log(traceback.format_exc())

    def transform(self, filePath):
        try:
            # Selecting new location
            rand_loc = random.choice(self.locations)
            if rand_loc in self.HIGH_PROFILE_LOCS:
                loc = self.HIGH_PROFILE_LOCS[rand_loc]
                # Randomize a bit to make blacklisting harder
                lat = loc["lat"] + random.uniform(-0.004, 0.004)
                lon = loc["lon"] + random.uniform(-0.004, 0.004)

            # Reading EXIF data
            self.root.log("Transforming %s - EXIF GPS Location: %s - new LON: %s new LAT: %s" % (filePath, rand_loc, lon, lat))
            GPS = 'Exif.GPSInfo.GPS'
            metadata = ImageMetadata(filePath)
            metadata.read()

            metadata[GPS + 'Latitude']     = decimal_to_dms(lat)
            metadata[GPS + 'LatitudeRef']  = 'N' if lat >= 0 else 'S'
            metadata[GPS + 'Longitude']    = decimal_to_dms(lon)
            metadata[GPS + 'LongitudeRef'] = 'E' if lon >= 0 else 'W'

            metadata.write()

        except Exception, e:
            self.root.log(traceback.format_exc())