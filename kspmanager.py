import argparse
import os
import zipfile
import json
import tempfile
import requests
from cfgnode import ConfigNode


SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models'.format(SKETCHFAB_DOMAIN)

class SkfbUploader(object):
    @staticmethod
    def parse_options():
        parser = argparse.ArgumentParser(description='Upload to Sketchfab')
        parser.add_argument('--title', default='', nargs='?',
                            help='Model title')
        parser.add_argument('--description', default='', nargs='?',
                            help='Model description')
        parser.add_argument('--tags', default='', nargs='?',
                            help='Space separated list of tags')
        parser.add_argument('--token',
                            help='[Mandatory] User token')
        return parser.parse_known_args()[0]

    @staticmethod
    def post(url, archive, **params):
        try:
            with open(archive, 'rb') as data:
                response = requests.post(url,
                                         files={'modelFile': data},
                                         data=params,
                                         verify=False)
            if response.status_code == 201:
                return SKETCHFAB_MODEL_URL + '/' + json.loads(response.content)['uid']
            else:
                return json.loads(response.content)['detail']

        except Exception as e:
            return str(e)

    @staticmethod
    def upload(archive, **options):
        if not options:
            options = vars(SkfbUploader.parse_options())
        params = {
            'token': options.get('token').decode('utf8'),
            'title': options.get('title', 'Craft').decode('utf8'),
            'description': options.get('description', '').decode('utf8'),
            'tags': options.get('tags', 'KSP').decode('utf8'),
            'source': 'ksp-exporter'
        }

        return SkfbUploader.post(SKETCHFAB_API_URL, archive, **params)

    @staticmethod
    def qt_upload(archive, **options):
        from PyQt4 import QtNetwork, QtCore

        def part_parameter(key, value):
            part = QtNetwork.QHttpPart()
            part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader, "form-data; name=\"%s\"" % (key))
            part.setBody(value)
            return part

        multiPart = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
        multiPart.append(part_parameter("title", options.get('title').decode('utf8')))
        multiPart.append(part_parameter("description", options.get('description').decode('utf8')))
        multiPart.append(part_parameter("tags", options.get('tags').decode('utf8')))
        multiPart.append(part_parameter("token", options.get('token').decode('utf8')))
        multiPart.append(part_parameter("source", "ksp-exporter"))

        modelPart = QtNetwork.QHttpPart()
        modelPart.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/octet-stream")
        modelPart.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader, "form-data; name=\"modelFile\"; filename=\"%s\"" % (archive))
        data = QtCore.QFile(archive)
        data.open(QtCore.QIODevice.ReadOnly)
        modelPart.setBodyDevice(data)
        data.setParent(multiPart)
        multiPart.append(modelPart)

        url = QtCore.QUrl(SKETCHFAB_API_URL)
        request = QtNetwork.QNetworkRequest(url)
        manager = QtNetwork.QNetworkAccessManager()
        reply = manager.post(request, multiPart)
        multiPart.setParent(reply)

        return (manager, reply)

class KSPPathException(Exception):
    pass

class KSP2Skfb(object):
    def __init__(self, game_dir=None):
        self.craft_files = []
        self.craft_parts = set()
        self.parts = dict()
        self.game_dir = game_dir or 'C:\\Kerbal Space Program'
        if not os.path.exists(self.game_dir) or not os.path.isdir(self.game_dir):
            raise KSPPathException("Error: directory '{}' not found. Aborting.".format(self.game_dir))

        self.list_crafts()

    def list_crafts(self):
        for root, dirs, files in os.walk(self.game_dir):
            for filename in files:
                if os.path.splitext(filename)[-1] == '.craft':
                    self.craft_files.append(os.path.join(root, filename))

    def list_parts(self):
        for root, dirs, files in os.walk(self.game_dir):
            for filename in files:
                if os.path.splitext(filename)[-1] == '.cfg':
                    self.get_part_name_from_cfg(os.path.join(root, filename))

    def get_part_name_from_cfg(self, cfg_filepath):
        with open(cfg_filepath, 'r') as cfg_file:
            for line in cfg_file:
                token = line.split('=')[0].strip()
                if token == 'name':
                    partname = line.split('=')[1].strip()
                    self.parts[partname] = os.path.dirname(cfg_filepath)

    def list(self):
        print('\n'.join(map(lambda name: '{}. {}'.format(name[0], name[1]),
                            enumerate(map(os.path.basename,
                                map(lambda x: os.path.splitext(x)[0],
                                    self.craft_files))))))

    def get_craft_list(self):
        return map(lambda name: '{}. {}'.format(name[0], name[1]),
                            enumerate(map(os.path.basename,
                                map(lambda x: os.path.splitext(x)[0],
                                    self.craft_files))))

    def upload(self, craft_name, **options):
        archive = self.make_craft_archive(craft_name)
        return SkfbUploader.qt_upload(archive, **options)

    def make_craft_archive(self, craft_name):
        self.list_parts()
        craft_path = self.get_craft_path(craft_name)
        craft_folders = self.list_craft_parts_folder(craft_path)
        craft_name = os.path.splitext(os.path.basename(craft_path))[0]
        return self.build_zip(craft_name, craft_path, craft_folders)

    def get_craft_path(self, name):
        try:
            return self.craft_files[int(name)]
        except TypeError:
            print('Not supported')

    def list_craft_parts_folder(self, filepath):
        ''' Reads the craft file and return all cfg folders '''
        folders = set()
        with open(filepath, 'r') as craft_file:
            craft_data = craft_file.read()
            craftnodes = ConfigNode.load(craft_data)
            # FIXME: is part always the first value?
            for node in craftnodes.nodes:
                label, value = node[1].values[0]
                if label == 'part':
                    partname = value.rsplit('_', 1)[0].replace('.', '_')
                    try:
                        folders.add(self.parts[partname])
                    except KeyError:
                        print("Warning: part '{}' not found".format(partname))
        return folders

    def build_zip(self, craft_name, craft_file, folders):
        def list_folder_files(folder):
            filenames = []
            path = os.path.abspath(folder)
            for root, _, files in os.walk(path, topdown=True):
                filenames.extend(map(lambda x: os.path.join(root, x), files))
            return filenames

        output = tempfile.gettempdir()
        archive = os.path.join(output, craft_name + '.zip')
        zip = zipfile.ZipFile(archive, 'w')
        zip.write(craft_file, os.path.basename(craft_file))
        map(zip.write, set(reduce(lambda x, y: x + y,
                map(list_folder_files, folders))))
        zip.close()
        return archive


def parse_options(args=None):
    parser = argparse.ArgumentParser(description="List and select craft to upload to Sketchfab")
    parser.add_argument("-g", "--game-dir", dest="game_dir",
                        help="The main KSP directory (<C:\Kerbal Space Program> by default)", nargs='?', default=KSP2Skfb().game_dir)
    parser.add_argument("-u", "--upload", dest="upload", nargs='?',
                        help="Craft to upload", default=None)
    parser.add_argument("-l", "--list", dest="list",
                        help="List all available crafts", action='store_true', default=False)
    return parser.parse_known_args(args)[0]


def main():
    options = parse_options()

    manager = KSP2Skfb(options.game_dir)
    if options.list:
        manager.list()
    elif options.upload:
        print(manager.upload(options.upload))
    else:
        # print usage
        parse_options([])


if __name__ == '__main__':
    main()
