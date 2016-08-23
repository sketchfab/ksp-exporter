# -*- coding: utf8 -*-
import os
import tempfile
import pyglet
from struct import unpack
from math import sqrt
from PIL import Image, ImageFilter, ImageChops
from pyglet.image.codecs.dds import DDSImageDecoder


class Converter(object):
    # Code snippet from http://www.pythonstuff.org/glsl/normalmaps_from_heightmaps.html
    def height2bump(self,  heightBand ): # normal[0..2] band-array
        global verbose
        r = ImageChops.constant(heightBand, 128)
        g = ImageChops.constant(heightBand, 128)
        b = ImageChops.constant(heightBand, 128)
        rr=r.load()
        gg=g.load()
        bb=b.load()
        width = heightBand.size[0]
        height = heightBand.size[1]
        data = list(heightBand.getdata())
        bits = 256
        for y in range(1, height - 1):
            ypos = y * width
            for x in range(1, width - 1):
                pixel = (ypos + x)
                pixelL = pixel - 1
                pixelR = pixel + 1
                pixelT = pixel - width
                pixelB = pixel + width
                dx = -((data[pixelR] - data[pixelL]) / (bits *2.0))
                dy = -((data[pixelT] - data[pixelB]) / (bits *2.0))
                l = sqrt(1 + dx**2 + dy**2)
                dz = 1  / l
                dx = dx / l
                dy = dy / l

                #rgba  tex direct
                #pixelPos = pixel * 4
                #outp[pixel * 4] = dx
                #outp[pixel ] = dy
                #outp[pixel + 2] = dz
                rr[x, y] = 3
                rr[x, y] = int(dx * bits + 128)
                gg[x, y] = int(dy * bits + 128)
                bb[x, y] = int(dz * bits + 128)

        return([r, g, b])


    def readHeight2Bump(self, input_image):
        height = input_image.split()[0]
        normal = self.height2bump(height)
        input_image = Image.merge('RGB', normal)

        return input_image

    def load_mbm(self, mbmpath):
        print(mbmpath)
        mbmfile = open(mbmpath, "rb")
        header = mbmfile.read(20)
        magic, width, height, bump, bpp = unpack("<5i", header)
        img_format = 'RGBA' if bpp == 32 else 'RGB'
        pixels = mbmfile.read(width * height * 4)
        img = Image.frombuffer(img_format, (width, height), pixels, 'raw', img_format, 0, 1)

        # Needs to flip top/bottom in order to get the right image
        img = img.transpose(1)
        if bump:
            img = self.readHeight2Bump(img)
            print(mbmpath)

        return img

    def load_dds(self, ddspath, convert_tonormal):
        da = pyglet.image.load(ddspath, decoder=DDSImageDecoder()).get_texture().get_image_data()
        img_format = 'RGBA' if len(da.format) == 4 else 'RGB'

        imagedata=da.get_data(img_format, len(da.format) * da.width)
        img = Image.frombytes(img_format, (da.width, da.height), imagedata)
        img = img.transpose(1)
        if convert_tonormal:
            img = self.readHeight2Bump(img)

        return img


    def load_image(self, filepath, convert_tonormal=False):
        ''' Converts image to png'''
        if os.path.splitext(filepath)[-1] == '.mbm':
            img = self.load_mbm(filepath)
        else:
            img = self.load_dds(filepath, convert_tonormal)

        filename = os.path.splitext(os.path.basename(filepath))[0] + '.png'
        output = tempfile.gettempdir()
        subfolder = os.path.split(os.path.split(os.path.splitdrive(filepath)[1])[0])[1]
        output = os.path.join(output, subfolder)
        if not os.path.isdir(output):
            os.mkdir(output)

        img.save(os.path.join(output, filename))

        return os.path.join(output, filename)