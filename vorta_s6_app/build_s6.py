import os
import shutil
import subprocess
import sys
import zipfile

APP_DIR = os.path.abspath(os.path.dirname(__file__))
BUILD_DIR = os.path.join(APP_DIR, "build")
GEN_DIR = os.path.join(BUILD_DIR, "gen")
CLASSES_DIR = os.path.join(BUILD_DIR, "classes")

SDK_DIR = r"C:\Users\Kimyoongyeom\AppData\Local\Android\Sdk"
BUILD_TOOLS_DIR = os.path.join(SDK_DIR, r"build-tools\35.0.0")
AAPT2 = os.path.join(BUILD_TOOLS_DIR, "aapt2.exe")
D8 = os.path.join(BUILD_TOOLS_DIR, "d8.bat")
ZIPALIGN = os.path.join(BUILD_TOOLS_DIR, "zipalign.exe")
APKSIGNER = os.path.join(BUILD_TOOLS_DIR, "apksigner.bat")
ANDROID_JAR = os.path.join(SDK_DIR, r"platforms\android-36\android.jar")
KEYSTORE = r"C:\Users\Kimyoongyeom\.android\debug.keystore"
JAVAC = r"C:\Program Files\Android\Android Studio\jbr\bin\javac.exe"
if not os.path.exists(JAVAC):
    JAVAC = r"C:\Program Files\RedHat\java-1.8.0-openjdk-1.8.0.492-1\bin\javac.exe"

ADB = os.path.join(SDK_DIR, r"platform-tools\adb.exe")
DEVICE_SERIAL = "06157df622d5ad1d"

JAVA_HOME = r"C:\Program Files\Android\Android Studio\jbr"
custom_env = os.environ.copy()
custom_env["JAVA_HOME"] = JAVA_HOME
custom_env["PATH"] = os.path.join(JAVA_HOME, "bin") + os.path.pathsep + custom_env.get("PATH", "")

def run_cmd(cmd, desc):
    print(f"[{desc}] Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=APP_DIR, shell=(True if isinstance(cmd, str) else False), env=custom_env, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {desc}\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
        sys.exit(res.returncode)
    if res.stdout.strip():
        print(res.stdout.strip())
    return res.stdout

def main():
    print("[1/8] Cleaning and preparing build directory...")
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(GEN_DIR, exist_ok=True)
    os.makedirs(CLASSES_DIR, exist_ok=True)

    print("[2/8] Compiling resources with AAPT2...")
    flata = os.path.join(BUILD_DIR, "compiled_res.flata")
    run_cmd([AAPT2, "compile", "--dir", "res", "-o", flata], "AAPT2 Compile")

    print("[3/8] Linking APK and generating R.java...")
    base_apk = os.path.join(BUILD_DIR, "base_unaligned.apk")
    manifest = os.path.join(APP_DIR, "AndroidManifest.xml")
    run_cmd([
        AAPT2, "link",
        "-o", base_apk,
        "-I", ANDROID_JAR,
        "--manifest", manifest,
        flata,
        "--java", GEN_DIR,
        "--auto-add-overlay"
    ], "AAPT2 Link")

    print("[4/8] Compiling Java classes with javac...")
    r_java = os.path.join(GEN_DIR, "com", "vorta", "s6frequency", "R.java")
    src_dir = os.path.join(APP_DIR, "src", "com", "vorta", "s6frequency")
    java_files = [r_java] + [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith(".java")]
    run_cmd([
        JAVAC,
        "-source", "1.8",
        "-target", "1.8",
        "-cp", ANDROID_JAR,
        "-d", CLASSES_DIR
    ] + java_files, "javac compile")

    print("[5/8] Converting bytecode to classes.dex with d8...")
    class_files = [os.path.join(CLASSES_DIR, "com", "vorta", "s6frequency", f)
                   for f in os.listdir(os.path.join(CLASSES_DIR, "com", "vorta", "s6frequency"))
                   if f.endswith(".class")]
    run_cmd([
        D8,
        "--min-api", "21",
        "--output", BUILD_DIR
    ] + class_files, "D8 dex conversion")

    print("[6/8] Packaging classes.dex into base APK...")
    dex_file = os.path.join(BUILD_DIR, "classes.dex")
    with zipfile.ZipFile(base_apk, "a") as z:
        z.write(dex_file, "classes.dex")

    print("[7/8] Zipaligning and signing APK...")
    aligned_apk = os.path.join(BUILD_DIR, "aligned.apk")
    final_apk = os.path.join(BUILD_DIR, "vorta_s6_pro.apk")
    run_cmd([ZIPALIGN, "-f", "4", base_apk, aligned_apk], "zipalign")
    run_cmd([
        APKSIGNER, "sign",
        "--ks", KEYSTORE,
        "--ks-pass", "pass:android",
        "--out", final_apk,
        aligned_apk
    ], "apksigner sign")
    run_cmd([APKSIGNER, "verify", final_apk], "apksigner verify")
    print(f"[SUCCESS] Built and signed: {final_apk}")

    # Check if device is connected
    adb_devs = subprocess.run([ADB, "devices"], capture_output=True, text=True).stdout
    if DEVICE_SERIAL in adb_devs:
        print(f"[8/8] Installing onto Galaxy S6 ({DEVICE_SERIAL})...")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "install", "-r", final_apk], "ADB install")

        print("Launching Vorta Reso S6 v3.0...")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "shell", "am", "start", "-n", "com.vorta.s6frequency/.MainActivity"], "ADB launch")

        print("Configuring system safe volume unlock and screen-off normalization...")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "shell", "pm", "grant", "com.vorta.s6frequency", "android.permission.WRITE_SECURE_SETTINGS"], "Grant permission")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "shell", "settings", "put", "system", "volume_limiter_enable", "0"], "Disable vol limiter")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "shell", "settings", "put", "system", "volume_limiter_value", "15"], "Set limiter max 15")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "shell", "settings", "put", "global", "audio_safe_volume_state", "2"], "Safe volume state 2")
        run_cmd([ADB, "-s", DEVICE_SERIAL, "shell", "settings", "put", "global", "stay_on_while_plugged_in", "0"], "Stay on 0")
        # screen_off_timeout is untouched (respecting user UX preferences)
    else:
        print(f"[INFO] Galaxy S6 ({DEVICE_SERIAL}) not connected via USB. APK ready at: {final_apk}")

    # Copy final APK to app root for easy transfer
    root_apk = os.path.join(APP_DIR, "vorta_s6_pro.apk")
    shutil.copy2(final_apk, root_apk)
    print(f"[READY] Copied final APK to: {root_apk}")

if __name__ == "__main__":
    main()
