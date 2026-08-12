import unittest
from datetime import datetime, timezone
from backend.schemas.land_lease import LandLeaseInputSchema
from backend.services.land_lease_valuation import normalize_to_acres, calculate_land_valuation, get_base_rate_for_district
from backend.services.land_lease_ai import generate_land_lease_ai_assessment
from backend.services.land_lease_report import generate_land_lease_pdf
from backend.models.land_lease import LandLeaseEstimate


class TestLandLeasingValuationEngine(unittest.TestCase):

    def test_unit_normalization(self):
        self.assertAlmostEqual(normalize_to_acres(1.0, "Acre"), 1.0)
        self.assertAlmostEqual(normalize_to_acres(1.0, "Hectare"), 2.47105)
        self.assertAlmostEqual(normalize_to_acres(40.0, "Guntha"), 1.0)
        self.assertAlmostEqual(normalize_to_acres(10.0, "Guntha"), 0.25)

    def test_district_base_rates(self):
        self.assertEqual(get_base_rate_for_district("Bengaluru Urban"), 48000.0)
        self.assertEqual(get_base_rate_for_district("Mandya"), 35000.0)
        self.assertEqual(get_base_rate_for_district("Bagalkot"), 18000.0)
        self.assertEqual(get_base_rate_for_district("Unknown District"), 22000.0)

    def test_land_valuation_calculation(self):
        input_data = LandLeaseInputSchema(
            district="Bagalkot",
            input_size=2.0,
            input_unit="Acre",
            water_availability="Regular Water (Perennial/Borewell)",
            electricity_available=True,
            electricity_reliability="3-Phase Dedicated Line",
            road_access="Paved Road / Main Highway",
            infrastructure=["Perimeter Fencing & Gate", "Motor Pump Set / Solar Pump"]
        )

        res = calculate_land_valuation(input_data)

        self.assertEqual(res["acres"], 2.0)
        self.assertGreater(res["calculated_max_price"], res["calculated_min_price"])
        self.assertIn(res["confidence_score"], ["HIGH", "MODERATE"])
        self.assertGreater(len(res["positive_factors"]), 0)

    def test_groq_ai_fallback(self):
        input_data = LandLeaseInputSchema(
            district="Mandya",
            input_size=1.0,
            input_unit="Hectare"
        )
        valuation = calculate_land_valuation(input_data)
        ai_res = generate_land_lease_ai_assessment(input_data, valuation, api_key=None)

        self.assertIn("summary", ai_res)
        self.assertIn("estimated_range_explanation", ai_res)
        self.assertIn("recommendations", ai_res)
        self.assertGreater(len(ai_res["recommendations"]), 0)

    def test_pdf_report_generation(self):
        estimate = LandLeaseEstimate(
            id=1,
            user_id=1,
            report_id="LL-TEST-1234",
            state="Karnataka",
            district="Mandya",
            taluk="Srirangapatna",
            village="Ganjam",
            input_size=2.5,
            input_unit="Acre",
            acres=2.5,
            water_availability="Regular Water (Perennial/Borewell)",
            electricity_available=True,
            road_access="Paved Road",
            base_rate_per_acre=35000.0,
            calculated_min_price=70000.0,
            calculated_max_price=90000.0,
            confidence_score="HIGH",
            created_at=datetime.now(timezone.utc)
        )

        pdf_bytes = generate_land_lease_pdf(estimate, user_name="Test Farmer")
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
