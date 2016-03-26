# coding=utf-8
import os, array, json, ctypes, struct
from itertools import chain

def pack_magic_all(magi_name):
    with open('./json/' + magi_name, 'rb') as magi:
        sss = json.load(magi)
        print len(sss)
        data_magic = [UnDmagic(v['___DATA']) for v in sss.itervalues()]
        magic_array = sorted(data_magic, key=lambda x: x[1])
        mm = [m[0] for m in magic_array]
        print len(mm)
        with open('./recon/data4.bin', 'wb') as data4:
            newFileByteArray = bytearray(list(chain.from_iterable(mm)))
            data4.write(newFileByteArray)
        # json.loads(str) => obj
        # json.dumps()

def UnDmagic(magic):
    data = [0]*16
    data[0] = int(magic['00_efx_img'], 0)
    data[1] = magic['01_efx_repeat']
    data[2] = magic['02_X_offset']
    data[3] = magic['03_Y_offset']
    data[4] = magic['04_summon_efx']
    data[5] = magic['05_efx_speed']
    data[6] = magic['06_efx_lasting']
    data[7] = magic['07_preaction_frame_count']
    data[8] = magic['08_postaction_frame_count']
    data[9] = magic['09_ground_shaking']
    data[10] = magic['10_scene_distort']
    data[11] = magic['11_unknown']
    data[12] = magic['12_MP']
    data[13] = magic['13_damage']
    data[14] = magic['14_elemental']
    data[15] = magic['15_sound_fx']

    ret = [ctypes.c_uint16(i).value for i in data]
    br = struct.pack('H'*16, *ret)
    id = magic['000_id']
    return (br, id)

if __name__ == '__main__':
    pack_magic_all('magic_all.json')
