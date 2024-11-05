import os
from sklearn.metrics import mean_squared_error
import rasterio as rio
import numpy as np
import pandas as pd

def calc_binwise_rmse(bins, experiment_name, inference_results, labels_path, csv_out_path):
    """Calculates bin-wise RMSE metrics

        Args:
            bins (list[list[floats]]): Nested list of bins defining lower and upper bound of each bin.
            experiment_name (str): Name of experiment used as label in csv table. 
            inference_results (str): list of inference results.
            labels_path (str): Paths to the image labels corresponding to inference input images.
            csv_out_path (str): Path to the CSV file to save metrics table (created or appended if existing).
    """

    che_actual = []
    che_pred = []
    rmse_lst = []
    for label_file,prediction in zip(labels_path, inference_results):

        #Flatten and only pick the non -1 labels to plot the actual v/s predicted
        mass = rio.open(label_file).read()
        preds = prediction.detach().cpu().unsqueeze(0).numpy()

        mask = np.squeeze(mass.swapaxes(0, 1).swapaxes(1, 2)).flatten()
        
        inf_flat = np.squeeze(preds.swapaxes(0, 1).swapaxes(1, 2)).flatten()

        label_locs = np.where((mask >= 0), True, False)
        mask1 = mask[label_locs].tolist()
        preds1 = inf_flat[label_locs].tolist()

        rmse = np.sqrt(mean_squared_error(mask1, preds1))
        rmse_lst.append(rmse)
        che_actual.extend(mask1)
        che_pred.extend(preds1)

    che_CA = pd.DataFrame({'che_actual_tile': che_actual,
                           'che_pred_unet_tile': che_pred})

    che_CA = pd.DataFrame({
        'che_actual_tile': che_actual,
        'che_pred_tile': che_pred
    })

    for ibin in bins:
        che_CA[f'che_{ibin[0]}_{ibin[1]}'] = 0
        che_CA.loc[(
            (che_CA.che_actual_tile>=ibin[0]) & (che_CA.che_actual_tile<ibin[1])
        ), f'che_{ibin[0]}_{ibin[1]}'] = 1
    
    rmse_df = pd.DataFrame()
    rmse_df['experiment_name'] = [experiment_name]

    for ibin in bins:
        rmse_df[f'{ibin[0]}-{ibin[1]}'] = [np.sqrt(
            mean_squared_error(che_CA[che_CA[f'che_{ibin[0]}_{ibin[1]}']==1]['che_actual_tile'],
                               che_CA[che_CA[f'che_{ibin[0]}_{ibin[1]}']==1]['che_pred_tile'])
        )]
    
    # append data frame to CSV file
    if os.path.exists(csv_out_path):
        rmse_df.to_csv(csv_out_path, mode='a', index=False, header=False)
    else:
        rmse_df.to_csv(csv_out_path, mode='a', index=False, header=True)