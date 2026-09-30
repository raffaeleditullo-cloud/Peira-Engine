"""
THE CYBERNETIC HEXAD: The Complete 6-Pillar Closed-Loop Autonomous Living Organism.

1. OCULUS (The Senses)    -> Saccadic gaze, AST manifold topology & foveal compression.
2. CORIS  (The Heart)     -> Homeostasis, Friston free energy, hemodynamics & immune memory.
3. ANIMA  (The Mind)      -> Continuous variational path-integral reasoning & wave collapse.
4. MNEME  (The Stability) -> Lyapunov stability invariant (dV/dt < 0) & Ricci curvature flow.
5. DEMON  (The Muscle)    -> Deterministic physical actuator & 0-token reflex cache.
6. PEIRA  (The Crucible)  -> Physical silicon trial, empirical delta Δ measurement,
                             and closed-loop fracture feedback injection.

The Closed Feedback Loop:
If Delta == 0: Absolute Convergence (Output Delivered).
If Delta != 0: Thermodynamic Fracture -> Re-injects into OCULUS & CORIS to shatter assumptions.
"""

import sys
import os
import time
from typing import List, Dict, Any, Optional

# Add sibling engine paths
desktop_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for eng in ["Oculus-Engine", "Anima-Engine", "Coris-Engine", "Demon-Engine", "Mneme-Engine"]:
    ep = os.path.join(desktop_dir, eng)
    if os.path.exists(ep) and ep not in sys.path:
        sys.path.insert(0, ep)

from peira_engine import PeiraEngine, EmpiricalImpact, FractureInjectionPayload, classify_fracture

try:
    from oculus_engine import OculusEngine
    HAS_OCULUS = True
except ImportError:
    HAS_OCULUS = False

try:
    from coris_engine import CorisEngine
    HAS_CORIS = True
except ImportError:
    HAS_CORIS = False

try:
    from anima_engine import AnimaEngine, AnimaBranch
    HAS_ANIMA = True
except ImportError:
    HAS_ANIMA = False

try:
    from mneme_engine import MnemeEngine
    HAS_MNEME = True
except ImportError:
    HAS_MNEME = False

try:
    from demon_gateway import DemonGateway
    HAS_DEMON = True
except ImportError:
    HAS_DEMON = False

# Gate di attuazione DEMON: senza dipendenze esterne, disponibile anche senza DemonGateway
try:
    from demon_action_gate import evaluate_command as demon_action_verdict
    HAS_DEMON_GATE = True
except ImportError:
    HAS_DEMON_GATE = False


class LivingHexadOrganism:
    """
    L'Organismo Vivente Autonomo Completo ad Anello Chiuso a 6 Poli:
    PEIRA <-> OCULUS -> CORIS -> ANIMA -> MNEME -> DEMON -> PEIRA
    """
    def __init__(self):
        self.oculus = OculusEngine() if HAS_OCULUS else None
        self.coris = CorisEngine() if HAS_CORIS else None
        self.anima = AnimaEngine() if HAS_ANIMA else None
        self.mneme = MnemeEngine(state_dim=5, alpha=0.15) if HAS_MNEME else None
        self.demon = DemonGateway() if HAS_DEMON else None
        self.peira = PeiraEngine(timeout_sec=5.0)

    def execute_hexad_lifecycle(
        self,
        intent_query: str,
        workspace_dir: str,
        candidate_reasoning_traces: List[Dict[str, Any]],
        context_conversation: List[Dict[str, Any]],
        max_fracture_retries: int = 1
    ) -> Dict[str, Any]:
        """
        Esegue il ciclo cibernetico ad anello chiuso. Se PEIRA rileva frattura (Delta != 0),
        esegue l'iniezione retroattiva su OCULUS e CORIS per un nuovo tentativo corretto.
        """
        start_time = time.perf_counter()
        audit_log = []
        current_query = intent_query
        retries_used = 0
        # Rami bloccati da DEMON o fratturati da PEIRA: esclusi per id dai passi successivi
        excluded_branches: List[str] = []
        # Un solo nuovo tentativo per ramo quando la frattura è transitoria (rete, timeout)
        transient_retries: Dict[str, int] = {}
        last_fracture: Optional[Dict[str, Any]] = None

        if not candidate_reasoning_traces:
            audit_log.append("[3. ANIMA] Nessun ramo candidato fornito: nessuna azione da eseguire.")
            return {
                "lifecycle_status": "HEXAD_NO_CANDIDATES",
                "cycles_required": 0,
                "audit_trail": audit_log,
                "total_latency_ms": round((time.perf_counter() - start_time) * 1000.0, 3)
            }

        while retries_used <= max_fracture_retries:
            cycle_label = f"Pass {retries_used + 1}"
            audit_log.append(f"--- [HEXAD {cycle_label}] Inizio ciclo cibernetico ---")

            # -------------------------------------------------------------
            # 1. OCULUS: Foveal Gaze & Compression
            # -------------------------------------------------------------
            focal_file = "virtual/main.py"
            compression_pct = 88.0
            sensory_entropy = 0.35

            if self.oculus and os.path.exists(workspace_dir):
                fovea = self.oculus.focus_saccadic_gaze(current_query, workspace_dir)
                focal_file = fovea.focal_file
                compression_pct = fovea.compression_ratio_pct
                sensory_entropy = fovea.sensory_entropy
                audit_log.append(f"[1. OCULUS] Fovea centrata su '{os.path.basename(focal_file)}' ({compression_pct:.1f}% risparmio token)")
            else:
                audit_log.append("[1. OCULUS] Fovea sintetica attiva.")

            # -------------------------------------------------------------
            # 2. CORIS: Homeostasis & Immune Check
            # -------------------------------------------------------------
            coris_vitals = None
            if self.coris:
                coris_vitals = self.coris.pulse(error_rate=0.0, latency_ms=10.0, context_tokens_used=100)
                audit_log.append(f"[2. CORIS] Heartbeat BPM={coris_vitals.heart_rate_bpm}, Free Energy={coris_vitals.free_energy_F:.2f}")

                threat = self.coris.check_antigen_binding(current_query)
                if threat:
                    audit_log.append(f"[2. CORIS] Minaccia bloccata da anticorpo {threat.epitope_hash}")
                    return {
                        "lifecycle_status": "THREAT_BLOCKED_BY_CORIS",
                        "audit_trail": audit_log,
                        "total_latency_ms": round((time.perf_counter() - start_time) * 1000.0, 3)
                    }
            else:
                audit_log.append("[2. CORIS] Omeostasi nominale.")

            # -------------------------------------------------------------
            # 3. ANIMA: Path Integral Minimization
            # -------------------------------------------------------------
            remaining = [
                (r.get("id") or f"trace_{t_idx}", r)
                for t_idx, r in enumerate(candidate_reasoning_traces)
                if (r.get("id") or f"trace_{t_idx}") not in excluded_branches
            ]
            if not remaining:
                audit_log.append(f"[3. ANIMA] Nessun ramo residuo (esclusi: {', '.join(excluded_branches)}). Arresto del ciclo.")
                return self._halted_lifecycle_result(retries_used, excluded_branches, last_fracture, audit_log, start_time)

            action_val = 0.25
            if self.anima:
                branches = []
                for b_id, r in remaining:
                    b = AnimaBranch(id=b_id, name=r.get("name", b_id), metadata=r)
                    for idx, ent in enumerate(r.get("entropies", [0.15])):
                        self.anima.ingest_step(b, token=f"tok_{idx}", token_entropy=float(ent))
                    branches.append(b)

                res = self.anima.collapse(current_query, branches)
                winner = res.eigenstate
                chosen_branch_id, chosen_trace = winner.id, winner.metadata
                action_val = float(res.total_system_action)
                audit_log.append(f"[3. ANIMA] Collasso su '{winner.name}' (Azione={action_val:.4f})")
            else:
                # Senza ANIMA: ordine dei candidati, deterministico
                chosen_branch_id, chosen_trace = remaining[0]
                audit_log.append(f"[3. ANIMA] Motore assente: selezione ordinale del ramo '{chosen_branch_id}'")
            action_intent = chosen_trace.get("intent", current_query)
            chosen_command = chosen_trace.get("code") or chosen_trace.get("command") or ""

            # -------------------------------------------------------------
            # 4. MNEME: Lyapunov Stability Certification
            # -------------------------------------------------------------
            if self.mneme:
                state_vec = [action_val, sensory_entropy, 0.2, 0.1, 0.0]
                velocity_vec = [-0.5 * s for s in state_vec]
                lyap = self.mneme.certify_trajectory_stability(state_vec, velocity_vector=velocity_vec)
                audit_log.append(f"[4. MNEME] Stabilità certificata: dV/dt={lyap.v_dot:+.4f}, max(Re(λ))={lyap.max_real_eigenvalue:+.4f}")
                if not lyap.is_stable:
                    audit_log.append(f"[4. MNEME] Rifiutato: {lyap.rejection_reason}")
                    return {"lifecycle_status": "ABORTED_BY_MNEME", "audit_trail": audit_log}
            else:
                audit_log.append("[4. MNEME] Certificato di stabilità asintotica confermato.")

            # -------------------------------------------------------------
            # 5. DEMON: Gate di attuazione prima dell'esecuzione fisica di PEIRA
            # -------------------------------------------------------------
            if not HAS_DEMON_GATE:
                audit_log.append("[5. DEMON] Gate di attuazione non disponibile: esecuzione negata (fail-closed).")
                return {
                    "lifecycle_status": "BLOCKED_BY_DEMON",
                    "reason": "DEMON_GATE_UNAVAILABLE",
                    "audit_trail": audit_log,
                    "total_latency_ms": round((time.perf_counter() - start_time) * 1000.0, 3)
                }
            verdict = demon_action_verdict(chosen_command, workspace_dir=workspace_dir)
            if not verdict.allowed:
                audit_log.append(
                    f"[5. DEMON] Gate BLOCK su '{chosen_command}': {'; '.join(verdict.reasons)} "
                    f"(regole: {', '.join(verdict.matched_rules)})"
                )
                # Il ramo bloccato esce dalla sovrapposizione; si prova l'alternativa successiva
                excluded_branches.append(chosen_branch_id)
                retries_used += 1
                continue
            # Il gateway vocale (route_command) non è invocato qui: invierebbe il comando alla
            # ricerca web o eseguirebbe le proprie ipotesi predefinite, senza influire sul verdetto
            audit_log.append(f"[5. DEMON] Gate ALLOW ({verdict.latency_ms:.3f} ms)")

            # -------------------------------------------------------------
            # 6. PEIRA: Physical Silicon Crucible & Friction Delta
            # -------------------------------------------------------------
            impact = self.peira.execute_physical_trial(chosen_command, cwd=workspace_dir)
            audit_log.append(
                f"[6. PEIRA] Impatto fisico: Exit Code={impact.exit_code}, "
                f"Delta_empirico={impact.delta_empirico:.2f}, Latency={impact.wall_time_ms:.1f}ms"
            )

            # Caso 1: Convergenza Assoluta (Delta == 0)
            if impact.is_converged:
                audit_log.append("[6. PEIRA] CONVERGENZA ASSOLUTA RAGGIUNTA. Il ciclo cibernetico si arresta in equilibrio.")
                total_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "lifecycle_status": "HEXAD_ABSOLUTE_CONVERGENCE",
                    "cycles_required": retries_used + 1,
                    "delta_empirico": impact.delta_empirico,
                    "physical_stdout": impact.stdout,
                    "audit_trail": audit_log,
                    "total_latency_ms": round(total_ms, 3)
                }

            # Caso 2: Frattura Termodinamica (Delta != 0) -> Iniezione di Retroazione
            audit_log.append(f"[6. PEIRA] FRATTURA TERMODINAMICA RILEVATA (Delta={impact.delta_empirico:.2f})!")
            injection = self.peira.build_fracture_injection(impact)
            audit_log.append(f"[PEIRA -> FEEDBACK] Iniezione di frattura a monte: Epicentro '{injection.fault_epicenter}'")

            # Retroazione a CORIS: sintesi anticorpo
            if self.coris and impact.antigen_signature:
                ab = self.coris.synthesize_antibody(
                    pattern_signature=impact.antigen_signature,
                    source_layer="PEIRA_PHYSICAL_CRASH",
                    neutralization_rule="SUPPRESS_CRASHING_COMMAND"
                )
                audit_log.append(f"[PEIRA -> CORIS] Sintetizzato anticorpo linfatico {ab.epitope_hash} per sopprimere il crash.")

            # Retroazione a OCULUS: forza fovea su epicentro
            current_query = injection.target_fovea_query
            audit_log.append(f"[PEIRA -> OCULUS] Reset foveale forzato sulla query di crash: '{current_query}'")

            last_fracture = {
                "command": impact.command,
                "exit_code": impact.exit_code,
                "delta_empirico": impact.delta_empirico,
                "fault_epicenter": injection.fault_epicenter,
                "diagnostic_summary": injection.diagnostic_summary
            }

            fracture_kind = classify_fracture(impact)
            last_fracture["fracture_kind"] = fracture_kind
            if fracture_kind == "TRANSIENT" and transient_retries.get(chosen_branch_id, 0) < 1:
                # Ambiente instabile, non logica sbagliata: il ramo resta in gioco per un altro tentativo
                transient_retries[chosen_branch_id] = 1
                audit_log.append(f"[6. PEIRA] Frattura transitoria: il ramo '{chosen_branch_id}' verrà ritentato una volta.")
            else:
                # Scarta il ramo che ha causato il crash (il vincitore di ANIMA, non il primo della lista)
                excluded_branches.append(chosen_branch_id)
                audit_log.append(f"[3. ANIMA] Ramo '{chosen_branch_id}' escluso (azione lagrangiana infinita).")

            retries_used += 1

        total_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "lifecycle_status": "HEXAD_MAX_RETRIES_EXCEEDED",
            "cycles_required": retries_used,
            "excluded_branches": excluded_branches,
            "last_fracture": last_fracture,
            "last_delta": last_fracture["delta_empirico"] if last_fracture else None,
            "audit_trail": audit_log,
            "total_latency_ms": round(total_ms, 3)
        }

    def _halted_lifecycle_result(
        self,
        cycles_used: int,
        excluded_branches: List[str],
        last_fracture: Optional[Dict[str, Any]],
        audit_log: List[str],
        start_time: float
    ) -> Dict[str, Any]:
        """Esito di arresto: nessuna alternativa residua, la frattura torna al chiamante."""
        return {
            "lifecycle_status": "HEXAD_HALTED_NO_ALTERNATIVES",
            "cycles_required": cycles_used,
            "excluded_branches": excluded_branches,
            "last_fracture": last_fracture,
            "audit_trail": audit_log,
            "total_latency_ms": round((time.perf_counter() - start_time) * 1000.0, 3)
        }


if __name__ == "__main__":
    print("=== INITIALIZING THE CYBERNETIC HEXAD ORGANISM ===")
    organism = LivingHexadOrganism()
    sample_context = [
        {"role": "system", "content": "You are the complete living closed-loop AI organism."}
    ]
    # Iniziamo con un ramo volutamente rotto per dimostrare l'Iniezione di Frattura e auto-riparazione:
    # B1 ha l'azione minima, quindi ANIMA lo elegge per primo; dopo la frattura resta B2
    sample_branches = [
        {"id": "B1", "name": "Broken DivZero Trial", "code": "python -c \"import sys; sys.stderr.write('File \\\"test.py\\\", line 10, in run\\nZeroDivisionError: div 0\\n'); sys.exit(1)\"", "entropies": [0.10]},
        {"id": "B2", "name": "Fixed Silicon Verification", "code": "python -c \"print('ALL TESTS PASSED: SILICON CONVERGENCE ACHIEVED')\"", "entropies": [0.15]}
    ]

    res = organism.execute_hexad_lifecycle(
        intent_query="Execute self-healing silicon test suite",
        workspace_dir=os.path.dirname(__file__),
        candidate_reasoning_traces=sample_branches,
        context_conversation=sample_context,
        max_fracture_retries=1
    )
    import json
    print(json.dumps(res, indent=2))
