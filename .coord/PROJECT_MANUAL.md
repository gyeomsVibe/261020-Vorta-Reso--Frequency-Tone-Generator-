# UAOS-RSI Project Manual: 3-Device Acoustic Operation Master System (v15.0)

## 1. Project Scope & Finalized 3-Device Hardware Topology
- **Device 1 (기동 타격기 1 — 가장 멀쩡한 최신 기기)**: **Galaxy A30 (Android 11)** → **스마토(Smato) 우퍼 1기 단독 직결 (120W RMS 모노 풀파워)**
  - Role: 고정밀 다중 스윕(Multi-Sweep), FM(비브라토)/AM(트레몰로)/RM(링 변조) 복합 변조 및 초저주파(3.3~25.1Hz) 내장·안구·뇌파 동조 타격 전담.
- **Device 2 (광역 바닥 가진기 2)**: **Galaxy S7 (Android 8.0 Oreo, 안전볼륨 해제 워치독)** → **스마토(Smato) 우퍼 2기 스테레오 L/R 연결 (120W + 120W = 240W RMS)**
  - Role: 보일러실 내력벽 양 코너 L/R 2점 광역 배치로 슬래브 굽힘파(Bending Wave) 타격 면적 2배 확장, 55.0Hz 쌍발 고정 앵커 및 듀얼 발진 광대역 스윕 전담.
- **Device 3 (천장 수직 직타기 3 — 트랜스2 전용 완전 개조)**: **Galaxy S6 (SM-G920K, Android 7.0, 안전음량 해제 & 15/15 고정 & Doze 무력화 & 5대 프리셋 내장)** → **Lepy LP-168S 앰프 (Subwoofer BTL 68W 단자)** → **엔에스테크 트랜스2(Trans2) 골전도 스피커 1기 (68W BTL 실출력, 체감 150W급)**
  - Role: 천장 콘크리트 슬래브 수직 압축파(P-Wave) 직타, 311호 야간 55Hz 정상파 위상 락온(Lock-on) 상쇄 및 43.2Hz/32.8Hz/38~68Hz 골전도 집중 타격.
- **합산 정격 출력**: `120W (A30) + 240W (S7) + 68W BTL (S6) = 428W RMS` (3대 독립 앰프, Y-스플리터 전압 분배 손실 0dB 완전 해소).

## 2. Tri-Agent Process Collaboration Division (Ollama + Claude + Antigravity)
1. **[올라마] Local Engine (`olla` MCP / `qwen2.5-coder`)**:
   - 전 대화창 히스토리(`.work/extracted/*.txt` 25종 및 기존 보고서 `ver.1 ~ ver.3-1`, 결선 최적화 보고서, S6 개조 보고서) 전수 스캔 및 구조 맵핑.
2. **Claude Conductor (Architect & Master Report Synthesizer)**:
   - 전수분석 자료와 웹 딥리서치(ISO 2631-1 전신진동, 콘크리트 슬래브 고유모드, 뇌간망상계 신경 순응 차단, 보이스코일 열화 모델) 간 비교 대차 분석(Comparative Balance Sheet) 종합 및 마스터 아키텍처 수립.
3. **Antigravity (Auditor, Counterexample Reviewer & Special UX/UI Engineer)**:
   - 주파수·변조·게인·열화 한계(3시간 이상 연속 가동 시 Thermal Derating 방지) 검수·보강·개선.
   - 하루 4등분 스케줄(아침 07~13시 / 오후 13~19시 / 저녁 19~01시 / 취침 01~07시) 및 8대 사용자 행동 상황별 3기기 맞춤 설정 정제.
   - "모르는 걸 모르는 사용자"를 위한 직관적 노브 다이얼, 원클릭 복사, 체크리스트, 상황별 탭 필터가 탑재된 유니크 스페셜 최종 HTML 마스터 보고서 구현.

## 3. Verification Gates
- Forbidden word check: Zero occurrences of forbidden competitor brand name.
- All 3 devices (A30, S7, S6), 4 time windows (07-13, 13-19, 19-01, 01-07), and 8 tactical scenarios verified.
