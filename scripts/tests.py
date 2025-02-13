import unittest
import pandas as pd
import numpy as np
import os
from analysis import load_data, preprocess_data, run_bayesian_model

class TestReproducibilityScript(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Load data once for efficiency
        cls.camels_hydro, cls.camels_topo, cls.camels_geos = load_data()
        cls.camels_basins = preprocess_data(cls.camels_hydro, cls.camels_topo, cls.camels_geos)

    def test_load_data(self):
        """Test that the data files are loaded correctly and have expected columns."""
        self.assertFalse(self.camels_hydro.empty, "Hydro dataset should not be empty")
        self.assertFalse(self.camels_topo.empty, "Topographic dataset should not be empty")
        self.assertFalse(self.camels_geos.empty, "Geospatial dataset should not be empty")
        
        self.assertIn("gauge_id", self.camels_hydro.columns, "Hydro dataset missing gauge_id column")
        self.assertIn("gauge_id", self.camels_topo.columns, "Topo dataset missing gauge_id column")
        self.assertIn("geometry", self.camels_geos.columns, "Geospatial dataset missing geometry column")

    def test_preprocess_data(self):
        """Test preprocessing function produces a dataset with expected transformations."""
        self.assertFalse(self.camels_basins.empty, "Processed dataset should not be empty")
        self.assertIn("q_mean_cms", self.camels_basins.columns, "Processed dataset missing 'q_mean_cms' column")
        
        # Check unit conversion is applied
        original_q_mean = self.camels_basins['q_mean'].mean()
        converted_q_mean = self.camels_basins['q_mean_cms'].mean()
        self.assertNotEqual(original_q_mean, converted_q_mean, "Unit conversion was not applied correctly")

    def test_bayesian_model_reproducibility(self):
        """Test that Bayesian model results remain consistent with fixed random seed."""
        trace_1 = run_bayesian_model(self.camels_basins)
        trace_2 = run_bayesian_model(self.camels_basins)
        
        np.testing.assert_array_almost_equal(trace_1["alpha"].mean(), trace_2["alpha"].mean(), decimal=2, 
                                             err_msg="Alpha parameter means are inconsistent")
        np.testing.assert_array_almost_equal(trace_1["beta"].mean(), trace_2["beta"].mean(), decimal=2, 
                                             err_msg="Beta parameter means are inconsistent")

if __name__ == "__main__":
    unittest.main()
