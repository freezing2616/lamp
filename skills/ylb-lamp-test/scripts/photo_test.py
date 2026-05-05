#!/usr/bin/env python3
"""
[套件] 拍照测试
[步骤] 1步
[耗时] ~20s
[描述] 触发设备拍照并下载图片，校验文件存在且可读取
[触发] 拍照测试 / 拍照取图 / 相机测试 / 拍张照测试
"""
import os, sys, time, subprocess
from pathlib import Path

QUEUE = "/tmp/lamp_cmd_queue.txt"
SESSION = os.path.expanduser("~/.openclaw/workspace/skills/.ylb-lamp/session.json")

def send(cmd, wait=1):
    try:
        with open(QUEUE, "w") as f:
            f.write(cmd)
        print(f"  [CMD] {cmd[:60]}{'...' if len(cmd) > 60 else ''}")
    except Exception:
        pass
    time.sleep(wait)

def tts(text, wait=2):
    send(f"tts:{text}", wait)

def find_photo_script():
    p1 = Path(os.path.expanduser("~/.openclaw/workspace/skills/ylb-lamp-setup/scripts/lamp_photo.py"))
    if p1.exists():
        return p1
    p2 = Path(__file__).resolve().parents[2] / "ylb-lamp-setup" / "scripts" / "lamp_photo.py"
    if p2.exists():
        return p2
    return None

def parse_result(output):
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith("SUCCESS:"):
            return ("success", line[len("SUCCESS:"):].strip())
        if line.startswith("FAIL:"):
            return ("fail", line[len("FAIL:"):].strip())
    return ("unknown", None)

def check_image_file(path_str):
    p = Path(path_str)
    if not p.exists():
        raise FileNotFoundError(f"图片文件不存在: {p}")
    size = p.stat().st_size
    if size <= 0:
        raise ValueError(f"图片文件为空: {p}")
    with open(p, "rb") as f:
        head = f.read(8)
    if head.startswith(b"\xff\xd8"):
        return (p, size, "jpeg")
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return (p, size, "png")
    raise ValueError(f"未知图片格式头: {head!r}")

def main():
    print("拍照测试 开始")
    if not os.path.exists(SESSION):
        print(f"FAIL:session 不存在，请先运行 ylb-lamp-setup 完成登录: {SESSION}")
        sys.exit(1)

    photo_script = find_photo_script()
    if not photo_script:
        print("FAIL:未找到 lamp_photo.py（需要 ylb-lamp-setup 安装/同步到 ~/.openclaw/workspace/skills）")
        sys.exit(1)

    tts("开始拍照测试")

    env = dict(os.environ)
    env.setdefault("YLBLAMP_PHOTOS", "/tmp/lamp_photos_test")
    proc = subprocess.run(
        [sys.executable, str(photo_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    output = proc.stdout or ""
    print(output.rstrip())

    status, payload = parse_result(output)
    if status != "success":
        if status == "fail":
            print(f"FAIL:{payload}")
        else:
            print("FAIL:未解析到 SUCCESS/FAIL 输出")
        sys.exit(1)

    try:
        p, size, kind = check_image_file(payload)
    except Exception as e:
        print(f"FAIL:图片校验失败 {e}")
        sys.exit(1)

    tts("拍照测试完成")
    print(f"SUCCESS:{p} ({kind}, {size} bytes)")

if __name__ == "__main__":
    main()
