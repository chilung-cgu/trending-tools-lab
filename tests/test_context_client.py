import sys
import time

import pytest

from context.mcp_experiment import MCPClient


def test_partial_json_line_obeys_timeout(tmp_path):
    server = tmp_path / 'partial.py'
    server.write_text('import sys,time\nsys.stdin.readline()\nsys.stdout.write("{")\nsys.stdout.flush()\ntime.sleep(2)\n')
    client = MCPClient(sys.executable, str(server), str(tmp_path / 'storage'), str(tmp_path / 'stderr'))
    client.start()
    started = time.monotonic()
    try:
        with pytest.raises(TimeoutError):
            client.send_request('initialize', {}, timeout=0.1)
        assert time.monotonic() - started < 1
    finally:
        client.close()


def test_server_notification_is_preserved_in_receipts(tmp_path):
    server = tmp_path / 'notifications.py'
    server.write_text('import json,sys\n'
                      'req=json.loads(sys.stdin.readline())\n'
                      'print(json.dumps({"jsonrpc":"2.0","method":"notifications/message","params":{"data":"index ready"}}),flush=True)\n'
                      'print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":{}}),flush=True)\n'
                      'sys.stdin.read()\n')
    client = MCPClient(sys.executable, str(server), str(tmp_path / 'storage'), str(tmp_path / 'stderr'))
    client.start()
    try:
        client.send_request('initialize', {})
        assert any(entry.get('server_message', {}).get('method') == 'notifications/message'
                   for entry in client.receipts), 'Server notifications must remain in raw receipts'
    finally:
        client.close()


def test_close_reaps_server_that_ignores_termination(tmp_path):
    server = tmp_path / 'stubborn.py'
    server.write_text('import json,signal,sys,time\n'
                      'signal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                      'req=json.loads(sys.stdin.readline())\n'
                      'print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":{}}),flush=True)\n'
                      'time.sleep(20)\n')
    client = MCPClient(sys.executable, str(server), str(tmp_path / 'storage'), str(tmp_path / 'stderr'))
    client.start()
    try:
        client.send_request('initialize', {})
        client.close()
        assert client.process.returncode is not None, 'Forced kill must wait for child exit'
    finally:
        client.process.kill()
        client.process.wait(timeout=3)
