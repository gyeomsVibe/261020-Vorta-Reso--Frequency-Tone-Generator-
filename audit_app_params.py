# -*- coding: utf-8 -*-
import re, sys

forbidden_words = ["스마토", "Wavelet", "젠보르타", "레조웨이브", "Resonix"]

def audit_file(path, app_name):
    print(f"=== Auditing {app_name}: {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Forbidden words check
    for word in forbidden_words:
        assert word not in content, f"FAILED: Forbidden word '{word}' found in {path}!"
    print("  [PASS] 0 forbidden words found.")

    # 2. Max frequency check
    # Find all float literals near Hz or in startPresetWithDsp
    calls = re.findall(r'startPresetWithDsp\(([\s\S]+?)\);', content)
    print(f"  [INFO] Total presets found: {len(calls)}")
    
    sweep_count = 0
    single_count = 0
    fm_count = 0
    am_count = 0
    rm_count = 0
    pure_count = 0

    for i, c in enumerate(calls):
        if 'boolean' in c or 'float freq' in c:
            continue
        args = [a.strip() for a in c.split(',')]
        # args[0]: isSweep (boolean)
        # args[1]: freq (float)
        # args[2]: subFreq (float)
        # args[3]: sweepMin (float)
        # args[4]: sweepMax (float)
        # args[5]: sweepSec (float)
        # args[6]: fmOn
        # args[7]: fmDepth
        # args[8]: fmRate
        # args[9]: amOn
        # args[10]: amDepth
        # args[11]: amRate
        # args[12]: rmOn
        # args[13]: rmDepth
        # args[14]: rmRate
        is_sweep = args[0] == 'true'
        freq = float(args[1].replace('f', ''))
        sub_freq = float(args[2].replace('f', ''))
        sweep_min = float(args[3].replace('f', ''))
        sweep_max = float(args[4].replace('f', ''))
        
        # Check frequency <= 55.0Hz
        if is_sweep:
            sweep_count += 1
            assert sweep_min <= 55.0, f"Preset {i+1} sweep_min {sweep_min} > 55.0Hz!"
            assert sweep_max <= 55.0, f"Preset {i+1} sweep_max {sweep_max} > 55.0Hz!"
            assert sweep_min >= 1.0, f"Preset {i+1} sweep_min {sweep_min} < 1.0Hz!"
        else:
            single_count += 1
            assert freq <= 55.0, f"Preset {i+1} freq {freq} > 55.0Hz!"
            assert freq >= 1.0, f"Preset {i+1} freq {freq} < 1.0Hz!"

        fm_on = args[6] == 'true'
        am_on = args[9] == 'true'
        rm_on = args[12] == 'true'

        if fm_on: fm_count += 1
        if am_on: am_count += 1
        if rm_on: rm_count += 1
        if not fm_on and not am_on and not rm_on: pure_count += 1

    print(f"  [BALANCE] Single: {single_count} | Sweep: {sweep_count} (Total: {len(calls)})")
    print(f"  [MODULATION] FM: {fm_count} | AM: {am_count} | RM: {rm_count} | Pure: {pure_count}")
    
    # Check that Single and Sweep are balanced (neither is < 30% of total)
    ratio = single_count / len(calls)
    assert 0.40 <= ratio <= 0.60, f"Ratio of Single ({ratio:.2f}) is biased! Must be 40%~60%."
    print(f"  [PASS] Single/Sweep balance ratio: {ratio:.1%} Single vs {1-ratio:.1%} Sweep")
    print(f"=== {app_name} Audit PASSED ===\n")

if __name__ == '__main__':
    audit_file('vorta_s7_app/src/com/vorta/s7frequency/MainActivity.java', 'Galaxy S7 App')
    audit_file('vorta_s6_app/src/com/vorta/s6frequency/MainActivity.java', 'Galaxy S6 App')
