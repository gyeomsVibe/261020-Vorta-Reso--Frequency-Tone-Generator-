# 📱 갤럭시 S6 (SM-G920K) Lepy LP-168S 앰프 전용 머신 하드웨어·OS 전수개조 마스터 명세서

> **MIA 전략절차 11단계 표준 프레임워크 준수 | UAOS-RSI Canonical Architecture**  
> **타겟 장비: 삼성 갤럭시 S6 (SM-G920K, Android 7.0 Nougat, Wolfson WM1840 DAC)**  
> **전용 앰프: Lepy LP-168S (2.1채널 Hi-Fi 45W×2 + 68W BTL 서브우퍼)**  
> **타겟 스피커: 골전도 트랜스듀서 2호 (트랜스2 천장 슬래브 수직 압착 앵커)**

---

## 1. 개조 개요 및 공학적 배경
단순한 주파수 발생기 앱 업데이트가 아니라, **갤럭시 S6 스마트폰 자체의 하드웨어 오디오 HAL 및 안드로이드 OS 전역 환경**을 Lepy LP-168S 앰프 전용 오디오 소스 발생기 머신으로 전수개조(Overhaul)하여 타격력 손실 원인을 원천 제거했습니다.

---

## 2. 스마트폰 6대 영역 전수개조(Overhaul) 상세 규격

### 2.1 삼성 SoundAlive 음장 및 DRC 필터 영구 동결
- **조치:** `pm disable-user --user 0 com.sec.android.app.soundalive`, `com.sec.hearingadjust`, `com.samsung.android.game.gos`
- **효과:** 안드로이드 프레임워크 단에서 30Hz 이하 초저역을 잘라내고 다이내믹 레인지를 압축하던 삼성 오디오 이펙트를 100% 동결하여 순수 원음 전달.

### 2.2 안드로이드 안전음량(Safe Volume) & 리미터 영구 무력화
- **조치:** `settings put global audio_safe_volume_state 2`, `safe_media_volume_active 0`, `safe_media_volume_enabled 0`, `setprop audio.safemedia.bypass true`
- **효과:** 3.5mm 이어폰/AUX 체결 시 9/15로 강제 감쇄되는 보호 기능 영구 차단. 20시간 경고 팝업 없이 항시 15/15 유지.

### 2.3 3.5mm AUX 라인출력 15/15 (0.00dBFS Line-Out Max) 강제 고정
- **조치:** `settings put system volume_music 15`, `volume_music_headset 15`, `volume_music_headphone 15`
- **효과:** Wolfson WM1840 DAC의 최대 전압 스윙(~0.8V RMS)을 Lepy LP-168S 입력단에 100% 인가하여 앰프 정격 전력 완전 인출.

### 2.4 시스템 알림, 벨소리, 터치음, 진동 100% 무음화
- **조치:** `volume_ring 0`, `volume_notification 0`, `volume_system 0`, `sound_effects_enabled 0`, `dtmf_tone 0`, `haptic_feedback_enabled 0`
- **효과:** 천장 골전도 진동자로 시스템 비프음, 알림음 등 잡음 유입 원천 차단.

### 2.5 24/7 Always-On 화면 유지 및 잠금화면 완전 해제
- **조치:** `settings put global stay_on_while_plugged_in 7`, `settings put secure lockscreen.disabled 1`, `screen_off_timeout 2147483647`, `screen_brightness 15`
- **효과:** 무인 상시 충전 가동 및 전원 연결 즉시 헤드리스 제어 가능, 초저휘도 설정으로 발열/번인 최소화.

### 2.6 Doze 모드 및 백그라운드 절전 킬러 완전 차단
- **조치:** `settings put global sem_low_power_mode 0`, `dumpsys deviceidle whitelist +com.vorta.s6frequency`, `dumpsys deviceidle disable`
- **효과:** 백그라운드 LMK 프로세스 킬 차단으로 24시간 무중단 발진 보장.

---

## 3. Lepy LP-168S 앰프 노브 정밀 매칭 가이드
- **SUB VOLUME:** **3.5 ~ 4.0 (9시 30분 ~ 10시 방향)** (68W BTL 무왜곡 드라이브)
- **X-OVER:** **65 Hz ~ 85 Hz (8시 30분 ~ 10시 방향)** (55Hz/40Hz/22Hz/7Hz 무손실 통과, 고주파 차단)
- **TREBLE:** **7시 방향 고정 (-10dB 최소)** (앰프 스위칭 노이즈 100% 차단, 211호 스텔스 유지)
- **BASS:** **12시 ~ 1시 방향 (0 ~ +2dB)** (50~60Hz 슬래브 굽힘파 진동 보강)
- **MAIN VOLUME:** **5.5 ~ 6.0 (12시 30분 ~ 1시 방향)** (안정적 정격 출력 전압 공급)

---

## 4. 원클릭 실행 스크립트 및 도구
- **스마트폰 내부 상주 데몬:** `/data/local/tmp/s6_lepy_dedicated.sh` (기기 자체 실행)
- **PC 원클릭 전수개조 배치:** `d:\D_Workspace_NB\주파수\갤럭시S6_Lepy168S_전용기기_전수개조.bat`
- **사용자용 시각화 HTML 보고서:** `d:\D_Workspace_NB\주파수\갤럭시S6_Lepy168S_전용기기_전수개조_사용자_보고서.html`
