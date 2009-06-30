# Makefile for the kegnet protobuf code.

all: proto/kegnet_pb2.py proto/rpc_pb2.py proto/unittest_pb2.py

proto/kegnet_pb2.py: kegnet.proto
	protoc --python_out=proto $<

proto/rpc_pb2.py: rpc.proto
	protoc --python_out=proto $<

proto/unittest_pb2.py: unittest.proto
	protoc --python_out=proto $<

