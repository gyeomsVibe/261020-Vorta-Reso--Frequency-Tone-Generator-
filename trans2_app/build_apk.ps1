$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:PATH = "$env:JAVA_HOME\bin;" + $env:PATH

$BUILD_TOOLS = "C:\Users\Kimyoongyeom\AppData\Local\Android\Sdk\build-tools\35.0.0"
$AAPT2 = "$BUILD_TOOLS\aapt2.exe"
$D8 = "$BUILD_TOOLS\d8.bat"
$APKSIGNER = "$BUILD_TOOLS\apksigner.bat"
$ANDROID_JAR = "C:\Users\Kimyoongyeom\AppData\Local\Android\Sdk\platforms\android-36\android.jar"
$JAVAC = "$env:JAVA_HOME\bin\javac.exe"
$JAR = "$env:JAVA_HOME\bin\jar.exe"

Set-Location $PSScriptRoot

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
New-Item -ItemType Directory -Force -Path "build\compiled_res", "build\gen", "build\classes", "build\dex" | Out-Null

Write-Host "[1/5] Compiling resources with aapt2..."
& $AAPT2 compile --dir res -o build\compiled_res\compiled.zip
& $AAPT2 link -I $ANDROID_JAR --manifest AndroidManifest.xml -o build\unaligned.apk --java build\gen build\compiled_res\compiled.zip --auto-add-overlay

Write-Host "[2/5] Compiling Java sources with javac..."
$javaFiles = Get-ChildItem -Recurse -Filter "*.java" src, build\gen | Select-Object -ExpandProperty FullName
& $JAVAC -encoding UTF-8 -cp $ANDROID_JAR -d build\classes $javaFiles

Write-Host "[3/5] Generating DEX bytecode with d8..."
$classFiles = Get-ChildItem -Recurse -Filter "*.class" build\classes | Select-Object -ExpandProperty FullName
& $D8 --lib $ANDROID_JAR --output build\dex $classFiles

Write-Host "[4/5] Packaging classes.dex into unaligned.apk..."
& $JAR uf build\unaligned.apk -C build\dex classes.dex

Write-Host "[5/5] Signing APK with persistent debug keystore..."
$KEYSTORE = "debug.keystore"
$KEYTOOL = "$env:JAVA_HOME\bin\keytool.exe"
if (-not (Test-Path $KEYSTORE)) {
    & $KEYTOOL -genkeypair -v -keystore $KEYSTORE -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
}

& $APKSIGNER sign --ks $KEYSTORE --ks-pass pass:android --ks-key-alias androiddebugkey --key-pass pass:android --out trans2_pro.apk build\unaligned.apk

Write-Host "[SUCCESS] trans2_pro.apk v2.0 created and signed successfully!"
