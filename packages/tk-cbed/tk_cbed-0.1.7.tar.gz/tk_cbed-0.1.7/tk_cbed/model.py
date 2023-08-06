"""
tk_cbed network suites designed to align and restore CBED data

Author: Ivan Lobato
Email: Ivanlh20@gmail.com
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, Concatenate, Add, Multiply, Activation

#########################################################################################
#########################################################################################
#########################################################################################
def fcn_fm_conv_bkl(x, ftr_squeeze, krn_sz_squeeze, stri_squeeze, act_str_squeeze, ftr_expand, krn_sz_expand, act_str_expand, use_bi, pad, name):
    name_squeeze = name + "_squeeze_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_squeeze, krn_sz_squeeze[0], krn_sz_squeeze[1], 1, 1)
    name_expand_left = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, 1, 1, 1, 1)
    name_expand_right = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, krn_sz_expand[0], krn_sz_expand[1], 1, 1)

    x = Conv2D(ftr_squeeze, kernel_size=krn_sz_squeeze, strides=stri_squeeze, activation=act_str_squeeze, use_bias=use_bi, padding=pad, name=name_squeeze)(x)
    x_left = Conv2D(ftr_expand//2, kernel_size=(1, 1), strides=(1, 1), activation=act_str_expand, use_bias=use_bi, padding=pad, name=name_expand_left)(x)
    x_right = Conv2D(ftr_expand//2, kernel_size=krn_sz_expand, strides=(1, 1), activation=act_str_expand, use_bias=use_bi, padding=pad, name=name_expand_right)(x)

    x = Concatenate(axis=-1, name=name + '_concat')([x_left, x_right])
    return x

def fcn_fm_dconv_bkl(x, ftr_squeeze, krn_sz_squeeze, stri_squeeze, act_str_squeeze, ftr_expand, krn_sz_expand, act_str_expand, use_bi, pad, name):
    name_squeeze = name + "_squeeze_{:d}_{:d}x{:d}_{:d}x{:d}_dconv".format(ftr_squeeze, krn_sz_squeeze[0], krn_sz_squeeze[1], 1, 1)
    name_expand_left = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, 1, 1, 1, 1)
    name_expand_right = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, krn_sz_expand[0], krn_sz_expand[1], 1, 1)

    x = Conv2DTranspose(ftr_squeeze, kernel_size=krn_sz_squeeze, strides=stri_squeeze, activation=act_str_squeeze, use_bias=use_bi, padding=pad, name=name_squeeze)(x)
    x_left = Conv2D(ftr_expand//2, kernel_size=(1, 1), strides=(1, 1), activation=act_str_expand, use_bias=use_bi, padding=pad, name=name_expand_left)(x)
    x_right = Conv2D(ftr_expand//2, kernel_size=krn_sz_expand, strides=(1, 1), activation=act_str_expand, use_bias=use_bi, padding=pad, name=name_expand_right)(x)

    x = Concatenate(axis=-1, name=name + '_concat')([x_left, x_right])
    return x

def fcn_sqz_conv_bkl(x, ftr_squeeze, krn_sz_squeeze, stri_squeeze, act_str_squeeze, ftr_expand, krn_sz_expand, act_str_expand, use_bi, pad, name):
    name_squeeze = name + "_squeeze_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_squeeze, krn_sz_squeeze[0], krn_sz_squeeze[1], 1, 1)
    name_expand = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, krn_sz_expand[0], krn_sz_expand[1], 1, 1)

    x = Conv2D(ftr_squeeze, kernel_size=krn_sz_squeeze, strides=stri_squeeze, activation=act_str_squeeze, use_bias=use_bi, padding=pad, name=name_squeeze)(x)
    x = Conv2D(ftr_expand, kernel_size=krn_sz_expand, strides=(1, 1), activation=act_str_expand, use_bias=use_bi, padding=pad, name=name_expand)(x)

    return x

def fcn_res_sqz_conv_bkl(x, ftr_squeeze, krn_sz_squeeze, act_str_squeeze, ftr_expand, krn_sz_expand, act_str_add, use_bi, pad, name):
    name_squeeze = name + "_squeeze_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_squeeze, krn_sz_squeeze[0], krn_sz_squeeze[1], 1, 1)
    name_expand = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, krn_sz_expand[0], krn_sz_expand[1], 1, 1)

    x_sk = Conv2D(ftr_squeeze, kernel_size=krn_sz_squeeze, strides=(1, 1), activation=act_str_squeeze, use_bias=use_bi, padding=pad, name=name_squeeze)(x)
    x_sk = Conv2D(ftr_expand, kernel_size=krn_sz_expand, strides=(1, 1), activation=None, use_bias=use_bi, padding=pad, name=name_expand)(x_sk)
    x = Add(name=name + '_add')([x, x_sk])
    x = Activation(act_str_add, name = name + '_' + act_str_add)(x)
 
    return x

def fcn_sqz_dconv_bkl(x, ftr_squeeze, krn_sz_squeeze, stri_squeeze, act_str_squeeze, ftr_expand, krn_sz_expand, act_str_expand, use_bi, pad, name):
    name_squeeze = name + "_squeeze_{:d}_{:d}x{:d}_{:d}x{:d}_dconv".format(ftr_squeeze, krn_sz_squeeze[0], krn_sz_squeeze[1], 1, 1)
    name_expand = name + "_expand_{:d}_{:d}x{:d}_{:d}x{:d}_conv".format(ftr_expand, krn_sz_expand[0], krn_sz_expand[1], 1, 1)

    x = Conv2DTranspose(ftr_squeeze, kernel_size=krn_sz_squeeze, strides=stri_squeeze, activation=act_str_squeeze, use_bias=use_bi, padding=pad, name=name_squeeze)(x)
    x = Conv2D(ftr_expand, kernel_size=krn_sz_expand, strides=(1, 1), activation=act_str_expand, use_bias=use_bi, padding=pad, name=name_expand)(x)

    return x

def fcn_attm_bkl(x, x_sk, ftr, act_str_add, use_bi, pad, name):
    x_t = Conv2D(ftr, kernel_size=(1, 1), strides=(1, 1), activation=None, use_bias=use_bi, padding=pad, name=name + '_left_1x1_conv')(x)
    x_sk_t = Conv2D(ftr, kernel_size=(1, 1), strides=(1, 1), activation=None, use_bias=use_bi, padding=pad, name=name + '_right_1x1_conv')(x_sk)
    x_a = Add(name=name + '_add')([x_t, x_sk_t])
    x_a = Activation(act_str_add, name = name + '_' + act_str_add)(x_a)
    x_a = Conv2D(1, kernel_size=(1, 1), strides=(1, 1), activation='sigmoid', use_bias=use_bi, padding=pad, name=name + '_map_1x1x1_conv')(x_a)
    x = Multiply(name=name + '_mul')([x_a, x_sk])
    return x

def fcn_fm_res_sqz_attm_u_net(x, ftrs_o, net_parm, name):
    use_bi = True

    ftr_enc = net_parm['ftr_enc']
    ftr_fm_res_sqz = net_parm['ftr_fm_res_sqz']
    ftr_sqz_dconv = net_parm['ftr_sqz_dconv']
    ftr_attm = net_parm['ftr_attm']

    act_str = net_parm['act_str']
    act_str_fst = net_parm['act_str_fst']
    act_str_last = net_parm['act_str_last']
    
    act_str_dspl = net_parm['act_str_dspl']
    act_str_uspl = net_parm['act_str_uspl']
    
    act_str_add = net_parm['act_str_add']
    act_str_attm = net_parm['act_str_attm']

    kn_sz = net_parm['kn_sz']
    kn_sz_fst = net_parm['kn_sz_fst']
    kn_sz_last = net_parm['kn_sz_last']
    
    kn_sz_dspl_fst = net_parm['kn_sz_dspl_fst']
    kn_sz_dspl = net_parm['kn_sz_dspl']

    kn_sz_uspl = net_parm['kn_sz_uspl']
    kn_sz_uspl_last = net_parm['kn_sz_uspl_last']

    stri_dspl = (2, 2)
    stri_uspl = (2, 2)

    ###############################################################################################################################################
    x_e_256 = Conv2D(ftr_enc[0], kernel_size=kn_sz_fst, strides=(1, 1), activation=act_str_fst, use_bias=True, padding='same', name=name + 'dsm_1_conv_1_{:d}x{:d}_conv'.format(kn_sz_fst[0], kn_sz_fst[1]))(x)
    x_e_256 = Conv2D(ftr_enc[0], kernel_size=kn_sz, strides=(1, 1), activation=act_str, use_bias=use_bi, padding='same', name=name + 'dsm_1_conv_2_{:d}x{:d}_conv'.format(kn_sz[0], kn_sz[1]))(x_e_256)

    ###############################################################################################################################################
    x_e_128 = fcn_fm_conv_bkl(x_e_256, ftr_fm_res_sqz[0], kn_sz_dspl_fst, stri_dspl, act_str_dspl, ftr_enc[1], kn_sz, act_str, use_bi, 'same', name + 'dsm_1_fmc_1')
    x_e_128 = fcn_res_sqz_conv_bkl(x_e_128, ftr_fm_res_sqz[0], kn_sz, act_str, ftr_enc[1], kn_sz, act_str_add, use_bi, 'same', name + 'dsm_1_rsc_1')                  # 128

    x_e_64 = fcn_fm_conv_bkl(x_e_128, ftr_fm_res_sqz[1], kn_sz_dspl, stri_dspl, act_str_dspl, ftr_enc[2], kn_sz, act_str, use_bi, 'same', name + 'dsm_2_fmc_1')
    x_e_64 = fcn_res_sqz_conv_bkl(x_e_64, ftr_fm_res_sqz[1], kn_sz, act_str, ftr_enc[2], kn_sz, act_str_add, use_bi, 'same', name + 'dsm_2_rsc_2')                    # 64

    x_e_32 = fcn_fm_conv_bkl(x_e_64, ftr_fm_res_sqz[2], kn_sz_dspl, stri_dspl, act_str_dspl, ftr_enc[3], kn_sz, act_str, use_bi, 'same', name + 'dsm_3_fmc_1')
    x_e_32 = fcn_res_sqz_conv_bkl(x_e_32, ftr_fm_res_sqz[2], kn_sz, act_str, ftr_enc[3], kn_sz, act_str_add, use_bi, 'same', name + 'dsm_3_rsc_2')                    # 32

    ###############################################################################################################################################    
    x_e_16 = fcn_fm_conv_bkl(x_e_32, ftr_fm_res_sqz[3], kn_sz_dspl, stri_dspl, act_str_dspl, ftr_enc[4], kn_sz, act_str, use_bi, 'same', name + 'dsm_4_fmc_1')
    x_d_16 = fcn_res_sqz_conv_bkl(x_e_16, ftr_fm_res_sqz[3], kn_sz, act_str, ftr_enc[4], kn_sz, act_str_add, use_bi, 'same', name + 'dsm_4_rsc_2')                    # 16

    ###############################################################################################################################################
    x_d_32 = fcn_sqz_dconv_bkl(x_d_16, ftr_sqz_dconv[0], kn_sz_uspl, stri_uspl, act_str_uspl, ftr_enc[3], kn_sz, act_str, use_bi, 'same', name + 'usm_1_sdc_1')
    x_e_32 = fcn_attm_bkl(x_d_32, x_e_32, ftr_attm[0], act_str_attm, use_bi, 'same', name + 'usm_1_attm_1')
    x_d_32 = Concatenate(axis=3, name=name + 'usm_1_concat_1')([x_e_32, x_d_32])
    x_d_32 = fcn_fm_conv_bkl(x_d_32, ftr_fm_res_sqz[2], kn_sz, (1, 1), act_str, ftr_enc[3], kn_sz, act_str, use_bi, 'same', name + 'usm_1_fmc_1')
    x_d_32 = fcn_res_sqz_conv_bkl(x_d_32, ftr_fm_res_sqz[2], kn_sz, act_str, ftr_enc[3], kn_sz, act_str_add, use_bi, 'same', name + 'usm_1_rsc_1')                    # 32

    ###############################################################################################################################################
    x_d_64 = fcn_sqz_dconv_bkl(x_d_32, ftr_sqz_dconv[1], kn_sz_uspl, stri_uspl, act_str_uspl, ftr_enc[2], kn_sz, act_str, use_bi, 'same', name + 'usm_2_sdc_1')
    x_e_64 = fcn_attm_bkl(x_d_64, x_e_64, ftr_attm[1], act_str_attm, use_bi, 'same', name + 'usm_2_attm_1')
    x_d_64 = Concatenate(axis=3, name=name + 'usm_2_concat_1')([x_e_64, x_d_64])
    x_d_64 = fcn_fm_conv_bkl(x_d_64, ftr_fm_res_sqz[1], kn_sz, (1, 1), act_str, ftr_enc[2], kn_sz, act_str, use_bi, 'same', name + 'usm_2_fmc_1')
    x_d_64 = fcn_res_sqz_conv_bkl(x_d_64, ftr_fm_res_sqz[1], kn_sz, act_str, ftr_enc[2], kn_sz, act_str_add, use_bi, 'same', name + 'usm_2_rsc_1')                    # 64

    ###############################################################################################################################################
    x_d_128 = fcn_sqz_dconv_bkl(x_d_64, ftr_sqz_dconv[2], kn_sz_uspl, stri_uspl, act_str_uspl, ftr_enc[1], kn_sz, act_str, use_bi, 'same', name + 'usm_3_sdc_1')
    x_e_128 = fcn_attm_bkl(x_d_128, x_e_128, ftr_attm[2], act_str_attm, use_bi, 'same', name + 'usm_3_attm_1')
    x_d_128 = tf.keras.layers.Concatenate(axis=3, name=name + 'usm_3_concat_1')([x_e_128, x_d_128])
    x_d_128 = fcn_fm_conv_bkl(x_d_128, ftr_fm_res_sqz[0], kn_sz, (1, 1), act_str, ftr_enc[1], kn_sz, act_str, use_bi, 'same', name + 'usm_3_fmc_1')
    x_d_128 = fcn_res_sqz_conv_bkl(x_d_128, ftr_fm_res_sqz[0], kn_sz, act_str, ftr_enc[1], kn_sz, act_str_add, use_bi, 'same', name + 'usm_3_rsc_1')                  # 128

    ###############################################################################################################################################
    x_d_256 = fcn_sqz_dconv_bkl(x_d_128, ftr_sqz_dconv[3], kn_sz_uspl_last, stri_uspl, act_str_uspl, ftr_enc[0], kn_sz, act_str, use_bi, 'same', name + 'usm_4_sdc_1')
    x_e_256 = fcn_attm_bkl(x_d_256, x_e_256, ftr_attm[3], act_str_attm, use_bi, 'same', name + 'usm_4_attm_1')
    x_d_256 = Concatenate(axis=3, name= name + 'usm_4_concat_1')([x_e_256, x_d_256])
    x_d_256 = Conv2D(ftr_enc[0], kernel_size=kn_sz, strides=(1, 1), activation=act_str, use_bias=use_bi, padding='same', name=name + 'usm_4_conv_1_{:d}x{:d}_conv'.format(kn_sz[0], kn_sz[1]))(x_d_256)
    y_256 = Conv2D(ftr_enc[0], kernel_size=kn_sz, strides=(1, 1), activation=act_str, use_bias=use_bi, padding='same', name=name + 'usm_4_conv_2_y_256_{:d}x{:d}_conv'.format(kn_sz[0], kn_sz[1]))(x_d_256)
    y_256 = Conv2D(ftrs_o, kernel_size=kn_sz_last, strides=(1, 1), activation=act_str_last, use_bias=True, padding='same', name=name + 'y_256_{:d}x{:d}_conv'.format(kn_sz_last[0], kn_sz_last[1]))(y_256)   # 256
    
    return y_256