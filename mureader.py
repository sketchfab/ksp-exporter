from struct import pack, unpack

def get_mu_textures(mu_path):
	''' Returns the list of the referenced texture paths'''
        self.textures = []
        with open(mu_path, "rb") as self.file:
            self.magic, self.version = self.read_int(2)
            if (self.magic != MuEnum.MODEL_BINARY or self.version < 0
                or self.version > MuEnum.FILE_VERSION):
                return None
            self.name = self.read_string()
            #print("version: %d '%s'" % (self.version, self.name))
            self.obj = MuObject().read(self)
            #self.read_materials()
            #self.read_textures()
            del self.file
            return self

class MuEnum:
    MODEL_BINARY = 76543
    FILE_VERSION = 3

    ET_CHILD_TRANSFORM_START = 0
    ET_CHILD_TRANSFORM_END = 1
    ET_ANIMATION = 2
    ET_MESH_COLLIDER = 3
    ET_SPHERE_COLLIDER = 4
    ET_CAPSULE_COLLIDER = 5
    ET_BOX_COLLIDER = 6
    ET_MESH_FILTER = 7
    ET_MESH_RENDERER = 8
    ET_SKINNED_MESH_RENDERER = 9
    ET_MATERIALS = 10
    ET_MATERIAL = 11    #XXX not used?
    ET_TEXTURES = 12
    ET_MESH_START = 13
    ET_MESH_VERTS = 14
    ET_MESH_UV = 15
    ET_MESH_UV2 = 16
    ET_MESH_NORMALS = 17
    ET_MESH_TANGENTS = 18
    ET_MESH_TRIANGLES = 19
    ET_MESH_BONE_WEIGHTS = 20
    ET_MESH_BIND_POSES = 21
    ET_MESH_END = 22
    ET_LIGHT = 23
    ET_TAG_AND_LAYER = 24
    ET_MESH_COLLIDER2 = 25
    ET_SPHERE_COLLIDER2 = 26
    ET_CAPSULE_COLLIDER2 = 27
    ET_BOX_COLLIDER2 = 28
    ET_WHEEL_COLLIDER = 29
    ET_CAMERA = 30
    ENTRY_TYPES = {
        'ET_CHILD_TRANSFORM_START':ET_CHILD_TRANSFORM_START,
        'ET_CHILD_TRANSFORM_END':ET_CHILD_TRANSFORM_END,
        'ET_ANIMATION':ET_ANIMATION,
        'ET_MESH_COLLIDER':ET_MESH_COLLIDER,
        'ET_SPHERE_COLLIDER':ET_SPHERE_COLLIDER,
        'ET_CAPSULE_COLLIDER':ET_CAPSULE_COLLIDER,
        'ET_BOX_COLLIDER':ET_BOX_COLLIDER,
        'ET_MESH_FILTER':ET_MESH_FILTER,
        'ET_MESH_RENDERER':ET_MESH_RENDERER,
        'ET_SKINNED_MESH_RENDERER':ET_SKINNED_MESH_RENDERER,
        'ET_MATERIALS':ET_MATERIALS,
        'ET_MATERIAL':ET_MATERIAL,
        'ET_TEXTURES':ET_TEXTURES,
        'ET_MESH_START':ET_MESH_START,
        'ET_MESH_VERTS':ET_MESH_VERTS,
        'ET_MESH_UV':ET_MESH_UV,
        'ET_MESH_UV2':ET_MESH_UV2,
        'ET_MESH_NORMALS':ET_MESH_NORMALS,
        'ET_MESH_TANGENTS':ET_MESH_TANGENTS,
        'ET_MESH_TRIANGLES':ET_MESH_TRIANGLES,
        'ET_MESH_BONE_WEIGHTS':ET_MESH_BONE_WEIGHTS,
        'ET_MESH_BIND_POSES':ET_MESH_BIND_POSES,
        'ET_MESH_END':ET_MESH_END,
        'ET_LIGHT':ET_LIGHT,
        'ET_TAG_AND_LAYER':ET_TAG_AND_LAYER,
        'ET_MESH_COLLIDER2':ET_MESH_COLLIDER2,
        'ET_SPHERE_COLLIDER2':ET_SPHERE_COLLIDER2,
        'ET_CAPSULE_COLLIDER2':ET_CAPSULE_COLLIDER2,
        'ET_BOX_COLLIDER2':ET_BOX_COLLIDER2,
        'ET_WHEEL_COLLIDER':ET_WHEEL_COLLIDER,
        'ET_CAMERA':ET_CAMERA,
    }

    ST_CUSTOM = 0
    ST_DIFFUSE = 1
    ST_SPECULAR = 2
    ST_BUMPED = 3
    ST_BUMPED_SPECULAR = 4
    ST_EMISSIVE = 5
    ST_EMISSIVE_SPECULAR = 6
    ST_EMISSIVE_BUMPED_SPECULAR = 7
    ST_ALPHA_CUTOUT = 8
    ST_ALPHA_CUTOUT_BUMPED = 9
    ST_ALPHA = 10
    ST_ALPHA_SPECULAR = 11
    ST_ALPHA_UNLIT = 12
    ST_UNLIT = 13
    SHADER_TYPES = {
        'ST_CUSTOM':ST_CUSTOM,
        'ST_DIFFUSE':ST_DIFFUSE,
        'ST_SPECULAR':ST_SPECULAR,
        'ST_BUMPED':ST_BUMPED,
        'ST_BUMPED_SPECULAR':ST_BUMPED_SPECULAR,
        'ST_EMISSIVE':ST_EMISSIVE,
        'ST_EMISSIVE_SPECULAR':ST_EMISSIVE_SPECULAR,
        'ST_EMISSIVE_BUMPED_SPECULAR':ST_EMISSIVE_BUMPED_SPECULAR,
        'ST_ALPHA_CUTOUT':ST_ALPHA_CUTOUT,
        'ST_ALPHA_CUTOUT_BUMPED':ST_ALPHA_CUTOUT_BUMPED,
        'ST_ALPHA':ST_ALPHA,
        'ST_ALPHA_SPECULAR':ST_ALPHA_SPECULAR,
        'ST_ALPHA_UNLIT':ST_ALPHA_UNLIT,
        'ST_UNLIT':ST_UNLIT,
    }
    ShaderNames = (
        "",
        "KSP/Diffuse",
        "KSP/Specular",
        "KSP/Bumped",
        "KSP/Bumped Specular",
        "KSP/Emissive/Diffuse",
        "KSP/Emissive/Specular",
        "KSP/Emissive/Bumped Specular",
        "KSP/Alpha/Cutoff",
        "KSP/Alpha/Cutoff Bumped",
        "KSP/Alpha/Translucent",
        "KSP/Alpha/Translucent Specular",
        "KSP/Alpha/Unlit Transparent",
        "KSP/Unlit",
    )

    AT_TRANSFORM = 0
    AT_MATERIAL = 1
    AT_LIGHT = 2
    AT_AUDIO_SOURCE = 3
    ANIMATION_TYPES = {
        'AT_TRANSFORM':AT_TRANSFORM,
        'AT_MATERIAL':AT_MATERIAL,
        'AT_LIGHT':AT_LIGHT,
        'AT_AUDIO_SOURCE':AT_AUDIO_SOURCE,
    }

    TT_TEXTURE = 0
    TT_NORMAL_MAP = 1
    TEXTURE_TYPES = {
        'TT_TEXTURE':TT_TEXTURE,
        'TT_NORMAL_MAP':TT_NORMAL_MAP,
    }

class MuTexture:
    def __init__(self):
        pass
    def read(self, mu):
        #print("MuTexture")
        self.name = mu.read_string()
        self.type = mu.read_int()
        #print("   ", self.name, self.type)
        return self


class MuMatTex:
    def __init__(self):
        pass
    def read(self, mu):
        #print("MuMatTex")
        self.index = mu.read_int()
        self.scale = mu.read_float(2)
        self.offset = mu.read_float(2)
        return self


class MuMaterial:
    def __init__(self):
        pass
    def read(self, mu):
        self.name = mu.read_string()
        self.type = mu.read_int()
        if self.type == MuEnum.ST_SPECULAR:
            self.mainTex = MuMatTex().read(mu)
            self.specColor = mu.read_float(4)
            self.shininess = mu.read_float()
        elif self.type == MuEnum.ST_BUMPED:
            self.mainTex = MuMatTex().read(mu)
            self.bumpMap = MuMatTex().read(mu)
        elif self.type == MuEnum.ST_BUMPED_SPECULAR:
            self.mainTex = MuMatTex().read(mu)
            self.bumpMap = MuMatTex().read(mu)
            self.specColor = mu.read_float(4)
            self.shininess = mu.read_float()
        elif self.type == MuEnum.ST_EMISSIVE:
            self.mainTex = MuMatTex().read(mu)
            self.emissive = MuMatTex().read(mu)
            self.emissiveColor = mu.read_float(4)
        elif self.type == MuEnum.ST_EMISSIVE_SPECULAR:
            self.mainTex = MuMatTex().read(mu)
            self.specColor = mu.read_float(4)
            self.shininess = mu.read_float()
            self.emissive = MuMatTex().read(mu)
            self.emissiveColor = mu.read_float(4)
        elif self.type == MuEnum.ST_EMISSIVE_BUMPED_SPECULAR:
            self.mainTex = MuMatTex().read(mu)
            self.bumpMap = MuMatTex().read(mu)
            self.specColor = mu.read_float(4)
            self.shininess = mu.read_float()
            self.emissive = MuMatTex().read(mu)
            self.emissiveColor = mu.read_float(4)
        elif self.type == MuEnum.ST_ALPHA_CUTOUT:
            self.mainTex = MuMatTex().read(mu)
            self.cutoff = mu.read_float()
        elif self.type == MuEnum.ST_ALPHA_CUTOUT_BUMPED:
            self.mainTex = MuMatTex().read(mu)
            self.bumpMap = MuMatTex().read(mu)
            self.cutoff = mu.read_float()
        elif self.type == MuEnum.ST_ALPHA:
            self.mainTex = MuMatTex().read(mu)
        elif self.type == MuEnum.ST_ALPHA_SPECULAR:
            self.mainTex = MuMatTex().read(mu)
            self.gloss = mu.read_float()
            self.specColor = mu.read_float(4)
            self.shininess = mu.read_float()
        elif self.type == MuEnum.ST_ALPHA_UNLIT:
            self.mainTex = MuMatTex().read(mu)
            self.color = mu.read_float(4)
        elif self.type == MuEnum.ST_UNLIT:
            self.mainTex = MuMatTex().read(mu)
            self.color = mu.read_float(4)
        elif self.type == MuEnum.ST_DIFFUSE:
            self.mainTex = MuMatTex().read(mu)
        else:
            raise ValueError("MuMaterial %d" % self.type)
        return self


class MuTransform:
    def __init__(self):
        pass
    def read(self, mu):
        self.name = mu.read_string()
        self.localPosition = mu.read_vector()
        self.localRotation = mu.read_quaternion()
        self.localScale = mu.read_vector()
        #      self.localScale)
        return self


class MuTagLayer:
    def __init__(self):
        pass
    def read(self, mu):
        self.tag = mu.read_string()
        self.layer = mu.read_int()
        return self


class MuKey:
    def __init__(self):
        pass
    def read(self, mu):
        self.time = mu.read_float()
        self.value = mu.read_float()
        self.tangent = mu.read_float(2) # in, out
        self.tangentMode = mu.read_int()
        # editable, smooth, linear, stepped (0..3?)
        return self


class MuCurve:
    def __init__(self):
        pass
    def read(self, mu):
        self.path = mu.read_string()
        self.property = mu.read_string()
        self.type = mu.read_int()
        self.wrapMode = mu.read_int(2)  # pre, post
        num_keys = mu.read_int()
        self.keys = []
        for i in range(num_keys):
            self.keys.append(MuKey().read(mu))
        return self


class MuClip:
    def __init__(self):
        self.curves = []
    def read(self, mu):
        self.name = mu.read_string()
        self.lbCenter = mu.read_vector()
        self.lbSize = mu.read_vector()
        self.wrapMode = mu.read_int()
        num_curves = mu.read_int()
        for i in range(num_curves):
            self.curves.append(MuCurve().read(mu))
        return self


class MuAnimation:
    def __init__(self):
        self.clips = []
    def read(self, mu):
        num_clips = mu.read_int()
        for i in range(num_clips):
            self.clips.append(MuClip().read(mu))
        self.clip = mu.read_string()
        self.autoPlay = mu.read_byte()
        return self


class MuBoneWeight:
    def __init__(self):
        self.indices = []
        self.weights = []
    def read(self, mu):
        for i in range(4):
            self.indices.append(mu.read_int())
            self.weights.append(mu.read_float())
        return self


class MuMesh:
    def __init__(self):
        self.verts = []
        self.uvs = []
        self.uv2s = []
        self.normals = []
        self.tangents = []
        self.boneWeights = []
        self.bindPoses = []
        self.submeshes = []
    def read(self, mu):
        start = mu.read_int()
        if start != MuEnum.ET_MESH_START:
            raise
        num_verts, submesh_count = mu.read_int(2)
        while True:
            type = mu.read_int()
            if type == MuEnum.ET_MESH_END:
                break
            elif type == MuEnum.ET_MESH_VERTS:
                for i in range(num_verts):
                    self.verts.append(mu.read_vector())
            elif type == MuEnum.ET_MESH_UV:
                for i in range(num_verts):
                    self.uvs.append(mu.read_float(2))
            elif type == MuEnum.ET_MESH_UV2:
                for i in range(num_verts):
                    self.uv2s.append(mu.read_float(2))
            elif type == MuEnum.ET_MESH_NORMALS:
                for i in range(num_verts):
                    self.normals.append(mu.read_vector())
            elif type == MuEnum.ET_MESH_TANGENTS:
                for i in range(num_verts):
                    self.tangents.append(mu.read_tangent())
            elif type == MuEnum.ET_MESH_BONE_WEIGHTS:
                for i in range(num_verts):
                    self.boneWeights.append(MuBoneWeight().read(mu))
            elif type == MuEnum.ET_MESH_BIND_POSES:
                num_poses = mu.read_int()
                for i in range(num_poses):
                    self.bindPoses.append(mu.read_float(16))
            elif type == MuEnum.ET_MESH_TRIANGLES:
                num_tris = mu.read_int()
                tris = []
                for i in range(int(num_tris / 3)):
                    tri = mu.read_int(3)
                    #reverse the triangle winding for Blender (because of the
                    # LHS/RHS swap)
                    #avoid putting 0 at the end of the list (Blender doesn't
                    #like that)
                    if not tri[0]:
                        tri = tri[0], tri[2], tri[1]
                    else:
                        tri = tri[2], tri[1], tri[0]
                    tris.append(tri)
                self.submeshes.append(tris)
            else:
                raise ValueError("MuMesh %x %d" % (mu.file.tell(), type))
        return self


class MuRenderer:
    def __init__(self):
        self.castShadows = 1
        self.receiveShadows = 1
    def read(self, mu):
        if mu.version > 0:
            self.castShadows = mu.read_byte()
            self.receiveShadows = mu.read_byte()
        num_mat = mu.read_int()
        self.materials = mu.read_int(num_mat, True)
        return self


class MuSkinnedMeshRenderer:
    def __init__(self):
        self.materials = []
        self.bones = []
    def read(self, mu):
        num_mat = mu.read_int()
        for i in range(num_mat):
            self.materials.append(mu.read_int())
        self.center = mu.read_vector()
        self.size = mu.read_vector()
        self.quality = mu.read_int()
        self.updateWhenOffscreen = mu.read_byte()
        nBones = mu.read_int()
        for i in range(nBones):
            self.bones.append(mu.read_string())
        self.mesh = MuMesh().read(mu)
        return self


class MuCollider_Base:
    def __init__(self, type):
        self.type = type

class MuColliderMesh(MuCollider_Base):
    def read(self, mu):
        self.isTrigger = 0
        if self.type:
            self.isTrigger = mu.read_byte()
        self.convex = mu.read_byte()
        self.mesh = MuMesh().read(mu)
        return self


class MuColliderSphere(MuCollider_Base):
    def read(self, mu):
        self.isTrigger = 0
        if self.type:
            self.isTrigger = mu.read_byte()
        self.radius = mu.read_float()
        self.center = mu.read_vector()
        return self


class MuColliderCapsule(MuCollider_Base):
    def read(self, mu):
        self.isTrigger = 0
        if self.type:
            self.isTrigger = mu.read_byte()
        self.radius = mu.read_float()
        self.height = mu.read_float()
        self.direction = mu.read_int()
        self.center = mu.read_vector()
        return self


class MuColliderBox(MuCollider_Base):
    def read(self, mu):
        self.isTrigger = 0
        if self.type:
            self.isTrigger = mu.read_byte()
        self.size = mu.read_vector()
        self.center = mu.read_vector()
        return self


class MuSpring:
    def __init__(self):
        pass
    def read(self, mu):
        self.spring = mu.read_float()
        self.damper = mu.read_float()
        self.targetPosition = mu.read_float()
        return self


class MuFriction:
    def __init__(self):
        pass
    def read(self, mu):
        self.extremumSlip = mu.read_float()
        self.extremumValue = mu.read_float()
        self.asymptoteSlip = mu.read_float()
        self.asymptoteValue = mu.read_float()
        self.stiffness = mu.read_float()
        return self


class MuColliderWheel(MuCollider_Base):
    def __init__(self):
        MuCollider_Base.__init__(self, 0)
    def read(self, mu):
        self.mass = mu.read_float()
        self.radius = mu.read_float()
        self.suspensionDistance = mu.read_float()
        self.center = mu.read_vector()
        self.suspensionSpring = MuSpring().read(mu)
        self.forwardFriction = MuFriction().read(mu)
        self.sidewaysFriction = MuFriction().read(mu)
        return self


def MuCollider(type):
    if type in [MuEnum.ET_MESH_COLLIDER, MuEnum.ET_MESH_COLLIDER2]:
        return MuColliderMesh(type == MuEnum.ET_MESH_COLLIDER2)
    elif type in [MuEnum.ET_SPHERE_COLLIDER, MuEnum.ET_SPHERE_COLLIDER2]:
        return MuColliderSphere(type == MuEnum.ET_SPHERE_COLLIDER2)
    elif type in [MuEnum.ET_CAPSULE_COLLIDER, MuEnum.ET_CAPSULE_COLLIDER2]:
        return MuColliderCapsule(type == MuEnum.ET_CAPSULE_COLLIDER2)
    elif type in [MuEnum.ET_BOX_COLLIDER, MuEnum.ET_BOX_COLLIDER2]:
        return MuColliderBox(type == MuEnum.ET_BOX_COLLIDER2)
    elif type in [MuEnum.ET_WHEEL_COLLIDER]:
        return MuColliderWheel()
    else:
        raise ValueError("MuCollider %d" % type)


class MuCamera:
    def __init__(self):
        pass
    def read(self, mu):
        self.clearFlags = mu.read_int()
        self.backgroundColor = mu.read_float(4)
        self.cullingMask = mu.read_int()
        self.orthographic = mu.read_int()
        self.fov = mu.read_float()
        self.near = mu.read_float()
        self.far = mu.read_float()
        self.dept = mu.read_float()
        return self


class MuLight:
    def __init__(self):
        pass
    def read(self, mu):
        self.type = mu.read_int()
        self.intensity = mu.read_float()
        self.range = mu.read_float()
        self.color = mu.read_float(4)
        self.cullingMask = mu.read_int()
        if mu.version > 1:
            self.spotAngle = mu.read_float()
        return self


class MuObject:
    def __init__(self, name=""):
        self.name = name
        self.children = []
    def read(self, mu):
        #print("MuObject")
        self.transform = MuTransform().read(mu)
        while True:
            try:
                entry_type = mu.read_int()
            except EOFError:
                break
            if entry_type == MuEnum.ET_CHILD_TRANSFORM_START:
                self.children.append(MuObject().read(mu))
            elif entry_type == MuEnum.ET_CHILD_TRANSFORM_END:
                break
            elif entry_type == MuEnum.ET_TAG_AND_LAYER:
                self.tag_and_layer = MuTagLayer().read(mu)
            elif entry_type in [MuEnum.ET_MESH_COLLIDER,
                                MuEnum.ET_SPHERE_COLLIDER,
                                MuEnum.ET_CAPSULE_COLLIDER,
                                MuEnum.ET_BOX_COLLIDER,
                                MuEnum.ET_MESH_COLLIDER2,
                                MuEnum.ET_SPHERE_COLLIDER2,
                                MuEnum.ET_CAPSULE_COLLIDER2,
                                MuEnum.ET_BOX_COLLIDER2,
                                MuEnum.ET_WHEEL_COLLIDER]:
                self.collider = MuCollider(entry_type).read(mu)
            elif entry_type == MuEnum.ET_MESH_FILTER:
                self.shared_mesh = MuMesh().read(mu)
            elif entry_type == MuEnum.ET_MESH_RENDERER:
                self.renderer = MuRenderer().read(mu)
            elif entry_type == MuEnum.ET_SKINNED_MESH_RENDERER:
                self.skinned_mesh_renderer = MuSkinnedMeshRenderer().read(mu)
            elif entry_type == MuEnum.ET_ANIMATION:
                self.animation = MuAnimation().read(mu)
            elif entry_type == MuEnum.ET_CAMERA:
                self.camera = MuCamera().read(mu)
            elif entry_type == MuEnum.ET_LIGHT:
                self.light = MuLight().read(mu)
            elif entry_type == MuEnum.ET_MATERIALS:
                mat_count = mu.read_int()
                for i in range(mat_count):
                    mu.materials.append(MuMaterial().read(mu))
            elif entry_type == MuEnum.ET_TEXTURES:
                tex_count = mu.read_int()
                for i in range(tex_count):
                    mu.textures.append(MuTexture().read(mu))
            else:
                #print(entry_type, hex(mu.file.tell()))
                pass
        return self


class Mu:
    def read_byte(self, count=1, force_list=False):
        size = 1 * count
        data = self.file.read(size)
        if len(data) < size:
            raise EOFError
        data = unpack("<%dB" % count, data)
        if count == 1 and not force_list:
            return data[0]
        return data

    def read_int(self, count=1, force_list=False):
        size = 4 * count
        data = self.file.read(size)
        if len(data) < size:
            raise EOFError
        data = unpack("<%di" % count, data)
        if count == 1 and not force_list:
            return data[0]
        return data

    def read_float(self, count=1, force_list=False):
        size = 4 * count
        data = self.file.read(size)
        if len(data) < size:
            raise EOFError
        data = unpack("<%df" % count, data)
        if count == 1 and not force_list:
            return data[0]
        return data

    def read_vector(self):
        v = self.read_float(3)
        #convert from Unity's LHS to Blender's RHS
        v = v[0], v[2], v[1]
        return v

    def read_quaternion(self):
        q = self.read_float(4)
        # Unity is xyzw, blender is wxyz. However, Unity is left-handed and
        # blender is right handed. To convert between LH and RH (either
        # direction), just swap y and z and reverse the rotation direction.
        q = q[3], -q[0], -q[2], -q[1]
        return q

    def read_tangent(self):
        t = self.read_float(4)
        t = t[0], t[2], t[1], -t[3]
        return t

    def read_bytes(self, size):
        data = self.file.read(size)
        if len(data) < size:
            raise EOFError
        return data

    def read_string(self):
        size = self.read_byte()
        data = self.file.read(size)
        if len(data) < size:
            raise EOFError
        if type(data) == type(""):
            return data
        s = ""
        for c in data:
            s = s + chr(c)
        return s

    def __init__(self, name = "mu"):
        self.name = name
        pass
    def read(self, filepath):
        self.materials = []
        self.textures = []
        self.file = open(filepath, "rb")
        self.magic, self.version = self.read_int(2)
        if (self.magic != MuEnum.MODEL_BINARY or self.version < 0
            or self.version > MuEnum.FILE_VERSION):
            return None
        self.name = self.read_string()
        #print("version: %d '%s'" % (self.version, self.name))
        self.obj = MuObject().read(self)
        #self.read_materials()
        #self.read_textures()
        del self.file
        return self
