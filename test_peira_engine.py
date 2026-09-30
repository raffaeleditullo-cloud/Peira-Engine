"""
Unit and Integration Test Suite for PEIRA Engine.
Verifies empirical Delta measurement, physical trial runner,
traceback dissection, and closed-loop fracture injection generation.
"""

import unittest
import sys
import os
import json
import subprocess
import tempfile
import shutil
from unittest import mock
from peira_engine import PeiraEngine, EmpiricalImpact, FractureInjectionPayload
import peira_hexad_organism


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


class TestPeiraDemonGate(unittest.TestCase):
    """Verifica che ogni ingresso verso PEIRA passi dal gate DEMON (fail-closed)."""

    def setUp(self):
        self.workspace = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def _organism(self):
        organism = peira_hexad_organism.LivingHexadOrganism()
        organism.demon = None  # Evita la ricerca web del gateway: il gate è indipendente
        if organism.coris:
            # Gli anticorpi dei crash di prova restano nel workspace temporaneo, non in Coris-Engine
            organism.coris = type(organism.coris)(immune_store_path=os.path.join(self.workspace, "immune_memory.json"))
        return organism

    def _run_organism(self, organism, command, traces=None, retries=0):
        traces = traces or [{"id": "B1", "name": "Trace", "code": command, "entropies": [0.1]}]
        return organism.execute_hexad_lifecycle(
            intent_query="Verify gate",
            workspace_dir=self.workspace,
            candidate_reasoning_traces=traces,
            context_conversation=[],
            max_fracture_retries=retries
        )

    def test_organism_gate_blocks_before_peira(self):
        """Un comando bloccato da DEMON non raggiunge mai PEIRA e il ramo viene escluso."""
        # Innocuo se eseguito (è solo un echo), ma riconosciuto dal gate come distruzione di database
        res = self._run_organism(self._organism(), "echo DROP TABLE users", retries=1)
        self.assertEqual(res["lifecycle_status"], "HEXAD_HALTED_NO_ALTERNATIVES")
        self.assertEqual(res["excluded_branches"], ["B1"])
        self.assertTrue(any("Gate BLOCK" in line and "database" in line for line in res["audit_trail"]))
        self.assertFalse(any("[6. PEIRA]" in line for line in res["audit_trail"]))

    def test_organism_blocked_branch_falls_back_to_safe_one(self):
        """Dopo un blocco DEMON l'organismo prova il ramo alternativo invece di arrendersi."""
        traces = [
            {"id": "RISKY", "code": "echo DROP TABLE users", "entropies": [0.1]},
            {"id": "SAFE", "code": "python -c \"print('SAFE PATH')\"", "entropies": [0.3]},
        ]
        res = self._run_organism(self._organism(), None, traces=traces, retries=1)
        self.assertEqual(res["lifecycle_status"], "HEXAD_ABSOLUTE_CONVERGENCE")
        self.assertIn("SAFE PATH", res["physical_stdout"])

    def test_organism_excludes_the_winner_not_the_first(self):
        """La frattura esclude il ramo eletto da ANIMA, anche se non è il primo della lista."""
        traces = [
            {"id": "GOOD", "code": "python -c \"print('GOOD BRANCH')\"", "entropies": [0.3]},
            {"id": "BROKEN", "code": "python -c \"import sys; sys.exit(3)\"", "entropies": [0.1]},
        ]
        res = self._run_organism(self._organism(), None, traces=traces, retries=1)
        self.assertEqual(res["lifecycle_status"], "HEXAD_ABSOLUTE_CONVERGENCE")
        self.assertIn("GOOD BRANCH", res["physical_stdout"])
        self.assertEqual(res["cycles_required"], 2)

    def test_organism_single_failure_is_not_reported_as_success(self):
        """Un unico ramo fallito si arresta con la frattura, senza eseguire un comando segnaposto."""
        traces = [{"id": "ONLY", "code": "python -c \"import sys; sys.exit(3)\"", "entropies": [0.1]}]
        res = self._run_organism(self._organism(), None, traces=traces, retries=1)
        self.assertEqual(res["lifecycle_status"], "HEXAD_HALTED_NO_ALTERNATIVES")
        self.assertEqual(res["last_fracture"]["exit_code"], 3)
        self.assertEqual(sum("[6. PEIRA] Impatto fisico" in line for line in res["audit_trail"]), 1)

    def test_organism_fail_closed_without_gate(self):
        """Senza gate l'organismo nega l'esecuzione invece di dichiarare una barriera inesistente."""
        with mock.patch.object(peira_hexad_organism, "HAS_DEMON_GATE", False):
            res = self._run_organism(self._organism(), "python -c \"print('ok')\"")
        self.assertEqual(res["lifecycle_status"], "BLOCKED_BY_DEMON")
        self.assertEqual(res["reason"], "DEMON_GATE_UNAVAILABLE")
        self.assertFalse(any("Barriera balistica" in line for line in res["audit_trail"]))
        self.assertFalse(any("[6. PEIRA]" in line for line in res["audit_trail"]))

    def test_organism_allowed_command_reaches_peira(self):
        """Un comando ammesso dal gate viene eseguito e misurato da PEIRA."""
        res = self._run_organism(self._organism(), "python -c \"print('GATE ALLOW OK')\"")
        self.assertEqual(res["lifecycle_status"], "HEXAD_ABSOLUTE_CONVERGENCE")
        self.assertIn("GATE ALLOW OK", res["physical_stdout"])

    def _call_mcp_trial(self, command):
        server = os.path.join(os.path.dirname(os.path.abspath(__file__)), "peira_mcp.py")
        request = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "peira_execute_sandboxed_trial",
                       "arguments": {"command": command, "cwd": self.workspace}}
        }
        proc = subprocess.run(
            [sys.executable, server], input=json.dumps(request) + "\n",
            capture_output=True, text=True, timeout=30
        )
        response = json.loads(proc.stdout.strip().splitlines()[0])
        return response["result"], json.loads(response["result"]["content"][0]["text"])

    def test_mcp_trial_blocked_by_gate(self):
        """Lo strumento MCP rifiuta i comandi bloccati senza eseguirli."""
        result, payload = self._call_mcp_trial("echo DROP TABLE users")
        self.assertTrue(result.get("isError"))
        self.assertFalse(payload["execution_occurred"])
        self.assertIn("database_destruction", payload["matched_rules"])

    def test_mcp_trial_allowed_executes(self):
        """Lo strumento MCP esegue i comandi ammessi dal gate."""
        result, payload = self._call_mcp_trial("python -c \"print('MCP OK')\"")
        self.assertNotIn("isError", result)
        self.assertEqual(payload["exit_code"], 0)
        self.assertIn("MCP OK", payload["stdout_snippet"])


if __name__ == "__main__":
    unittest.main()
