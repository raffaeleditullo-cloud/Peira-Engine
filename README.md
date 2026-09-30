<p align="center">
  <img src="logo.png" width="300" alt="PEIRA Engine Logo" />
</p>

<h1 align="center">PEIRA ENGINE</h1>

<p align="center">
  <b>The Empirical Grounding, Physical Impact & Closed-Loop Crucible</b><br>
  <i>The 6th Pillar of the Cybernetic Oracle Hexad (From Open Chain to Closed Loop)</i>
</p>

<p align="center">
  <a href="#theoretical-foundations"><img src="https://img.shields.io/badge/Empirical_Delta-%CE%94_%3D_%E2%88%A5y__real_--_y__sim%E2%88%A5-00f5d4.svg" alt="Empirical Delta"></a>
  <a href="#theoretical-foundations"><img src="https://img.shields.io/badge/Closed_Loop-Cybernetic_Hexad-7b2cbf.svg" alt="Closed Loop"></a>
  <a href="#mcp-protocol"><img src="https://img.shields.io/badge/Protocol-Model_Context_Protocol_(MCP)-blue.svg" alt="MCP Protocol"></a>
</p>

---

## 🏛️ The Cybernetic Hexad: The Closed Feedback Loop

Without **PEIRA**, multi-agent systems exist solely in symbolic abstraction (an open feedforward chain). **PEIRA** provides empirical grounding: it collides theoretical outputs against the non-negotiable laws of silicon, OS, hardware, and compilers.

```
                       ┌───────────────────────────────┐
                       │          1. OCULUS            │
                       │     (Retina & Manifold)       │
                       └──────────────▲────────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               │                                             │
               │ (Se Δ ≠ 0: Frattura Empirica)               │ Iniezione Coordinate
               │ Reset Foveale su Traceback                  │ Compresse
               │                                             ▼
┌──────────────┴────────────────┐             ┌───────────────────────────────┐
│          6. PEIRA             │             │          2. CORIS             │
│    (Crucible & Silicio)       │             │   (Homeostasis & Heart)       │
│  Misura Δ = y_real - y_pred   │             └──────────────┬────────────────┘
└──────────────▲────────────────┘                            │
               │                                             │ Ambiente Asettico
               │ Esecuzione Fisica                           │ & Pressione Bassa
               │ Shell / Docker / API                        ▼
┌──────────────┴────────────────┐             ┌───────────────────────────────┐
│          5. DEMON             │             │          3. ANIMA             │
│     (Muscolo & Barrier)       │             │   (Variational Trajectory)    │
│  Actuation Blast-Radius = 0   │             └──────────────┬────────────────┘
└───────────────────────────────┘                            │
               ▲                                             │ Minima Azione
               │                                             │ Continua
               └──────────────────────┬──────────────────────┘
                                      │
                       ┌──────────────▼────────────────┐
                       │          4. MNEME             │
                       │   (Lyapunov Stability)        │
                       │   Certificato Spettrale λ < 0 │
                       └───────────────────────────────┘
```

1. **OCULUS (The Senses):** Compresses reality into essential AST topological coordinates ($\mathcal{M}$).
2. **CORIS (The Heart):** Regulates metabolic free energy ($\mathcal{F}$) and synthesizes immune antibodies.
3. **ANIMA (The Mind):** Computes continuous variational path-integral geodesics minimizing Lagrangian action ($\delta S = 0$).
4. **MNEME (The Stability & Memory):** Certifies asymptotic convergence via the Lyapunov invariant $\dot{V} \le -\alpha \|x-x^*\|^2$ and Ricci flow.
5. **DEMON (The Muscle):** Enforces hard OS security boundaries ($\mathcal{C}_{safe}$) and zero-token reflex actuation.
6. **PEIRA (The Crucible):** Tests physical execution against silicon, measuring empirical friction $\Delta$, and closing the feedback loop.

---

## 📐 Mathematical & Physical Foundations

### 1. The Empirical Friction Delta
PEIRA computes the distance between physical reality and theoretical expectation:
$$\Delta_{\text{empirico}} = \|\mathbf{y}_{\text{fisico}} - \hat{\mathbf{y}}_{\text{simulato}}\|$$

Where $\mathbf{y}_{\text{fisico}} = [\text{exit\_code}, \text{error\_severity}, \text{latency\_drift}, \text{output\_diff}]$ and $\hat{\mathbf{y}}_{\text{simulato}} = [0, 0, 0, 0]$.

### 2. The Binary States of PEIRA

#### State 1: Absolute Convergence ($\Delta_{\text{empirico}} = 0$)
- **Condition:** Exit code == 0, output matches contract, zero compiler warnings, zero unhandled signals.
- **Action:** Releases the invariant to the environment/user. The cybernetic organism halts in stable homeostasis.

#### State 2: Thermodynamic Fracture ($\Delta_{\text{empirico}} \ne 0$)
- **Condition:** Segmentation fault, non-zero exit code, unhandled exception, syntax error.
- **Action (The Reality Reset):** Dissects the physical traceback and injects raw crash coordinates:
  - **OCULUS:** Forces an instant saccadic foveal jump directly to the crash line (`file:line`).
  - **CORIS:** Synthesizes an instantaneous neutralizing antibody targeting the crash epitope signature.
  - **MNEME:** Invalidates the previous basin of attraction ($\dot{V} \ge 0$).
  - **ANIMA:** Penalizes the failed variational branch with infinite Lagrangian action cost.

---

## ⚡ Model Context Protocol (MCP) Interface

PEIRA exposes 4 tools over stdio JSON-RPC 2.0:

| Tool | Signature | Description |
| :--- | :--- | :--- |
| `peira_evaluate_empirical_impact` | `(command, exit_code, stdout, stderr)` | Evaluates execution results, computes $\Delta_{\text{empirico}}$, returns convergence vs fracture verdict. |
| `peira_execute_sandboxed_trial` | `(command, cwd)` | Runs a real physical command against silicon/OS, capturing raw exit code and telemetry. |
| `peira_inject_fracture_feedback` | `(command, stderr)` | Formats the multi-engine fracture injection payload for OCULUS, CORIS, ANIMA, and MNEME. |
| `peira_audit_hexad_loop` | `(task_description)` | Audits the 6-engine Cybernetic Hexad closed loop operational status. |

---

## 🚀 Quickstart

### 1. Run Unit Tests
```bash
python test_peira_engine.py
```

### 2. Run the Full Living Hexad Organism (Closed Loop)
```bash
python peira_hexad_organism.py
```

### 3. Launch as an MCP Server
```json
{
  "mcpServers": {
    "peira-engine": {
      "command": "python",
      "args": ["path/to/Peira-Engine/peira_mcp.py"]
    }
  }
}
```

---

## 📜 License
MIT License. Copyright (c) 2026 Raffaele Di Tullo.
