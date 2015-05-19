import argparse
import os
import zipfile
import json
import tempfile
from cfgnode import ConfigNode
from mureader import Mu
from texture_converter import Converter

SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models'.format(SKETCHFAB_DOMAIN)


class SkfbUploader(object):
    @staticmethod
    def parse_options():
        parser = argparse.ArgumentParser(description='Upload to Sketchfab')
        parser.add_argument('--name', default='', nargs='?',
                            help='Model name')
        parser.add_argument('--description', default='', nargs='?',
                            help='Model description')
        parser.add_argument('--tags', default='', nargs='?',
                            help='Space separated list of tags')
        parser.add_argument('--token',
                            help='[Mandatory] User token')
        return parser.parse_known_args()[0]

    @staticmethod
    def post(url, archive, **params):
        import requests
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
        if not options.get('token'):
            print('Error : Please set your Sketchfab API token')
            return 'Cancelled : missing Sketchfab API token'
        params = {
            'token': options.get('token').decode('utf8'),
            'name': options.get('name', 'Craft').decode('utf8'),
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
        multiPart.append(part_parameter("name", options.get('name', '').decode('utf8')))
        multiPart.append(part_parameter("description", options.get('description', '').decode('utf8')))
        multiPart.append(part_parameter("tags", options.get('tags', 'KSP').decode('utf8')))
        multiPart.append(part_parameter("token", options.get('token', '').decode('utf8')))
        multiPart.append(part_parameter("source", "ksp-exporter"))

        modelPart = QtNetwork.QHttpPart()
        modelPart.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/octet-stream")
        modelPart.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                            "form-data; name=\"modelFile\"; filename=\"%s\"" % (archive))
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


class KSP2Skfb(object):
    def __init__(self, game_dir=None, uses_qt=False):
        self.craft_files = []
        self.craft_parts = set()
        self.parts = dict()
        self.temp_files = set()
        self.uses_qt = uses_qt
        if self.uses_qt:
            from PyQt4 import QtCore
            self.emitter = QtCore.QObject()
        self.sign = None
        self.set_game_dir(game_dir or 'C:\\Kerbal Space Program')

    def set_game_dir(self, game_dir_path):
        self.game_dir = game_dir_path
        if os.path.exists(self.game_dir) and os.path.isdir(self.game_dir):
            self.list_crafts()

    def list_crafts(self):
        self.craft_files = []
        for root, dirs, files in os.walk(self.game_dir):
            for filename in files:
                if os.path.splitext(filename)[-1] == '.craft':
                    self.craft_files.append(os.path.join(root, filename))

    def list_parts(self):
        for root, dirs, files in os.walk(self.game_dir):
            if self.uses_qt:
                from PyQt4 import QtCore
                self.emitter.emit(QtCore.SIGNAL('building(QString, int, int)'), "Scanning game directory...", -1, -1)
            for filename in files:
                if os.path.splitext(filename)[-1] == '.cfg':
                    self.get_part_name_from_cfg(os.path.join(root, filename))

    def look_for_mu_file(self, cfg_filepath):
        ''' Look for a matching mu file '''
        cfg_dir = os.path.split(cfg_filepath)[0]
        mesh_path = None
        # In some cases, the mu has the same name as the associated cfg
        if os.path.exists(os.path.splitext(cfg_filepath)[0] + '.mu'):
            mesh_path = os.path.splitext(cfg_filepath)[0] + '.mu'
        else:
            for root, _, files in os.walk(cfg_dir):
                # Get the first mu file
                for f in files:
                    if os.path.splitext(f)[-1] == '.mu':
                        mesh_path = os.path.join(cfg_dir, f)
                        break
        if mesh_path:
            print("A substitution mu file '{}' was found.".format(os.path.basename(mesh_path)))

        return mesh_path

    # TODO check if declaring the dict in the if name is always ok with the if mesh
    def get_part_name_from_cfg(self, cfg_filepath):
        ''' Get part name and model file path '''
        with open(cfg_filepath, 'r') as cfg_file:
            part_assets = []
            part_name = None
            cfg_dir = None
            # Add the cfg path to the part assets
            part_assets.append(cfg_filepath)
            for line in cfg_file:
                token = line.split('=')[0].strip()
                if token == 'name':
                    part_name = line.split('=')[1].strip()
                    cfg_dir = os.path.dirname(cfg_filepath)
                if token == 'mesh' or token == 'model':
                    if token == 'mesh':
                        mesh_path = line.rsplit('=')[1].strip()
                        # Need to clean the path given by the cfg file.
                        mesh_path = os.path.join(cfg_dir, mesh_path)
                    else:
                        # filename in value is given without .mu extention, so add it
                        mesh_path = os.path.split(line.rsplit('=')[1].strip())[-1] + '.mu'
                        # filename is given with an internal game path, unuseful for us
                        mesh_path = os.path.join(cfg_dir, mesh_path)

                    if not os.path.exists(mesh_path):
                        mesh_path = self.look_for_mu_file(cfg_filepath)

                    if not mesh_path or not os.path.exists(mesh_path):
                        print ("Warning: Part '{}' was skipped (model was not found)".format(part_name))
                        return
                    # Add the mesh to the part assets
                    part_assets.append(mesh_path)
                if part_name and not part_name in self.parts:
                    self.parts[part_name] = part_assets

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
        if options.get('use_requests', False):
            options.pop('use_requests', None)
            return SkfbUploader.upload(archive, **options)
        else:
            return SkfbUploader.qt_upload(archive, **options)

    def make_craft_archive(self, craft_name):
        self.list_parts()
        craft_path = self.get_craft_path(craft_name)
        craft_assets = self.list_craft_assets(craft_path)
        craft_name = os.path.splitext(os.path.basename(craft_path))[0]
        return self.build_zip(craft_name, craft_path, craft_assets)

    def get_craft_path(self, name):
        try:
            return self.craft_files[int(name)]
        except TypeError:
            print('Not supported')

    def convert(self, filepath, normal=False):
        c = Converter()
        converted = c.load_image(filepath, normal)

        return converted

    def get_existing_texture_file(self, filepath):
        exts = ['.dds', '.mbm', '.png', '.tga']
        base_path = os.path.splitext(filepath)[0]
        for ext in exts:
            if os.path.exists(os.path.splitext(filepath)[0] + ext):
                return os.path.splitext(filepath)[0] + ext

        return None

    def convert_textures(self, mutextures, path, convert_indexes):
        ''' Get the textures and convert them when needed'''
        textures = set()
        for idx in range(len(mutextures)):
            # Extension can differ bewteen the path in the model file and the real texture file
            existing_texture = self.get_existing_texture_file(os.path.join(path, mutextures[idx].name))
            if existing_texture:
                # DDS and MBM need to be converted into PNG
                if os.path.splitext(existing_texture)[-1] in ['.dds', '.mbm']:
                    # Get the converted texture
                    source_image = self.convert(existing_texture, idx in convert_indexes)
                    self.temp_files.add(source_image)

                    archive_path = os.path.splitext(existing_texture)[0] + '.png'
                    # We create a tuple to store both the real(temp) path of the converted texture
                    # and the path to set in the .zip so that it is in the same directory that the model
                    if self.uses_qt:
                        from PyQt4 import QtCore
                        self.emitter.emit(QtCore.SIGNAL('converting(QString)'), "Converting : {}".format(os.path.basename(archive_path)))
                    textures.add((source_image, archive_path))
                else:
                    textures.add(existing_texture)

        return textures

    def get_mu_textures(self, mu_file):
        mu = Mu()
        mu_data = mu.read(mu_file)
        path = os.path.split(mu_file)[0]

        # Check for textures that need to be converted to normal map
        normalmaps_index = []
        for mat in mu_data.materials:
            try:
                mat.bumpMap
                normalmaps_index.append(mat.bumpMap.index)
            except AttributeError:
                pass
        converted_textures = []
        converted_textures = self.convert_textures(mu_data.textures, path, normalmaps_index)
        return converted_textures

    def get_asset_files(self, part_assets):
        ''' Get the assets files (cfg + mu + textures)'''
        c = Converter()
        files = set()
        try:
            for f in part_assets:
                files.add(f)
                if os.path.splitext(f)[-1] == '.mu':
                    # Read the .mu file to get textures
                    files.update(self.get_mu_textures(f))

            return list(files)
        except EOFError:
            print("Warning: the part was skipped")
            return []

    def get_craft_unique_assets(self, craftnodes):
        ''' Get a set of craft assets '''
        assets_set = set()
        for node in craftnodes.nodes:
            label, value = node[1].values[0]
            if label == 'part':
                partname = value.rsplit('_', 1)[0].replace('.', '_')
                assets_set.add(partname)
        return assets_set

    def list_craft_assets(self, filepath):
        ''' Reads the craft file and return all cfg folders '''
        craft_assets = set()
        with open(filepath, 'r') as craft_file:
            craft_data = craft_file.read()
            craftnodes = ConfigNode.load(craft_data)
            # FIXME: is part always the first value?
            assets_set = self.get_craft_unique_assets(craftnodes)
            for asset in assets_set:
                if asset not in self.parts:
                    print("Warning: part '{}' not found".format(partname))
                else:
                    if self.uses_qt:
                        from PyQt4 import QtCore
                        self.emitter.emit(QtCore.SIGNAL('building(QString, int, int)'), "Building", list(assets_set).index(asset), len(assets_set))
                    print('Getting files for {}'.format(asset))
                    craft_assets.update(self.get_asset_files(self.parts[asset]))
        return craft_assets

    def build_zip(self, craft_name, craft_file, craft_assets):
        ''' Build a zip with craft_assets names'''
        output = tempfile.gettempdir()
        archive = os.path.join(output, craft_name + '.zip')
        self.temp_files.add(archive)
        zip = zipfile.ZipFile(archive, 'w')
        zip.write(craft_file, os.path.basename(craft_file))
        # When textures are converted, PNGs are put in the archive from the temp path but
        # with the MBM (game) path to keep their relative path with the model, inside the archive
        print('Building the .zip')
        for f in craft_assets:
            if isinstance(f, tuple):
                zip.write(f[0], f[1])
            else:
                zip.write(f)
        zip.close()

        return archive


    def clear_tmp_files(self):
        ''' Clear temp files '''
        print('Cleaning temp files...')
        for d in self.temp_files:
            if tempfile.gettempdir() in d:
                if os.path.isdir(d):
                    for f in os.listdir(d):
                        try:
                            os.remove(os.path.join(d,f))
                        except:
                            pass
                    try:
                        os.rmdir(d)
                    except:
                        pass
                else:
                    try:
                        os.remove(d)
                    except:
                        pass
        print('Temp files cleaned')


def parse_options(args=None):
    parser = argparse.ArgumentParser(description="List and select craft to upload to Sketchfab")
    parser.add_argument("-g", "--game-dir", dest="game_dir",
                        help="The main KSP directory (<C:\Kerbal Space Program> by default)", nargs='?')
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
        try:
            print(manager.upload(options.upload, use_requests=True))
            manager.clear_tmp_files()
        except Exception as e:
            print(e)
    else:
        # print usage
        parse_options([])


if __name__ == '__main__':
    main()
