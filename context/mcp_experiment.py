#!/usr/bin/env python3
"""
context/mcp_experiment.py

Automated MCP experiment with real context-mode@1.0.169 over stdio JSON-RPC.
- Performs MCP handshake (initialize, notifications/initialized, tools/list).
- Indexes synthetic BitBake log via ctx_index according to schema.
- Searches for 3 unique error markers individually and batched via ctx_search.
- Verifies and asserts surrounding diagnostic context is preserved for each marker.
- Calls ctx_stats to record session statistics.
- Measures exact UTF-8 bytes and characters. Strictly NO token estimation / impersonation.
- Uses selectors for non-blocking I/O with true timeout.
- Redirects server stderr to a file to prevent pipe deadlock.
- Spawns server with cwd=PROJECT_ROOT, local PATH including .tools/node/bin, and CONTEXT_MODE_DIR.
- Saves raw MCP receipts to evidence/context/mcp_receipts.json.
- Saves benchmark metrics to evidence/context/benchmark.json.
"""

import json
import os
import selectors
import subprocess
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NODE_BIN = os.path.join(PROJECT_ROOT, ".tools", "node", "bin", "node")
SERVER_SCRIPT = os.path.join(PROJECT_ROOT, "node_modules", "context-mode", "server.bundle.mjs")
FIXTURE_PATH = os.path.join(PROJECT_ROOT, "context", "bitbake_synthetic_build.log")
EVIDENCE_DIR = os.path.join(PROJECT_ROOT, "evidence", "context")
STORAGE_DIR = os.path.join(EVIDENCE_DIR, ".storage")
RECEIPTS_FILE = os.path.join(EVIDENCE_DIR, "mcp_receipts.json")
BENCHMARK_FILE = os.path.join(EVIDENCE_DIR, "benchmark.json")
LOG_FILE = os.path.join(EVIDENCE_DIR, "mcp_experiment.log")
STDERR_LOG = os.path.join(EVIDENCE_DIR, "mcp_server.stderr.log")

MARKER_1 = "BB_ERR_BBAP_FETCH_HASH_MISMATCH_9841"
MARKER_2 = "BB_ERR_SYSCALL_SECCOMP_BLOCKED_4412"
MARKER_3 = "BB_ERR_DEVICE_TREE_DTC_SYNTAX_7719"

class MCPClient:
    def __init__(self, node_bin, server_script, storage_dir, stderr_log):
        self.node_bin = node_bin
        self.server_script = server_script
        self.storage_dir = storage_dir
        self.stderr_log = stderr_log
        self.process = None
        self.stderr_f = None
        self.selector = None
        self.request_id = 0
        self.receipts = []
        self.response_buffer = b""

    def start(self):
        os.makedirs(self.storage_dir, exist_ok=True)
        self.stderr_f = open(self.stderr_log, "w", encoding="utf-8")
        env = dict(os.environ)
        env["PATH"] = f"{os.path.join(PROJECT_ROOT, '.tools', 'node', 'bin')}:{env.get('PATH', '')}"
        env["CONTEXT_MODE_DIR"] = self.storage_dir
        env["CONTEXT_MODE_DATA_DIR"] = self.storage_dir
        env["CLAUDE_CONFIG_DIR"] = os.path.join(self.storage_dir, "isolated-claude")
        self.process = subprocess.Popen(
            [self.node_bin, self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.stderr_f,
            text=True,
            bufsize=1,
            cwd=PROJECT_ROOT,
            env=env
        )
        self.selector = selectors.DefaultSelector()
        os.set_blocking(self.process.stdout.fileno(), False)
        self.selector.register(self.process.stdout, selectors.EVENT_READ)

    def send_request(self, method, params=None, timeout=20.0):
        self.request_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        if params is not None:
            req["params"] = params
        
        req_line = json.dumps(req)
        self.process.stdin.write(req_line + "\n")
        self.process.stdin.flush()

        deadline = time.monotonic() + timeout
        while True:
            while b"\n" in self.response_buffer:
                line, self.response_buffer = self.response_buffer.split(b"\n", 1)
                try:
                    resp = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                if resp.get("id") == self.request_id:
                    self.receipts.append({"request": req, "response": resp})
                    return resp
                self.receipts.append({"server_message": resp})
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Timed out after {timeout}s awaiting response for id {self.request_id} ({method})")
            events = self.selector.select(timeout=remaining)
            if not events:
                continue
            for key, _ in events:
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    raise RuntimeError(f"Server closed connection unexpectedly while awaiting id {self.request_id}")
                self.response_buffer += chunk

    def send_notification(self, method, params=None):
        notif = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params is not None:
            notif["params"] = params
        notif_line = json.dumps(notif)
        self.process.stdin.write(notif_line + "\n")
        self.process.stdin.flush()
        self.receipts.append({
            "notification": notif
        })

    def close(self):
        if self.selector:
            try:
                self.selector.unregister(self.process.stdout)
            except Exception:
                pass
            self.selector.close()
        if self.process:
            try:
                if self.process.stdin:
                    self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                self.process.kill()
                self.process.wait(timeout=3)
            if self.process.stdout:
                self.process.stdout.close()
        if self.stderr_f:
            try:
                self.stderr_f.close()
            except Exception:
                pass

def run_experiment():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    log("==================================================================")
    log("Task 6: context-mode@1.0.169 MCP Experiment & Benchmark")
    log("==================================================================")
    log(f"Project root: {PROJECT_ROOT}")
    log(f"Node binary:  {NODE_BIN}")
    log(f"MCP Server:   {SERVER_SCRIPT}")
    log(f"Fixture:      {FIXTURE_PATH}")

    # 1. Read full fixture and measure baseline (exact UTF-8 bytes and unicode characters only)
    if not os.path.exists(FIXTURE_PATH):
        raise FileNotFoundError(f"Fixture not found at {FIXTURE_PATH}. Run generate_fixture.py first.")

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        full_content = f.read()

    full_bytes = len(full_content.encode("utf-8"))
    full_chars = len(full_content)
    full_lines = len(full_content.splitlines())

    log(f"\n[1] Baseline Synthetic BitBake Log Metrics:")
    log(f"    - Lines:         {full_lines}")
    log(f"    - UTF-8 Bytes:   {full_bytes:,} bytes")
    log(f"    - Unicode Chars: {full_chars:,} characters")
    log("    (Note: Exactly measured UTF-8 bytes and characters; no token estimation or impersonation)")

    # 2. Start MCP server client
    client = MCPClient(NODE_BIN, SERVER_SCRIPT, STORAGE_DIR, STDERR_LOG)
    client.start()
    log("\n[2] Connected to context-mode MCP server via stdio.")

    try:
        # 3. MCP Handshake: initialize
        init_resp = client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "trending-tools-lab-benchmark-runner",
                "version": "1.0.0"
            }
        })
        server_info = init_resp.get("result", {}).get("serverInfo", {})
        log(f"    - Initialize OK: Server={server_info.get('name')} v{server_info.get('version')}")
        assert server_info.get("name") == "context-mode", "Server name mismatch"
        assert server_info.get("version") == "1.0.169", "Server version mismatch"

        # 4. notifications/initialized
        client.send_notification("notifications/initialized")
        log("    - Sent notifications/initialized.")

        # 5. tools/list
        tools_resp = client.send_request("tools/list", {})
        tools_list = tools_resp.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools_list]
        log(f"    - tools/list returned {len(tools_list)} tools: {', '.join(tool_names)}")
        assert "ctx_index" in tool_names, "ctx_index missing"
        assert "ctx_search" in tool_names, "ctx_search missing"
        assert "ctx_stats" in tool_names, "ctx_stats missing"

        # 6. Index synthetic log via ctx_index
        log("\n[3] Calling ctx_index to index synthetic BitBake log...")
        index_resp = client.send_request("tools/call", {
            "name": "ctx_index",
            "arguments": {
                "path": FIXTURE_PATH,
                "source": "synthetic-bitbake-build-log"
            }
        })
        index_text = index_resp.get("result", {}).get("content", [{}])[0].get("text", "")
        log(f"    - ctx_index response: {index_text.strip()}")
        assert "Indexed" in index_text, "ctx_index failed to index fixture"

        # 7. Search for 3 markers individually and verify surrounding context
        log("\n[4] Searching for 3 unique error markers individually...")
        search_results = {}

        # Search Marker 1
        resp_m1 = client.send_request("tools/call", {
            "name": "ctx_search",
            "arguments": {
                "queries": [MARKER_1],
                "source": "synthetic-bitbake-build-log"
            }
        })
        text_m1 = resp_m1.get("result", {}).get("content", [{}])[0].get("text", "")
        search_results["marker_1"] = text_m1
        log(f"    - Search Marker 1 ({MARKER_1}): {len(text_m1)} chars returned")
        assert MARKER_1 in text_m1, f"Marker 1 not found in search result: {MARKER_1}"
        assert "linux-aspeed" in text_m1, "Surrounding context 'linux-aspeed' missing for Marker 1"
        assert "SHA256 checksum" in text_m1 or "checksum" in text_m1, "Surrounding context 'checksum' missing for Marker 1"
        assert "雜湊值不符" in text_m1 or "來源壓縮檔" in text_m1, "Surrounding Unicode context missing for Marker 1"
        log("      [✓] Marker 1 found & surrounding diagnostic context verified.")

        # Search Marker 2
        resp_m2 = client.send_request("tools/call", {
            "name": "ctx_search",
            "arguments": {
                "queries": [MARKER_2],
                "source": "synthetic-bitbake-build-log"
            }
        })
        text_m2 = resp_m2.get("result", {}).get("content", [{}])[0].get("text", "")
        search_results["marker_2"] = text_m2
        log(f"    - Search Marker 2 ({MARKER_2}): {len(text_m2)} chars returned")
        assert MARKER_2 in text_m2, f"Marker 2 not found in search result: {MARKER_2}"
        assert "phosphor-hwmon" in text_m2, "Surrounding context 'phosphor-hwmon' missing for Marker 2"
        assert "clone3" in text_m2, "Surrounding context 'clone3' missing for Marker 2"
        assert "seccomp" in text_m2, "Surrounding context 'seccomp' missing for Marker 2"
        assert "感測器驅動" in text_m2 or "AST2600" in text_m2, "Surrounding Unicode context missing for Marker 2"
        log("      [✓] Marker 2 found & surrounding diagnostic context verified.")

        # Search Marker 3
        resp_m3 = client.send_request("tools/call", {
            "name": "ctx_search",
            "arguments": {
                "queries": [MARKER_3],
                "source": "synthetic-bitbake-build-log"
            }
        })
        text_m3 = resp_m3.get("result", {}).get("content", [{}])[0].get("text", "")
        search_results["marker_3"] = text_m3
        log(f"    - Search Marker 3 ({MARKER_3}): {len(text_m3)} chars returned")
        assert MARKER_3 in text_m3, f"Marker 3 not found in search result: {MARKER_3}"
        assert "aspeed-bmc-facebook-yosemite4.dts" in text_m3 or "aspeed-device-tree" in text_m3, "Surrounding context DTS missing for Marker 3"
        assert "i2c11" in text_m3, "Surrounding context 'i2c11' missing for Marker 3"
        assert "syntax error" in text_m3, "Surrounding context 'syntax error' missing for Marker 3"
        assert "Yosemite 4" in text_m3 or "PCA9548" in text_m3, "Surrounding Unicode context missing for Marker 3"
        log("      [✓] Marker 3 found & surrounding diagnostic context verified.")

        # 8. Batched query test (optimal MCP pattern recommended by context-mode)
        log("\n[5] Calling ctx_search with batched queries array (recommended single-call pattern)...")
        resp_batch = client.send_request("tools/call", {
            "name": "ctx_search",
            "arguments": {
                "queries": [MARKER_1, MARKER_2, MARKER_3],
                "source": "synthetic-bitbake-build-log"
            }
        })
        text_batch = resp_batch.get("result", {}).get("content", [{}])[0].get("text", "")
        search_results["batch_all"] = text_batch
        assert MARKER_1 in text_batch, "Marker 1 missing in batch search"
        assert MARKER_2 in text_batch, "Marker 2 missing in batch search"
        assert MARKER_3 in text_batch, "Marker 3 missing in batch search"
        log("    - [✓] Batched search returned all 3 markers in a single MCP round trip.")

        # 9. ctx_stats
        log("\n[6] Calling ctx_stats to record session statistics...")
        stats_resp = client.send_request("tools/call", {
            "name": "ctx_stats",
            "arguments": {}
        })
        stats_text = stats_resp.get("result", {}).get("content", [{}])[0].get("text", "")
        assert "Preferences learned" not in stats_text, "Unexpected memory metadata in isolated benchmark"
        log("    - ctx_stats output:")
        for line in stats_text.splitlines()[:15]:
            log(f"      {line}")

        # 10. Compute Benchmark Metrics (UTF-8 Bytes and Unicode Characters strictly)
        retrieval_bytes = len(text_batch.encode("utf-8"))
        retrieval_chars = len(text_batch)

        byte_savings = full_bytes - retrieval_bytes
        char_savings = full_chars - retrieval_chars
        byte_reduction_ratio = byte_savings / full_bytes
        char_reduction_ratio = char_savings / full_chars

        log("\n[7] Benchmark Results (Exact UTF-8 Bytes vs Unicode Characters):")
        log(f"    - Full Log Bytes:          {full_bytes:,} UTF-8 bytes")
        log(f"    - Retrieved Bytes (batch): {retrieval_bytes:,} UTF-8 bytes")
        log(f"    - Byte Reduction:          {byte_reduction_ratio*100:.2f}% (Saved {byte_savings:,} bytes)")
        log(f"    - Full Log Chars:          {full_chars:,} characters")
        log(f"    - Retrieved Chars:         {retrieval_chars:,} characters")
        log(f"    - Char Reduction:          {char_reduction_ratio*100:.2f}% (Saved {char_savings:,} chars)")
        log("    --------------------------------------------------------------")
        log("    CRITICAL ASSERTION: bytes != tokens and chars != tokens.")
        log("    Bytes measure raw UTF-8 byte length on disk/wire.")
        log("    Characters measure Unicode code point count.")
        log("    No token counts are estimated without model-specific tokenizers.")
        log("    --------------------------------------------------------------")

        benchmark_data = {
            "version": "1.0.0",
            "tool": "context-mode@1.0.169",
            "node_runtime": NODE_BIN,
            "architecture": "linux-aarch64",
            "benchmark_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "fixture": {
                "path": "context/bitbake_synthetic_build.log",
                "synthetic": True,
                "contains_private_data": False,
                "markers": [MARKER_1, MARKER_2, MARKER_3]
            },
            "metrics": {
                "full_log": {
                    "lines": full_lines,
                    "utf8_bytes": full_bytes,
                    "characters": full_chars
                },
                "retrieved_batch": {
                    "utf8_bytes": retrieval_bytes,
                    "characters": retrieval_chars
                },
                "retrieved_individual": {
                    "marker_1_bytes": len(text_m1.encode("utf-8")),
                    "marker_1_chars": len(text_m1),
                    "marker_2_bytes": len(text_m2.encode("utf-8")),
                    "marker_2_chars": len(text_m2),
                    "marker_3_bytes": len(text_m3.encode("utf-8")),
                    "marker_3_chars": len(text_m3)
                },
                "savings": {
                    "byte_reduction_ratio": round(byte_reduction_ratio, 4),
                    "byte_reduction_percent": round(byte_reduction_ratio * 100, 2),
                    "char_reduction_ratio": round(char_reduction_ratio, 4),
                    "char_reduction_percent": round(char_reduction_ratio * 100, 2),
                    "bytes_saved": byte_savings,
                    "characters_saved": char_savings
                }
            },
            "contract_compliance": {
                "bytes_are_not_tokens": True,
                "chars_are_not_tokens": True,
                "no_token_impersonation": True,
                "distinction_explicitly_documented": True,
                "all_markers_verified": True,
                "surrounding_context_verified": True
            },
            "server_stats_raw": stats_text
        }

        # Save receipts
        with open(RECEIPTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "server_info": server_info,
                "tools_list": tools_list,
                "receipts": client.receipts
            }, f, indent=2, ensure_ascii=False)
        log(f"\n[8] Raw MCP JSON-RPC receipts saved to: {RECEIPTS_FILE}")

        # Save benchmark
        with open(BENCHMARK_FILE, "w", encoding="utf-8") as f:
            json.dump(benchmark_data, f, indent=2, ensure_ascii=False)
        log(f"    Structured benchmark saved to:        {BENCHMARK_FILE}")

    finally:
        client.close()

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    log(f"    Experiment execution log saved to:    {LOG_FILE}")
    log("==================================================================")
    log("All assertions passed successfully!")
    log("==================================================================")

if __name__ == "__main__":
    run_experiment()
