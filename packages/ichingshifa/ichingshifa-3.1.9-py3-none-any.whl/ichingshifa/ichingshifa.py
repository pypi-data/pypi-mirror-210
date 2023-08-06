# -*- coding: utf-8 -*-#
import pickle, random, datetime, os,itertools
from ephem import Date
import numpy as np
from sxtwl import fromSolar
import cn2an
from cn2an import an2cn


class Iching():
    #64卦、4096種卦爻組合資料庫，爻由底(左)至上(右)起
    def __init__(self):
        base = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(base, 'data.pkl')
        self.data = pickle.load(open(path, "rb"))
        self.sixtyfourgua = self.data.get("數字排六十四卦")
        self.sixtyfourgua_description = self.data.get("易經卦爻詳解")
        self.eightgua = self.data.get("八卦數值")
        self.eightgua_element = self.data.get("八卦卦象")
        self.bagua_pure_code = self.data.get("八宮卦純卦")
        self.tiangan = self.data.get("干")
        self.dizhi = self.data.get("支")
        self.wuxin = self.data.get("五行")
        self.down = self.data.get("下卦數")
        self.up = self.data.get("上卦數")
        self.gua = self.data.get("八卦")
        self.shen = self.data.get("世身")
        self.sixtyfour_gua_index = self.data.get("六十四卦")
        self.shiying2 = self.data.get("世應排法")
        self.findshiying = dict(zip(list(self.data.get("八宮卦").values()), self.shiying2))
        self.liuqin = self.data.get("六親")
        self.liuqin_w = self.data.get("六親五行")
        self.mons = self.data.get("六獸")
        self.chin_list = self.data.get("二十八宿")
        self.gua_down_code = dict(zip(self.gua,self.down))
        self.gua_up_code = dict(zip(self.gua,self.up))
        self.ymc = [11,12,1,2,3,4,5,6,7,8,9,10]
        self.rmc = list(range(1,32))

    def new_list(self, olist, o):
        zhihead_code = olist.index(o)
        res1 = []
        for i in range(len(olist)):
            res1.append( olist[zhihead_code % len(olist)])
            zhihead_code = zhihead_code + 1
        return res1

    def chin_iter(self, olist, chin):
        new_chin_list = self.new_list(olist, chin)
        return itertools.cycle(new_chin_list)
    
    def jiazi(self):
        tiangan = self.tiangan
        dizhi = self.dizhi
        jiazi = [tiangan[x % len(tiangan)] + dizhi[x % len(dizhi)] for x in range(60)]
        return jiazi
    
    def multi_key_dict_get(self, d, k):
        for keys, v in d.items():
            if k in keys:
                return v
        return None
    
    def find_six_mons(self, daygangzhi):
        mons = [i[1] for i in self.data.get("六獸")]
        return self.new_list(mons, self.multi_key_dict_get(dict(zip([tuple(i) for i in '甲乙,丙丁,戊,己,庚辛,壬癸'.split(",")], mons)), daygangzhi[0]))

    def rev(self, l):
        r = []
        for i in l:
            r.insert(0, i)
        return r
    
    def show_sixtyfourguadescription(self, gua):
        sixtyfourguadescription = self.sixtyfourgua_description
        return sixtyfourguadescription.get(gua)
    
    #五虎遁，起正月
    def find_lunar_month(self, year):
        fivetigers = {
        tuple(list('甲己')):'丙寅',
        tuple(list('乙庚')):'戊寅',
        tuple(list('丙辛')):'庚寅',
        tuple(list('丁壬')):'壬寅',
        tuple(list('戊癸')):'甲寅'
        }
        if self.multi_key_dict_get(fivetigers, year[0]) == None:
            result = self.multi_key_dict_get(fivetigers, year[1])
        else:
            result = self.multi_key_dict_get(fivetigers, year[0])
        return dict(zip(range(1,13), self.new_list(self.jiazi(), result)[:12]))
    
    #五鼠遁，起子時
    def find_lunar_hour(self, day):
        fiverats = {
        tuple(list('甲己')):'甲子',
        tuple(list('乙庚')):'丙子',
        tuple(list('丙辛')):'戊子',
        tuple(list('丁壬')):'庚子',
        tuple(list('戊癸')):'壬子'
        }
        if self.multi_key_dict_get(fiverats, day[0]) == None:
            result = self.multi_key_dict_get(fiverats, day[1])
        else:
            result = self.multi_key_dict_get(fiverats, day[0])
        return dict(zip(list(self.dizhi), self.new_list(self.jiazi(), result)[:12]))
    #農曆
    def lunar_date_d(self, year, month, day):
        day = fromSolar(year, month, day)
        return {"年":day.getLunarYear(),  "月": day.getLunarMonth(), "日":day.getLunarDay()}
    #干支
    def gangzhi(self, year, month, day, hour, minute):
        if year == 0:
            return ["無效"]
        if year < 0:
            year = year + 1 
        if hour == 23:
            d = Date(round((Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day+1).zfill(2), str(0).zfill(2)))), 3))
        else:
            d = Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
        dd = list(d.tuple())
        cdate = fromSolar(dd[0], dd[1], dd[2])
        yTG,mTG,dTG,hTG = "{}{}".format(self.tiangan[cdate.getYearGZ().tg], self.dizhi[cdate.getYearGZ().dz]), "{}{}".format(self.tiangan[cdate.getMonthGZ().tg],self.dizhi[cdate.getMonthGZ().dz]), "{}{}".format(self.tiangan[cdate.getDayGZ().tg], self.dizhi[cdate.getDayGZ().dz]), "{}{}".format(self.tiangan[cdate.getHourGZ(dd[3]).tg], self.dizhi[cdate.getHourGZ(dd[3]).dz])
        if year < 1900:
            mTG1 = self.find_lunar_month(yTG).get(self.lunar_date_d(year, month, day).get("月"))
        else:
            mTG1 = mTG
        hTG1 = self.find_lunar_hour(dTG).get(hTG[1])
        gangzhi_minute = self.minutes_jiazi_d().get(str(hour)+":"+str(minute))
        return [yTG, mTG1, dTG, hTG1, gangzhi_minute]
   
    #分干支
    def minutes_jiazi_d(self):
        t = [f"{h}:{m}" for h in range(24) for m in range(60)]
        c = list(itertools.chain.from_iterable([[i]*24 for i in self.jiazi()]))
        #minutelist = dict(zip(t, cycle(repeat_list(2, jiazi()))))
        return dict(zip(t, c))

    def mget_bookgua_details(self, guayao):
        getgua = self.multi_key_dict_get(self.sixtyfourgua, guayao)
        yao_results = self.sixtyfourgua_description.get(getgua)
        bian_yao = guayao.replace("6","1").replace("9","1").replace("7","0").replace("8","0")
        dong_yao = bian_yao.count("1")
        explaination = "動爻有【"+str(dong_yao )+"】根。"
        dong_yao_change = guayao.replace("6","7").replace("9","8")
        g_gua = self.multi_key_dict_get(self.sixtyfourgua, dong_yao_change)
        g_gua_result = self.sixtyfourgua_description.get(g_gua)
        b_gua_n_g_gua = "【"+getgua+"之"+g_gua+"】"
        top_bian_yao = bian_yao.rfind("1")+int(1)
        second_bian_yao = bian_yao.rfind("1",0, bian_yao.rfind("1"))+int(1)
        top_jing_yao = bian_yao.rfind("0") + int(1)
        second_jing_yao = bian_yao.rfind("0", 0, bian_yao.rfind("0"))+int(1)
        top = yao_results.get(top_bian_yao)
        second = yao_results.get(second_bian_yao)
        #top_2 = yao_results.get(top_jing_yao)
        #second_2 = yao_results.get(second_jing_yao)
        explaination2 = None
        try:
            if dong_yao == 0:
                explaination2 = explaination, "主要看【"+getgua+"】卦彖辭。",  yao_results[7][2:]
            elif dong_yao == 1: 
                explaination2 = explaination, b_gua_n_g_gua, "主要看【"+top[:2]+"】",  top
            elif dong_yao == 2:
                explaination2 = b_gua_n_g_gua, explaination, "主要看【"+top[:2]+"】，其次看【"+second[:2]+"】。", top, second
            elif dong_yao == 3:
                if bian_yao.find("1") == 0:
                    explaination2 = b_gua_n_g_gua, explaination,  "【"+getgua+"】卦為貞(我方)，【"+g_gua+"】卦為悔(他方)。前十卦，主貞【"+getgua+"】卦，請參考兩卦彖辭", yao_results[7][2:], g_gua_result[7][2:]
                elif bian_yao.find("1") > 0:
                    explaination2 = b_gua_n_g_gua, explaination,  "【"+getgua+"】卦為貞(我方)，【"+g_gua+"】卦為悔(他方)。後十卦，主悔【"+g_gua+"】卦，請參考兩卦彖辭", g_gua_result[7][2:],  yao_results[7][2:]
            elif dong_yao == 4:
                explaination2 = b_gua_n_g_gua, explaination, "主要看【"+g_gua+"】的"+g_gua_result.get(second_jing_yao)[:2]+"，其次看"+g_gua_result.get(top_jing_yao)[:2]+"。", g_gua_result.get(second_jing_yao), g_gua_result.get(top_jing_yao)
            elif dong_yao == 5:    
                explaination2 = b_gua_n_g_gua, explaination,  "主要看【"+g_gua+"】的"+g_gua_result.get(top_jing_yao)[:2]+"。", g_gua_result.get(top_jing_yao)
            elif dong_yao == 6:
                explaination2 = b_gua_n_g_gua, explaination, "主要看【"+g_gua+"】卦的彖辭。", g_gua_result[7][2:]
        except (TypeError, UnboundLocalError):
            pass
        return [guayao, getgua, g_gua, yao_results, explaination2]
    
    def bookgua(self): #由底至上起爻
        shifa_results = []
        for i in range(6):
            stalks_first = 50-1 #一變 (分二、掛一、揲四、歸奇)
            dividers = sorted(random.sample(range(24, stalks_first), 1))
            first_division  = [a - b for a, b in zip(dividers + [stalks_first+10], [10] + dividers)]
            guayi = 1
            right = first_division[0] - guayi
            left_extract = first_division[1] % 4 
            if left_extract == 0:
                left_extract = 4
            right_extract = right % 4
            if right_extract == 0:
                right_extract = 4
            yibian  = left_extract + right_extract + guayi #二變 (分二、掛一、揲四、歸奇)
            stalks_second = stalks_first - yibian
            second_dividers = sorted(random.sample(range(12, stalks_second), 1))
            second_division  = [a - b for a, b in zip(second_dividers + [stalks_second+5], [5] + second_dividers)]
            right_second = second_division[0] - guayi
            left_extract_second = second_division[1] % 4 
            if left_extract_second == 0:
                left_extract_second = 4
            right_extract_second = right_second % 4 
            if right_extract_second == 0:
                right_extract_second = 4
            erbian = left_extract_second + right_extract_second + guayi #三變 (分二、掛一、揲四、歸奇)
            stalks_third = stalks_second - erbian
            third_dividers = sorted(random.sample(range(6, stalks_third), 1))
            third_division  = [a - b for a, b in zip(third_dividers + [stalks_third+3], [3] + third_dividers)]
            right_third = third_division[0] - guayi
            left_extract_third = third_division[1] % 4
            if left_extract_third  == 0:
                left_extract_third = 4
            right_extract_third = right_third % 4 
            if right_extract_third == 0:
                right_extract_third = 4
            sanbian = left_extract_third + right_extract_third + guayi
            yao = int((stalks_first - yibian - erbian - sanbian) / 4)
            shifa_results.append(yao)
        return "".join(str(e) for e in shifa_results[:6])

    def datetime_bookgua(self, y,m,d,h,minute):
        gangzhi = self.gangzhi(y,m,d,h,minute)
        ld = self.lunar_date_d(y,m,d)
        zhi_code = dict(zip(self.dizhi, range(1,13)))
        yz_code = zhi_code.get(gangzhi[0][1])
        hz_code = zhi_code.get(gangzhi[3][1])
        cm = ld.get("月")
        cd =  ld.get("日")
        eightgua = {1:"777", 2:"778", 3:"787", 4:"788", 5:"877", 6:"878", 7:"887", 8:"888"}
        upper_gua_remain = (yz_code +cm+cd+hz_code) % 8
        if upper_gua_remain == 0:
            upper_gua_remain = int(8)
        upper_gua = eightgua.get(upper_gua_remain)
        lower_gua_remain = (yz_code+cm+cd) % 8
        if lower_gua_remain == 0:
            lower_gua_remain = int(8)
        lower_gua = eightgua.get(lower_gua_remain)
        combine_gua1 =lower_gua+upper_gua
        combine_gua = list(combine_gua1)
        bian_yao = (yz_code+cm+cd+hz_code) % 6
        if bian_yao == 0:
            bian_yao = int(6)
        elif bian_yao != 0:
            combine_gua[bian_yao -1] = combine_gua[bian_yao-1].replace("7","9").replace("8","6")
        bian_gua = "".join(combine_gua)
        ben_gua = self.multi_key_dict_get(self.sixtyfourgua, bian_gua)
        description = self.multi_key_dict_get(self.sixtyfourgua_description,  ben_gua)
        g_gua = self.multi_key_dict_get(self.sixtyfourgua, (bian_gua.replace("6", "7").replace("9", "8")))
        return ben_gua+"之"+g_gua, self.eightgua_element.get(upper_gua_remain)+self.eightgua_element.get(lower_gua_remain)+ben_gua , "變爻為"+description[bian_yao][:2], description[bian_yao][3:]
        
    def bookgua_details(self):
        return self.mget_bookgua_details(self.bookgua())

    #現在時間起卦
    def current_bookgua(self):
        now = datetime.datetime.now()
        return self.datetime_bookgua(int(now.year), int(now.month), int(now.day), int(now.hour))
    
    def dc_gua(self, gua):
        fivestars = self.data.get("五星")
        eightgua = self.data.get("數字排八卦")
        sixtyfourgua =  self.data.get("數字排六十四卦")
        su_yao = self.data.get("二十八宿配干支")
        shiying = self.multi_key_dict_get(self.data.get("八宮卦"), self.multi_key_dict_get(sixtyfourgua, gua))
        Shiying = list(self.findshiying.get(shiying))
        dgua = self.multi_key_dict_get(eightgua, gua[0:3])
        down_gua = self.gua_down_code.get(dgua)
        ugua = self.multi_key_dict_get(eightgua,gua[3:6])
        up_gua = self.gua_up_code.get(ugua)
        dt = [self.tiangan[int(g[0])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dd = [self.dizhi[int(g[1])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dw = [self.wuxin[int(g[2])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        ut = [self.tiangan[int(g[0])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        ud = [self.dizhi[int(g[1])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        uw = [self.wuxin[int(g[2])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        t = dt+ut
        d = dd+ud
        w = dw+uw
        find_gua_wuxing = self.multi_key_dict_get(self.data.get("八宮卦五行"), self.multi_key_dict_get(sixtyfourgua, gua))
        #liuqin = [i[0] for i in self.liuqin]
        lq = [self.multi_key_dict_get(self.liuqin_w,i+find_gua_wuxing) for i in dw+uw]
        gua_name = self.multi_key_dict_get(sixtyfourgua, gua)
        find_su = dict(zip(self.sixtyfour_gua_index, self.chin_iter(self.chin_list, "參"))).get(gua_name)
        sy = dict(zip(self.sixtyfour_gua_index, su_yao)).get(gua_name)
        ng = [t[i]+d[i] for i in range(0,6)]
        sy2 =  [c== sy for c in ng]
        sy3 = [str(i).replace("False", "").replace("True", find_su) for i in sy2]
        ss = dict(zip(self.sixtyfour_gua_index, self.chin_iter(fivestars, "鎮星"))).get(gua_name)
        position = sy3.index(find_su)
        if position == 0:
            g = self.new_list(self.chin_list, find_su)[0:6]
        elif position == 5:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:]
        elif position == 4:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][1:] + [list(reversed(self.new_list(self.chin_list, find_su)))[0]] 
        elif position == 3:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][2:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:2] 
        elif position == 2:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][3:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:3] 
        elif position == 1:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][4:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:4] 
        build_month_code = dict(zip(self.data.get("六十四卦"),self.data.get("月建"))).get(gua_name)
        build_month = self.new_list(self.jiazi(), build_month_code)[0:6]
        accumulate_code = dict(zip(self.data.get("六十四卦"),self.data.get("積算"))).get(gua_name)
        accumulate = self.new_list(self.jiazi(), accumulate_code)
        return {"卦":gua_name, 
                "五星":ss, 
                "世應卦":shiying+"卦",  
                "星宿":g, 
                "天干":t, 
                "地支":d, 
                "五行":w, 
                "世應":Shiying, 
                "六親用神":lq, 
                "納甲":ng, 
                "建月":build_month, 
                "積算":[list(i) for i in np.array_split(accumulate, 10)]}
    
    def decode_gua(self, gua, daygangzhi):
        fivestars = self.data.get("五星")
        eightgua = self.data.get("數字排八卦")
        sixtyfourgua =  self.data.get("數字排六十四卦")
        su_yao = self.data.get("二十八宿配干支")
        shiying = self.multi_key_dict_get(self.data.get("八宮卦"), self.multi_key_dict_get(sixtyfourgua, gua))
        Shiying = list(self.findshiying.get(shiying))
        dgua = self.multi_key_dict_get(eightgua, gua[0:3])
        down_gua = self.gua_down_code.get(dgua)
        ugua = self.multi_key_dict_get(eightgua,gua[3:6])
        up_gua = self.gua_up_code.get(ugua)
        dt = [self.tiangan[int(g[0])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dd = [self.dizhi[int(g[1])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dw = [self.wuxin[int(g[2])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        ut = [self.tiangan[int(g[0])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        ud = [self.dizhi[int(g[1])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        uw = [self.wuxin[int(g[2])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        t = dt+ut
        d = dd+ud
        w = dw+uw
        find_gua_wuxing = self.multi_key_dict_get(self.data.get("八宮卦五行"), self.multi_key_dict_get(sixtyfourgua, gua))
        liuqin = [i[0] for i in self.liuqin]
        lq = [self.multi_key_dict_get(self.liuqin_w,i+find_gua_wuxing) for i in dw+uw]
        gua_name = self.multi_key_dict_get(sixtyfourgua, gua)
        find_su = dict(zip(self.sixtyfour_gua_index, self.chin_iter(self.chin_list, "參"))).get(gua_name)
        sy = dict(zip(self.sixtyfour_gua_index, su_yao)).get(gua_name)
        ng = [t[i]+d[i] for i in range(0,6)]
        sy2 =  [c== sy for c in ng]
        sy3 = [str(i).replace("False", "").replace("True", find_su) for i in sy2]
        ss = dict(zip(self.sixtyfour_gua_index, self.chin_iter(fivestars, "鎮星"))).get(gua_name)
        position = sy3.index(find_su)
        if position == 0:
            g = self.new_list(self.chin_list, find_su)[0:6]
        elif position == 5:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:]
        elif position == 4:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][1:] + [list(reversed(self.new_list(self.chin_list, find_su)))[0]] 
        elif position == 3:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][2:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:2] 
        elif position == 2:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][3:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:3] 
        elif position == 1:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][4:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:4] 
        build_month_code = dict(zip(self.data.get("六十四卦"),self.data.get("月建"))).get(gua_name)
        build_month = self.new_list(self.jiazi(), build_month_code)[0:6]
        accumulate_code = dict(zip(self.data.get("六十四卦"),self.data.get("積算"))).get(gua_name)
        accumulate = self.new_list(self.jiazi(), accumulate_code)
        aa = list(set(lq))
        fu =  str(str([value for value in liuqin if value not in aa]).replace("['","").replace("']",""))
        fu_gua = self.dc_gua(self.multi_key_dict_get(self.bagua_pure_code, gua_name))
        fu_gua_gang = fu_gua.get("天干")
        fu_gua_zhi = fu_gua.get("地支")
        fu_gua_wu = fu_gua.get("五行")
        fu_gua_lq = fu_gua.get("六親用神")
        shen = self.multi_key_dict_get(self.shen, d[Shiying.index("世")])
        
        try:
            fu_num = fu_gua_lq.index(fu)
            fuyao = [str(g ==fu) for g in fu_gua_lq].index('True')
            fuyao1 = fu_gua_lq[fu_num] + fu_gua_gang[fu_num] +  fu_gua_zhi[fu_num] + fu_gua_wu[fu_num]
            fu_yao = {"伏神所在爻": lq[fuyao], "伏神六親":fu, "伏神排爻數字":fu_num, "本卦伏神所在爻":lq[fu_num]+t[fu_num]+d[fu_num]+w[fu_num], "伏神爻":fuyao1}
            
        except (ValueError, IndexError ,AttributeError):
            fu_yao = ""
        
        return {"卦":gua_name, 
                "五星":ss, 
                "世應卦":shiying+"卦",  
                "星宿":g, 
                "天干":t, 
                "地支":d, 
                "五行":w, 
                "世應爻":Shiying, 
                "身爻":lq[shen]+t[shen]+d[shen]+w[shen],
                "六親用神":lq, 
                "伏神":fu_yao,
                "六獸":self.find_six_mons(daygangzhi),
                "納甲":ng, 
                "建月":build_month, 
                "積算":[list(i) for i in np.array_split(accumulate, 10)]}
    
    
    def decode_two_gua(self, bengua, ggua, daygangzhi):
        a = self.decode_gua(bengua, daygangzhi)
        b = self.decode_gua(ggua, daygangzhi)
        try:
            fu_yao = a.get("伏神").get("伏神爻")
            fu_ben_yao = a.get("伏神").get('本卦伏神所在爻')
            g_yao = b.get("六親用神") + b.get("天干") + b.get("地支") + b.get("五行")
            if fu_yao == g_yao:
                fei = fu_ben_yao
            else:
                fei = ""
        except (ValueError, IndexError ,AttributeError):
            fei = ""
        
        return {"本卦":a, "之卦":b, "飛神":fei}

    def qigua_time(self, y, m, d, h, minute):
        gangzhi = self.gangzhi(y,m,d,h, minute)
        ld = self.lunar_date_d(y,m,d)
        zhi_code = dict(zip(self.dizhi, range(1,13)))
        yz_code = zhi_code.get(gangzhi[0][1])
        hz_code = zhi_code.get(gangzhi[3][1])
        cm = ld.get("月")
        cd =  ld.get("日")
        eightgua = self.data.get("八卦數值")
        upper_gua_remain = (yz_code +cm+cd+hz_code) % 8
        if upper_gua_remain == 0:
            upper_gua_remain = int(8)
        upper_gua = eightgua.get(upper_gua_remain)
        lower_gua_remain = (yz_code+cm+cd) % 8
        if lower_gua_remain == 0:
            lower_gua_remain = int(8)
        lower_gua = eightgua.get(lower_gua_remain)
        combine_gua1 =lower_gua+upper_gua
        combine_gua = list(combine_gua1)
        bian_yao = (yz_code+cm+cd+hz_code) % 6
        if bian_yao == 0:
            bian_yao = int(6)
        elif bian_yao != 0:
            combine_gua[bian_yao -1] = combine_gua[bian_yao-1].replace("7","9").replace("8","6")
        bian_gua = "".join(combine_gua)
        ggua = bian_gua.replace("6","7").replace("9","8")
        return {**{'日期':gangzhi[0]+"年"+gangzhi[1]+"月"+gangzhi[2]+"日"+gangzhi[3]+"時"}, **{"大衍筮法":self.mget_bookgua_details(bian_gua)}, **self.decode_two_gua(bian_gua, ggua, gangzhi[2])}

    def qigua_now(self):
        now = datetime.datetime.now()
        return self.qigua_time(int(now.year), int(now.month), int(now.day), int(now.hour), int(now.minute))
    
    def display_pan(self, year, month, day, hour, minute):
        gz = self.gangzhi(year, month, day, hour, minute)
        oo = self.qigua_time(year, month, day, hour, minute).get('大衍筮法')
        ogua = self.qigua_time(year, month, day, hour, minute).get('大衍筮法')[0]
        bengua = self.qigua_time(year, month, day, hour, minute).get("本卦")
        ggua = self.qigua_time(year, month, day, hour, minute).get("之卦")
        gb = ogua.replace("9","8").replace("6","7")
        b1 = self.qigua_time(year, month, day, hour, minute).get("本卦").get("星宿")
        b2 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('六親用神')
        b3 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('納甲')
        b4 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('五行')
        b5 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('世應爻')
        g1 = self.qigua_time(year, month, day, hour, minute).get("之卦").get("星宿")
        g2 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('六親用神')
        g3 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('納甲')
        g4 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('五行')
        g5 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('世應爻')
        guayaodict = {"6":"▅▅　▅▅ X", "7":"▅▅▅▅▅  ", "8":"▅▅　▅▅  ", "9":"▅▅▅▅▅ O"}
        bg = [guayaodict.get(i) for i in list(ogua)]
        gb1 = [guayaodict.get(i) for i in list(gb)]
        a = "起卦時間︰{}年{}月{}日{}時{}分\n".format(year, month, day, hour, minute)
        b = "農曆︰{}{}月{}日\n".format(cn2an.transform(str(year)+"年", "an2cn"), an2cn(self.lunar_date_d(year, month, day).get("月")), an2cn(self.lunar_date_d(year,month, day).get("日")))
        c = "干支︰{}年  {}月  {}日  {}時\n\n".format(gz[0], gz[1], gz[2], gz[3])
        d = "　　　　　　　　　　{}卦　　　　　　　　　　　　　　　　{}卦                \n".format(bengua.get("卦"), ggua.get("卦"))
        e = "六神　　伏神　　本　　　卦　　　　　　　　　　　 　　之　　　卦\n"
        f = "玄武 　　　　　 {} {}{}{} {}{}　　　　　{} {}{}{} {}{}　\n".format(b1[5],b2[5],b3[5],b4[5],b5[5],bg[5],g1[5],g2[5],g3[5],g4[5],g5[5],gb1[5])
        g = "白虎 　　　　　 {} {}{}{} {}{}　　　　　{} {}{}{} {}{}  \n".format(b1[4],b2[4],b3[4],b4[4],b5[4],bg[4],g1[4],g2[4],g3[4],g4[4],g5[4],gb1[4])
        h = "螣蛇 　　　　　 {} {}{}{} {}{}　　　　　{} {}{}{} {}{}  \n".format(b1[3],b2[3],b3[3],b4[3],b5[3],bg[3],g1[3],g2[3],g3[3],g4[3],g5[3],gb1[3])
        i = "勾陳 　　　　　 {} {}{}{} {}{}　　　　　{} {}{}{} {}{}  \n".format(b1[2],b2[2],b3[2],b4[2],b5[2],bg[2],g1[2],g2[2],g3[2],g4[2],g5[2],gb1[2])
        j = "朱雀 　　　　　 {} {}{}{} {}{}　　　　　{} {}{}{} {}{}  \n".format(b1[1],b2[1],b3[1],b4[1],b5[1],bg[1],g1[1],g2[1],g3[1],g4[1],g5[1],gb1[1])
        k = "青龍 　　　　　 {} {}{}{} {}{}　　　　　{} {}{}{} {}{}  \n\n\n".format(b1[0],b2[0],b3[0],b4[0],b5[0],bg[0],g1[0],g2[0],g3[0],g4[0],g5[0],gb1[0])
        l = "【大衍筮法】\n"
        try:
            m = "求得【{}之{}】，{}{}{}\n\n".format(oo[1], oo[2], oo[4][0], oo[4][2], oo[4][3])
        except IndexError:
            m = "求得【{}之{}】，{}{}\n\n".format(oo[1], oo[2], oo[4][0], oo[4][2])
        n = "{}卦\n【卦辭】︰{}\n【彖】︰{}\n{}\n{}\n{}\n{}\n{}\n{}".format(oo[1],oo[3].get(0), oo[3].get(7)[2:], oo[3].get(6), oo[3].get(5), oo[3].get(4), oo[3].get(3), oo[3].get(2), oo[3].get(1)  )
        return a+b+c+d+e+f+g+h+i+j+k+l+m+n
        
    
    
if __name__ == '__main__':
    #print(Iching().data)
    print(Iching().display_pan(2023,5,27,12,0))