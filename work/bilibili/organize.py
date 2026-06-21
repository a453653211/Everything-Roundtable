# -*- coding: utf-8 -*-
import os, re, sys, shutil
reload(sys)
sys.setdefaultencoding('utf-8')

d = u'淘沙博士_字幕'
cutoff = '2024-01-01'

def date_of(f):
    m = re.search(u'【(\d{4}-\d{2}-\d{2})】', f)
    return m.group(1) if m else None

files = os.listdir(d)

KW = {
    'AI': [u'英伟达', u'达子', u'芯片', u'半导体', u'算力', u'寒武纪', u'华为', u'存储', u'HBM', u'光模块',
           u'人工智能', u'闪迪', u'美光', u'台积电', u'国产替代', u'半导体设备', u'升腾', u'AMD', u'大模型',
           u'AGI', u'硅基', u'碳基', u'AI算力', u'消费电子', u'PCB', u'封装', u'服务器', u'液冷', u'电源',
           u'字节', u'SpaceX', u'星舰', u'商业航天', u'机器人', u'智驾', u'自动驾驶', u'脑机',
           u'DeepSeek', u'deepseek', u'Grok', u'马斯克', u'特斯拉', u'周鸿祎', u'OpenAI', u'ChatGPT',
           u'文心', u'豆包', u'Kimi', u'智谱', u'AI公务员', u'AI巨头', u'AI霸权', u'AI芯片'],
    'MACRO': [u'利率', u'通胀', u'CPI', u'加息', u'降息', u'鲍威尔', u'沃什', u'美联储', u'汇率', u'人民币',
              u'美元', u'黄金', u'金价', u'原油', u'油价', u'大宗', u'铜', u'关税', u'特朗普', u'懂王',
              u'伊朗', u'美伊', u'海峡', u'霍尔木兹', u'俄乌', u'中东', u'地缘', u'国债', u'流动性',
              u'货币', u'衰退', u'复交', u'停火', u'巴菲特', u'发钱', u'去杠杆', u'杠杆', u'收益率',
              u'日本', u'日债', u'韩国', u'海力士', u'日韩', u'韩存', u'制裁', u'光缆',
              u'房地产', u'楼市', u'房价', u'楼盘', u'楼王', u'契税', u'万达', u'工资', u'薪资', u'月薪',
              u'退休', u'延迟退休', u'生育', u'PMI', u'退市', u'餐饮', u'消费降级', u'就业', u'失业'],
    'MARKET': [u'A股', u'沪指', u'上证', u'深成', u'创业板', u'沪深', u'大盘', u'成交额', u'成交', u'万亿',
               u'涨停', u'跌停', u'牛市', u'熊市', u'券商', u'北证', u'美股', u'纳斯达克', u'纳指', u'道琼斯',
               u'道指', u'标普', u'收盘', u'收跌', u'收涨', u'新高', u'跳水', u'反弹', u'回调', u'港股',
               u'恒生', u'恒科', u'抄底', u'减仓', u'仓位', u'见顶', u'见底', u'分化', u'缩量', u'放量',
               u'恐慌', u'暴涨', u'暴跌', u'权重', u'中芯', u'茅台'],
}
PRI = ['AI', 'MACRO', 'MARKET']
CAT_DIR = {
    'AI': u'01_AI科技投资主线',
    'MACRO': u'02_宏观与全球局势',
    'MARKET': u'03_市场行情与大盘点评',
}
ARCHIVE = u'_2024年前_已排除'

def classify(f, body):
    txt = body.lower()
    ttl = f.lower()
    scores = {}
    for cat, kws in KW.items():
        body_c = sum(txt.count(kw.lower()) for kw in kws)
        ttl_c = sum(1 for kw in kws if kw.lower() in ttl)
        scores[cat] = ttl_c * 6 + body_c
    ranked = sorted(scores.items(), key=lambda x: (-x[1], PRI.index(x[0])))
    top_cat = ranked[0][0]
    if ranked[0][1] == 0:
        top_cat = 'MACRO'
    return top_cat

# 创建目标目录
def ensure_dir(p):
    if not os.path.isdir(p):
        os.makedirs(p)
for cat, name in CAT_DIR.items():
    ensure_dir(os.path.join(d, name))
ensure_dir(os.path.join(d, ARCHIVE))

moved = {'AI': 0, 'MACRO': 0, 'MARKET': 0}
archived = 0
for f in files:
    src = os.path.join(d, f)
    if not os.path.isfile(src):
        continue
    dt = date_of(f)
    if dt and dt >= cutoff:
        try:
            body = open(src, 'r').read().decode('utf-8', 'ignore')
        except:
            body = u''
        cat = classify(f, body)
        dst = os.path.join(d, CAT_DIR[cat], f)
        shutil.move(src, dst)
        moved[cat] += 1
    else:
        dst = os.path.join(d, ARCHIVE, f)
        shutil.move(src, dst)
        archived += 1

print(u'=== 移动完成 ===')
for cat in PRI:
    print(u'%s: %d' % (CAT_DIR[cat], moved[cat]))
print(u'%s: %d' % (ARCHIVE, archived))
print(u'2024后合计: %d' % sum(moved.values()))
