# %%

import json
import os
import numpy as np
import tensorflow as tf
import model, sample, encoder

# %%

# !ln -s ../models models # hack to make models "appear" in two places

# %%

model_name = '124M'
seed = None
nsamples = 1
batch_size = 1
length = 160
temperature = 1  # 0 is deterministic
top_k = 40  # 0 means no restrictions
models_dir = 'models',

assert nsamples % batch_size == 0

models_dir = os.path.expanduser(os.path.expandvars('models'))
enc = encoder.get_encoder(model_name)
hparams = model.default_hparams()
with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
    hparams.override_from_dict(json.load(f))

if length is None:
    length = hparams.n_ctx // 2
elif length > hparams.n_ctx:
    raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

# %%

sess = tf.InteractiveSession()

# replace with this in script:
# with tf.Session(graph=tf.Graph()) as sess:

# %%

context = tf.placeholder(tf.int32, [batch_size, None])
np.random.seed(seed)
tf.set_random_seed(seed)
output = sample.sample_sequence(
    hparams=hparams, length=length,
    context=context,
    batch_size=batch_size,
    temperature=temperature, top_k=top_k
)

saver = tf.train.Saver()
ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
saver.restore(sess, ckpt)

# %%

# from utils.list_all_files import *
import unicodedata
import os, re, random

mapping = {
    '\xa0': ' ',
    'Æ': 'AE',
    'æ': 'ae',
    'è': 'e',
    'é': 'e',
    'ë': 'e',
    'ö': 'o',
    '–': '-',
    '—': '-',
    '‘': "'",
    '’': "'",
    '“': '"',
    '”': '"'
}


def remove_special(text):
    return ''.join([mapping[e] if e in mapping else e for e in text])


# Regular expression正则表达式
# \W all worls not ralted to number/_/word, \w all world,_,numbers
# re.sub 去除掉字母数字下划线以外的字符
def strip_word(word):
    word = re.sub('^\W*|\W*$', '', word).lower()  # re.sub用于检索和替换，
    return word


basenames = []
all_poems = {}
total_lines = 0
words = set()


# 遍历文件夹下所有的文件，并保存在数组中
def get_file_path(root_path, file_list, dir_list):
    # get all files and path
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        dir_file_path = os.path.join(root_path, dir_file)
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            # recursion
            get_file_path(dir_file_path, file_list, dir_list)
        else:
            file_list.append(dir_file_path)


root_path = r"output"
file_list = []
dir_list = []
get_file_path(root_path, file_list, dir_list)

for fn in file_list:
    with open(fn) as f:  # 如果文件不存在会反馈错误
        original = open(fn).read()
        text = remove_special(original).split('\n')
        poem = text[1:]  # 前三行是诗的信息，从第四行到最后的截取，并且以换行分割
        basename = os.path.basename(fn)  # 返回最后的文件名
        basename = os.path.splitext(basename)[0]  # 去掉了后缀名
        basenames.append(basename)
        all_poems[basename] = {  # 诗歌数组是以文件名为key的字典，字典里面存的还是字典
            'title': text[0],
            'poem': poem
        }
        total_lines += len(poem)
        poem = '\n'.join(poem)
        words.update([strip_word(e) for e in poem.split()])  # 移除特殊字符，update添加一个字典到另外一个字典中
words.remove('')  # 移除空格
words = list(words)  # list() 方法用于将元组转换为列表，元祖类似于数字只是元素不能被修改


# all of the worlds


# Capitalized title 大写第一个字母
def titlecase_word(word):
    return word[0].upper() + word[1:]


titlecase_word("carpenter's"), "carpenter's".title()


# 取length长度的字符串

def random_chunk(array, length):
    start = random.randint(0, max(0, len(array) - length - 1))  # 至少从倒数length处开始
    return array[start:start + length]  # 任意的取一段


# 任意取一个元素
def random_item(array):
    return array[random.randint(0, len(array) - 1)]


# 第一首诗的两个词，
random_chunk(all_poems[basenames[0]]['poem'], 2), titlecase_word(random_item(words))

# %%

seeds = '''
love
justice  
trust 
bias 
desire 
dream
'''.split()
len(seeds)


# seeds = '''
# catch
# bend
# jump
# shake
# kiss
# flow 
# sustain 
# drop 
# slow
# punch
# '''.split()
# len(seeds)

# from utils.progress import progress

def clean(text):
    return text.split('<|endoftext|>')[0]


import json


def writeNewPoetry(all_results):
    with open('generated.json', 'rb') as f, open('temGenerated.json', 'w') as f2:
        params = json.load(f)
        for seed in seeds:
            cur = params[seed]
            newPoety = all_results[seed]
            cur.update(newPoety)
            params[seed] = cur
        json.dump(params, f2, separators=(',', ':'))
        os.remove('generated.json')
        os.rename('temGenerated.json', 'generated.json')


def generate(inspiration, seed):
    inspiration = remove_special(inspiration).strip()
    seed = titlecase_word(seed).strip()

    raw_text = inspiration + '\n' + seed
    context_tokens = enc.encode(raw_text)
    n_context = len(context_tokens)

    results = []
    str = ''
    for _ in range(nsamples // batch_size):
        out = sess.run(output, feed_dict={
            context: [context_tokens for _ in range(batch_size)]
        })
        for sample in out:
            text = enc.decode(sample[n_context:])
            result = seed + text
            results.append(result)
            return result


# 多少行诗歌作为参数
inspiration_lines = 16


class AIPoetry:
    def generatePeriod(input_text, title):
        # 随机选一首，生成新的
        seedIndex = random.randint(0, len(seeds) - 1)
        seed = seeds[seedIndex]
        randomIndex = random.randint(0, len(basenames) - 1)
        basename = basenames[randomIndex]
        inspiration = random_chunk(all_poems[basename]['poem'], inspiration_lines)
        inspiration = title + '\n' + '\n'.join(inspiration)
        print("rawText=======")
        print(inspiration)
        results = generate(inspiration, seed)
        print("generated=======")
        print(results)
        return results

    generatePeriod("demo", "demo")

    # def timer(n):
    #     while True:
    #         generatePeriod("demo")
    #         time.sleep(n)
    # timer(120)


aiLive = AIPoetry()
