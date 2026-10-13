#!/usr/bin/env python3
"""
Generate synthetic BitBake build log fixture for context-mode MCP benchmark.

Constraints:
- Strictly synthetic and non-private data.
- Contains 3 unique error markers.
- Contains repetitive compilation and BitBake task noise.
- Contains rich Unicode characters (Traditional Chinese comments, warning symbols, etc.).
- Structured with markdown headings so context-mode chunks by section.
"""

import os
import sys

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "bitbake_synthetic_build.log")

MARKER_1 = "BB_ERR_BBAP_FETCH_HASH_MISMATCH_9841"
MARKER_2 = "BB_ERR_SYSCALL_SECCOMP_BLOCKED_4412"
MARKER_3 = "BB_ERR_DEVICE_TREE_DTC_SYNTAX_7719"

def generate_log():
    lines = []
    lines.append("# Synthetic BitBake Build Log (Non-private benchmark test fixture)")
    lines.append("# Project: openbmc-phosphor-build-benchmark-synthetic-v1")
    lines.append("# Machine: facebook-yosemite4-synthetic (ARMv7 Aspeed AST2600 BMC)")
    lines.append("# Build Configuration: Yocto Scarthgap 5.0.3 / BitBake 2.8.0")
    lines.append("# Notice: 本文件為全合成測試用建置紀錄，無任何真實機密或私人資料。")
    lines.append("# 建立時間戳記：2026-10-13 04:10:00 UTC | 繁體中文注釋與符號測試")
    lines.append("")

    # Repetitive recipe names
    recipes = [
        ("phosphor-pid-control", "3.2.0+git"),
        ("phosphor-sel-logger", "0.1.0+git"),
        ("phosphor-user-manager", "1.0.0+git"),
        ("systemd", "255.4"),
        ("sdbusplus", "1.0+git"),
        ("phosphor-dbus-interfaces", "1.0+git"),
        ("entity-manager", "0.1+git"),
        ("ipmitool", "1.8.19"),
        ("busybox", "1.36.1"),
        ("u-boot-aspeed", "2019.04+git"),
        ("dropbear", "2024.84"),
        ("openssl", "3.2.1"),
        ("zlib", "1.3.1"),
        ("ncurses", "6.4"),
        ("glibc", "2.39"),
        ("boost", "1.84.0"),
        ("bison-native", "3.8.2"),
        ("flex-native", "2.6.4"),
        ("cmake-native", "3.28.3"),
        ("ninja-native", "1.11.1"),
        ("linux-aspeed", "6.6.21+git"),
        ("phosphor-hwmon", "1.0.0+git"),
        ("aspeed-device-tree", "1.0"),
    ]

    task_id = 0

    for rep in range(3):
        for name, ver in recipes:
            task_id += 1
            section_title = f"Task {task_id}: {name}_{ver}:do_compile"
            lines.append(f"## {section_title}")
            lines.append(f"NOTE: Executing RunQueue Token {task_id:04d} (ID: {task_id}, virtual:native:{name})")
            lines.append(f"NOTE: recipe {name}-{ver}: task do_compile: Started [PID {20000 + task_id}]")
            lines.append(f"/* 模組狀態：正在處理 {name} 編譯管線 | Target architecture: armv7ahf-vfpv4d16 */")
            lines.append("arm-openbmc-linux-gnueabi-g++ -mthumb -mfpu=vfpv4-d16 -mfloat-abi=hard -mcpu=cortex-a7 "
                         "-O2 -pipe -g -feliminate-unused-debug-types -fmacro-prefix-map -fdebug-prefix-map "
                         "-fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wformat -Wformat-security "
                         f"-I./include -I../src/{name} -c -o obj/{name}.o src/{name}/main.cpp")

            # Check if this section should host error marker 1
            if name == "linux-aspeed" and rep == 1:
                lines.append(f"ERROR: {MARKER_1} detected during do_fetch for linux-aspeed-6.6.21+git")
                lines.append("ERROR: Recipe meta-openbmc/recipes-kernel/linux/linux-aspeed_6.6.bb: Fetch failed for SRC_URI commit 89e27a9f73c6")
                lines.append("Details: Expected SHA256 checksum e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855, but upstream provided 01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b")
                lines.append("診斷摘要：來源壓縮檔的 SHA256 雜湊值不符，請檢查 commit 雜湊或更新 bbappend 檔內的 SRC_URI[sha256sum]")
                lines.append("影響元件：Linux Kernel 核心原始碼下載失敗，造成核心驅動映像檔建置中斷 [✗ 關鍵失敗]")

            # Check if this section should host error marker 2
            elif name == "phosphor-hwmon" and rep == 1:
                lines.append(f"ERROR: {MARKER_2} encountered while compiling phosphor-hwmon/sensor_manager.cpp")
                lines.append("ERROR: Host container security profile active; system call 435 (clone3) was trapped and blocked by seccomp policy.")
                lines.append("Details: g++ internal compiler error: Operation not permitted (syscall clone3 blocked, errno 1).")
                lines.append("診斷摘要：容器安全防護 seccomp filter 攔截了編譯器派生執行緒的 clone3 系統呼叫，需在容器設定中增加 seccomp=unconfined 或升級 libseccomp")
                lines.append("影響元件：BMC 硬體感測器驅動 (ASPEED AST2600 PWM/Tachometer) 監控常駐程式無法編譯 [✗ 關鍵失敗]")

            # Check if this section should host error marker 3
            elif name == "aspeed-device-tree" and rep == 1:
                lines.append(f"ERROR: {MARKER_3} device tree compilation failure for aspeed-bmc-facebook-yosemite4.dts")
                lines.append("arch/arm/boot/dts/aspeed-bmc-facebook-yosemite4.dts:142.17: syntax error: unexpected IDENTIFIER in node &i2c11")
                lines.append("Details: dtc -I dts -O dtb -o aspeed-bmc-facebook-yosemite4.dtb aspeed-bmc-facebook-yosemite4.dts failed with exit code 1.")
                lines.append("診斷摘要：Device Tree 節點 &i2c11 定義中缺少分號或屬性名稱格式錯誤，PCA9548 多工器頻道設定遺失屬性結尾。")
                lines.append("影響元件：Yosemite 4 伺服器主機板樹狀設定檔語法解析失敗，無法產生 DTB 二進位檔 [✗ 關鍵失敗]")

            else:
                # Normal compilation progress lines (repetitive noise)
                for step in range(12):
                    lines.append(f"  [Progress] Step {step+1}/12: Building translation unit {name}_part_{step}.cpp ... [✓ OK] (Δt = {step*12.4:.1f}ms)")
                    lines.append(f"  DEBUG: Symbol resolution for namespace phosphor::{name} offset 0x{step*0x100:04x} mapped to .text")
                lines.append(f"NOTE: recipe {name}-{ver}: task do_compile: Succeeded [✓ 100%]")

            lines.append("/* 繁體中文環境測試：溫度上限 85°C，風扇轉差率容限 ±5%，I2C 匯流排多工器切換頻道 3 */")
            lines.append("---")
            lines.append("")

    content = "\n".join(lines) + "\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    utf8_bytes = len(content.encode("utf-8"))
    chars = len(content)
    # Estimate tokens: cl100k_base rule of thumb is ~3.5 to 4 chars per token for code/logs, but here we report exact chars & bytes
    print(f"Generated fixture at: {OUTPUT_FILE}")
    print(f"Total lines: {len(lines)}")
    print(f"UTF-8 Bytes: {utf8_bytes}")
    print(f"Character count: {chars}")

if __name__ == "__main__":
    generate_log()

