# coding=utf-8
import os, array
from mkf import MKFDecoder

def unpack_mkf(mkfname):
    mkf = MKFDecoder(path= ('%s.mkf' % mkfname))
    if not os.path.exists('./%s'%mkfname):
        os.makedirs('./%s'%mkfname)
    for i in xrange(mkf.getFileCount()):
        arrayH = array.array('H', mkf.read(i))
        newFileByteArray = arrayH
        with open('./%s/%s_%d.bin'%(mkfname, mkfname, i), 'wb') as file:
            file.write(newFileByteArray)

unpack_mkf('data')
