import rasterio as rio
import numpy as np
import pandas as pd
import os

def calc_mean_std(img_folder):
    """Calculate data mean and standard deviation

        Args:
            img_folder (str): Path to directory with geotiff data for which to calculate the scalers.
        Returns:
            Pandas Dataframe with mean and std for all available bands in input data. 
    """

    count = 0
    mean = np.zeros(10)
    for img_file in os.listdir(img_folder):
        if '.tif' in img_file:
            with rio.open(os.path.join(img_folder,img_file)) as f:
              imm = f.read().astype('float32')
            c, h, w = imm.shape
            imm[imm==-9999] = np.nan
            nb_pixels = h * w - (np.count_nonzero(np.isnan(imm)))
            sum = np.nansum(imm, axis=(1,2))
            mean = (count * mean + sum) / (count + nb_pixels)
            count += nb_pixels

    count = 0
    variance = np.zeros_like(mean)
    for img_file in os.listdir(img_folder):
        if '.tif' in img_file:
            with rio.open(os.path.join(img_folder,img_file)) as f:
              imm = f.read().astype('float32')
            c, h, w = imm.shape
            imm[imm==-9999] = np.nan
            nb_pixels = h * w - (np.count_nonzero(np.isnan(imm)))
            sum_squared = np.nansum((imm.transpose(1,2,0)-mean)**2, axis=(0,1))
            variance = (count * variance + sum_squared) / (count + nb_pixels)
            count += nb_pixels

    std = np.sqrt(variance)

    return( pd.DataFrame({'mean': mean,'std': std}) )
