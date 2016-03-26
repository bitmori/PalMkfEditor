# coding=utf-8
import os, array, json
# from mkf import MKFDecoder

# def unpack_mkf(mkfname):
#     mkf = MKFDecoder(path= ('%s.mkf' % mkfname))
#     if not os.path.exists('./%s'%mkfname):
#         os.makedirs('./%s'%mkfname)
#     for i in xrange(mkf.getFileCount()):
#         arrayH = array.array('H', mkf.read(i))
#         newFileByteArray = arrayH
#         with open('./%s/%s_%d.bin'%(mkfname, mkfname, i), 'wb') as file:
#             file.write(newFileByteArray)
#
# unpack_mkf('data')
class WordData:
    def __init__(self):
        with open('WORD.DAT', mode='rb') as file: # b is important -> binary
            fileContent = file.read()
            theBuffer = get_chunks(fileContent, 10)
            self.words = [ss.strip().decode('big5').encode('utf8') for ss in theBuffer]
            self.length = len(self.words)

    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, type, value, trace):
    #     pass

    def get_object_name(self, objId):
        if objId < self.length:
            return self.words[objId]
        else:
            return None

def get_chunks(l, n):
    llen = len(l)
    return [l[i:i+n] for i in xrange(0, llen, n)]

def unpack_sss_0_event(sss0_name):
    with open('./sss/' + sss0_name, 'rb') as sss0:
        bin_events = array.array('H', sss0.read())
        # json.loads(str) => obj
        # json.dumps()

def unpack_sss_2_objects(sss2_name, words):
    with open('./sss/' + sss2_name, 'rb') as sss2:
        bin_objects = array.array('H', sss2.read())
        allObjDef = get_chunks(bin_objects, 6)

        inventory_address = 0x3D
        inventories = {key+inventory_address: Pinventory(obj, key+inventory_address, words.get_object_name(key+inventory_address)) for (key, obj) in enumerate(allObjDef[inventory_address:0x127])}
        # new inventory in pal dream
        inventories[564] = Pinventory(allObjDef[564], 564, words.get_object_name(564))
        inventories[565] = Pinventory(allObjDef[565], 565, words.get_object_name(565))
        inventories[579] = Pinventory(allObjDef[579], 579, words.get_object_name(579))
        text_file = open("./json/inventory.json", "w")
        text_file.write(json.dumps(inventories, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        text_file.close()

        magic_address = 295
        magics = {key+magic_address: Pmagic(obj, key+magic_address, words.get_object_name(key+magic_address)) for (key, obj) in enumerate(allObjDef[magic_address:398])}
        for i in xrange(566, 572):
            magics[i] = Pmagic(allObjDef[i], i, words.get_object_name(i))
        i = 580
        magics[i] = Pmagic(allObjDef[i], i, words.get_object_name(i))
        text_file = open("./json/magic.json", "w")
        text_file.write(json.dumps(magics, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        text_file.close()

        monster_address = 398
        monsters = {key+monster_address: Pmonster(obj, key+monster_address, words.get_object_name(key+monster_address)) for (key, obj) in enumerate(allObjDef[monster_address:551])}
        for i in xrange(572, 577):
            monsters[i] = Pmonster(allObjDef[i], i, words.get_object_name(i))
        text_file = open("./json/monster.json", "w")
        text_file.write(json.dumps(monsters, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        text_file.close()

        poison_address = 551
        poisons = {key+poison_address: Ppoison(obj, key+poison_address, words.get_object_name(key+poison_address)) for (key, obj) in enumerate(allObjDef[poison_address:564])}
        poisons[577] = Ppoison(allObjDef[577], 577, words.get_object_name(577))
        poisons[578] = Ppoison(allObjDef[578], 578, words.get_object_name(578))
        for i in xrange(581, 589):
            poisons[i] = Ppoison(allObjDef[i], i, words.get_object_name(i))
        text_file = open("./json/poison.json", "w")
        text_file.write(json.dumps(poisons, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        text_file.close()

        return magics


class hexint(int):
    def __str__(self):
        return hex(self)

def Pinventory(data, id, name):
    inventory = {
        '_line': id*12,
        '0address' : "{0:#0{1}x}".format(id,6),
        '1name' : name,
        '2image_in_ball' : "{0:#0{1}x}".format(data[0],6),
        '3price' : data[1],
        '4script_use' : "{0:#0{1}x}".format(data[2],6),
        '5script_equip' : "{0:#0{1}x}".format(data[3],6),
        '6script_throw' : "{0:#0{1}x}".format(data[4],6),
        '7properties' : {
            '1usable' : (data[5] & 1),
            '2wearable' : ( data[5] & 2) >> 1,
            '3throwable' : ( data[5] & 4) >> 2,
            '4consuming' : ( data[5] & 8) >> 3,
            '5for_all' : ( data[5] & 16) >> 4,
            '6sellable' : ( data[5] & 32) >> 5,
            '_1XY' : ( data[5] & 64) >> 6,
            '_2O2' : ( data[5] & 128) >> 7,
            '_3YR' : ( data[5] & 256) >> 8,
            '_4WH' : ( data[5] & 512) >> 9,
            '_5NU' : ( data[5] & 1024) >> 10,
            '_6GL' : ( data[5] & 2048) >> 11
        }
    }
    return inventory

def Pmagic(data, id, name):
    magic = {
        '_line': id*12,
        '0address' : "{0:#0{1}x}".format(id,6),
        '1name' : name,
        '2addr_in_data': "{0:#0{1}x}".format(data[0],6),
        '4before_script': "{0:#0{1}x}".format(data[3],6),
        '3after_script': "{0:#0{1}x}".format(data[2],6),
        '5properties':{
            '1use_on_map' : (data[5] & 1),
            '2use_in_battle' : ( data[5] & 2) >> 1,
            '3unknown' : ( data[5] & 4) >> 2,
            '4on_enemy' : ( data[5] & 8) >> 3,
            '5for_all' : ( data[5] & 16) >> 4,
        }
    }
    return magic

def Pmonster(data, id, name):
    monster = {
        '_line': id*12,
        '0address' : "{0:#0{1}x}".format(id,6),
        '1name' : name,
        '2addr_in_data_abc': "{0:#0{1}x}".format(data[0],6),
        '3curse_resistance': data[1],
        '4before_script': "{0:#0{1}x}".format(data[2],6),
        '5after_script': "{0:#0{1}x}".format(data[3],6),
        '6ai_attack_script': "{0:#0{1}x}".format(data[4],6),
    }
    return monster

def Ppoison(data, id, name):
    poison = {
        '_line': id*12,
        '0address' : "{0:#0{1}x}".format(id,6),
        '1name' : name,
        '2intensity': data[0],
        '3color' : data[1],
        '4on_heroes_script' : data[2],
        '5on_enemies_script' : data[4],
    }
    return poison

def Dmagic(data, id):
    # 属性:12345风雷水火土，6毒，7非 若法术特性为9则为召唤术，法术特效重定位到“特效”处，法术召唤+10为神形 3变身    2辅助    1一方    0三叠
    magic = {
        '000_address': id*32,
        '000_addr_hex': "{0:#0{1}x}".format(id*32,6),
        '000_id': id,
        '00_efx_img': "{0:#0{1}x}".format(data[0],6) if data[0] >= 0 else "0xffff",
        '01_efx_repeat': data[1],
        '02_X_offset': data[2],
        '03_Y_offset': data[3],
        '04_summon_efx': data[4],
        '05_efx_speed':data[5],
        '06_efx_lasting': data[6],
        '07_preaction_frame_count': data[7],
        '08_postaction_frame_count': data[8],
        '09_ground_shaking': data[9],
        '10_scene_distort': data[10],
        '11_unknown': data[11],
        '12_MP': data[12],
        '13_damage': data[13],
        '14_elemental': data[14],
        '15_sound_fx': data[15],
    }
    return magic

def unpack_data_4_magic(data4_name):
    with open('./data/' + data4_name, 'rb') as data4:
        bin_objects = array.array('h', data4.read())
        magic_data = get_chunks(bin_objects, 16)

        magics = {"{0:#0{1}x}".format(key,6): Dmagic(obj, key) for (key, obj) in enumerate(magic_data)}

        text_file = open("./json/magic_data.json", "w")
        text_file.write(json.dumps(magics, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        text_file.close()

        return magics


def combine_magic_data(data_m, sss_m):
    data_m_len = len(data_m)
    id_list = [0]*data_m_len
    for key, value in sss_m.iteritems():
        value['___DATA'] = data_m[value['2addr_in_data']]
        id_list[int(value['2addr_in_data'], 16)] = 1
    for k in xrange(data_m_len):
        if id_list[k] == 0:
            key = "{0:#0{1}x}".format(k,6)
            sss_m[key] = {
                '___DATA': data_m[key]
            }
    return sss_m




def main():
    g_words = WordData()
    data_magics = unpack_data_4_magic('data_4.bin')
    sss_magics = unpack_sss_2_objects('objects.bin', g_words)
    final_magics = combine_magic_data(data_magics, sss_magics)
    text_file = open("./json/magic_all.json", "w")
    text_file.write(json.dumps(final_magics, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
    text_file.close()




if __name__ == '__main__':
    main()
