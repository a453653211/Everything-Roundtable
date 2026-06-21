# -*- coding: utf-8 -*-
"""
Organize subtitles for 王晓 (小王Albert) and 杨博士 (杨博士说AI).
- Keep content since 2024-01-01, archive earlier files into _2024年前_已排除.
- Classify post-2024 files into <=3 content categories via keyword scoring.
Mirrors the 淘沙博士 organize.py naming convention (01_/02_/03_ prefix + archive folder).
"""
import os, re, io, shutil

CUTOFF = '2024-01-01'

def read_text(path):
    try:
        return io.open(path, 'r', encoding='utf-8', errors='ignore').read()
    except Exception:
        return u''

def date_of(f):
    m = re.search(u'【(\d{4}-\d{2}-\d{2})】', f)
    return m.group(1) if m else None

def score(text, kws):
    return sum(text.count(k) for k in kws)

def classify(txt, cats, default):
    scores = {k: score(txt, kws) for k, kws in cats.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default

def ensure_dir(p):
    if not os.path.isdir(p):
        os.makedirs(p)

def run(root, cats, cat_dir, default, archive):
    ensure_dir(os.path.join(root, archive))
    for cat in cat_dir:
        ensure_dir(os.path.join(root, cat_dir[cat]))
    moved = {cat: 0 for cat in cats}
    archived = 0
    no_date = 0
    for f in os.listdir(root):
        src = os.path.join(root, f)
        if not os.path.isfile(src):
            continue
        dt = date_of(f)
        if dt is None:
            no_date += 1
            continue
        if dt >= CUTOFF:
            body = read_text(src)
            txt = f + u'\n' + body
            cat = classify(txt, cats, default)
            shutil.move(src, os.path.join(root, cat_dir[cat], f))
            moved[cat] += 1
        else:
            shutil.move(src, os.path.join(root, archive, f))
            archived += 1
    return moved, archived, no_date

# ---------------- 王晓 ----------------
WX = {
    u'AFRICA': [u'西非', u'中非', u'东非', u'南非', u'北非', u'非洲', u'马里', u'布基纳法索', u'尼日尔',
        u'塞内加尔', u'几内亚', u'科特迪瓦', u'贝宁', u'塞拉利昂', u'佛得角', u'坦桑尼亚', u'坦赞',
        u'加蓬', u'乍得', u'圣多美', u'赤道几内亚', u'安哥拉', u'柏林会议', u'撒哈拉', u'黑人', u'部落'],
    u'POWER': [u'中东', u'伊朗', u'以色列', u'哈马斯', u'土耳其', u'埃及', u'库尔德', u'穆兄会',
        u'霍尔木兹', u'海湾', u'俄乌', u'普京', u'乌克兰', u'委内瑞拉', u'马杜罗', u'特朗普', u'大选',
        u'中美', u'霸权', u'关税', u'台湾', u'民进党', u'贸易', u'北约', u'欧盟', u'法国', u'德国',
        u'朔尔茨', u'默克尔', u'意大利', u'英国', u'沙特', u'核武', u'停火', u'战争', u'世界'],
    u'CHINA': [u'汽车', u'出口', u'换道超车', u'新能源', u'工业', u'鸿蒙', u'再全球化', u'一带一路',
        u'基建', u'政策', u'市场准入', u'AI', u'游戏', u'经济', u'开放', u'核心竞争力', u'仰望',
        u'制造业', u'产业'],
}
WX_DIR = {
    u'AFRICA': u'01_非洲地缘系列',
    u'POWER':  u'02_大国博弈与热点冲突',
    u'CHINA':  u'03_中国产业升级与经济洞察',
}

# ---------------- 杨博士 ----------------
YB = {
    u'COMPANY': [u'OpenAI', u'ChatGPT', u'奥特曼', u'Sama', u'Anthropic', u'Claude', u'DeepSeek',
        u'Deepseek', u'Google', u'Gemini', u'xAI', u'Grok', u'Meta', u'微软', u'Kimi', u'千问',
        u'Qwen', u'豆包', u'智谱', u'Minimax', u'Mythos', u'Fable', u'GPT', u'英伟达', u'SpaceX',
        u'软银', u'苹果', u'Cursor', u'Perplexity', u'Manus', u'融资', u'估值', u'上市', u'递表',
        u'收购', u'OpenClaw', u'龙虾', u'Windsurf', u'Cognition', u'Figure', u'宇树', u'特斯拉',
        u'Tesla', u'NeuralLink', u'Waymo', u'Sora', u'混元', u'Seedance', u'GTC', u'Gemma'],
    u'TECH': [u'强化学习', u'RL', u'预训练', u'后训练', u'蒸馏', u'scaling', u'缩放', u'上下文工程',
        u'context', u'多智能体', u'multi-agent', u'Mixture', u'Agent', u'智能体', u'世界模型',
        u'多模态', u'OCR', u'RAG', u'记忆', u'Harness', u'论文', u'数学', u'IMO', u'ACM', u'陶哲轩',
        u'Karpathy', u'LeCun', u'Hinton', u'Hassabis', u'DeepMind', u'吴恩达', u'李飞飞', u'开源',
        u'架构', u'算法', u'benchmark', u'自监督', u'训练', u'验证器', u'姚顺雨', u'姚顺宇', u'林俊旸',
        u'Sutton', u'Genie', u'JEPA', u'Willow', u'量子', u'token'],
    u'BIZ': [u'商业模式', u'C端', u'2C', u'2B', u'ARR', u'DAU', u'流量', u'泡沫', u'经济学', u'定价',
        u'A16Z', u'a16z', u'红杉', u'YC', u'创业', u'SaaS', u'投资', u'护城河', u'壁垒', u'指标',
        u'市场', u'增长', u'AI原生', u'裁员', u'就业', u'应用', u'社交', u'电商', u'短剧', u'政务',
        u'博彩', u'游戏', u'搜索', u'品牌', u'罗永浩', u'拉布布', u'营销', u'新加坡', u'生活中的AI',
        u'Vibe', u'编程', u'Coding', u'性价比', u'2Pro', u'prosumer', u'复活亡者'],
}
YB_DIR = {
    u'COMPANY': u'01_模型公司与巨头动态',
    u'TECH':    u'02_技术原理与前沿论文',
    u'BIZ':     u'03_商业化产品与投资',
}

ARCHIVE = u'_2024年前_已排除'

out = io.open(u'_organize_report.txt', 'w', encoding='utf-8')
def p(s): out.write(unicode(s) + u'\n')

for label, root, cats, cat_dir, default in [
    (u'王晓', u'王晓_字幕', WX, WX_DIR, u'POWER'),
    (u'杨博士', u'杨博士_字幕', YB, YB_DIR, u'BIZ'),
]:
    moved, archived, no_date = run(root, cats, cat_dir, default, ARCHIVE)
    p(u'===== %s =====' % label)
    total = sum(moved.values())
    for cat in cats:
        p(u'  %s: %d' % (cat_dir[cat], moved[cat]))
    p(u'  %s: %d' % (ARCHIVE, archived))
    p(u'  2024后合计: %d   无日期跳过: %d' % (total, no_date))
    p(u'')

out.close()
print('organize done')
