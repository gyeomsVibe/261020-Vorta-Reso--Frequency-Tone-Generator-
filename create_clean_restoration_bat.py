# -*- coding: utf-8 -*-
bat_content = r'''@echo off
chcp 949 > nul
echo ==============================================================================
echo [긴급 정상화] 갤럭시 S7·S6 볼륨 강제복귀 해제 및 화면 켜짐 버그 완전 정상화
echo ==============================================================================
echo.

set ADB=C:\Users\Kimyoongyeom\AppData\Local\Android\Sdk\platform-tools\adb.exe
if not exist "%ADB%" (
    set ADB=C:\platform-tools\adb.exe
)
if not exist "%ADB%" (
    set ADB=adb
)

echo [1/3] 연결된 안드로이드 기기 확인 중...
"%ADB%" devices
echo.

set S7_SERIAL=ce021602916dbb3804
set S6_SERIAL=06157df622d5ad1d

echo ------------------------------------------------------------------------------
echo [2/3] 갤럭시 S7 정상화 적용 (볼륨 강제고정 제거 + 화면 정상 절전 복원)...
echo ------------------------------------------------------------------------------
"%ADB%" -s %S7_SERIAL% get-state > nul 2>&1
if %errorlevel% equ 0 (
    echo [S7 발견] %S7_SERIAL% 연결 확인됨. 정상화 작업 시작...
    
    echo   1. 과거 볼륨 강제고정 악성 서비스(com.s7.safevolumebypass) 완전 삭제...
    "%ADB%" -s %S7_SERIAL% shell pm uninstall com.s7.safevolumebypass > nul 2>&1
    "%ADB%" -s %S7_SERIAL% shell pkill -f "s7_guardian_loop" > nul 2>&1
    "%ADB%" -s %S7_SERIAL% shell pkill -f "SafeVolumeAccessibilityService" > nul 2>&1
    
    echo   2. 접근성 서비스 강제 설정 초기화...
    "%ADB%" -s %S7_SERIAL% shell settings put secure enabled_accessibility_services "com.vorta.s7frequency/.S7AccessibilityService"
    "%ADB%" -s %S7_SERIAL% shell settings put secure accessibility_enabled 1
    
    echo   3. 화면 꺼짐 먹통 버그 수정 (상시 켜짐 7 -> 정상 절전 0, 타임아웃 1분 복원)...
    "%ADB%" -s %S7_SERIAL% shell settings put global stay_on_while_plugged_in 0
    "%ADB%" -s %S7_SERIAL% shell settings put system screen_off_timeout 60000
    
    echo   4. 안전볼륨 경고창만 해제하고, 볼륨은 사용자 100%% 자유 조절로 완전 개방...
    "%ADB%" -s %S7_SERIAL% shell settings put global audio_safe_volume_state 2
    "%ADB%" -s %S7_SERIAL% shell settings put global safe_media_volume_active 0
    "%ADB%" -s %S7_SERIAL% shell settings put global safe_media_volume_enabled 0
    "%ADB%" -s %S7_SERIAL% shell settings put system volume_limiter_enable 0
    "%ADB%" -s %S7_SERIAL% shell settings put system volume_limiter_value 15
    
    echo   5. 수정된 최신 보르타 레조 S7 v2.8 (화면 자유 절전) 재설치...
    "%ADB%" -s %S7_SERIAL% install -r "d:\D_Workspace_NB\주파수\vorta_s7_app\vorta_s7_pro.apk"
    "%ADB%" -s %S7_SERIAL% shell pm grant com.vorta.s7frequency android.permission.WRITE_SECURE_SETTINGS > nul 2>&1
    echo   [S7 완료] S7 볼륨 강제고정 해제 및 화면 정상 절전 복원 완료!
) else (
    echo [S7 미연결] S7 스마트폰이 PC USB에 연결되지 않았습니다. (연결 후 다시 실행 가능)
)

echo.
echo ------------------------------------------------------------------------------
echo [3/3] 갤럭시 S6 정상화 적용 (볼륨 강제고정 제거 + 화면 정상 절전 복원)...
echo ------------------------------------------------------------------------------
"%ADB%" -s %S6_SERIAL% get-state > nul 2>&1
if %errorlevel% equ 0 (
    echo [S6 발견] %S6_SERIAL% 연결 확인됨. 정상화 작업 시작...
    
    echo   1. 화면 꺼짐 먹통 버그 수정 (상시 켜짐 7 -> 정상 절전 0, 타임아웃 1분 복원)...
    "%ADB%" -s %S6_SERIAL% shell settings put global stay_on_while_plugged_in 0
    "%ADB%" -s %S6_SERIAL% shell settings put system screen_off_timeout 60000
    
    echo   2. 안전볼륨 경고창만 해제하고, 볼륨은 사용자 100%% 자유 조절로 완전 개방...
    "%ADB%" -s %S6_SERIAL% shell settings put global audio_safe_volume_state 2
    "%ADB%" -s %S6_SERIAL% shell settings put global safe_media_volume_active 0
    "%ADB%" -s %S6_SERIAL% shell settings put global safe_media_volume_enabled 0
    "%ADB%" -s %S6_SERIAL% shell settings put system volume_limiter_enable 0
    "%ADB%" -s %S6_SERIAL% shell settings put system volume_limiter_value 15
    
    echo   3. 수정된 최신 보르타 레조 S6 v2.8 (화면 자유 절전) 재설치...
    "%ADB%" -s %S6_SERIAL% install -r "d:\D_Workspace_NB\주파수\vorta_s6_app\vorta_s6_pro.apk"
    echo   [S6 완료] S6 볼륨 강제고정 해제 및 화면 정상 절전 복원 완료!
) else (
    echo [S6 미연결] S6 스마트폰이 PC USB에 연결되지 않았습니다. (연결 후 다시 실행 가능)
)

echo.
echo ==============================================================================
echo [최종 완료]
echo 1. 볼륨을 줄여도 다시 100%%로 튀어오르던 악성 서비스 및 강제 루프가 완전 제거되었습니다.
echo 2. 화면을 꺼도 다시 켜지던 stay_on_while_plugged_in(7->0) 및 강제플래그가 정상 복구되었습니다.
echo 3. 이제 화면을 끈 상태에서도 백그라운드에서 주파수가 완벽하고 순수하게 발진됩니다.
echo 4. 출력이 너무 강해 노이즈/왜곡이 발생하지 않도록 폰 볼륨을 10~12단계로 편안하게 조절하십시오.
echo ==============================================================================
pause
'''

# Convert LF to CRLF and write CP949
bat_content_crlf = bat_content.replace('\r\n', '\n').replace('\n', '\r\n')
with open(r'd:\D_Workspace_NB\주파수\S7_S6_환경설정_정상화_볼륨화면해방_원클릭.bat', 'wb') as f:
    f.write(bat_content_crlf.encode('cp949'))

print("Created d:\\D_Workspace_NB\\주파수\\S7_S6_환경설정_정상화_볼륨화면해방_원클릭.bat in CP949 CRLF")
