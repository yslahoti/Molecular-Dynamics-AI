import MDAnalysis as mda
from MDAnalysis.lib.formats.libdcd import DCDFile
import tensorflow.compat.v1 as tf
import numpy as np
from learning_to_simulate import reading_utils
import functools


tf.enable_eager_execution()

def normalize(l, nmin, nmax, omin, omax):
    OldRange = (omax - omin)
    NewRange = (nmax - nmin)
    l = (((l - omin) * NewRange) / OldRange) + nmin
    return l

def getDataPlot(i, split):
    u = mda.Universe('datasets/solvate.pdb',
                     'datasets/' + split + '/wat' + str(i) +
                     '/wat' + str(i) +'_out.dcd')
    p = u.atoms.positions
#Not sure if this is right normalization factor
    p = normalize(p, .2, .8, 0, 30)
    t = u.atoms.types
    return t, p

def getDataFrames(i, split):
    u = mda.Universe('datasets/solvate.pdb',
                     'datasets/' + split + '/wat' + str(i) +
                     '/wat' + str(i) +'_out.dcd')
    t = u.atoms.types
    t[t == "O"] = 0
    t[t == "H"] = 3
    t = np.asarray(t).astype('int32')

    l = []
    with DCDFile('datasets/' + split + '/wat' + str(i) +
                 '/wat' + str(i) +'_out.dcd') as f:
        for frame in f:
            ff = frame.xyz
            ff = normalize(ff, .2, .8, 0, 30)
            l.append(ff)
    return t,l

def make_dict_tensor(t,p):
    t_tensor = tf.convert_to_tensor(t)
    p_tensor = tf.convert_to_tensor(np.asarray(p))

    type_dict = {
      "particle_type": t_tensor,
#      "key": tf.convert_to_tensor(0),
    }
    pos_dict = {
      "position": p_tensor
    }
    return type_dict, pos_dict

# making TF dataset

def getDs1(num):
    model_input_features = {}
    pos_stack = []
    global_stack = []
    for i in range(1,num+1):
        t, p = getDataFrames(i)
        x, y = make_dict_tensor(t, p)
        global_stack.append(x['particle_type'])
        pos_stack.append(y['position'])

    model_input_features['particle_type'] = tf.stack(global_stack)
    model_input_features['position'] = tf.stack(pos_stack)

    return tf.data.Dataset.from_tensor_slices(model_input_features)




# #import train
# def getDs2(num, mode, split):
#     if ("one_step" in mode):
#         t,p = getDataFrames(1, split)
#         x,y = make_dict_tensor(t,p)
#         s = reading_utils.split_trajectory(x,y)
#         print(1)
#         for i in range(2,num+1):
#             print(i)
#             t,p = getDataFrames(i, split)
#             x,y = make_dict_tensor(t,p)
#             temp = reading_utils.split_trajectory(x,y)
#             s = s.concatenate(temp)
#         s = s.map(train
#                   .prepare_inputs)
#         if ("train" in mode):
#             s = s.repeat()
#             s = s.shuffle(512)
#         ds = batch_concat(ds, batch_size)
#         return s
#     elif (mode == "rollout"):
#         t,p = getDataFrames(1)
#         x,y = make_dict_tensor(t,p)
#         print(1)
#         s = train.prepare_rollout_inputs(x,y)
#         return s







def getDictConcat(num):
    t,p = getDataFrames(1)
    x,y = make_dict_tensor(t,p)
    print(1)
    for i in range(2,num+1):
        print(i)
        t,p = getDataFrames(i)
        t1,t2 = make_dict_tensor(t,p)
        x = {**t1, **x}
        y = {**t2, **y}
    return x,y












# for example in all_dat:
#     print(type(example))
#     print(len(example))
#     for key, value in example[1].items():
#         print(key)
#         print(value)
#
# #ds = tf.data.Dataset.from_tensor_slices(all_dat)
#
# tf.data.Dataset.from.



