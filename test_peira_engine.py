"""
Unit and Integration Test Suite for PEIRA Engine.
Verifies empirical Delta measurement, physical trial runner,
traceback dissection, and closed-loop fracture injection generation.
"""

import unittest
import sys
from peira_engine import PeiraEngine, EmpiricalImpact, FractureInjectionPayload


class TestPeiraEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PeiraEngine(timeout_sec=5.0)

    def test_absolute_convergence_delta_zero(self):
        """Testa lo stato di Convergenza Assoluta (Delta = 0, exit code 0)."""
        impact = self.engine.evaluate_physical_result(
            command="pytest tests/test_core.py",
            exit_code=0,
            stdout="5 passed in 0.12s",
            stderr="",
            wall_time_ms=120.0
        )
        self.assertTrue(impact.is_converged)
        self.assertFalse(impact.is_fractured)
        self.assertEqual(impact.delta_empirico, 0.0)
        self.assertIsNone(impact.fault_file)

    def test_thermodynamic_fracture_traceback_dissection(self):
        """Testa la dissezione anatomica di un crash reale con traceback Python."""
        fake_stderr = """
Traceback (most recent call last):
  File "c:\\project\\engine\\core.py", line 42, in execute_action
    raise ZeroDivisionError("division by zero in phase calculation")
ZeroDivisionError: division by zero in phase calculation
"""
        impact = self.engine.evaluate_physical_result(
            command="python main.py",
            exit_code=1,
            stdout="",
            stderr=fake_stderr,
            wall_time_ms=45.0
        )
        self.assertFalse(impact.is_converged)
        self.assertTrue(impact.is_fractured)
        self.assertGreater(impact.delta_empirico, 0.0)
        self.assertEqual(impact.fault_file, "c:\\project\\engine\\core.py")
        self.assertEqual(impact.fault_line, 42)
        self.assertEqual(impact.error_type, "ZeroDivisionError")
        self.assertIsNotNone(impact.antigen_signature)

    def test_fracture_injection_payload_generation(self):
        """Testa la creazione del payload di iniezione cibernetica per OCULUS/CORIS/MNEME."""
        fake_stderr = """
Traceback (most recent call last):
  File "auth.py", line 88, in verify_token
    raise PermissionError("Access denied")
PermissionError: Access denied
"""
        impact = self.engine.evaluate_physical_result(
            command="python run_auth.py",
            exit_code=1,
            stderr=fake_stderr
        )
        payload = self.engine.build_fracture_injection(impact)
        
        self.assertIsInstance(payload, FractureInjectionPayload)
        self.assertIn("auth.py:88", payload.fault_epicenter)
        self.assertIn("PermissionError in auth.py line 88", payload.target_fovea_query)
        self.assertTrue(payload.coris_epitope_signature.startswith("AB_"))
        self.assertEqual(len(payload.mneme_invalidated_state), 5)
        self.assertIn("FRACTURE_EVENT", payload.diagnostic_summary)

    def test_execute_physical_trial_real_command(self):
        """Testa l'esecuzione fisica reale contro il sistema operativo."""
        # Esecuzione comando valido
        res_ok = self.engine.execute_physical_trial('python -c "print(1 + 1)"')
        self.assertTrue(res_ok.is_converged)
        self.assertEqual(res_ok.stdout, "2")
        self.assertEqual(res_ok.exit_code, 0)

        # Esecuzione comando con errore reale
        res_fail = self.engine.execute_physical_trial('python -c "import non_existent_quantum_pkg"')
        self.assertTrue(res_fail.is_fractured)
        self.assertEqual(res_fail.exit_code, 1)
        self.assertEqual(res_fail.error_type, "ModuleNotFoundError")


if __name__ == "__main__":
    unittest.main()
