# -*- coding: utf8 -*-
import png
from struct import unpack
import sys
import os
from PyQt4 import QtGui, QtCore
import tempfile

class Converter(object):
    def load_mbm(self, mbmpath):
        mbmfile = open(mbmpath, "rb")
        header = mbmfile.read(20)
        magic, width, height, bump, bpp = unpack("<5i", header)
        img_format = 'RGBA'
        pixels = []
        if magic != 0x50534b03: # "\x03KSP" as little endian
            raise
        if bpp == 32:
            for j in range(height):
                w = []
                for i in range(width):
                    w.append(unpack("B", mbmfile.read(1))[0])
                    w.append(unpack("B", mbmfile.read(1))[0])
                    w.append(unpack("B", mbmfile.read(1))[0])
                    w.append(unpack("B", mbmfile.read(1))[0])
                # FIXME : why do we have to insert at the beginning ?
                # Behaviour of the png function ?
                pixels.insert(0, w)
        elif bpp == 24:
            img_format = 'RGB'
            for j in range(height):
                w = []
                for i in range(width):
                    w.append(unpack("B", mbmfile.read(1))[0])
                    w.append(unpack("B", mbmfile.read(1))[0])
                    w.append(unpack("B", mbmfile.read(1))[0])
                pixels.insert(0, w)
        else:
            raise

        output = tempfile.gettempdir()
        subfolder = os.path.split(os.path.split(os.path.splitdrive(mbmpath)[1])[0])[1]
        output = os.path.join(output, subfolder)
        if not os.path.isdir(output):
            os.mkdir(output)

        filename = os.path.splitext(os.path.basename(mbmpath))[0] + '.png'
        png.from_array(pixels, img_format).save(os.path.join(output, filename))

        return os.path.join(output, filename)

