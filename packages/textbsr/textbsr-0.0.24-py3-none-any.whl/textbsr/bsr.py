
import torch
from torch.hub import download_url_to_file, get_dir
from utils import utils_image as util
from models.TextEnhancement import TextRestoration as TextRestoration
import cv2 
import numpy as np
import os.path
import torch.nn.functional as F
import time
import argparse
import os.path as osp
from urllib.parse import urlparse

pretrain_model_url = {
    'x4': 'https://github.com/macuper/tmppp/releases/download/v1/bsrgan_text.pth',
}

def load_file_from_url(url, model_dir=None, progress=True, file_name=None):
    if model_dir is None:  # use the pytorch hub_dir
        hub_dir = get_dir()
        model_dir = os.path.join(hub_dir, 'checkpoints')

    os.makedirs(model_dir, exist_ok=True)

    parts = urlparse(url)
    filename = os.path.basename(parts.path)
    if file_name is not None:
        filename = file_name
    cached_file = os.path.abspath(os.path.join(model_dir, filename))
    if not os.path.exists(cached_file):
        print(f'Downloading: "{url}" to {cached_file}\n')
        download_url_to_file(url, cached_file, hash_prefix=None, progress=progress)
    return cached_file

def bsr(test_path=None, sr_path=None, save_path=None, is_aligned=False, save_text=False):
    if test_path is None:
        exit('input image path is none. Please see our document')
    if save_path is None:
        TIMESTAMP = time.strftime("%m-%d_%H-%M", time.localtime())
        save_path = osp.join(test_path+'_'+TIMESTAMP+'_BSRGAN-Text')
    os.makedirs(save_path, exist_ok=True)

    
    lq_imgs = []
    sq_imgs = []
    lq_imgs = util.get_image_paths(test_path)
    if len(lq_imgs) ==0:
        exit('No Image in the LR path.')
    if sr_path is not None:
        sq_imgs = util.get_image_paths(sr_path)
        if len(sq_imgs) != len(lq_imgs):
            exit('The LQ path has {} images, while the SR path has {} ones. Please check whether the two paths are consistent.'.format(lr_num, sr_num))

    #print('#'*64)
    

    scale_factor = 4 # upsample scale factor for the final output, fixed

    use_cuda = torch.cuda.is_available()
    device = torch.device('cuda' if use_cuda else 'cpu')
    weight_path = load_file_from_url(pretrain_model_url['x4'])
    TextModel = TextRestoration(ModelName='RRDB', TextModelPath=weight_path, device=device)

    print('{:>25s} : {:s}'.format('Model Name', 'BSRGAN'))
    if use_cuda:
        print('{:>25s} : {:<d}'.format('GPU ID', torch.cuda.current_device()))
    else:
        print('{:>25s} : {:s}'.format('GPU ID', 'No GPU is available. Use CPU instead.'))
    torch.cuda.empty_cache()

    #print('################################## Handling {:s} ##################################'.format(test_path))
    L_path = test_path
    E_path = save_path # save path
    print('{:>25s} : {:s}'.format('Input Path', L_path))
    print('{:>25s} : {:s}'.format('Output Path', E_path))
    print('{:>25s} : {:s}'.format('Background SR Path', sr_path if sr_path else 'None'))
    if is_aligned:
        print('{:>25s} : {:s}'.format('Image Details', 'Aligned Text Layout. No text detection is used.'))
    else:
        print('{:>25s} : {:s}'.format('Image Details', 'UnAligned Text Image. It will crop text region using CnSTD, restore, and paste results back.'))
    print('{:>25s} : {:s}'.format('Save LR & SR text layout', 'True' if save_text else 'False'))



    idx = 0

    
    for img in lq_imgs:
        ####################################
        #####(1) Read Image
        ####################################
        idx += 1
        img_name, ext = os.path.splitext(os.path.basename(img))
        print('{:>20s} {:04d} : x{:<d} --> {:<s}'.format('Restoring ', idx, scale_factor, img_name+ext))

        img_L = util.imread_uint(img, n_channels=3) #RGB 0~255
        width_L = img_L.shape[1]
        height_L = img_L.shape[0]

        width_S, height_S = 0, 0
        

        if len(sq_imgs) > 0:
            sq_img = sq_imgs[idx-1]
            img_E = util.imread_uint(sq_img, n_channels=3)
            width_S = img_E.shape[1]
            height_S = img_E.shape[0]

        else:
            img_E = img_L
        img_E = cv2.resize(img_E, (width_L*scale_factor, height_L*scale_factor), interpolation = cv2.INTER_AREA)
        
        
        ####################################
        #####(2) Restore Each Region and Paste to the whole image
        ####################################
        SQ, ori_texts, en_texts  = TextModel.handle_texts(img=img_L, bg=img_E, sf=scale_factor, is_aligned=is_aligned)
        if not is_aligned:
            if width_S == 0 or height_S == 0:
                width_S = (width_L * scale_factor)
                height_S = (height_L * scale_factor)
            SQ = cv2.resize(SQ.astype(np.float32), (width_S, height_S), interpolation=cv2.INTER_AREA)
            cv2.imwrite(os.path.join(E_path, img_name +'_BSRGANText.png'), SQ[:,:,::-1])
        else:
            cv2.imwrite(os.path.join(E_path, img_name +'_BSRGANText.png'), en_texts[0])
        ####################################
        #####(3) Save Cropped Results
        ####################################
        if save_text and not is_aligned:
            for m, (et, ot) in enumerate(zip(en_texts, ori_texts)): ##save each face region
                w, h, c = et.shape
                ot = cv2.resize(ot, (h, w))
                cv2.imwrite(os.path.join(E_path, img_name +'_patch_{}.png'.format(m)), np.hstack((ot, et)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--test_path', type=str, default='./testsets/LQ', help='the lr image path')
    parser.add_argument('-b', '--sr_path', type=str, default=None, help='the background sr path, default:None')
    parser.add_argument('-o', '--save_path', type=str, default=None, help='the text sr save path')
    parser.add_argument('-a', '--aligned', action='store_true', help='whether the input contains only text region, default:False')
    parser.add_argument('-p', '--save_text', action='store_true', help='whether save the LR and SR text layout, default:False')
    args = parser.parse_args()

    bsr(args.test_path, args.sr_path, args.save_path, args.aligned, args.save_text)