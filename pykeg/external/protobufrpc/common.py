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

from google.protobuf.service import RpcController

def flatten( l ):
	result = []
	for i in l:
		if hasattr( i, "__iter__" ) and not isinstance( i, basestring ):
			result.extend( flatten( i ) )
		else:
			result.append( i )
	return result

class Controller( RpcController ):
	def Reset( self ):
		pass

	def Failed( self ):
		pass

	def ErrorText( self ):
		pass

	def StartCancel( self ):
		pass

	def SetFailed( self, reason ):
		print "SetFailed:", reason

	def IsCancelled( self ):
		pass

	def NotifyOnCancel( self, callback ):
		pass

class ServiceContainer( dict ):
	def __getattr__( self, key ):
		return self[ key ] 
