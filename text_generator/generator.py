#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf

from text_generator import model
from text_generator import sample
from text_generator import encoder

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

class AI:
    def generate_text(self, input_text):
        model_name='124M'
        seed=None
        nsamples=1
        batch_size=1
        length=80
        temperature=1
        top_k=40
        top_p=0.0
        self.response = ""

        if batch_size is None:
            batch_size = 1
        assert nsamples % batch_size == 0

        enc = encoder.get_encoder(model_name)
        hparams = model.default_hparams()
        cur_path = os.path.dirname(__file__) + "/models" + "/" + model_name
        print(cur_path)
        with open(cur_path + '/hparams.json') as f:
            hparams.override_from_dict(json.load(f))

        if length is None:
            length = hparams.n_ctx // 2
        elif length > hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

        sess = tf.InteractiveSession()
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
        ckpt = tf.train.latest_checkpoint(cur_path)
        saver.restore(sess, ckpt)

        context_tokens = enc.encode(input_text)
        generated = 0

        for _ in range(nsamples // batch_size):
            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(batch_size)]
            })
            for i in range(batch_size):
                generated += 1
                text = enc.decode(out[i])
                self.response = text

        return self.response

class AI_Noninteractive:
    def generate_text(self, input_text):
        model_name='124M_TRAINED'
        seed=None
        nsamples=0
        batch_size=1
        length=None
        temperature=1
        top_k=0
        top_p=0.0
        self.response = ""

        if batch_size is None:
            batch_size = 1
        assert nsamples % batch_size == 0

        enc = encoder.get_encoder(model_name)
        hparams = model.default_hparams()
        cur_path = os.path.dirname(__file__) + "/models" + "/" + model_name
        print(cur_path)
        with open(cur_path + '/hparams.json') as f:
            hparams.override_from_dict(json.load(f))

        if length is None:
            length = hparams.n_ctx // 2
        elif length > hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

        sess = tf.Session()
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            start_token=enc.encoder['<|endoftext|>'],
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )[:, 1:]

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(cur_path)
        saver.restore(sess, ckpt)

        context_tokens = enc.encode(input_text)
        generated = 0

        # for _ in range(nsamples // batch_size):
        #     out = sess.run(output)
        #     for i in range(batch_size):
        #         generated += 1
        #         text = enc.decode(out[i])
        #         self.response = text
        #
        # return self.response

        generated = 0
        while nsamples == 0 or generated < nsamples:
            out = sess.run(output)
            for i in range(batch_size):
                generated += batch_size
                text = enc.decode(out[i])
                print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
                print(text)


def remove_special(text):
    return ''.join([mapping[e] if e in mapping else e for e in text])
def strip_word(word):
    word = re.sub('^\W*|\W*$', '', word).lower()
    return word
def titlecase_word(word):
    return word[0].upper() + word[1:]
titlecase_word("carpenter's"), "carpenter's".title()

class AIPoetry:

    def generate_text(self, input_text, title):
        model_name = '124M'
        seed = None
        nsamples = 1
        batch_size = 1
        length = 80
        temperature = 1
        top_k = 40
        top_p = 0.0
        self.response = ""

        if batch_size is None:
            batch_size = 1
        assert nsamples % batch_size == 0

        enc = encoder.get_encoder(model_name)
        hparams = model.default_hparams()
        cur_path = os.path.dirname(__file__) + "/models" + "/" + model_name
        print(cur_path)
        with open(cur_path + '/hparams.json') as f:
            hparams.override_from_dict(json.load(f))

        if length is None:
            length = hparams.n_ctx // 2
        elif length > hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

        sess = tf.InteractiveSession()
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
        ckpt = tf.train.latest_checkpoint(cur_path)
        saver.restore(sess, ckpt)

        input_text = remove_special(input_text).strip()
        title = titlecase_word(title).strip()
        raw_text = input_text + '\n' + title
        context_tokens = enc.encode(raw_text)
        n_context = len(context_tokens)

        context_tokens = enc.encode(input_text)
        generated = 0
        results = []
        for _ in range(nsamples // batch_size):
            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(batch_size)]
            })
            finalpoetry = ""
            for i in out:
                text = enc.decode(i[n_context:])
                result = title + text
                results.append(result)
                finalpoetry = finalpoetry + text
        return finalpoetry

ai = AIPoetry()
