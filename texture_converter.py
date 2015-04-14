# -*- coding: utf8 -*-
import png
from struct import unpack
import os
from PyQt4 import QtGui
import tempfile


class Converter(object):
    def convert_bump(self, pixels, width, height, nb_components):
        outp = []
        for y in range(1, height - 1):
            w = []
            for x in range(1, (width * nb_components) - 1, nb_components):
                vdx = QtGui.QVector3D(1, 0, (pixels[y][x+1] - pixels[y][x-1]) / 60.0)
                vdy = QtGui.QVector3D(0, 1, (pixels[y+1][x] - pixels[y-1][x]) / 60.0)
                vdz = QtGui.QVector3D.normal(vdx, vdy)
                vdz = vdz.__mul__(QtGui.QVector3D(127, 127, 127))
                vdz = vdz.__add__(QtGui.QVector3D(128, 128, 128))
                w.append(vdz.x())
                w.append(vdz.y())
                w.append(vdz.z())
            outp.append(w)
        return outp

    def load_mbm(self, mbmpath):
        mbmfile = open(mbmpath, "rb")
        header = mbmfile.read(20)
        magic, width, height, bump, bpp = unpack("<5i", header)
        img_format = 'RGBA'
        pixels = []
        if magic != 0x50534b03:  # "\x03KSP" as little endian
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

        if bump and len(pixels) > 2:
            pixels = self.convert_bump(pixels, width, height, bpp/8)
            img_format = 'RGB'
        output = tempfile.gettempdir()
        subfolder = os.path.split(os.path.split(os.path.splitdrive(mbmpath)[1])[0])[1]
        output = os.path.join(output, subfolder)
        if not os.path.isdir(output):
            os.mkdir(output)

        filename = os.path.splitext(os.path.basename(mbmpath))[0] + '.png'
        png.from_array(pixels, img_format).save(os.path.join(output, filename))

        return os.path.join(output, filename)
