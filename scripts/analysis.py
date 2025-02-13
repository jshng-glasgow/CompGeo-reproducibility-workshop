import pandas as pd
import numpy as np
import pymc3 as pm
import arviz as az
import matplotlib.pyplot as plt
import geopandas as gpd
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set random seed for reproducibility
SEED = 42
np.random.seed(SEED)

# Define file paths
DATA_DIR = os.path.join(os.getcwd(), "data")
RESULTS_DIR = os.path.join(os.getcwd(), "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Function to load datasets
def load_data():
    logging.info("Loading datasets...")
    hydro_path = os.path.join(DATA_DIR, "camels_hydro.txt")
    topo_path = os.path.join(DATA_DIR, "camels_topo.txt")
    geos_path = os.path.join(DATA_DIR, "camel_data.shp")
    
    camels_hydro = pd.read_csv(hydro_path, delimiter=';')
    camels_topo = pd.read_csv(topo_path, delimiter=';')
    camels_geos = gpd.read_file(geos_path)
    
    camels_hydro['hru_id'] = camels_hydro['gauge_id']
    camels_topo['hru_id'] = camels_topo['gauge_id']
    
    return camels_hydro, camels_topo, camels_geos

# Function to preprocess data
def preprocess_data(camels_hydro, camels_topo, camels_geos):
    logging.info("Merging and processing datasets...")
    camels_basins = pd.merge(camels_geos, camels_hydro, on='hru_id')
    camels_basins = pd.merge(camels_basins, camels_topo, on='hru_id')
    
    # Convert units (mm/day to m^3/s)
    sec_per_day = 86400
    camels_basins['q_mean_cms'] = camels_basins['q_mean'] * (1e-3) * (camels_basins['area_gages2'] * 1e6) * (1 / sec_per_day)
    
    # Convert to GeoDataFrame
    camels_basins = gpd.GeoDataFrame(camels_basins, geometry='geometry')
    return camels_basins

# Function to visualize data
def plot_data(camels_basins):
    logging.info("Generating spatial plots...")
    fig, ax = plt.subplots(2, 1, figsize=(6, 6))
    camels_basins.plot(ax=ax[0], legend=True, column='q_mean')
    camels_basins.plot(ax=ax[1], legend=True, column='area_gages2')
    ax[0].set_title('Mean Daily Discharge (mm/day)')
    ax[1].set_title('Catchment Area (km²)')
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig1.png'))

# Function to run Bayesian regression
def run_bayesian_model(camels_basins):
    logging.info("Running Bayesian regression model...")
    sample_data = camels_basins.sample(n=100, random_state=SEED)
    
    xs = np.log(sample_data['area_gages2'].fillna(sample_data['area_gages2'].mean()))
    ys = np.log(sample_data['q_mean_cms'].fillna(sample_data['q_mean_cms'].mean()))
    
    slope_prior, intercept_prior = np.polyfit(xs.values.flatten(), ys.values.flatten(), 1)
    
    with pm.Model() as model:
        alpha = pm.Normal('alpha', mu=intercept_prior, sigma=10)
        beta = pm.Normal('beta', mu=slope_prior, sigma=10)
        sigma = pm.HalfNormal('sigma', sigma=1)
        
        mu = alpha + beta * xs
        y = pm.Normal('y', mu=mu, sigma=sigma, observed=ys)
        
        trace = pm.sample(200, cores=1, random_seed=SEED)
    
    az.plot_trace(trace, figsize=(12, 6))
    plt.savefig(os.path.join(FIGURES_DIR, 'fig2.png'))
    
    results = az.summary(trace)
    results.to_csv(os.path.join(RESULTS_DIR, 'results.csv'))
    return trace

# Main script execution
def main():
    camels_hydro, camels_topo, camels_geos = load_data()
    camels_basins = preprocess_data(camels_hydro, camels_topo, camels_geos)
    plot_data(camels_basins)
    trace = run_bayesian_model(camels_basins)
    logging.info("Script execution complete.")

if __name__ == '__main__':
    main()