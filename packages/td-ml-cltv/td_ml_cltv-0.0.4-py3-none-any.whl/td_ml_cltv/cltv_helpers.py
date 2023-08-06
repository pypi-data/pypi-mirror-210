import time
import pytd
import numpy as np
import pandas as pd
import re
from pandiet import Reducer
import tdclient
from memory_profiler import profile
from itertools import islice
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor, plot_importance
# import lightgbm as lgb
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics
from scipy.stats import skew, kurtosis, binned_statistic

import shap
import warnings
warnings.filterwarnings("ignore")

#Read data from TD using new optimized query     
@profile
def new_query(database, query_syntax, td_api_key, td_api_server):

    #set dictonaries where you will store column name-datatype pairs
    dtype_list = [('object', np.object_),('float16', np.float16) , ('float32', np.float32), ('uint8', np.uint8), 
                  ('uint16', np.uint16), ('uint32', np.uint32)]
    object_dict = {}

    #query db.table in TD and save job.results() as np.array
    with tdclient.Client(apikey=td_api_key, endpoint=td_api_server) as td:
            job = td.query(database, query_syntax, type='presto')
            job.wait()
            raw_array = np.array(list(job.result()))
            columns = [f[0] for f in job.result_schema]
            
            #take a small slice of the job.results object and create a small sample DF
            sliced = islice(job.result(), 10)
            sample_df = pd.DataFrame(sliced, columns=columns)
            
            #apply reducer to sample_df to exctract the optimal datatypes for each column
            test_df = Reducer(use_null_int=False, n_jobs = 1).reduce(sample_df, verbose=False)
            
            #below stores a list of column names, index positions in DF and converted datatypes after reducer was applied
            for data_type in dtype_list:
                cols_idxs = [(col, test_df.columns.get_loc(col)) for col in test_df.columns if test_df[col].dtype.name == data_type[0]]
                if len(cols_idxs):
                    object_dict[data_type[0]] = cols_idxs
            
            #Generate a base array by extracting all Object dtypes using indexes on the job_results array
            object_arr =  np.take(raw_array, [item[1] for item in object_dict['object']], axis = 1)
            object_arr = object_arr.astype(np.object_)
            base_df = pd.DataFrame(object_arr, columns = [item[0] for item in object_dict['object']])
            
            #Loop through list of all other datatypes, create temporary DFs for each and concat to base_df 
            for tup in dtype_list[1:]:
                if tup[0] in list(object_dict.keys()):
                    new_arr = np.take(raw_array, [item[1] for item in object_dict[tup[0]]], axis = 1)
                    new_arr = new_arr.astype(np.float32).astype(tup[1])
                    names = [item[0] for item in object_dict[tup[0]]]
                    new_df = pd.DataFrame(new_arr, columns = names)
                    base_df = pd.concat([base_df, new_df], axis = 1)
                    
                    #delete temp df after concating to base_df, to free space
                    del new_df
                    
    return base_df


# Function below replaces outliers with desired percentile of data. It also allows to change the 1.5 coeff
def replace_outliers(target, q_up = 0.98, q_low = 0.02, coeff = 1):
    Q1 = target.quantile(0.25)
    Q3 = target.quantile(0.75)
    IQR = Q3 - Q1
    
    #code below replaces outliers wit hthe 98th and 2nd percentile values from target distribution
    #these can also be controled using q_up and q_low coeffs
    target = target.where(target < (Q3 + coeff * IQR), target.quantile(q_up))
    target = target.where(target > (Q1 - coeff * IQR), target.quantile(q_low))
    
    return target


def query_data_splits(database, input_table, num_splits = 1):

    #create split ratio based on how many times you want to split original table
    split = 1.0 / num_splits
    
    #empty list to store temporary DFs
    df_list = []
    
    #Loop through count of splits and query original table in TD in smaller chunks and reduce each chunk
    for i in list(range(num_splits)):
        query_syntax = f'select * from {input_table} where rnd > {i*split} AND rnd <= {(i+1)*split}'
        print(query_syntax)
        
        temp_df = new_query(database, query_syntax)
        temp_df = Reducer(use_null_int=False, n_jobs = 1).reduce(temp_df, verbose=False)
        df_list.append(temp_df)
        del temp_df
        
    #Concactenate all reduced chunk into a final DF and reduce one last time
    df_final= pd.concat(df_list, ignore_index = True)
    # df_final= Reducer(use_null_int=False, n_jobs = 1).reduce(df_final, verbose=False)
    
    return df_final



   
# Function for getting importances via coefficients
@profile
def impt_coef(model, x_data, target, k=100):

    try:
        importances = model.coef_
    except:
        importances = model.feature_importances_

    features = x_data.columns
    
    feat_impt = sorted(list(zip(features, importances)), key=lambda x: x[1])
    
    return pd.DataFrame(feat_impt, columns=['feature', 'weight'])

# Feature importances for trees
def impt_tree(model, x_data, target, k=100):

    try:
      #Try Standard Method
        baseline = get_feature_kmeans(x_data)
        shap_values = shap.TreeExplainer(model).shap_values(baseline)

        #Get SHAP Values from Kmeans features
        features = baseline.columns
        shap_vals = np.abs(shap_values).mean(0)
        shap_list = list(zip(features, shap_vals))
        shap_sorted = sorted(shap_list, key=lambda tup: tup[1], reverse = True)
        shap_df = pd.DataFrame(shap_sorted, columns = ['feature', 'shap'])

        #Get SHAP from Model
        model.get_booster().feature_names = features.tolist()
        shap_df = pd.DataFrame(shap_list, columns = ['feature', 'shap'])

        #Get Feature IMportances from Model
        impt = model.get_booster().get_score(importance_type="weight")

        #merge feature importnaces and shape values in one dataframe
        impt_df = pd.merge(shap_df, pd.DataFrame.from_dict(impt, orient='index', 
                                                         columns=['weight']), 
                         right_index=True, left_on='feature').sort_values('weight')

    except:   
        features = x_data.columns
        impt = model.get_booster().get_score(importance_type="weight")
        impt_df = pd.DataFrame(impt.items(), columns=['feature', 'weight'])
    
    return impt_df

#Function for getting summary of Target Variable Stats
def target_describe(df, target, outlier_coeff):
    
    target_df = pd.DataFrame(df[target].describe()).transpose().rename_axis('target').reset_index()
    target_df['skewness'] = round(df[target].skew(), 2)
    target_df['kurtosis'] = round(df[target].kurt(), 2)

    #Outliers count
    Q1 = df[target].quantile(0.25)
    Q3 = df[target].quantile(0.75)
    IQR = Q3 - Q1

    target_df['low_outliers'] = (df[target] < (Q1 - outlier_coeff * IQR)).sum()
    target_df['high_outliers'] = (df[target] > (Q3 + outlier_coeff * IQR)).sum()

    return target_df

# Function to get stats for target and predicted var
def get_metric_stats(np_array, target, outlier_coeff, dataset = 'Original'):
    
    #Get necessary stats
    predicted_value = target
    count = len(np_array)
    mean = round(np_array.mean(), 1)
    stdev = round(np_array.std(), 1)
    min_val = round(np_array.min(), 1)
    q1_25 = round(np.percentile(np_array, 25), 1)
    q2_50 = round(np.percentile(np_array, 50), 1)
    q3_75 = round(np.percentile(np_array, 75), 1)
    max_val = round(np_array.max(), 1)
    skewnewss = round(skew(np_array), 2)
    kurt = round(kurtosis(np_array), 2)
    IQR = round(q3_75 - q1_25, 1)
    low_outliers = len(np_array[np_array < q1_25 - outlier_coeff*IQR])
    high_outliers = len(np_array[np_array > q3_75 + outlier_coeff*IQR])
    
    #make dictionary of stats and turn into pandas DF
    stats = dict(dataset = dataset, predicted_value = predicted_value, count = count, mean = mean, stdev = stdev, 
                    min_val = min_val, q1_25 = q1_25, q2_50 = q2_50, q3_75 = q3_75, max_val= max_val, iqr = IQR,
                    skew = skewnewss, kurt = kurt, low_outliers = low_outliers, high_outliers = high_outliers)
    
    return  pd.DataFrame(stats, index = [0])

#Get Binned Data for Metrics Histogram
def get_binned_stats(metric_array, bin_num = 100):
    
    mean_stat = binned_statistic(metric_array, metric_array,
                             statistic='mean', 
                             bins=bin_num, 
                             )
    #Get Array of Bin Averages
    bin_avg = np.round(mean_stat.statistic, 2)
    bin_avg_str = np.array([str(item) for item in bin_avg])
    
    #Get Bin Counts for Each Average
    bin_labels = mean_stat.binnumber
    bin_info = np.unique(bin_labels, return_counts=True)
    bin_cnts = bin_info[1]
    
    #Create DF with Bins
    hist = dict(bin_avg = bin_avg, bin_avg_str = bin_avg_str,  bin_cnts = bin_cnts)
    
    return pd.DataFrame(hist)

#Get distribution of model predictions
def get_predicted_label_stats(predicted, target, session_id = 0):
    
    stats_dict = {'above_avg': [], 'below_avg': [], 'above_median': [], 'below_median': []}
    
    mean_tar = np.mean(target)
    median_tar = np.median(target)
    total = len(target)
    
    above_avg = len(predicted[predicted > mean_tar]) / total
    below_avg = len(predicted[predicted <= mean_tar]) / total
    above_median = len(predicted[predicted > median_tar]) / total
    below_median = len(predicted[predicted <= median_tar]) / total
    
    stats_dict['above_avg'].append(round(above_avg, 3))
    stats_dict['below_avg'].append(round(below_avg, 3))
    stats_dict['above_median'].append(round(above_median, 3))
    stats_dict['below_median'].append(round(below_median, 3))
    
    df = pd.DataFrame(stats_dict)
    df['session_id'] = session_id
    
    return df

#Optimize SHAP Value calculation for Memory Efficiency
def kmeans(X, k, round_values=True, keep_index=True):
    """Summarize a dataset with k mean samples weighted by the number of data points they
    each represent.

    Parameters
    ----------
    X : numpy.array or pandas.DataFrame or any scipy.sparse matrix
        Matrix of data samples to summarize (# samples x # features)

    k : int
        Number of means to use for approximation.

    round_values : bool
        For all i, round the ith dimension of each mean sample to match the nearest value
        from X[:,i]. This ensures discrete features always get a valid value.

    Returns
    -------
    DenseData object.
    """
    from sklearn.cluster import KMeans
    from sklearn.impute import SimpleImputer
    from scipy.sparse import issparse

    group_names = [str(i) for i in range(X.shape[1])]
    df_X = X
    if str(type(X)).endswith("'pandas.core.frame.DataFrame'>"):
        group_names = X.columns
        X = X.values

    # in case there are any missing values in data impute them
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    X = imp.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=0).fit(X)

    if keep_index:
        return df_X.iloc[sorted(np.bincount(kmeans.labels_))]

    if round_values:
        for i in range(k):
            for j in range(X.shape[1]):
                xj = X[:, j].toarray().flatten() if issparse(X) else X[:, j]  # sparse support courtesy of @PrimozGodec
                ind = np.argmin(np.abs(xj - kmeans.cluster_centers_[i, j]))
                kmeans.cluster_centers_[i, j] = X[ind, j]
    from shap.utils._legacy import DenseData

    return DenseData(kmeans.cluster_centers_, group_names, None, 1.0 * np.bincount(kmeans.labels_))

def get_feature_kmeans(x_data, canonical_id):
    
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    
    #drop index from DF
    df = x_data.copy()
    df.reset_index(inplace = True)
    df.drop([canonical_id], axis =1, inplace = True)
    
    #Convert Categorical Vars into 0-1
    for column_name in df.columns:
        if pd.api.types.is_categorical_dtype(df[column_name]):
            df[column_name] = le.fit_transform(df[column_name])
        else:
            pass
        
    #return cluster means and their indexes
    kmeans_idx = kmeans(df.sample(frac=0.4, random_state=1, ignore_index=True), 10)
    
    del df, le
    
    baseline = x_data.iloc[kmeans_idx.index]
    
    return baseline