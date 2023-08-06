"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

try:
    import cStringIO.StringIO as BytesIO
except ImportError:
    from io import BytesIO
import struct

class lcmt_jaco_command(object):
    __slots__ = ["utime", "num_joints", "joint_position", "joint_velocity", "num_fingers", "finger_position", "finger_velocity"]

    __typenames__ = ["int64_t", "int32_t", "double", "double", "int32_t", "double", "double"]

    __dimensions__ = [None, None, ["num_joints"], ["num_joints"], None, ["num_fingers"], ["num_fingers"]]

    def __init__(self):
        self.utime = 0
        self.num_joints = 0
        self.joint_position = []
        self.joint_velocity = []
        self.num_fingers = 0
        self.finger_position = []
        self.finger_velocity = []

    def encode(self):
        buf = BytesIO()
        buf.write(lcmt_jaco_command._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack(">qi", self.utime, self.num_joints))
        buf.write(struct.pack('>%dd' % self.num_joints, *self.joint_position[:self.num_joints]))
        buf.write(struct.pack('>%dd' % self.num_joints, *self.joint_velocity[:self.num_joints]))
        buf.write(struct.pack(">i", self.num_fingers))
        buf.write(struct.pack('>%dd' % self.num_fingers, *self.finger_position[:self.num_fingers]))
        buf.write(struct.pack('>%dd' % self.num_fingers, *self.finger_velocity[:self.num_fingers]))

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = BytesIO(data)
        if buf.read(8) != lcmt_jaco_command._get_packed_fingerprint():
            raise ValueError("Decode error")
        return lcmt_jaco_command._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = lcmt_jaco_command()
        self.utime, self.num_joints = struct.unpack(">qi", buf.read(12))
        self.joint_position = struct.unpack('>%dd' % self.num_joints, buf.read(self.num_joints * 8))
        self.joint_velocity = struct.unpack('>%dd' % self.num_joints, buf.read(self.num_joints * 8))
        self.num_fingers = struct.unpack(">i", buf.read(4))[0]
        self.finger_position = struct.unpack('>%dd' % self.num_fingers, buf.read(self.num_fingers * 8))
        self.finger_velocity = struct.unpack('>%dd' % self.num_fingers, buf.read(self.num_fingers * 8))
        return self
    _decode_one = staticmethod(_decode_one)

    def _get_hash_recursive(parents):
        if lcmt_jaco_command in parents: return 0
        tmphash = (0x4a39790e1f27e20b) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff) + (tmphash>>63)) & 0xffffffffffffffff
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None

    def _get_packed_fingerprint():
        if lcmt_jaco_command._packed_fingerprint is None:
            lcmt_jaco_command._packed_fingerprint = struct.pack(">Q", lcmt_jaco_command._get_hash_recursive([]))
        return lcmt_jaco_command._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

    def get_hash(self):
        """Get the LCM hash of the struct"""
        return struct.unpack(">Q", lcmt_jaco_command._get_packed_fingerprint())[0]

