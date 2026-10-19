$ErrorActionPreference = "Stop"
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:PATH = "$env:JAVA_HOME\bin;" + $env:PATH

$sdk = "C:\Users\Kimyoongyeom\AppData\Local\Android\Sdk"
$bt = "$sdk\build-tools\35.0.0"
$androidJar = "$sdk\platforms\android-36\android.jar"
$javac = "$env:JAVA_HOME\bin\javac.exe"

Set-Location $PSScriptRoot

Write-Host "[1/6] Cleaning and preparing build folders..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
New-Item -ItemType Directory -Path "build\gen" -Force | Out-Null
New-Item -ItemType Directory -Path "build\obj" -Force | Out-Null
New-Item -ItemType Directory -Path "build\dex" -Force | Out-Null

Write-Host "[2/6] Compiling resources with aapt2 (relative paths)..."
& "$bt\aapt2.exe" compile --dir res -o build\res.zip
& "$bt\aapt2.exe" link -o build\unsigned.apk -I $androidJar --manifest AndroidManifest.xml --java build\gen build\res.zip --auto-add-overlay

Write-Host "[3/6] Compiling Java classes with javac..."
$javaFiles = Get-ChildItem -Path src, build\gen -Recurse -Filter "*.java" | Select-Object -ExpandProperty FullName
& $javac -encoding UTF-8 -source 1.8 -target 1.8 -bootclasspath $androidJar -classpath $androidJar -d build\obj $javaFiles

Write-Host "[4/6] Creating DEX bytecode with d8..."
$classFiles = Get-ChildItem -Path build\obj -Recurse -Filter "*.class" | Select-Object -ExpandProperty FullName
& "$bt\d8.bat" --lib $androidJar --output build\dex $classFiles

Write-Host "[5/6] Packaging classes.dex..."
Copy-Item "build\unsigned.apk" "build\unaligned.apk"
$JAR = "$env:JAVA_HOME\bin\jar.exe"
& $JAR uf build\unaligned.apk -C build\dex classes.dex

Write-Host "[6/6] Zipaligning and signing APK..."
& "$bt\zipalign.exe" -f -p 4 build\unaligned.apk build\aligned.apk
$keystore = (Resolve-Path "..\trans2_app\debug.keystore").Path
& "$bt\apksigner.bat" sign --ks $keystore --ks-pass pass:android --key-pass pass:android --out vorta_s7_pro.apk build\aligned.apk
& "$bt\apksigner.bat" verify -v vorta_s7_pro.apk

Write-Host "[SUCCESS] Vorta Reso S7 v2.6 APK created and signed successfully!"
