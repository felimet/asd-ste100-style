"""Build the three description arms of the held-out 3 trigger test. Usage: build_trig_arms.py <ev4>
Each arm is the commit 21831a6 skill folder with SKILL.md line 4 set to the description in heldout3-protocol.md.
The sha256 values are the ones listed in that protocol; the script stops if a built SKILL.md differs.
All files are written with LF. The arms used in the 2026-11-13 run kept the Windows working-copy line endings (CRLF)
in the files other than SKILL.md; the content is the same."""
import hashlib
import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

COMMIT, FOLDER = "21831a6", "plugins/asd-ste100-style/skills/asd-ste100-zh-tw"
ARMS = {
    "old": (None, "0dca1520bf83eaf1f4c49daa3190a18e9ceefcd1825b9e3123136759f7c8fcad"),
    "descA": ('description: 使用者要求 STE 風格、清楚精確且易於掃讀的繁體中文回覆，或已將此風格設為對話預設時使用。參考 ASD-STE100 部分原則的非官方改編，調整 AI Agent 的繁體中文對話風格，適用於日常問答、概念解釋、建議、討論與進度回報，也可延伸至文件表達。',
              "d35efa7187081266bb78764c77224bfe1ff0d3b16e37ce687fcb40b74d778160"),
    "descB": ('description: 使用者要求 STE 或 ASD-STE100 風格，或要求以清楚、精確、一句一重點且易於掃讀的繁體中文回覆、說明或改寫時使用；使用者已將此風格設為對話預設時也使用。參考 ASD-STE100 部分原則的非官方繁體中文對話風格，適用於日常問答、概念解釋、建議、討論與進度回報，也可延伸至文件表達。',
              "6cb562d2f3cf388988b5d6d1f3d03c7981187a181676ac5375f22ae275814595"),
}
ev = Path(sys.argv[1])
repo = Path(__file__).resolve().parents[3]
tar = subprocess.run(["git", "-C", str(repo), "archive", COMMIT, FOLDER], capture_output=True, check=True).stdout
for name, (line4, want) in ARMS.items():
    dest = ev / "arms" / name
    shutil.rmtree(dest, ignore_errors=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        for m in tf.getmembers():
            if m.isfile():
                out = dest / Path(m.name).relative_to(FOLDER)
                out.parent.mkdir(parents=True, exist_ok=True)
                # git archive follows core.autocrlf; the protocol hashes are LF
                out.write_bytes(tf.extractfile(m).read().replace(b"\r\n", b"\n"))
    skill = dest / "SKILL.md"
    if line4:
        parts = skill.read_bytes().decode("utf-8").split("\n")
        assert parts[3].startswith("description: ")
        parts[3] = line4
        skill.write_bytes("\n".join(parts).encode("utf-8"))
    got = hashlib.sha256(skill.read_bytes()).hexdigest()
    print(name, got, "OK" if got == want else "MISMATCH")
    if got != want:
        sys.exit(1)
