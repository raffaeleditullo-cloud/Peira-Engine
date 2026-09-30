"""
PEIRA Engine: The Empirical Grounding, Physical Impact & Closed-Loop Crucible.

Pillar 6 of the Cybernetic Oracle Hexad:
1. OCULUS (The Senses)    -> Sensory manifold & foveal compression.
2. CORIS  (The Heart)     -> Homeostasis, free energy & immune antibodies.
3. ANIMA  (The Mind)      -> Variational path-integral & continuous action phase.
4. MNEME  (The Stability) -> Lyapunov stability invariant & Ricci curvature flow.
5. DEMON  (The Muscle)    -> Safe deterministic OS enclave actuation.
6. PEIRA  (The Crucible)  -> Physical silicon trial, empirical delta Δ measurement,
                             and closed-loop fracture feedback injection.

Mathematical Formulation:
- Empirical Delta: Delta_emp = || y_physical - y_simulated ||
- State 1: Absolute Convergence (Delta_emp == 0) -> Release invariant to user/reality.
- State 2: Thermodynamic Fracture (Delta_emp != 0) -> Shatter theoretical manifold &
  inject raw failure coordinates directly into OCULUS, CORIS, and MNEME.
"""

import os
import sys
import time
import re
import subprocess
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class EmpiricalImpact:
    """Risultato dell'impatto fisico reale contro il silicio/OS."""
    command: str
    exit_code: int
    wall_time_ms: float
    stdout: str
    stderr: str
    delta_empirico: float               # Distanza empirica da y* (0 = convergenza perfetta)
    is_converged: bool                  # True se Delta == 0
    is_fractured: bool                  # True se Delta > 0 (crash / errore reale)
    fault_file: Optional[str] = None    # File su cui si è verificata la frattura
    fault_line: Optional[int] = None    # Riga del crash
    error_type: Optional[str] = None    # Tipo eccezione (es. AssertionError, SegFault, ImportError)
    antigen_signature: Optional[str] = None # Firma per la generazione anticorpi in CORIS
    raw_traceback: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class FractureInjectionPayload:
    """Payload di frattura iniettato a monte per resettare il ciclo vitale."""
    fault_epicenter: str                # file:line
    target_fovea_query: str             # Query per forzare il saccade di OCULUS
    coris_epitope_signature: str        # Firma antigene per CORIS
    mneme_invalidated_state: List[float]# Vettore di stato rigettato da marcare instabile
    anima_penalized_pattern: str        # Pattern da sopprimere in ANIMA
    diagnostic_summary: str


class PeiraEngine:
    """
    Il Banco di Prova Empirico e Sensore di Attrito Fisico (Il 6° Motore).
    Chiude l'anello di retroazione cibernetica tra la teoria e la realtà fisica.
    """

    def __init__(self, timeout_sec: float = 10.0):
        self.timeout_sec = timeout_sec
        self.trial_history: List[EmpiricalImpact] = []
        self.convergence_count = 0
        self.fracture_count = 0

    # =========================================================================
    # 1. MISURA DELL'ATTRITO EMPIRICO E CONTROLLO BINARIO
    #    Delta_emp = || y_physical - y_simulated ||
    # =========================================================================
    def evaluate_physical_result(
        self,
        command: str,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        wall_time_ms: float = 0.0,
        expected_exit_code: int = 0
    ) -> EmpiricalImpact:
        """
        Valuta i risultati grezzi dell'esecuzione fisica e calcola la discrepanza empirica Delta.
        """
        out_clean = stdout.strip()
        err_clean = stderr.strip()

        # Calcolo di Delta Empirico
        code_mismatch = abs(exit_code - expected_exit_code)
        has_err_output = 1.0 if err_clean and exit_code != 0 else 0.0
        
        # Delta = 0 solo se exit_code combacia e non ci sono panic/fatal errors
        delta = float(code_mismatch * 2.0 + has_err_output)
        
        is_converged = (delta == 0.0 and exit_code == expected_exit_code)
        is_fractured = not is_converged

        fault_file = None
        fault_line = None
        err_type = None
        raw_tb = None
        antigen_sig = None

        if is_fractured:
            self.fracture_count += 1
            fault_file, fault_line, err_type, raw_tb = self._dissect_failure(command, out_clean, err_clean)
            # Sintesi firma antigene univoca per CORIS
            raw_target = f"{command}:{err_type}:{fault_file}:{fault_line}"
            antigen_sig = "AB_" + hashlib.sha256(raw_target.encode()).hexdigest()[:12]
        else:
            self.convergence_count += 1

        impact = EmpiricalImpact(
            command=command,
            exit_code=exit_code,
            wall_time_ms=wall_time_ms,
            stdout=out_clean,
            stderr=err_clean,
            delta_empirico=delta,
            is_converged=is_converged,
            is_fractured=is_fractured,
            fault_file=fault_file,
            fault_line=fault_line,
            error_type=err_type,
            antigen_signature=antigen_sig,
            raw_traceback=raw_tb
        )
        self.trial_history.append(impact)
        return impact

    # =========================================================================
    # 2. ESECUZIONE DIRETTA NEL BANCO DI PROVA (Physical Trial Runner)
    # =========================================================================
    def execute_physical_trial(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> EmpiricalImpact:
        """
        Lancia direttamente il comando nell'ambiente fisico reale (shell/sandbox),
        cattura il responso hardware/OS e calcola Delta_empirico.
        """
        t_start = time.perf_counter()
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            wall_ms = (time.perf_counter() - t_start) * 1000.0
            return self.evaluate_physical_result(
                command=command,
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
                wall_time_ms=wall_ms
            )
        except subprocess.TimeoutExpired as te:
            wall_ms = (time.perf_counter() - t_start) * 1000.0
            return self.evaluate_physical_result(
                command=command,
                exit_code=124,  # Standard timeout exit code
                stdout=te.stdout.decode() if te.stdout else "",
                stderr=f"TIMEOUT EXPIRED: Execution exceeded limit of {self.timeout_sec}s",
                wall_time_ms=wall_ms
            )
        except Exception as ex:
            wall_ms = (time.perf_counter() - t_start) * 1000.0
            return self.evaluate_physical_result(
                command=command,
                exit_code=255,
                stdout="",
                stderr=f"FATAL LAUNCH EXCEPTION: {type(ex).__name__}: {str(ex)}",
                wall_time_ms=wall_ms
            )

    # =========================================================================
    # 3. GENERAZIONE DEL FEEDBACK DI FRATTURA (Closed-Loop Reality Reset)
    # =========================================================================
    def build_fracture_injection(self, impact: EmpiricalImpact) -> FractureInjectionPayload:
        """
        Trasforma l'impatto di frattura Delta > 0 nel payload cibernetico
        da iniettare simultaneamente in OCULUS, CORIS, ANIMA e MNEME.
        """
        assert impact.is_fractured, "Impossibile creare injection da uno stato convergente"

        epicenter = f"{impact.fault_file or 'unknown'}:{impact.fault_line or 0}"
        fovea_query = f"{impact.error_type or 'Error'} in {os.path.basename(impact.fault_file or '')} line {impact.fault_line or 0}"
        
        # Stato rigettato per MNEME con divergenza forzata
        invalidated_st = [1.0, 0.95, 0.90, 0.85, 1.0]

        summary = (
            f"FRACTURE_EVENT: Exit code {impact.exit_code} | Error: {impact.error_type} "
            f"at {epicenter} | Delta={impact.delta_empirico:.2f}"
        )

        return FractureInjectionPayload(
            fault_epicenter=epicenter,
            target_fovea_query=fovea_query,
            coris_epitope_signature=impact.antigen_signature or "AB_UNKNOWN",
            mneme_invalidated_state=invalidated_st,
            anima_penalized_pattern=impact.command[:60],
            diagnostic_summary=summary
        )

    # =========================================================================
    # PARSING ANATOMICO DEL TRACEBACK / SILICON RESPONSE
    # =========================================================================
    def _dissect_failure(
        self,
        command: str,
        stdout: str,
        stderr: str
    ) -> Tuple[Optional[str], Optional[int], Optional[str], Optional[str]]:
        """Estrae con precisione chirurgica il file, riga, tipo errore e traceback."""
        combined = f"{stderr}\n{stdout}"
        
        # 1. Ricerca pattern Traceback Python: File "...", line X, in ...
        py_matches = re.findall(r'File "([^"]+)", line (\d+)(?:, in (\w+))?', combined)
        if py_matches:
            last_match = py_matches[-1]
            fault_file = last_match[0]
            fault_line = int(last_match[1])
            
            # Cerca il tipo di eccezione
            exc_match = re.search(r'([A-Za-z0-9_]+Error|Exception|Panic|Signal|Fatal):? (.+)', combined)
            err_type = exc_match.group(1) if exc_match else "ExecutionFailure"
            raw_tb = combined[-400:].strip()
            return fault_file, fault_line, err_type, raw_tb

        # 2. Ricerca pattern C/C++/Rust/GCC: file.cpp:123:45: error: ...
        gcc_match = re.search(r'([A-Za-z0-9_./\\-]+\.[a-zA-Z0-9]+):(\d+):(?:\d+:)?\s*(error|fatal error):?\s*(.+)', combined, re.IGNORECASE)
        if gcc_match:
            fault_file = gcc_match.group(1)
            fault_line = int(gcc_match.group(2))
            err_type = "CompilationError"
            return fault_file, fault_line, err_type, combined[-300:].strip()

        # 3. SegFault / Abort / Out of Memory
        if "Segmentation fault" in combined or "SIGSEGV" in combined:
            return None, None, "SegmentationFault", "SIGSEGV (Memory access violation)"
        if "AssertionError" in combined:
            return None, None, "AssertionError", combined[-250:].strip()

        # Fallback generico
        err_type = "CommandNonZeroExit"
        raw_tb = stderr[-200:].strip() if stderr else stdout[-200:].strip()
        return None, None, err_type, raw_tb


# =============================================================================
# CLASSIFICAZIONE DELLA FRATTURA: transitoria (ambiente) o deterministica (logica)
# =============================================================================
# Un ramo che fallisce per rete, timeout o risorse momentaneamente indisponibili può
# essere corretto: escluderlo per sempre dopo un solo tentativo scarterebbe una soluzione
# valida. Un'asserzione o un errore di sintassi, invece, si ripeterebbero identici.
TRANSIENT_ERROR_TYPES = {
    "TimeoutError", "ConnectionError", "ConnectionResetError", "ConnectionRefusedError",
    "ConnectionAbortedError", "BrokenPipeError", "InterruptedError", "BlockingIOError",
}
TRANSIENT_MARKERS = (
    "temporary failure in name resolution", "timed out", "etimedout", "econnreset",
    "econnrefused", "503 service unavailable", "502 bad gateway", "504 gateway timeout",
    "429 too many requests", "resource temporarily unavailable", "text file busy",
    "the process cannot access the file because it is being used by another process",
)
TIMEOUT_EXIT_CODE = 124


def classify_fracture(impact: EmpiricalImpact) -> str:
    """
    Ritorna "CONVERGED", "TRANSIENT" o "DETERMINISTIC".
    TRANSIENT solo per segnali espliciti di ambiente instabile; nel dubbio DETERMINISTIC,
    così un fallimento logico non viene mai ripetuto alla cieca.
    """
    if impact.is_converged:
        return "CONVERGED"
    if impact.exit_code == TIMEOUT_EXIT_CODE:
        return "TRANSIENT"
    if impact.error_type in TRANSIENT_ERROR_TYPES:
        return "TRANSIENT"
    raw = f"{impact.stderr}\n{impact.stdout}"
    # Riga d'eccezione anche senza traceback completo, es. "ConnectionResetError: peer reset"
    if re.search(r"\b(" + "|".join(sorted(TRANSIENT_ERROR_TYPES)) + r")\s*:", raw):
        return "TRANSIENT"
    text = raw.lower()
    if any(marker in text for marker in TRANSIENT_MARKERS):
        return "TRANSIENT"
    return "DETERMINISTIC"
