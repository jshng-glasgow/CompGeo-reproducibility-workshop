# Bayesian Inference for Hydrological Modeling: A Case Study of Catchment Flow in the CAMELS Dataset
This repository contains code used to model catchment flows in the CAMELS dataset in the research paper `research_paper.pdf`. The code is based on [analysis found here](https://waterprogramming.wordpress.com/2024/04/11/introduction-to-bayesian-regression-using-pymc/).

## Dependencies
python==3.6.13
pymc3==3.10.0
pandas==1.1.5
geopandas==0.9.0
numpy==1.19.5
matplotlib==3.3.4
arviz==0.10.0

NOTE: This has been run successfully on both a Windows 10 and an Oracle Linux 9.5 Server

## Installation and Setup
1. **Clone the repository**
```
git clone https://github.com/jshng-glasgow/CompGeo-reproducibility-workshop.git
cd ComGeo-reproducibility-workshop
```
2. **Create a virutal environment**

If you have Conda installed on a windows machine, you can install directly from the `environment.yml` file:
```
conda create -f environment.yaml
conda activate reproducibility env
```
or you can install from `requirements.txt` in a fresh `python3.6` environment.
``` 
conda create --name my_env python=3.6.13
pip install -r requirements.txt
```
If you prefer to use Venv, then first download and install [python 3.6](https://www.python.org/downloads/release/python-360/), then run the following:
```
python3.6 -m venv CompGeo-reproducibility-env
source reproducibility_env/bin/activate 
```
Upgrade pip ind install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```
3. **Run the script**
Once everything is installed, you can run the analysis script:
```
python scripts/analysis.py
```
## Output
* Figures (`fig1.png`, `fig2.png` and `fig3.png`) are saved in `results\figures\`
* Regression results stored in `results\results.csv`
* Logs printed to terminal

## License
MIT License