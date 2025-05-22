import unittest
from dose_calculator import (
    perform_dose_per_weight_calculation,
    perform_infusion_preparation_calculation,
    perform_rate_duration_calculation
)

class TestDoseCalculations(unittest.TestCase):

    # Tests for perform_dose_per_weight_calculation
    def test_dpw_liquid_medication(self):
        # weight_kg, dose_mg_per_kg, concentration_value, concentration_unit_str
        total_mg, quantity, unit = perform_dose_per_weight_calculation(10, 2, 5, "mg/mL") # 10kg, 2mg/kg, 5mg/mL
        self.assertAlmostEqual(total_mg, 20)
        self.assertAlmostEqual(quantity, 4)
        self.assertEqual(unit, "mL")

    def test_dpw_solid_medication(self):
        total_mg, quantity, unit = perform_dose_per_weight_calculation(20, 1, 10, "mg/tablet") # 20kg, 1mg/kg, 10mg/tablet
        self.assertAlmostEqual(total_mg, 20)
        self.assertAlmostEqual(quantity, 2)
        self.assertEqual(unit, "tablets")

    def test_dpw_solid_medication_mg_tab_variant(self):
        total_mg, quantity, unit = perform_dose_per_weight_calculation(15, 2, 30, "mg/tab") # 15kg, 2mg/kg, 30mg/tab
        self.assertAlmostEqual(total_mg, 30)
        self.assertAlmostEqual(quantity, 1)
        self.assertEqual(unit, "tablets")
        
    def test_dpw_unrecognized_unit(self):
        total_mg, quantity, unit = perform_dose_per_weight_calculation(10, 1, 10, "mg/capsule")
        self.assertAlmostEqual(total_mg, 10)
        self.assertIsNone(quantity)
        self.assertEqual(unit, "unrecognized_unit")

    def test_dpw_zero_concentration(self):
        with self.assertRaisesRegex(ValueError, "Concentration value cannot be zero."):
            perform_dose_per_weight_calculation(10, 2, 0, "mg/mL")

    # Tests for perform_infusion_preparation_calculation
    def test_ip_typical_values(self):
        # total_dose_mg, drug_concentration_value_mg_ml, total_final_infusion_volume_ml
        drug_vol, diluent_vol, final_conc = perform_infusion_preparation_calculation(100, 20, 500) # 100mg drug, 20mg/mL conc, 500mL final vol
        self.assertAlmostEqual(drug_vol, 5)       # 100mg / 20mg/mL = 5mL
        self.assertAlmostEqual(diluent_vol, 495)  # 500mL - 5mL = 495mL
        self.assertAlmostEqual(final_conc, 0.2)   # 100mg / 500mL = 0.2mg/mL

    def test_ip_drug_volume_equals_final_volume(self):
        drug_vol, diluent_vol, final_conc = perform_infusion_preparation_calculation(100, 10, 10) # 100mg drug, 10mg/mL, 10mL final
        self.assertAlmostEqual(drug_vol, 10)      # 100mg / 10mg/mL = 10mL
        self.assertAlmostEqual(diluent_vol, 0)    # 10mL - 10mL = 0mL
        self.assertAlmostEqual(final_conc, 10)    # 100mg / 10mL = 10mg/mL
        
    def test_ip_zero_drug_concentration(self):
        with self.assertRaisesRegex(ValueError, "Drug concentration cannot be zero."):
            perform_infusion_preparation_calculation(100, 0, 500)

    def test_ip_zero_final_volume(self):
        with self.assertRaisesRegex(ValueError, "Total final infusion volume cannot be zero."):
            perform_infusion_preparation_calculation(100, 20, 0)

    def test_ip_drug_volume_exceeds_final_volume(self):
        with self.assertRaisesRegex(ValueError, "Volume of drug to draw exceeds the total final infusion volume."):
            perform_infusion_preparation_calculation(100, 10, 5) # 10mL drug needed, but only 5mL final volume

    # Tests for perform_rate_duration_calculation
    def test_rd_rate_from_duration(self):
        # total_volume_ml, total_drug_mg_in_infusion, value (duration_hours), mode
        rate, duration, drug_delivery = perform_rate_duration_calculation(500, 100, 5, 'rate_from_duration') # 500mL, 100mg, 5 hours
        self.assertAlmostEqual(rate, 100)          # 500mL / 5hr = 100mL/hr
        self.assertAlmostEqual(duration, 5)
        self.assertAlmostEqual(drug_delivery, 20)  # 100mg / 5hr = 20mg/hr

    def test_rd_duration_from_rate(self):
        # total_volume_ml, total_drug_mg_in_infusion, value (rate_ml_hr), mode
        rate, duration, drug_delivery = perform_rate_duration_calculation(500, 100, 100, 'duration_from_rate') # 500mL, 100mg, 100mL/hr
        self.assertAlmostEqual(rate, 100)
        self.assertAlmostEqual(duration, 5)        # 500mL / 100mL/hr = 5hr
        self.assertAlmostEqual(drug_delivery, 20)  # 100mg / 5hr = 20mg/hr (or 100mL/hr * (100mg/500mL))

    def test_rd_zero_duration(self):
        with self.assertRaisesRegex(ValueError, "Duration cannot be zero."):
            perform_rate_duration_calculation(500, 100, 0, 'rate_from_duration')

    def test_rd_zero_rate(self):
        with self.assertRaisesRegex(ValueError, "Infusion rate cannot be zero."):
            perform_rate_duration_calculation(500, 100, 0, 'duration_from_rate')
            
    def test_rd_zero_total_volume_in_duration_from_rate(self):
        # This is a specific case where total_volume_ml = 0 would cause DivByZero for drug_concentration_mg_per_mL
        with self.assertRaisesRegex(ValueError, "Total volume cannot be zero for drug concentration calculation in this mode."):
            perform_rate_duration_calculation(0, 100, 50, 'duration_from_rate')

    def test_rd_invalid_mode(self):
        with self.assertRaisesRegex(ValueError, "Invalid mode: unknown_mode"):
            perform_rate_duration_calculation(500, 100, 5, 'unknown_mode')

if __name__ == '__main__':
    unittest.main()
