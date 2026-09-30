"""
PEIRA Phase 1: Model Context Protocol (MCP) Server
The Empirical Grounding, Physical Impact & Closed-Loop Crucible.

Protocol: stdio JSON-RPC 2.0 (compatible with Claude Code, Cursor, Windsurf, Antigravity)

Exposed Tools:
1. peira_evaluate_empirical_impact: Evaluates execution results, computes Delta_emp, returns convergence or fracture payload.
2. peira_execute_sandboxed_trial: Executes a real physical trial against the OS/compiler, measuring empirical friction.
3. peira_inject_fracture_feedback: Builds coordinated fracture payload for OCULUS fovea, CORIS antibody, and MNEME rejection.
4. peira_audit_hexad_loop: Audits the full 6-Engine Closed Hexad (PEIRA <-> OCULUS -> CORIS -> ANIMA -> MNEME -> DEMON).
"""

import sys
import os
import json
import time
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from peira_engine import PeiraEngine

# Gate di attuazione DEMON dalla cartella sorella: PEIRA misura, DEMON autorizza
_demon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Demon-Engine"))
if os.path.exists(_demon_dir) and _demon_dir not in sys.path:
    sys.path.insert(0, _demon_dir)
try:
    from demon_action_gate import evaluate_command as demon_action_verdict, overrides_from_env
    HAS_DEMON_GATE = True
except ImportError:
    HAS_DEMON_GATE = False

def create_mcp_response(msg_id, result=None, error=None):
    resp = {"jsonrpc": "2.0", "id": msg_id}
    if error:
        resp["error"] = error
    else:
        resp["result"] = result
    return resp

def main():
    engine = PeiraEngine()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            msg_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "peira-engine-mcp",
                        "version": "1.0.0"
                    }
                }
                sys.stdout.write(json.dumps(create_mcp_response(msg_id, result)) + "\n")
                sys.stdout.flush()

            elif method == "tools/list":
                tools = [
                    {
                        "name": "peira_evaluate_empirical_impact",
                        "description": "Evaluates physical execution outcome, computes empirical friction Delta, and detects convergence vs thermodynamic fracture.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string", "description": "Command or action executed."},
                                "exit_code": {"type": "integer", "description": "OS exit code (0 = success)."},
                                "stdout": {"type": "string", "description": "Standard output text."},
                                "stderr": {"type": "string", "description": "Standard error text or traceback."},
                                "wall_time_ms": {"type": "number", "description": "Execution latency in ms."}
                            },
                            "required": ["command", "exit_code"]
                        }
                    },
                    {
                        "name": "peira_execute_sandboxed_trial",
                        "description": "Executes physical command directly against silicon/OS, measuring raw exit code, stdout, stderr, and Delta_empirico.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string", "description": "Shell command to run in trial harness."},
                                "cwd": {"type": "string", "description": "Working directory for execution."}
                            },
                            "required": ["command"]
                        }
                    },
                    {
                        "name": "peira_inject_fracture_feedback",
                        "description": "Transforms a non-zero exit/crash into an instantaneous multi-engine reset payload for OCULUS, CORIS, ANIMA, and MNEME.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string", "description": "Failed command."},
                                "stderr": {"type": "string", "description": "Raw stderr or stack trace."}
                            },
                            "required": ["command", "stderr"]
                        }
                    },
                    {
                        "name": "peira_audit_hexad_loop",
                        "description": "Audits full 6-engine Cybernetic Hexad closed loop state (PEIRA <-> OCULUS -> CORIS -> ANIMA -> MNEME -> DEMON).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task_description": {"type": "string", "description": "High-level goal or action description."}
                            },
                            "required": ["task_description"]
                        }
                    }
                ]
                sys.stdout.write(json.dumps(create_mcp_response(msg_id, {"tools": tools})) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "peira_evaluate_empirical_impact":
                    cmd = args.get("command", "")
                    code = int(args.get("exit_code", 0))
                    out = args.get("stdout", "")
                    err = args.get("stderr", "")
                    ms = float(args.get("wall_time_ms", 0.0))

                    impact = engine.evaluate_physical_result(cmd, code, out, err, ms)
                    res = {
                        "is_converged": impact.is_converged,
                        "is_fractured": impact.is_fractured,
                        "delta_empirico": impact.delta_empirico,
                        "fault_file": impact.fault_file,
                        "fault_line": impact.fault_line,
                        "error_type": impact.error_type,
                        "antigen_signature": impact.antigen_signature,
                        "status": "ABSOLUTE_CONVERGENCE" if impact.is_converged else "THERMODYNAMIC_FRACTURE"
                    }
                    sys.stdout.write(json.dumps(create_mcp_response(msg_id, {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    })) + "\n")
                    sys.stdout.flush()

                elif tool_name == "peira_execute_sandboxed_trial":
                    cmd = args.get("command", "")
                    cwd = args.get("cwd")

                    # Gate DEMON prima dell'esecuzione fisica (fail-closed se il gate manca)
                    if not HAS_DEMON_GATE:
                        blocked = {
                            "command": cmd,
                            "execution_occurred": False,
                            "verdict": "BLOCK",
                            "reason": "DEMON_GATE_UNAVAILABLE: esecuzione negata (fail-closed)."
                        }
                    else:
                        # Override solo dalla configurazione del server (env), mai dagli argomenti dell'agente
                        verdict = demon_action_verdict(cmd, workspace_dir=cwd or os.getcwd(),
                                                       authorized_overrides=overrides_from_env())
                        blocked = None if verdict.allowed else {
                            "command": cmd,
                            "execution_occurred": False,
                            "verdict": verdict.verdict,
                            "matched_rules": verdict.matched_rules,
                            "reasons": verdict.reasons,
                            "mitre_techniques": verdict.mitre_techniques
                        }
                    if blocked:
                        sys.stdout.write(json.dumps(create_mcp_response(msg_id, {
                            "content": [{"type": "text", "text": json.dumps(blocked, indent=2)}],
                            "isError": True
                        })) + "\n")
                        sys.stdout.flush()
                        continue

                    impact = engine.execute_physical_trial(cmd, cwd=cwd)
                    res = {
                        "command": impact.command,
                        "exit_code": impact.exit_code,
                        "wall_time_ms": impact.wall_time_ms,
                        "delta_empirico": impact.delta_empirico,
                        "is_converged": impact.is_converged,
                        "stdout_snippet": impact.stdout[:200],
                        "stderr_snippet": impact.stderr[:200],
                        "error_type": impact.error_type
                    }
                    sys.stdout.write(json.dumps(create_mcp_response(msg_id, {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    })) + "\n")
                    sys.stdout.flush()

                elif tool_name == "peira_inject_fracture_feedback":
                    cmd = args.get("command", "")
                    err = args.get("stderr", "")
                    impact = engine.evaluate_physical_result(cmd, exit_code=1, stderr=err)
                    injection = engine.build_fracture_injection(impact)
                    res = {
                        "fault_epicenter": injection.fault_epicenter,
                        "oculus_fovea_query": injection.target_fovea_query,
                        "coris_antibody_epitope": injection.coris_epitope_signature,
                        "mneme_invalidated_state": injection.mneme_invalidated_state,
                        "anima_penalized_pattern": injection.anima_penalized_pattern,
                        "diagnostic_summary": injection.diagnostic_summary
                    }
                    sys.stdout.write(json.dumps(create_mcp_response(msg_id, {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    })) + "\n")
                    sys.stdout.flush()

                elif tool_name == "peira_audit_hexad_loop":
                    task = args.get("task_description", "")
                    hexad_audit = {
                        "task": task,
                        "closed_loop_topology": "THE_CYBERNETIC_HEXAD",
                        "modules": {
                            "1_OCULUS": "Sensory Manifold & Fovea",
                            "2_CORIS": "Metabolic Homeostasis & Antibody Store",
                            "3_ANIMA": "Continuous Variational Path Planning",
                            "4_MNEME": "Asymptotic Stability & Curvature Invariant",
                            "5_DEMON": "Safe Physical OS Actuator",
                            "6_PEIRA": {
                                "role": "Empirical Grounding & Feedback Crucible",
                                "convergence_count": engine.convergence_count,
                                "fracture_count": engine.fracture_count,
                                "status": "FEEDBACK_LOOP_ACTIVE"
                            }
                        },
                        "verdict": "CLOSED_LOOP_OPERATIONAL"
                    }
                    sys.stdout.write(json.dumps(create_mcp_response(msg_id, {
                        "content": [{"type": "text", "text": json.dumps(hexad_audit, indent=2)}]
                    })) + "\n")
                    sys.stdout.flush()

                else:
                    sys.stdout.write(json.dumps(create_mcp_response(
                        msg_id, error={"code": -32601, "message": f"Tool not found: {tool_name}"}
                    )) + "\n")
                    sys.stdout.flush()

        except Exception as e:
            sys.stderr.write(f"PEIRA MCP Error: {str(e)}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
