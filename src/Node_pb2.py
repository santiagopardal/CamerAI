# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Node.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nNode.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1egoogle/protobuf/wrappers.proto\"@\n\x18UpdateSensitivityRequest\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x13\n\x0bsensitivity\x18\x02 \x01(\x01\")\n\x16NodeIdParameterRequest\x12\x0f\n\x07node_id\x18\x01 \x01(\r\"-\n\x18\x43\x61meraIdParameterRequest\x12\x11\n\tcamera_id\x18\x01 \x01(\r\"-\n\x16SwitchRecordingRequest\x12\x13\n\x0b\x63\x61meras_ids\x18\x01 \x03(\r\"\xeb\x01\n\nCameraInfo\x12\n\n\x02id\x18\x01 \x01(\r\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\n\n\x02ip\x18\x03 \x01(\t\x12\x11\n\thttp_port\x18\x04 \x01(\r\x12\x16\n\x0estreaming_port\x18\x05 \x01(\r\x12\x13\n\x0b\x66rame_width\x18\x06 \x01(\x11\x12\x14\n\x0c\x66rame_height\x18\x07 \x01(\x11\x12\x12\n\nframe_rate\x18\x08 \x01(\x11\x12\x0c\n\x04user\x18\t \x01(\t\x12\x10\n\x08password\x18\n \x01(\t\x12-\n\x0e\x63onfigurations\x18\x0b \x01(\x0b\x32\x15.CameraConfigurations\">\n\x14\x43\x61meraConfigurations\x12\x13\n\x0bsensitivity\x18\x01 \x01(\x01\x12\x11\n\trecording\x18\x02 \x01(\x08\x32\x8c\x04\n\x04Node\x12\x36\n\x04stop\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12G\n\x12update_sensitivity\x12\x19.UpdateSensitivityRequest\x1a\x16.google.protobuf.Empty\x12\x43\n\x0cis_recording\x12\x17.NodeIdParameterRequest\x1a\x1a.google.protobuf.BoolValue\x12\x39\n\x06record\x12\x17.SwitchRecordingRequest\x1a\x16.google.protobuf.Empty\x12\x41\n\x0estop_recording\x12\x17.SwitchRecordingRequest\x1a\x16.google.protobuf.Empty\x12\x31\n\nadd_camera\x12\x0b.CameraInfo\x1a\x16.google.protobuf.Empty\x12\x42\n\rremove_camera\x12\x19.CameraIdParameterRequest\x1a\x16.google.protobuf.Empty\x12I\n\x10get_snapshot_url\x12\x17.NodeIdParameterRequest\x1a\x1c.google.protobuf.StringValueb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Node_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_UPDATESENSITIVITYREQUEST']._serialized_start=75
  _globals['_UPDATESENSITIVITYREQUEST']._serialized_end=139
  _globals['_NODEIDPARAMETERREQUEST']._serialized_start=141
  _globals['_NODEIDPARAMETERREQUEST']._serialized_end=182
  _globals['_CAMERAIDPARAMETERREQUEST']._serialized_start=184
  _globals['_CAMERAIDPARAMETERREQUEST']._serialized_end=229
  _globals['_SWITCHRECORDINGREQUEST']._serialized_start=231
  _globals['_SWITCHRECORDINGREQUEST']._serialized_end=276
  _globals['_CAMERAINFO']._serialized_start=279
  _globals['_CAMERAINFO']._serialized_end=514
  _globals['_CAMERACONFIGURATIONS']._serialized_start=516
  _globals['_CAMERACONFIGURATIONS']._serialized_end=578
  _globals['_NODE']._serialized_start=581
  _globals['_NODE']._serialized_end=1105
# @@protoc_insertion_point(module_scope)
