
import torch
from utils import utils_image as util
from models.TextEnhancement import TextRestoration as TextRestoration
import cv2 
import numpy as np
import os.path
import torch.nn.functional as F
import time
import argparse
import os.path as osp

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

def main(test_path, save_path, is_aligned):
    #################################################
    ############### parameter settings ##############
    #################################################
    testsets = './testsets/'# set path of testsets
    testset_Ls = ['LQs']#['whole', 'blurry_faces'] # set path of each sub-set
    
    #################################################
    scale_factor = 4 # upsample scale factor for the final output, fixed
    SaveText = True

    t = time.strftime("%m-%d_%H-%M", time.localtime()) 

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    weight_path = load_file_from_url(pretrain_model_url['x4'])
    TextModel = TextRestoration(ModelName='RRDB', TextModelPath=weight_path, device=device)

    print('{:>16s} : {:s}'.format('Model Name', 'BSRGAN'))
    print('{:>16s} : {:<d}'.format('GPU ID', torch.cuda.current_device()))
    torch.cuda.empty_cache()

    print('################################## Handling {:s} ##################################'.format(test_path))
    L_path = test_path
    E_path = save_path # save path
    print('{:>16s} : {:s}'.format('Input Path', L_path))
    print('{:>16s} : {:s}'.format('Output Path', E_path))
    idx = 0

    for img in util.get_image_paths(L_path):
        ####################################
        #####(1) Read Image
        ####################################
        idx += 1
        img_name, ext = os.path.splitext(os.path.basename(img))
        print('{:>11s} {:04d} : x{:<d} --> {:<s}'.format('Restoring ', idx, scale_factor, img_name+ext))

        img_L = util.imread_uint(img, n_channels=3) #RGB 0~255

        # sc = 3
        # img_L = cv2.resize(img_L, (int(width/sc), int(height/sc)), interpolation = cv2.INTER_AREA)

        img_L_Text = img_L.copy() # 

        img_L = util.uint2tensor4(img_L) #N*C*W*H 0~1
        img_L = img_L.to(device)# 

        img_E = F.interpolate(img_L, scale_factor=scale_factor, mode='bilinear', align_corners=False)
        img_E = util.tensor2uint(img_E)
        
        ####################################
        #####(2) Restore Each Region and Paste to the whole image
        ####################################
        SQ, ori_texts, en_texts  = TextModel.handle_texts(img=img_L_Text, bg=img_E, sf=scale_factor, is_aligned=is_aligned)
        if not is_aligned:
            cv2.imwrite(os.path.join(E_path, img_name +'_Result.png'), SQ[:,:,::-1])
        ####################################
        #####(3) Save Results
        ####################################
        if SaveText:
            for m, (et, ot) in enumerate(zip(en_texts, ori_texts)): ##save each face region
                w, h, c = et.shape
                ot = cv2.resize(ot, (h, w))
                cv2.imwrite(os.path.join(E_path, img_name +'_patch_{}.png'.format(m)), np.hstack((ot, et)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--test_path', type=str, default='./testsets/LQs')
    parser.add_argument('-o', '--save_path', type=str, default=None)
    parser.add_argument('-a', '--is_aligned', action='store_true')
    args = parser.parse_args()

    save_path = args.save_path
    if save_path is None:
        TIMESTAMP = time.strftime("%m-%d_%H-%M", time.localtime())
        save_path = osp.join(args.test_path+'_'+TIMESTAMP+'_BSRGAN-Text')
    os.makedirs(save_path, exist_ok=True)
    print('#'*64)
    print('{:>25s} : {:s}'.format('Input Path', args.test_path))
    print('{:>25s} : {:s}'.format('Save Path', save_path))
    if args.is_aligned:
        print('{:>25s} : {:s}'.format('Image Details', 'Aligned Text Layout. No text detection is used.'))
    else:
        print('{:>25s} : {:s}'.format('Image Details', 'UnAligned Text Image. It will crop text region using CnSTD, restore, and paste back.'))

    main(args.test_path, save_path, args.is_aligned)