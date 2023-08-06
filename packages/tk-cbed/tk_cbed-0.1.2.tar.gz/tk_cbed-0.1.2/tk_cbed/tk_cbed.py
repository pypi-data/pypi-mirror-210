"""
tk_cbed network suites designed to align and restore CBED data

Author: Ivan Lobato
Email: Ivanlh20@gmail.com
"""
import os
import pathlib
from typing import Tuple

import h5py
import numpy as np
import tensorflow as tf
from .model import fcn_fm_res_sqz_attm_u_net

import tensorflow as tf

def set_crop_shape(crop_shape):
    if crop_shape is None:
        return None

    if isinstance(crop_shape, int):
        return [crop_shape, crop_shape]
    
    if isinstance(crop_shape, (list, tuple)) and len(crop_shape) >= 2:
        return [crop_shape[0], crop_shape[1]]
    
def crop_image(x, crop_shape):
    shape = tf.shape(x)
    ix_0 = (shape[2]-crop_shape[1])//2
    ix_e = ix_0 + crop_shape[1]
    iy_0 = (shape[1]-crop_shape[0])//2
    iy_e = iy_0 + crop_shape[0]
    return x[:, iy_0:iy_e, ix_0:ix_e, :]

def fcn_get_mask(x):
    x = x - tf.reduce_min(x, axis=[1,2], keepdims=True)
    thr = 0.5*tf.math.reduce_max(x, axis=[1,2], keepdims=True)
    mk = tf.cast(x > thr, x.dtype)
    thr = 0.5*tf.math.reduce_sum(mk*x, axis=[1,2], keepdims=True)/tf.math.reduce_sum(mk, axis=[1,2], keepdims=True)
    x = tf.cast(x > thr, x.dtype)
    return x

def fcn_get_gs_kr_1d(sigma, filter_shape):
    sigma = tf.convert_to_tensor(sigma)
    x = tf.range(-filter_shape//2 + 1, filter_shape//2 + 1)
    x = tf.cast(tf.square(x), sigma.dtype)
    x = tf.nn.softmax(-x /(2.0*(sigma**2)))
    return x

def fcn_gs_conv_2d(x, sigma, filter_shape):
    channels = tf.shape(x)[3]
    sigma = tf.cast(sigma, x.dtype)
    gs_kr = fcn_get_gs_kr_1d(sigma, filter_shape)
    gs_kr_x = gs_kr[tf.newaxis, :]
    gs_kr_y = gs_kr[:, tf.newaxis]
    gs_kr_2d = gs_kr_x*gs_kr_y
    gs_kr_2d = gs_kr_2d[:, :, tf.newaxis, tf.newaxis]
    gs_kr_2d = tf.tile(gs_kr_2d, [1, 1, channels, 1])

    x = tf.nn.depthwise_conv2d(input=x, filter=gs_kr_2d, strides=(1, 1, 1, 1), padding="SAME")
    return x

def fcn_get_rx_ry(sh):
    nx = tf.cast(sh[2], tf.int32)
    ny = tf.cast(sh[1], tf.int32)
    nxh = nx//2
    nyh = ny//2
    ry = tf.range(-nyh, ny-nyh, 1.0, dtype=tf.float32)
    ry = tf.reshape(ry, [1, sh[1], 1, 1])
    rx = tf.range(-nxh, nx-nxh, 1.0, dtype=tf.float32)
    rx = tf.reshape(rx, [1, 1, sh[2], 1])
    return rx, ry

def fcn_get_dr(mk, rx, ry):
    dx = tf.math.reduce_sum(mk*rx, axis=[1, 2])
    dy = tf.math.reduce_sum(mk*ry, axis=[1, 2])
    dr = tf.concat([dx, dy], axis=-1)
    return dr

def fcn_nn_spl(x, dr):
    # zero padding
    x = tf.pad(x, [[0, 0], [1, 1], [1, 1], [0, 0]])
 
    sh = tf.shape(x)
    nb, ny, nx = sh[0], sh[1], sh[2]

    dr = tf.expand_dims(tf.cast(tf.round(dr), tf.int32), axis=1)
    dix, diy = tf.split(dr, 2, axis=-1)

     # get interpolation indices
    ix = tf.reshape(tf.range(nx, dtype=tf.int32), (1, 1, -1))
    iy = tf.reshape(tf.range(ny, dtype=tf.int32), (1, -1, 1))
    ix = tf.tile(tf.clip_by_value(ix + dix, 0, nx-1), (1, ny, 1))
    iy = tf.tile(tf.clip_by_value(iy + diy, 0, ny-1), (1, 1, nx))
 
    # nearest neighbor interpolation
    ib = tf.reshape(tf.range(nb, dtype=tf.int32), (-1, 1, 1))
    ib = tf.tile(ib, (1, ny, nx))
    ind = tf.stack([ib, iy, ix], 3)

    # remove zero padding
    ind = ind[:, 1:-1, 1:-1, :]

    # gather interpolated values
    return tf.gather_nd(x, ind)

class lay_conv_thr(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @tf.function
    def call(self, x):
        sh = tf.shape(x)

        # gaussian convolution to smooth data
        sx = fcn_gs_conv_2d(x, 3.0, 19)

        # get center
        mk = fcn_get_mask(sx)
        rx, ry = fcn_get_rx_ry(sh)
        mk = mk/tf.math.reduce_sum(mk, axis=[1,2], keepdims=True)
        dr = fcn_get_dr(mk, rx, ry)

        return dr

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)  

class lay_conv_thr_nni(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
  
    @tf.function
    def call(self, x, crop_shape=None):
        sh = tf.shape(x)

        # gaussian convolution to smooth data
        sx = fcn_gs_conv_2d(x, 3.0, 19)

        # get center
        mk = fcn_get_mask(sx)
        rx, ry = fcn_get_rx_ry(sh)
        mk = mk/tf.math.reduce_sum(mk, axis=[1,2], keepdims=True)
        dr = fcn_get_dr(mk, rx, ry)

        # resample x
        x = fcn_nn_spl(x, dr)

        if crop_shape:
            return crop_image(x, crop_shape)
        else:
            return x

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class lay_c_cbed_pp(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @tf.function
    def call(self, x):
        # find and apply scaling factor
        x_sc = tf.reduce_max(x, axis=[1,2], keepdims=True)
        x_sc = tf.maximum(0.001, x_sc)
        x = x/x_sc - 0.5
        return x

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class lay_c_cbed_out(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @tf.function
    def call(self, mk):
        sh = tf.shape(mk)
        m_00 = tf.maximum(0.001, tf.math.reduce_sum(mk, axis=[1, 2, 3], keepdims=False))
        rx, ry = fcn_get_rx_ry(sh)
        m_10 = tf.math.reduce_sum(rx*mk, axis = [1, 2, 3], keepdims=False)
        m_01 = tf.math.reduce_sum(ry*mk, axis = [1, 2, 3], keepdims=False)
        dr = tf.stack([m_10/m_00, m_01/m_00], axis=1)
        return dr

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class lay_c_cbed_nni_out(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @tf.function
    def call(self, x, mk, crop_shape=None):
        sh = tf.shape(mk)
        m_00 = tf.maximum(0.001, tf.math.reduce_sum(mk, axis=[1, 2, 3], keepdims=False))
        rx, ry = fcn_get_rx_ry(sh)
        m_10 = tf.math.reduce_sum(rx*mk, axis = [1, 2, 3], keepdims=False)
        m_01 = tf.math.reduce_sum(ry*mk, axis = [1, 2, 3], keepdims=False)
        dr = tf.stack([m_10/m_00, m_01/m_00], axis=1)

        # resample x
        x = fcn_nn_spl(x, dr)

        if crop_shape:
            return crop_image(x, crop_shape)
        else:
            return x

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)  

class lay_r_cbed_pp(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tf.function
    def call(self, x):
        # find and apply scaling factor
        x_sc = tf.math.reduce_max(x, axis=[1,2], keepdims=True)
        x_sc = tf.math.maximum(0.001, x_sc)
        x = x/x_sc - 0.5

        return x, x_sc

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
class lay_r_cbed_out(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tf.function
    def call(self, x, sc):
        return x*sc

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class lay_rc_cbed_pp_dr(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @tf.function
    def call(self, x, dr, crop_shape=None):
        # resample x
        x = fcn_nn_spl(x, dr)

        if crop_shape:
            x = crop_image(x, crop_shape)

        # find and apply scaling factor
        x_sc = tf.math.reduce_max(x, axis=[1,2], keepdims=True)
        x_sc = tf.math.maximum(0.001, x_sc)
        x = x/x_sc - 0.5

        return x, x_sc

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
class lay_rc_cbed_out(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tf.function
    def call(self, x, sc):
        return x*sc

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)    
    
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
def model_conv_thr():
    model_name = 'c_cbed_conv_thr'
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name=model_name + '_input', dtype='float32')
    x = lay_conv_thr(name = model_name + '_lay_out', trainable=False)(x_i)
    model = tf.keras.models.Model(inputs=x_i, outputs=x, name=model_name)
    model.trainable = False
    model.compile()
    return model

def model_conv_thr_nni(crop_shape=None):
    model_name = 'c_cbed_conv_thr'
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name = model_name + '_input', dtype='float32')
    x = lay_conv_thr_nni(name = model_name + '_lay_nni_out', trainable=False)(x_i, crop_shape)
    model = tf.keras.models.Model(inputs=x_i, outputs=x, name=model_name)
    model.trainable = False
    model.compile()
    return model

def net_c_cbed(x_i, ftrs_conv_o, model_name):
    act_str = 'relu'
    prefix_layer = model_name + '_'

    x = lay_c_cbed_pp(name = prefix_layer + 'lay_pp', trainable=False)(x_i)
    
    net_parm = {'ftr_enc': [16, 32, 48, 64, 80],
                'ftr_fm_res_sqz': [16, 24, 32, 40],
                'ftr_sqz_dconv': [40, 32, 24, 16],
                'ftr_attm': [32, 24, 16, 8],
                'mr_opt': False, 'mr_ftr': 16,
                'act_str': act_str, 'act_str_fst': None, 
                'act_str_last': 'sigmoid', 
                'act_str_dspl': act_str, 'act_str_uspl': act_str, 
                'act_str_add':'leaky_relu', 'act_str_attm': 'leaky_relu',
                'kn_sz':(3, 3), 'kn_sz_fst':(3, 3), 'kn_sz_last' :(3, 3),
                'kn_sz_dspl_fst':(4, 4), 'kn_sz_dspl':(3, 3),
                'kn_sz_uspl': (2, 2), 'kn_sz_uspl_last':(4, 4)
                }
    
    x = fcn_fm_res_sqz_attm_u_net(x, ftrs_conv_o, net_parm, prefix_layer)
  
    return x

def model_c_cbed():
    model_name = 'c_cbed'
    ftrs_conv_o = 1
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name=model_name + '_input', dtype='float32')
    x = net_c_cbed(x_i, ftrs_conv_o, model_name)
    x = lay_c_cbed_out(name=model_name + '_lay_out', trainable=False)(x)
    return tf.keras.models.Model(inputs=x_i, outputs=x, name=model_name)

def model_c_cbed_nni(crop_shape=None):
    model_name = 'c_cbed'
    ftrs_conv_o = 1    
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name=model_name + '_input', dtype='float32')
    x = net_c_cbed(x_i, ftrs_conv_o, model_name)
    x = lay_c_cbed_nni_out(name=model_name + '_lay_nni_out', trainable=False)(x_i, x, crop_shape)
    return tf.keras.models.Model(inputs=x_i, outputs=x, name=model_name + '_nni')

###############################################################################################################################################
def net_r_cbed(x_i, ftrs_conv_o, model_name):
    act_str = 'relu'
    prefix_layer = model_name + '_'
    
    x, x_sc = lay_r_cbed_pp(name = prefix_layer + 'lay_pp', trainable=False)(x_i)

    net_parm = {'ftr_enc': [64, 128, 256, 512, 1024],
                'ftr_fm_res_sqz': [32, 48, 64, 80],
                'ftr_sqz_dconv': [80, 64, 48, 32],
                'ftr_attm': [128, 64, 32, 16],
                'mr_opt': False, 'mr_ftr': 16,
                'act_str': act_str, 'act_str_fst': None, 
                'act_str_last': 'softplus', 
                'act_str_dspl': act_str, 'act_str_uspl': act_str, 
                'act_str_add':'leaky_relu', 'act_str_attm': 'leaky_relu',
                'kn_sz':(3, 3), 'kn_sz_fst':(3, 3), 'kn_sz_last' :(3, 3),
                'kn_sz_dspl_fst':(4, 4), 'kn_sz_dspl':(3, 3),
                'kn_sz_uspl': (2, 2), 'kn_sz_uspl_last':(4, 4)
                }
    
    x = fcn_fm_res_sqz_attm_u_net(x, ftrs_conv_o, net_parm, prefix_layer)

    x = lay_r_cbed_out(name=prefix_layer + 'lay_out')(x, x_sc)
    
    return x

def model_r_cbed():
    model_name = 'r_cbed'
    ftrs_conv_o = 1
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name=model_name + '_input', dtype='float32')
    x = net_r_cbed(x_i, ftrs_conv_o, model_name)
    return tf.keras.models.Model(inputs=x_i, outputs=x, name=model_name)

###############################################################################################################################################
def net_rc_cbed(x_i, ftrs_conv_o, model_name, crop_shape):
    act_str = 'relu'
    prefix_layer = model_name + '_'
    
    x = net_c_cbed(x_i, 1, 'c_cbed')
    dr = lay_c_cbed_out(name='c_cbed_lay_out', trainable=False)(x)
    x, x_sc = lay_rc_cbed_pp_dr(name = prefix_layer + 'lay_pp_dr', trainable=False)(x_i, dr, crop_shape)

    net_parm = {'ftr_enc': [64, 128, 256, 512, 1024],
                'ftr_fm_res_sqz': [32, 48, 64, 80],
                'ftr_sqz_dconv': [80, 64, 48, 32],
                'ftr_attm': [128, 64, 32, 16],
                'mr_opt': False, 'mr_ftr': 16,
                'act_str': act_str, 'act_str_fst': None, 
                'act_str_last': 'softplus', 
                'act_str_dspl': act_str, 'act_str_uspl': act_str, 
                'act_str_add':'leaky_relu', 'act_str_attm': 'leaky_relu',
                'kn_sz':(3, 3), 'kn_sz_fst':(3, 3), 'kn_sz_last' :(3, 3),
                'kn_sz_dspl_fst':(4, 4), 'kn_sz_dspl':(3, 3),
                'kn_sz_uspl': (2, 2), 'kn_sz_uspl_last':(4, 4)
                }
    
    x = fcn_fm_res_sqz_attm_u_net(x, ftrs_conv_o, net_parm, prefix_layer)

    x = lay_rc_cbed_out(name=prefix_layer + 'lay_out')(x, x_sc)
    
    return x

def model_rc_cbed(crop_shape=None):
    model_name = 'rc_cbed'
    ftrs_conv_o = 1
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name=model_name + '_input', dtype='float32')
    x = net_rc_cbed(x_i, ftrs_conv_o, model_name, crop_shape)
    return tf.keras.models.Model(inputs=x_i, outputs=x, name=model_name)

###############################################################################################################################################
def model_c_cbed_r(crop_shape=None):
    model_name = 'r_cbed'
    ftrs_conv_o = 1
    x_i = tf.keras.layers.Input(shape=(None, None, 1), name=model_name + '_input', dtype='float32')
    x = net_rc_cbed(x_i, ftrs_conv_o, model_name, crop_shape)
    return tf.keras.models.Model(inputs=x_i, outputs=x, name='c_cbed_r')

###############################################################################################################################################
# Our Unet reduces the size of the image by a factor of 2^4 = 16
# therefore, we need to pad the input image to be a multiple of 16
allow_sizes = 16*np.arange(2, 129, dtype=np.int32)

# The following functions are used to pad the input image to be a multiple of 16
def select_size(n):
    ind = np.argmin(np.abs(allow_sizes - n))
    if allow_sizes[ind] < n:
        return allow_sizes[ind+1]
    else:
        return allow_sizes[ind]

def expand_dimensions(x):
    if x.ndim == 2:
        return np.expand_dims(x, axis=(0, 3))
    elif x.ndim == 3 and x.shape[-1] != 1:
        return np.expand_dims(x, axis=3)
    else:
        return x

def add_extra_rows_or_columns(x):
    ny = select_size(x.shape[1])
    if ny > x.shape[1]:
        v_bg = np.zeros((x.shape[0], ny-x.shape[1], x.shape[2], x.shape[-1]), dtype=x.dtype)
        x = np.concatenate((x, v_bg), axis=1)

    nx = select_size(x.shape[2])
    if nx > x.shape[2]:
        v_bg = np.zeros((x.shape[0], x.shape[1], nx-x.shape[2], x.shape[-1]), dtype=x.dtype)
        x = np.concatenate((x, v_bg), axis=2)

    return x

def remove_extra_rows_or_columns(x, x_i_sh):
    if x_i_sh != x.shape:
        return x[:, :x_i_sh[1], :x_i_sh[2], :]
    else:
        return x

def remove_extra_rows_or_columns_symm(x, x_i_sh):
    if x_i_sh != x.shape:
        nxh = x_i_sh[2]//2 if x_i_sh[2] % 2 == 0 else (x_i_sh[2]-1)//2
        nyh = x_i_sh[1]//2 if x_i_sh[1] % 2 == 0 else (x_i_sh[1]-1)//2
        ix_0 = x.shape[1]//2-nxh
        iy_0 = x.shape[2]//2-nyh
        
        return x[:, ix_0:(ix_0+x.shape[1]), iy_0:(iy_0+x.shape[2]), :]
    else:
        return x

def adjust_output_dimensions(x, x_i_shape):
    ndim = len(x_i_shape)
    if ndim == 2:
        return x.squeeze()
    elif ndim == 3:
        if x_i_shape[-1] == 1:
            return x.squeeze(axis=0)
        else:
            return x.squeeze(axis=-1)  
    else:
        return x
    
###############################################################################################################################################
class C_CBED(tf.keras.Model):
    def __init__(self, model_path):
        super().__init__()
        self.base_model = model_c_cbed()
        self.base_model.load_weights(model_path)
        self.base_model.trainable = False
        self.base_model.compile()
        
    def call(self, inputs, training=None, mask=None):
        return self.base_model(inputs, training=training, mask=mask)
        
    def summary(self):
        return self.base_model.summary()
    
    def predict(self, x, batch_size=16, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False):
        # Expanding dimensions based on the input shape
        x = expand_dimensions(x)

        # Converting to float32 if necessary
        x = x.astype(np.float32)

        # Adding extra row or column if necessary
        x = add_extra_rows_or_columns(x)

        batch_size = min(batch_size, x.shape[0])

        # Model prediction
        x = self.base_model.predict(x, batch_size, verbose, steps, callbacks, max_queue_size, workers, use_multiprocessing)

        return x

class C_CBED_NNI(tf.keras.Model):
    def __init__(self, model_path, crop_shape=None):
        super().__init__()
        self.base_model = model_c_cbed_nni(crop_shape)
        model_path = model_path.with_name(model_path.stem.replace("c_cbed_nni", "c_cbed") + model_path.suffix)
        self.base_model.load_weights(model_path)
        self.base_model.trainable = False
        self.base_model.compile()
        
    def call(self, inputs, training=None, mask=None):
        return self.base_model(inputs, training=training, mask=mask)
        
    def summary(self):
        return self.base_model.summary()
    
    def predict(self, x, batch_size=16, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False):
        x_i_sh = x.shape

        # Expanding dimensions based on the input shape
        x = expand_dimensions(x)

        # Converting to float32 if necessary
        x = x.astype(np.float32)

        x_i_sh_e = x.shape

        # Adding extra row or column if necessary
        x = add_extra_rows_or_columns(x)

        batch_size = min(batch_size, x.shape[0])

        # Model prediction
        x = self.base_model.predict(x, batch_size, verbose, steps, callbacks, max_queue_size, workers, use_multiprocessing)

        # Removing extra row or column if added
        x = remove_extra_rows_or_columns(x, x_i_sh_e)

        # Adjusting output dimensions to match input dimensions
        return adjust_output_dimensions(x, x_i_sh)

class C_CBED_R(tf.keras.Model):
    def __init__(self, model_path, crop_shape=None):
        super().__init__()
        self.base_model = model_c_cbed_r(crop_shape)
        model_path_c_cbed = model_path.with_name(model_path.stem.replace("c_cbed_r", "c_cbed") + model_path.suffix)
        self.base_model.load_weights(model_path_c_cbed, by_name=True, skip_mismatch=False)
        model_path_r_cbed = model_path.with_name(model_path.stem.replace("c_cbed_r", "r_cbed") + model_path.suffix)
        self.base_model.load_weights(model_path_r_cbed, by_name=True, skip_mismatch=False)
        self.base_model.trainable = False
        self.base_model.compile()
        
    def call(self, inputs, training=None, mask=None):
        return self.base_model(inputs, training=training, mask=mask)
        
    def summary(self):
        return self.base_model.summary()
    
    def predict(self, x, batch_size=16, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False):
        x_i_sh = x.shape

        # Expanding dimensions based on the input shape
        x = expand_dimensions(x)

        # Converting to float32 if necessary
        x = x.astype(np.float32)

        x_i_sh_e = x.shape

        # Adding extra row or column if necessary
        x = add_extra_rows_or_columns(x)

        batch_size = min(batch_size, x.shape[0])

        # Model prediction
        x = self.base_model.predict(x, batch_size, verbose, steps, callbacks, max_queue_size, workers, use_multiprocessing)

        # Removing extra row or column if added
        x = remove_extra_rows_or_columns(x, x_i_sh_e)

        # Adjusting output dimensions to match input dimensions
        return adjust_output_dimensions(x, x_i_sh)

class R_CBED(tf.keras.Model):
    def __init__(self, model_path):
        super().__init__()
        self.base_model = model_r_cbed()
        self.base_model.load_weights(model_path)
        self.base_model.trainable = False
        self.base_model.compile()
        
    def call(self, inputs, training=None, mask=None):
        return self.base_model(inputs, training=training, mask=mask)
        
    def summary(self):
        return self.base_model.summary()
    
    def predict(self, x, batch_size=16, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False):
        x_i_sh = x.shape

        # Expanding dimensions based on the input shape
        x = expand_dimensions(x)

        # Converting to float32 if necessary
        x = x.astype(np.float32)

        x_i_sh_e = x.shape

        # Adding extra row or column if necessary
        x = add_extra_rows_or_columns(x)

        batch_size = min(batch_size, x.shape[0])

        # Model prediction
        x = self.base_model.predict(x, batch_size, verbose, steps, callbacks, max_queue_size, workers, use_multiprocessing)

        # Removing extra row or column if added
        x = remove_extra_rows_or_columns(x, x_i_sh_e)

        # Adjusting output dimensions to match input dimensions
        return adjust_output_dimensions(x, x_i_sh)

class RC_CBED(tf.keras.Model):
    def __init__(self, model_path, crop_shape=None):
        super().__init__()
        self.crop_shape = crop_shape
        self.base_model = model_rc_cbed(self.crop_shape)
        self.base_model.load_weights(model_path)
        self.base_model.trainable = False
        self.base_model.compile()
        
    def call(self, inputs, training=None, mask=None):
        return self.base_model(inputs, training=training, mask=mask)
        
    def summary(self):
        return self.base_model.summary()
    
    def predict(self, x, batch_size=16, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False):
        x_i_sh = x.shape

        # Expanding dimensions based on the input shape
        x = expand_dimensions(x)

        # Converting to float32 if necessary
        x = x.astype(np.float32)

        x_i_sh_e = x.shape

        # Adding extra row or column if necessary
        x = add_extra_rows_or_columns(x)

        batch_size = min(batch_size, x.shape[0])

        # Model prediction
        x = self.base_model.predict(x, batch_size, verbose, steps, callbacks, max_queue_size, workers, use_multiprocessing)

        # Removing extra row or column if added
        x = remove_extra_rows_or_columns_symm(x, x_i_sh_e)

        # Adjusting output dimensions to match input dimensions
        return adjust_output_dimensions(x, x_i_sh)

def load_network(model_name: str = 'rc_cbed', crop_shape=None):
    """
    Load one of the tk_cbed neural network models.

    :param model_name: A string representing the name of the model.
    :return: A tensorflow.keras.Model object.
    """
    crop_shape = set_crop_shape(crop_shape)
    hdf5 = True
    model_name = model_name.lower()
    
    if os.path.isdir(model_name):
        model_path = pathlib.Path(model_name).resolve()
    else: 
        model_name = model_name.lower()
        model_file_name = model_name + '.h5' if hdf5 else model_name
        model_path = pathlib.Path(__file__).resolve().parent / 'models' / model_file_name

    if 'c_cbed' == model_name:
        model = C_CBED(model_path)
    elif 'c_cbed_nni' == model_name:
        model = C_CBED_NNI(model_path, crop_shape)
    elif 'c_cbed_r' == model_name:
        model = C_CBED_R(model_path, crop_shape)
    elif 'c_cbed_conv_thr' == model_name:
        model = model_conv_thr()
    elif 'c_cbed_conv_thr_nni' == model_name:
        model = model_conv_thr_nni(crop_shape)
    elif 'rc_cbed' == model_name:
        model = RC_CBED(model_path, crop_shape)
    elif 'r_cbed' == model_name:
        model = R_CBED(model_path)
    else:
        raise ValueError('Unknown model type.')

    return model

def load_sim_test_data(file_name: str = 'rc_cbed') -> Tuple[np.ndarray, np.ndarray]:
    """
    Load test data for r_em neural network.

    :param model_name: A string representing the name of the model.
    :return: A tuple containing two numpy arrays representing the input (x) and output (y) data.
    """
    if os.path.isfile(file_name):
        path = pathlib.Path(file_name).resolve()
    else:
        file_name = file_name.lower()
        path = pathlib.Path(__file__).resolve().parent / 'test_data' / 'cbed.h5'

    with h5py.File(path, 'r') as h5file:
        x = np.asarray(h5file['x'][:], dtype=np.float32).transpose(0, 3, 2, 1)
        
        if (file_name == 'c_cbed') or (file_name == 'c_cbed_conv_thr'):
            y = np.asarray(h5file['y_dr'][:], dtype=np.float32)
        else:
            y = np.asarray(h5file['y'][:], dtype=np.float32).transpose(0, 3, 2, 1)
            y = y[..., 0] if 'r_cbed' == file_name else y[..., 1]
            y = y[..., np.newaxis]  
              
    return x, y

def load_exp_test_data(file_name: str = 'exp_hrstem') -> Tuple[np.ndarray, np.ndarray]:
    """
    Load test data for r_em neural network.

    :param model_name: A string representing the name of the model.
    :return: A tuple containing two numpy arrays representing the input (x) and output (y) data.
    """

    if os.path.isfile(file_name):
        path = pathlib.Path(file_name).resolve()
    else:
        file_name = file_name.lower()
        path = pathlib.Path(__file__).resolve().parent / 'test_data' / f'{file_name}.h5'

    with h5py.File(path, 'r') as f:
        x = f['x'][:]
        if x.ndim == 4:
            x = np.asarray(x, dtype=np.float32).transpose(0, 3, 2, 1)
        else:
            x = np.asarray(x, dtype=np.float32).transpose(1, 0)
    
    return x