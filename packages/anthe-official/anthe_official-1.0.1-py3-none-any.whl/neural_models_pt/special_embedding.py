import torch
import torch.nn as nn
import torch.nn.functional as F

from pyaromatics.stay_organized.utils import str2val
from anthe_official.neural_models_pt.tensor_chain.convolutions import TCConv1D

from anthe_official.neural_models_pt.tensor_chain.embedding import TCEmbedding

import torch


def positional_encoding(max_len, d_model):
    depth = d_model // 2

    positions = torch.arange(max_len).unsqueeze(1)  # (seq, 1)
    depths = torch.arange(depth, dtype=torch.float32).unsqueeze(0) / depth  # (1, depth)

    angle_rates = 1 / (10000 ** depths)  # (1, depth)
    angle_rads = positions * angle_rates  # (pos, depth)

    pos_encoding = torch.cat([torch.sin(angle_rads), torch.cos(angle_rads)], dim=-1)

    return pos_encoding.float()


def angle(pos, index, d_model):
    pos = pos.float()
    return pos / (10000. ** (index // 2 * 1. / d_model))


class EmbeddingLayer(nn.Module):
    def __init__(self, vocab_size, d_model):
        super(EmbeddingLayer, self).__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model

        self.embedding = nn.Embedding(vocab_size, d_model)

    def forward(self, sequences):
        max_sequence_len = sequences.size(1)

        output = self.embedding(sequences)
        output = output * torch.sqrt(torch.tensor(self.d_model, dtype=torch.float32))
        pos = positional_encoding(max_sequence_len, self.d_model)

        output = output + pos

        return output


class SoftPOS(nn.Module):
    def __init__(self, add_units, n_subpos=3, repeat_subpos=2, initializer='orthogonal'):
        super(SoftPOS, self).__init__()

        self.add_units = add_units
        self.n_subpos = n_subpos
        self.repeat_subpos = repeat_subpos
        self.initializer = initializer

        if self.n_subpos > 0:
            self.spos = nn.Parameter(torch.Tensor(self.repeat_subpos, self.n_subpos, self.add_units))
            nn.init.orthogonal_(self.spos)

    def forward(self, inputs):
        x = inputs
        emb = x
        if self.n_subpos > 0:
            for i in range(self.repeat_subpos):
                spos_select = F.softmax(emb[..., i * self.n_subpos:(i + 1) * self.n_subpos], dim=-1)
                _spos = torch.matmul(spos_select, self.spos[i])
                x = torch.cat([x, _spos], dim=-1)

        return x


class HSoftPOS(nn.Module):
    def __init__(self, vocab_size, embed_dim, n_layers=2, tcembr=None, tcconvr=None, tclength=2):
        super(HSoftPOS, self).__init__()

        assert tcembr is None or isinstance(tcembr, float)
        assert tcconvr is None or isinstance(tcconvr, float)

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.n_layers = n_layers
        self.tcembr = tcembr
        self.tcconvr = tcconvr
        self.tclength = tclength

        local_d = int(embed_dim / 2 / n_layers)
        embd_d = embed_dim - local_d * (2 * n_layers - 1)

        if tcembr is None:
            self.emb = EmbeddingLayer(vocab_size, embd_d)
        else:
            self.emb = TCEmbedding(vocab_size, embd_d, ratio=tcembr, tc_length=tclength)

        if tcconvr is None:
            conv1d = nn.Conv1d
        else:
            conv1d = lambda *args, **kwargs: TCConv1D(*args, **kwargs, ratio=tcconvr, tc_length=tclength)

        self.spos, self.convs = nn.ModuleList(), nn.ModuleList()
        for i in range(n_layers):
            self.spos.append(SoftPOS(local_d, n_subpos=local_d, repeat_subpos=1))
            if i < n_layers - 1:
                self.convs.append(conv1d(local_d, local_d * 3, padding=2 ** i, dilation=2 ** i))

    def forward(self, inputs):
        x = self.emb(inputs)
        xs = [x]
        for conv in self.convs:
            x = conv(x)
            xs.append(x)

        ys = []
        for x, spos in zip(xs, self.spos):
            y = spos(x)
            ys.append(y)

        x = torch.cat(ys, dim=-1)

        return x


def select_embedding_type(self, comments, inputs_vocab_size, target_vocab_size, d_model):
    if not 'tcemb' in comments:
        emb = lambda vocab, embd: EmbeddingLayer(vocab, embd)
    else:
        tclength = str2val(comments, 'tclength', int, default=3)
        tcr = str2val(comments, 'tcemb', float, default=.2)
        emb = lambda vocab, embd: TCEmbedding(vocab, embd, ratio=tcr, tc_length=tclength)

    if 'layerhspos' in comments:
        n = str2val(comments, 'layerhspos', output_type=int, default=3)

        tclength = str2val(comments, 'tclength', int, default=2)
        tcembr, tcconvr = None, None
        if 'tcemb' in comments:
            tcembr = str2val(comments, 'tcemb', float, default=.2)

        if 'tcconv' in comments:
            tcconvr = str2val(comments, 'tcconv', float, default=.2)

        self.encoder_embedding_layer = HSoftPOS(
            inputs_vocab_size, d_model, n_layers=n, tcembr=tcembr, tcconvr=tcconvr, tclength=tclength
        )
        self.decoder_embedding_layer = HSoftPOS(
            target_vocab_size, d_model, n_layers=n, tcembr=tcembr, tcconvr=tcconvr, tclength=tclength
        )
    else:
        self.encoder_embedding_layer = emb(inputs_vocab_size, d_model)
        self.decoder_embedding_layer = emb(inputs_vocab_size, d_model)
