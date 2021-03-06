# -*- coding: UTF-8 -*-

import time
import requests
import subprocess

def send_request():
    start = time.time()

    url = "http://47.110.32.220:10002/api/algorithm/emr_struct"
    payload="{\n    \"args\": {\n        \"input_json\": {\n            \"content\": \"患者于2014年1月因“腹泻，大便带血”在我院消化科查肠镜示直肠癌？病理示(直肠肿物)符合中分化管状腺癌。确诊直肠癌。遂到我院胃肠外科住院，查腹部CT示考虑直肠癌，盆腔少量积液，左侧肾上腺稍增粗，前列腺钙化灶。于2014年1月23日行“腹腔镜直肠癌根治术”。术中见“腹膜反折处见直肠肿物约5x5cm，环绕肠腔，肠腔不全性梗阻，肿瘤已浸润浆膜层，与周围组织无明显粘连”。术后病理示（直肠肿物）腺癌II级，浸润肠壁全层；肠壁周围找到淋巴结16枚，均无癌转移，另在距癌灶5.5cm处见一绒毛-管状腺瘤，标本两侧切缘无癌残留；（直肠肿物下切缘）无癌残留。诊断直肠癌（T3N0M0)。于2014-02-27至2014-10-11予“雷替曲塞+奥沙利铂”化疗8周期。2015年5月复查全腹CT示直肠癌术后改变：未见明显复发或转移征象；升结肠盲肠局部管壁增厚（占位？）；左侧肾上腺增粗；前列腺钙化。肠镜示升结肠、直肠粘膜术后改变；升结肠吻合口炎；降结肠息肉；直肠粘膜隆起物性质待查。2015年6月反复出现解粘液血便，逐渐加重，2015年12月在我院胃肠外科查全腹部CT示直肠癌术后改变，考虑复发并盆腔淋巴结转移，不除外腹主动脉旁及髂血管旁淋巴结转移；肠镜示直肠癌术后复发?病理示（直肠）腺癌，。2016年1月7日行直肠癌切除术（Mile's 术式），肠粘连松解术，降结肠造瘘术，腹腔恶性肿瘤特殊理化治疗术。术中见“中下腹部广泛肠粘连。肿瘤位于腹膜反折下，距肛缘约6-9cm处直肠见溃疡型癌肿，周边呈围堤状隆起，大小约3X4X5cm，质硬。肿块环绕肠腔3/4圈，肿瘤浸润至直肠全层，侵润周围盆壁组织并固定。肠肿瘤系膜有数个肿大质硬的淋巴结”。术后病理示直肠中分化管状腺癌，浸润肠壁全层，累及血管、淋巴管及神经束，并形成腹壁癌结节，但肿瘤周围肠壁系膜上淋巴结（9个）均未见转移，两端切缘未见肿瘤残留。（游离肠段）结肠组织，未见肿瘤。术后查上、中腹CT示直肠癌根治术+结肠造瘘术后改变，小肠扩张积液，考虑不全性肠梗阻，少量腹水，两下肺炎症并两侧胸腔少量积液，心包少量积液。2016-1-28至2016-05-18予Folfir方案化疗6周期。2018年1月查盆腔MRI示直肠癌术后，考虑直肠癌复发，并怀疑侵犯前列腺及尾骨尖。拟前列腺中央腺体轻度增生。提示肿瘤复发，建议放疗，患者未同意。2018年2月8日查MRI示直肠癌根治术+结肠造瘘术后，考虑直肠癌复发，肿块较前增大，未除外累及前列腺及尾骨末节。目前患者腰骶部疼痛明显，疼痛评分5分，影响睡眠，恶心、便秘，为放疗到我院门诊就诊，门诊以“直肠癌术后复发”收入我科。目前患者精神、食欲可，睡眠及大便同前，小便正常，患病以来体重减轻约2Kg。\",\n            \"type\": \"XBS\"\n        }\n    }\n}"
    payload=payload.encode('utf-8')
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    cost = time.time() - start
    print("costs {} seconds".format(cost))
    print(response.text)
    return cost


requests_count = 100
s = 0
for i in range(requests_count):
    c = send_request()
    s = s + c
print(s)
