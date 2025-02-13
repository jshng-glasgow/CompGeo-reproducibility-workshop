from scipy import stats
import arviz as az
import numpy as np
import matplotlib.pyplot as plt
import pymc3 as pm
import seaborn as sns
import pandas as pd
from sklearn import preprocessing
import geopandas as gpd


def run():
    ## Data available here https://gdex.ucar.edu/dataset/camels/version/1.2/file.html
    # load data
    camels_hydro = pd.read_csv(r'C:\Users\jws10y\git\reproducibility_workshop\data\camels_hydro_new.csv')
    camels_hydro['hru_id'] = camels_hydro['gauge_id']
    camels_hydro.head()

    camels_topo= pd.read_csv(r'C:\Users\jws10y\git\reproducibility_workshop\data\camels_topo_new.csv')
    camels_topo['hru_id'] = camels_topo['gauge_id']
    camels_topo.head()

    camels_geos = gpd.read_file(r'C:\Users\jws10y\git\reproducibility_workshop\data\camel_data.shp')
    camels_geos.head()

    # merge datasets
    camels_basins = pd.merge(camels_geos, camels_hydro)
    camels_basins = pd.merge(camels_basins, camels_topo, on='hru_id')
    camels_basins.head()

    # convert units
    camels_basins['q_mean_cms'] = camels_basins['q_mean'] * (1e-3) *(camels_basins['area_gages2']*1000**2) * (1/(60*60*24)) 

    camels_basins = gpd.GeoDataFrame(camels_basins, geometry='geometry')
    fig, ax = plt.subplots(2,1, figsize=(6,6))
    camels_basins.plot(ax=ax[0], legend=True, column='q_mean')
    camels_basins.plot(ax=ax[1], legend=True, column='area_gages2')

    ax[0].set_title('Mean Daily Discharge (mm/day)')
    ax[1].set_title('Catchment Area (km2)')#
    fig.tight_layout()
    fig.savefig('fig1.png')

    # get a sample of the total dataset for analysis
    camels_basins = camels_basins.sample(n=100)

    # Pull out X and Y of interest
    x_ftr= 'area_gages2'
    y_ftr = 'q_mean_cms'
    xs = camels_basins[x_ftr]
    xs = xs.fillna(xs.mean())

    ys = camels_basins[y_ftr]
    ys = ys.fillna(ys.mean())

    # Take log-transform 
    xs = np.log(xs)
    ys = np.log(ys)

    # informative priors
    slope_prior, intercept_prior = np.polyfit(xs.values.flatten(), ys.values.flatten(), 1)

    ### PyMC linear model
    with pm.Model() as model:
        
        # Priors
        alpha = pm.Normal('alpha', mu=intercept_prior, sigma=10)
        beta = pm.Normal('beta', mu=slope_prior, sigma=10)
        sigma = pm.HalfNormal('sigma', sigma=1)
    
        # mean/expected value of the model
        mu = alpha + beta * xs
    
        # likelihood
        y = pm.Normal('y', mu=mu, sigma=sigma, observed=ys)
    
        # sample from the posterior
        trace = pm.sample(2000, cores=3)
        
    ax = az.plot_trace(trace, chain_prop='color', legend=True, figsize=(12,6))
    fig = ax.ravel()[0].figure
    fig.savefig('fig2.png')

    ## Generate posterior predictive samples
    ppc = pm.sample_posterior_predictive(trace, model=model)

    ### Plot the posterior predictive interval
    fig, ax = plt.subplots(ncols=2, figsize=(8,4))
    
    # log space
    az.plot_hdi(xs, ppc['y'], 
                color='cornflowerblue', ax=ax[0], hdi_prob=0.9)
    ax[0].scatter(xs, ys, alpha=0.6, s=20, color='k')
    ax[0].set_xlabel('Log ' + x_ftr)
    ax[0].set_ylabel('Log Mean Flow (m3/s)')
    
    # original dim space
    az.plot_hdi(np.exp(xs), np.exp(ppc['y']), 
                color='cornflowerblue', ax=ax[1], hdi_prob=0.9)
    ax[1].scatter(np.exp(xs), np.exp(ys), alpha=0.6, s=20, color='k')
    ax[1].set_xlabel(x_ftr)
    ax[1].set_ylabel('Mean Flow (m3/s)')
    plt.suptitle('90% Posterior Prediction Interval', fontsize=14)
    fig.savefig('fig3.png')

    results = az.summary(trace)
    results.to_csv('results.csv')
    
if __name__=='__main__':
    run()