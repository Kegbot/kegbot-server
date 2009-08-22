# Copyright (c) 2008 Alan Kligman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import socket
import google.protobuf.service
import threading
from protobufrpc.common import Controller
from protobufrpc.protobufrpc_pb2 import Rpc, Request, Response, Error
import struct
import SocketServer

__all__ = [ "TcpChannel", "TcpServer", "Proxy" ]

class TcpChannel( google.protobuf.service.RpcChannel ):
	id = 0
	def __init__( self, addr ):
		google.protobuf.service.RpcChannel.__init__( self )
		self._pending = {}
		self._tcpSocket = None
		self.connect( addr )
	
	def connect( self, addr ):
		self._tcpSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self._tcpSocket.connect( addr )
	
	def send_string( self, buffer ):
		networkOrderBufferLen = struct.pack( "!I", len( buffer ) )

		buffer = networkOrderBufferLen + buffer
		bytesSent = 0
		while bytesSent < len( buffer ):
			sent = self._tcpSocket.send( buffer[ bytesSent: ] )
			if sent == 0:
				raise RuntimeError( "socket connection broken" )
			bytesSent += sent

	def CallMethod( self, methodDescriptor, rpcController, request, responseClass, done=None ):
		self.id += 1
		self._pending[ self.id ] = ( responseClass, done )

		rpc = Rpc()
		rpcRequest = rpc.request.add()
		rpcRequest.method = methodDescriptor.containing_service.name + '.' + methodDescriptor.name
		rpcRequest.serialized_request = request.SerializeToString()
		rpcRequest.id = self.id
		self.send_string( rpc.SerializeToString() )

		buffer = self._tcpSocket.recv( struct.calcsize( "!I" ) )
		bufferLen = int( struct.unpack( "!I", buffer )[0] )
		buffer = self._tcpSocket.recv( bufferLen )
		r = self.string_received( buffer )
		return r

	def string_received( self, data ):
		rpc = Rpc()
		rpc.ParseFromString( data )
		for serializedResponse in rpc.response:
			id = serializedResponse.id
			if self._pending.has_key( id ) and self._pending[ id ] != None:
				responseClass = self._pending[ id ][ 0 ]
				done = self._pending[ id ][ 1 ]
				done( self.unserialize_response( serializedResponse, responseClass ) )
	
	def unserialize_response( self, serializedResponse, responseClass ):
		response = responseClass()
		response.ParseFromString( serializedResponse.serialized_response )
		return response

	def serialize_response( self, response, serializedRequest ):
		serializedResponse = Response ()
		serializedResponse.id = serializedRequest.id
		serializedResponse.serialized_response = response.SerializeToString()
		return serializedResponse

	def serialize_rpc( self, serializedResponse ):
		rpc = Rpc()
		rpcResponse = rpc.response.add()
		rpcResponse.serialized_response = serializedResponse.serialized_response
		rpcResponse.id = serializedResponse.id
		return rpc
	
class Proxy( object ):
	class _Proxy( object ):
		def __init__( self, stub ):
			self._stub = stub
		
		def __getattr__( self, key ):
			def call( method, request ):
				class callbackClass( object ):
					def __init__( self ):
						self.response = []
					def __call__( self, response ):
						self.response.append( response )
				controller = Controller()
				callback = callbackClass()
				method( controller, request, callback )
				return tuple( callback.response )
			return lambda request: call( getattr( self._stub, key ), request )
	
	def __init__( self, *stubs ):
		self._stubs = {}
		for s in stubs:
			self._stubs[ s.GetDescriptor().name ] = self._Proxy( s )
	
	def __getattr__( self, key ):
		return self._stubs[ key ]

class TcpServer( SocketServer.TCPServer ):
	def __init__( self, host, *services ):
		self.services = {}
		for s in services:
			self.services[ s.GetDescriptor().name ] = s
		self.channel = TcpChannel()
		SocketServer.TCPServer.__init__( self, host, TcpRequestHandler )

class TcpRequestHandler( SocketServer.BaseRequestHandler ):
	def handle( self ):
		print self.server
		buffer = self.request.recv( struct.calcsize( "!I" ) )
		bufferLen = int( struct.unpack( "!I", buffer )[0] )
		buffer = self.request.recv( bufferLen )
		self.string_received( buffer )

	def send_string( self, buffer ):
		networkOrderBufferLen = struct.pack( "!I", len( buffer ) )

		buffer = networkOrderBufferLen + buffer
		bytesSent = 0
		while bytesSent < len( buffer ):
			sent = self.request.send( buffer[ bytesSent: ] )
			if sent == 0:
				raise RuntimeError( "socket connection broken" )
			bytesSent += sent

	def string_received( self, data ):
		rpc = Rpc()
		rpc.ParseFromString( data )
		for serializedRequest in rpc.request:
			service = self.server.services[ serializedRequest.method.split( '.' )[ 0 ] ]
			method = service.GetDescriptor().FindMethodByName( serializedRequest.method.split( '.' )[ 1 ] )
			if method:
				request = service.GetRequestClass( method )()
				request.ParseFromString( serializedRequest.serialized_request )
				controller = Controller()

				class callbackClass( object ):
					def __init__( self ):
						self.response = None
					def __call__( self, response ):
						self.response = response
				callback = callbackClass()
				service.CallMethod( method, controller, request, callback )
				responseRpc = self.serialize_rpc( self.serialize_response( callback.response, serializedRequest ) )
				self.send_string( responseRpc.SerializeToString() )

	def serialize_response( self, response, serializedRequest ):
		serializedResponse = Response ()
		serializedResponse.id = serializedRequest.id
		serializedResponse.serialized_response = response.SerializeToString()
		return serializedResponse

	def serialize_rpc( self, serializedResponse ):
		rpc = Rpc()
		rpcResponse = rpc.response.add()
		rpcResponse.serialized_response = serializedResponse.serialized_response
		rpcResponse.id = serializedResponse.id
		return rpc
