#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 2010-7-19
@author: huangcd.thu@gmail.com
'''

import os
# import pygame
#from singleton import singleton
from struct import unpack
# from PIL import Image, ImageDraw

class MKFDecoder:
    '''
    MKF文件解码《仙剑》MKF文件的结构组成，以ABC.MKF为例：
    偏移         数据            含义
    00000000     6C 02 00 00     偏移表的长度，此值 / 4 - 2 = 包含文件个数
    00000004     6C 02 00 00     第1个子文件的偏移
    　     　                    第2-152个子件的偏移
    00000264     C2 6F 0F 00     第153个子文件的偏移
    00000268     64 9A 0F 00     此值指向文件末尾，也就是文件的长度
    0000026C     59 4A 5F 31     第1个子文件从这里开始，"YJ_1"是压缩文件的标志
    00000270     A0 08 00 00     这个值是文件的原始的长度
    00000274     12 07 00 00     这个值是文件压缩后的长度
    00000278     01 00           这个值是文件压缩占64K段的个数，通常为1
    0000027A     00 4A           这个值是数据压缩特征串表的长度
    0000027C     01 02 。。      从这开始是数据压缩特征串表
    000002C4     87 7B 02 4C     从这开始是压缩后的文件数据
    　     　                    其他压缩文件
    000F9A60     0B 12 80 38     文件的末尾
    '''

    def __init__(self, path = None, data = None):
        # path和data不能同时是None
        assert path or data
        self.yj1 = YJ1Decoder()
        try:
            # 优先使用path（优先从文件读取）
            if path:
                f = open(path, 'rb')
                self.content = f.read()
            else:
                self.content = data
            #===================================================================
            # 偏移（索引）表长度，假设文件前4位为6C 02 00 00（little-end的int值为
            # 26CH = 620），说明索引表长度为620字节，即620/4 = 155个整数，由于第一个
            # 整数被用于存储表长度，因此实际上只有后面154个整数存的是偏移量。另一方面，
            # 最后一个整数指向文件末尾，也就是文件的长度，因此实际上MKF内部的文件是由
            # 前后两个偏移量之间的byte表示的。这样由于一共有154个个偏移量，因此共有
            # 153个文件
            #
            # ！！！补充：第一个int（前四位）不仅是偏移表长度，也是第一个文件的开头
            # ABC.MFK中前面两个4位分别相等只是巧合（第一个文件为0）
            #===================================================================
            self.count = unpack('I', self.content[:4])[0] / 4# - 1
            self.indexes = []
            self.cache = {}
            for i in xrange(self.count):
                index = unpack('I', self.content[i << 2: (i + 1) << 2])[0]
                self.indexes.append(index)
            # 减去最后一个偏移量，对外而言，count就表示mkf文件中的子文件个数
            self.count -= 1
        except IOError:
            print 'error occurs when try to open file', path
        finally:
            if 'f' in dir():
                f.close()

    def check(self, index):
        assert index <= self.count and index >= 0

    def getFileCount(self):
        return self.count

    def isYJ1(self, index):
        '''
        判断文件是否为YJ_1压缩
        '''
        self.check(index)
        return self.content[self.indexes[index]:self.indexes[index] + 4] == '\x59\x4A\x5F\x31'

    def read(self, index):
        '''
        读取并返回指定文件，如果文件是经过YJ_1压缩的话，返回解压以后的内容
        '''
        self.check(index + 1)
        if not self.cache.has_key(index):
            data = self.content[self.indexes[index]:self.indexes[index + 1]]
            if self.isYJ1(index):
                data = self.yj1.decode(data)
            self.cache[index] = data
        return self.cache[index]

#@singleton
class YJ1Decoder:
    '''
    YJ_1文件解析
    YJ_1文件结构：
    0000000: 594a5f31 fe520000 321b0000                02（即data[0xC]) 00 00 57（即data[0xF]）
              Y J _ 1 新文件长 源文件长（包含'YJ_1'头）block数                loop数
    '''
    def __init__(self):
        pass

    def decode(self, data):
        '''
        解析YJ_1格式的压缩文件，如果文件不是YJ_1格式或者文件为空，则直接返回原始数据
        '''
        self.si = self.di = 0 #记录文件位置的指针 记录解开后保存数据所在数组中的指向位置
        self.first = 1
        self.key_0x12 = self.key_0x13 = 0
        self.flags = 0
        self.flagnum = 0

        pack_length = 0
        ext_length = 0
        if not data:
            print 'no data to decode'
            return ''
        self.data = data
        self.dataLen = len(data)
        if self.readInt() != 0x315f4a59: # '1' '_' 'J' 'Y'
            print 'not YJ_1 data'
            return data
        self.orgLen = self.readInt()
        self.fileLen = self.readInt()
        self.finalData = ['\x00' for _ in xrange(self.orgLen)]
        self.keywords = [0 for _ in xrange(0x14)]

        prev_src_pos = self.si
        prev_dst_pos = self.di

        blocks = self.readByte(0xC)

        self.expand()

        prev_src_pos = self.si
        self.di = prev_dst_pos
        for _ in xrange(blocks):
            if self.first == 0:
                prev_src_pos += pack_length
                prev_dst_pos += ext_length
                self.si = prev_src_pos
                self.di = prev_dst_pos
            self.first = 0

            ext_length = self.readShort()
            pack_length = self.readShort()

            if not pack_length:
                pack_length = ext_length + 4
                for _ in xrange(ext_length):
                    self.finalData[self.di] = self.data[self.si]
                    self.di += 1
                    self.si += 1
                ext_length = pack_length - 4
            else:
                d = 0
                for _ in xrange(0x14):
                    self.keywords[d] = self.readByte()
                    d += 1
                self.key_0x12 = self.keywords[0x12]
                self.key_0x13 = self.keywords[0x13]
                self.flagnum = 0x20
                self.flags = ((self.readShort() << 16) | self.readShort()) & 0xffffffff
                self.analysis()

        return ''.join([x for x in self.finalData if x != 0])

    def analysis(self):
        loop = 0
        numbytes = 0
        while True:
            loop = self.decodeloop()
            if loop == 0xffff:
                return
            for _ in xrange(loop):
                m = 0
                self.update(0x10)
                while True:
                    m = self.trans_topflag_to(m, self.flags, self.flagnum, 1)
                    self.flags = (self.flags << 1) & 0xffffffff
                    self.flagnum -= 1
                    if self.assist[m] == 0:
                        break
                    m = self.table[m]
                self.finalData[self.di] = chr(self.table[m] & 0xff)
                self.di += 1
            loop = self.decodeloop()
            if loop == 0xffff:
                return
            for _ in xrange(loop):
                numbytes = self.decodenumbytes()
                self.update(0x10)
                m = self.trans_topflag_to(0, self.flags, self.flagnum, 2)
                self.flags = (self.flags << 2) & 0xffffffff
                self.flagnum -= 2
                t = self.keywords[m + 8]
                n = self.trans_topflag_to(0, self.flags, self.flagnum, t)
                self.flags = (self.flags << t) & 0xffffffff
                self.flagnum -= t
                for _ in xrange(numbytes):
                    self.finalData[self.di] = self.finalData[self.di - n]
                    self.di += 1

    def readShort(self, si = None):
        if si:
            self.si = si
        if self.si >= self.dataLen:
            result = 0
        else:
            result, = unpack('H', self.data[self.si : self.si + 2])
        self.si += 2
        return result

    def readByte(self, si = None):
        if si:
            self.si = si
        if self.si >= self.dataLen:
            result = 0
        else:
            result, = unpack('B', self.data[self.si])
        self.si += 1
        return result

    def readInt(self, si = None):
        if si:
            self.si = si
        if self.si >= self.dataLen:
            result = 0
        else:
            result, = unpack('I', self.data[self.si : self.si + 4])
        self.si += 4
        return result

    def move_top(self, x):
        t = x >> 15
        return t & 0xffff

    def get_topflag(self, x, y):
        t = x >> 31
        return t & 0xffffffff

    def trans_topflag_to(self, x, y, z, n):
        for _ in xrange(n):
            x <<= 1
            x |= self.get_topflag(y, z)
            y  = (y << 1) & 0xffffffff
            z -= 1
        return x & 0xffffffff

    def update(self, x):
        if self.flagnum < x:
            self.flags |= self.readShort() << (0x10 - self.flagnum) & 0xffffffff
            self.flagnum += 0x10

    def decodeloop(self):
        self.update(3)
        loop = self.key_0x12
        if self.get_topflag(self.flags, self.flagnum) == 0:
            self.flags = (self.flags << 1) & 0xffffffff
            self.flagnum -= 1
            t = 0
            t = self.trans_topflag_to(t, self.flags, self.flagnum, 2)
            self.flags = (self.flags << 2) & 0xffffffff
            self.flagnum -= 2
            loop = self.key_0x13
            if t != 0:
                t = self.keywords[t + 0xE]
                self.update(t)
                loop = self.trans_topflag_to(0, self.flags, self.flagnum, t)
                if loop == 0:
                    self.flags = (self.flags << t) & 0xffffffff
                    self.flagnum -= t
                    return 0xffff
                else:
                    self.flags = (self.flags << t) & 0xffffffff
                    self.flagnum -= t
        else:
            self.flags = (self.flags << 1) & 0xffffffff
            self.flagnum -= 1
        return loop

    def decodenumbytes(self):
        self.update(3)
        numbytes = self.trans_topflag_to(0, self.flags, self.flagnum, 2)
        if numbytes == 0:
            self.flags = (self.flags << 2) & 0xffffffff
            self.flagnum -= 2
            numbytes = (self.keywords[1] << 8) | self.keywords[0]
        else:
            self.flags = (self.flags << 2) & 0xffffffff
            self.flagnum -= 2
            if self.get_topflag(self.flags, self.flagnum) == 0:
                self.flags = (self.flags << 1) & 0xffffffff
                self.flagnum -= 1
                numbytes = (self.keywords[numbytes * 2 + 1] << 8) | self.keywords[numbytes * 2]
            else:
                self.flags = (self.flags << 1) & 0xffffffff
                self.flagnum -= 1
                t = self.keywords[numbytes + 0xB]
                self.update(t)
                numbytes = 0
                numbytes = self.trans_topflag_to(numbytes, self.flags, self.flagnum, t)
                self.flags = (self.flags << t) & 0xffffffff
                self.flagnum -= t
        return numbytes


    def expand(self):
        loop = self.readByte(0xF)
        offset, flags = 0, 0
        self.di = self.si
        self.si += 2 * loop
        self.table = []
        self.assist = []
        for _ in xrange(loop):
            if offset % 16 == 0:
                flags = self.readShort()
            self.table.append(unpack('B', self.data[self.di])[0])
            self.table.append(unpack('B', self.data[self.di + 1])[0])
            self.di += 2
            self.assist.append(self.move_top(flags))
            flags = (flags << 1) & 0xffff
            self.assist.append(self.move_top(flags))
            flags = (flags << 1) & 0xffff
            offset += 2
