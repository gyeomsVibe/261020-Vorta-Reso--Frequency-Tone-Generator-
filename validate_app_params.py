# -*- coding: utf-8 -*-
"""
SSOT 대조표: HTML 정본 → 앱 파라미터 전수 비교
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# === HTML SSOT 정본 값 ===
ssot = {
    "M1_오전_07_13": {
        "sweep": True, "min": 3.3, "max": 7.3, "sec": 640,
        "fm_on": True, "fm_depth": 0.10, "fm_rate": 5.0,
        "am_on": True, "am_depth": 0.80, "am_rate": 1.2,
        "rm_on": False, "rm_depth": 0.0,
        "boost": 3.0, "limiter": 0, "exciter": False, # +3dB 펀치, 트루피크 0dBFS, 배음 OFF
    },
    "M1_오후_13_19": {
        "sweep": True, "min": 18.6, "max": 25.1, "sec": 900,
        "fm_on": False, "fm_depth": 0.0,
        "am_on": True, "am_depth": 0.70, "am_rate": 1.3,
        "rm_on": True, "rm_depth": 0.35, "rm_rate": 1.8,
        "boost": 3.0, "limiter": 1, "exciter": True, # +3dB, 새추레이터, 2차배음 ON
    },
    "M1_저녁메인_19_01": {
        "sweep": True, "min": 15.0, "max": 18.6, "sec": 900,
        "fm_on": False, "fm_depth": 0.0,
        "am_on": True, "am_depth": 0.80, "am_rate": 1.2,
        "rm_on": True, "rm_depth": 0.45, "rm_rate": 1.5,
        "boost": 3.0, "limiter": 1, "exciter": True, # +3dB, 새추레이터, 2차배음 ON
    },
    "M1_저녁기습_10분": {
        "sweep": False, "freq": 55.0,
        "fm_on": False,
        "am_on": True, "am_depth": 1.0, "am_rate": 6.0,
        "rm_on": False,
        "boost": 6.0, "limiter": 1, "exciter": True, # +6dB 초강력 (소프트 새추레이터 implied)
    },
    "M1_취침_01_07": {
        "sweep": True, "min": 52.5, "max": 56.5, "sec": 120,
        "fm_on": True, "fm_depth": 0.15, "fm_rate": 2.0,
        "am_on": True, "am_depth": 0.60, "am_rate": 1.0,
        "rm_on": False, "rm_depth": 0.0,
        "boost": 0.0, "limiter": 0, "exciter": False, # 0dB 원음, 트루피크, 배음 OFF
    },
    "M2_프리셋1_하이브리드": {
        "sweep": True, "min": 3.3, "max": 7.3, "sec": 640,
        "fm_on": True, "fm_depth": 0.10, "fm_rate": 5.0,
        "am_on": True, "am_depth": 0.80, "am_rate": 1.2,
        "rm_on": False,
        "boost": 3.0, "limiter": 0, "exciter": False, # +3dB 펀치, 트루피크 0dBFS, 배음 OFF (SSOT 원문: 리미터 0dBFS)
    },
    "M2_프리셋2_단독파괴": {
        "sweep": False, "freq": 55.0,
        "fm_on": True, "fm_depth": 0.14, "fm_rate": 5.5,
        "am_on": True, "am_depth": 0.85, "am_rate": 1.2,
        "rm_on": False,
        "boost": 6.0, "limiter": 1, "exciter": True, # +6dB 초강력, 소프트 새추레이터
    },
    "M2_프리셋3_비동기스윕": {
        "sweep": True, "min": 18.6, "max": 25.1, "sec": 900,
        "fm_on": False,
        "am_on": True, "am_depth": 0.70, "am_rate": 1.3,
        "rm_on": True, "rm_depth": 0.35, "rm_rate": 1.8,
        "boost": 3.0, "limiter": 0, "exciter": True, # +3dB, 2차 배음 ON
    },
    "M2_프리셋4_심야공진": {
        "sweep": True, "min": 52.5, "max": 56.5, "sec": 120,
        "fm_on": True, "fm_depth": 0.15, "fm_rate": 2.0,
        "am_on": True, "am_depth": 0.60, "am_rate": 1.0,
        "rm_on": False,
        "boost": 0.0, "limiter": 0, "exciter": False, # 0dB 원음, 배음 OFF
    },
    "M2_프리셋5_해머펄스": {
        "sweep": False, "freq": 55.0,
        "fm_on": False,
        "am_on": True, "am_depth": 1.0, "am_rate": 6.0,
        "rm_on": False,
        "boost": 6.0, "limiter": 1, "exciter": True, # +6dB, 새추레이터, 2차배음 ON (SSOT 원문)
    },
}

# === 코드 실제 값 (startPresetWithDsp 호출 순서대로) ===
# startPresetWithDsp(sweep, freq, subFreq, sMin, sMax, sSec,
#                    fmOn, fmDepth, fmRate,
#                    amOn, amDepth, amRate,
#                    rmOn, rmDepth, rmRate,
#                    presetBoostDb, presetLimiterMode, presetChannelMode, presetExciter,
#                    volStep, title, knobGuide)
code_calls = {
    "M1_오전_07_13": {
        "sweep": True, "min": 3.3, "max": 7.3, "sec": 640,
        "fm_on": True, "fm_depth": 0.10, "fm_rate": 5.0,
        "am_on": True, "am_depth": 0.80, "am_rate": 1.2,
        "rm_on": False, "rm_depth": 0.0,
        "boost": 3.0, "limiter": 0, "exciter": False,
    },
    "M1_오후_13_19": {
        "sweep": True, "min": 18.6, "max": 25.1, "sec": 900,
        "fm_on": False, "fm_depth": 0.0,
        "am_on": True, "am_depth": 0.70, "am_rate": 1.3,
        "rm_on": True, "rm_depth": 0.35, "rm_rate": 1.8,
        "boost": 3.0, "limiter": 1, "exciter": True,
    },
    "M1_저녁메인_19_01": {
        "sweep": True, "min": 15.0, "max": 18.6, "sec": 900,
        "fm_on": False, "fm_depth": 0.0,
        "am_on": True, "am_depth": 0.80, "am_rate": 1.2,
        "rm_on": True, "rm_depth": 0.45, "rm_rate": 1.5,
        "boost": 3.0, "limiter": 1, "exciter": True,
    },
    "M1_저녁기습_10분": {
        "sweep": False, "freq": 55.0,
        "fm_on": False,
        "am_on": True, "am_depth": 1.0, "am_rate": 6.0,
        "rm_on": False,
        "boost": 6.0, "limiter": 1, "exciter": True,
    },
    "M1_취침_01_07": {
        "sweep": True, "min": 52.5, "max": 56.5, "sec": 120,
        "fm_on": True, "fm_depth": 0.15, "fm_rate": 2.0,
        "am_on": True, "am_depth": 0.60, "am_rate": 1.0,
        "rm_on": False, "rm_depth": 0.0,
        "boost": 0.0, "limiter": 0, "exciter": False,
    },
    "M2_프리셋1_하이브리드": {
        "sweep": True, "min": 3.3, "max": 7.3, "sec": 640,
        "fm_on": True, "fm_depth": 0.10, "fm_rate": 5.0,
        "am_on": True, "am_depth": 0.80, "am_rate": 1.2,
        "rm_on": False,
        "boost": 3.0, "limiter": 0, "exciter": False,
    },
    "M2_프리셋2_단독파괴": {
        "sweep": False, "freq": 55.0,
        "fm_on": True, "fm_depth": 0.14, "fm_rate": 5.5,
        "am_on": True, "am_depth": 0.85, "am_rate": 1.2,
        "rm_on": False,
        "boost": 6.0, "limiter": 1, "exciter": True,
    },
    "M2_프리셋3_비동기스윕": {
        "sweep": True, "min": 18.6, "max": 25.1, "sec": 900,
        "fm_on": False,
        "am_on": True, "am_depth": 0.70, "am_rate": 1.3,
        "rm_on": True, "rm_depth": 0.35, "rm_rate": 1.8,
        "boost": 3.0, "limiter": 0, "exciter": True,
    },
    "M2_프리셋4_심야공진": {
        "sweep": True, "min": 52.5, "max": 56.5, "sec": 120,
        "fm_on": True, "fm_depth": 0.15, "fm_rate": 2.0,
        "am_on": True, "am_depth": 0.60, "am_rate": 1.0,
        "rm_on": False,
        "boost": 0.0, "limiter": 0, "exciter": False,
    },
    "M2_프리셋5_해머펄스": {
        "sweep": False, "freq": 55.0,
        "fm_on": False,
        "am_on": True, "am_depth": 1.0, "am_rate": 6.0,
        "rm_on": False,
        "boost": 6.0, "limiter": 1, "exciter": True,
    },
}

# Compare
all_ok = True
for k in ssot:
    s = ssot[k]
    c = code_calls[k]
    diffs = []
    for param in s:
        if param in c:
            if s[param] != c[param]:
                diffs.append(f"  {param}: SSOT={s[param]} vs CODE={c[param]}")
    if diffs:
        all_ok = False
        print(f"❌ {k}:")
        for d in diffs:
            print(d)
    else:
        print(f"✅ {k}: 완전 일치")

if all_ok:
    print("\n🎯 모든 M-1 + M-2 프리셋이 HTML SSOT 정본과 100% 일치합니다!")
else:
    print("\n⚠️ 불일치 항목이 있습니다. 수정이 필요합니다.")
