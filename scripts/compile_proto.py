import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

PROTO_DIR = "app/proto"
OUT_DIR = "app/api/grpc/v1"


def compile_proto():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("🚀 Compiling Protobuf files...")
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        f"--pyi_out={OUT_DIR}",
        *glob.glob(f"{PROTO_DIR}/*.proto"),
    ]
    subprocess.run(cmd, check=True)

    print("🔧 Fixing import paths in generated files...")
    for filepath in glob.glob(f"{OUT_DIR}/*_pb2_grpc.py"):
        # 1. อ่านเนื้อหาไฟล์เข้าหน่วยความจำก่อน (ยังไม่เปิดโหมด 'w')
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 2. ทำการแทนที่ Import Path
        new_content = re.sub(
            r"^import ([a-zA-Z0-9_]*_pb2) as",
            r"from . import \1 as",
            content,
            flags=re.MULTILINE,
        )

        new_content = re.sub(
            r"(return grpc\.experimental\..*)", r"\1  # type: ignore", new_content
        )

        # 3. เขียนเนื้อหาใหม่ทับลงไฟล์
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    # สร้าง __init__.py
    init_file = os.path.join(OUT_DIR, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, "a").close()

    print("✅ Protobuf compiled successfully!")


def clean():
    """ลบไฟล์ generated และ pycache ทั้งหมด"""
    print("🧹 Cleaning generated proto files...")

    # 1. ลบไฟล์ *_pb2.py และ *_pb2_grpc.py
    for pattern in ["*_pb2.pyi", "*_pb2.py", "*_pb2_grpc.py"]:
        for filepath in glob.glob(os.path.join(OUT_DIR, pattern)):
            try:
                os.remove(filepath)
                print(f"  Deleted: {filepath}")
            except OSError as e:
                print(f"  Error deleting {filepath}: {e}")

    # 2. ลบ __pycache__ ในโฟลเดอร์ output (ถ้ามี)
    pycache_dir = os.path.join(OUT_DIR, "__pycache__")
    if os.path.exists(pycache_dir):
        shutil.rmtree(pycache_dir)
        print(f"  Deleted: {pycache_dir}")

    print("✨ Clean complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Proto Compilation")
    parser.add_argument(
        "--clean", "-c", action="store_true", help="Clean generated proto files"
    )
    args = parser.parse_args()

    if args.clean:
        clean()
    else:
        compile_proto()
