@echo off
chcp 949 > nul
REM Run from the bat's own folder, so relative .sh/.apk paths work even when started as admin.
cd /d "%~dp0"
title [보르타 레조] A30 / S7 / S6 자동 모델 감지 및 1:1 맞춤형 전용기기 개조 원클릭 (v3.1)

echo ===============================================================================
echo  [보르타 레조] A30 / S7 / S6 스마트폰 환경개조 및 맞춤형 v3.0 원클릭 업데이트
echo ===============================================================================
echo  모든 기기 명령은 8초 시간제한(timeout)으로 실행되어 멈추지 않습니다.
echo.

set "ADB=adb"
if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
echo [*] ADB 실행 경로: %ADB%
"%ADB%" devices

set "TARGET_MODEL="
for /f "tokens=*" %%M in ('"%ADB%" shell getprop ro.product.model 2^>nul') do set "TARGET_MODEL=%%M"
if "%TARGET_MODEL%"=="" (
    echo [경고] 연결된 스마트폰이 없습니다. USB 연결 후 'USB 디버깅 허용'을 눌러주세요.
    goto :END
)
echo -------------------------------------------------------------------------------
echo [기기 식별 성공] 감지된 스마트폰 모델: %TARGET_MODEL%
echo -------------------------------------------------------------------------------

set "SH=debloat_device.sh"
set "APK="
set "PKG="
echo %TARGET_MODEL% | findstr /i "A305 A30" > nul && (set "APK=smato_a30_app\smato_a30_pro.apk" & set "PKG=com.smato.a30frequency")
echo %TARGET_MODEL% | findstr /i "G930 S7" > nul && (set "APK=vorta_s7_app\vorta_s7_pro.apk" & set "PKG=com.vorta.s7frequency")
echo %TARGET_MODEL% | findstr /i "G920 S6" > nul && (set "APK=vorta_s6_app\vorta_s6_pro.apk" & set "PKG=com.vorta.s6frequency" & set "SH=s6_vorta_dedicated.sh")

echo [*] 불필요 앱 삭제 및 24시간 환경설정 실행 (진행 상황이 한 줄씩 표시됩니다)...
if not exist "%SH%" (
    echo [오류] %SH% 파일이 없습니다: %CD%
    goto :END
)
"%ADB%" push "%SH%" /data/local/tmp/vorta_setup.sh
"%ADB%" shell sh /data/local/tmp/vorta_setup.sh

if "%APK%"=="" (
    echo [알림] 미등록 모델 %TARGET_MODEL% - 환경설정만 완료했습니다.
    goto :DONE
)
if not exist "%APK%" (
    echo [오류] APK 파일이 없습니다: %CD%\%APK%
    goto :END
)
echo [*] 보르타 레조 전용 APK 설치: %APK%
"%ADB%" install -r -d "%APK%"
if errorlevel 1 (
    echo [오류] APK 설치 실패
    goto :END
)
"%ADB%" shell am force-stop %PKG%
"%ADB%" shell am start -n %PKG%/.MainActivity
echo [성공] %PKG% 설치 및 실행 완료

:DONE
echo ===============================================================================
echo  [완료] 환경개조 및 보르타 v3.0 업데이트 완료
echo ===============================================================================
:END
pause
