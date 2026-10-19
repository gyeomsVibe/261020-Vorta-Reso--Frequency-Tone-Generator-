package com.smato.a30frequency;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.util.Log;

/**
 * A30 전용 경량 수신기 (핸드폰 리소스 최적화 절약 모드).
 * 재부팅(Boot Completed) 시 사용자의 이전 설정 및 활성 주파수 발진 상태를 자동 복원합니다.
 */
public class A30BootAndVolumeReceiver extends BroadcastReceiver {
    private static final String TAG = "A30BootRcvr";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) return;
        String action = intent.getAction();

        if (Intent.ACTION_BOOT_COMPLETED.equals(action)
                || "android.intent.action.LOCKED_BOOT_COMPLETED".equals(action)) {
            Log.i(TAG, "A30 Boot Completed: 시스템 준비 및 영구 설정 복원 시작");
            A30AudioGeneratorService.loadConfig(context);
            SharedPreferences sp = context.getSharedPreferences(A30AudioGeneratorService.PREF_NAME, Context.MODE_PRIVATE);
            boolean wasPlaying = sp.getBoolean(A30AudioGeneratorService.KEY_IS_PLAYING, false);
            if (wasPlaying) {
                Intent svc = new Intent(context, A30AudioGeneratorService.class);
                svc.putExtra("sweep", sp.getBoolean(A30AudioGeneratorService.KEY_IS_SWEEP, true));
                svc.putExtra("sweep_min", sp.getFloat(A30AudioGeneratorService.KEY_SWEEP_MIN, 3.3f));
                svc.putExtra("sweep_max", sp.getFloat(A30AudioGeneratorService.KEY_SWEEP_MAX, 7.3f));
                svc.putExtra("sweep_sec", sp.getFloat(A30AudioGeneratorService.KEY_SWEEP_SEC, 640.0f));
                svc.putExtra("freq", sp.getFloat(A30AudioGeneratorService.KEY_TARGET_FREQ, 18.98f));
                svc.putExtra("sub_freq", sp.getFloat(A30AudioGeneratorService.KEY_SUB_FREQ, 0.0f));
                svc.putExtra("fm_on", sp.getBoolean(A30AudioGeneratorService.KEY_FM_ON, true));
                svc.putExtra("fm_depth", sp.getFloat(A30AudioGeneratorService.KEY_FM_DEPTH, 0.10f));
                svc.putExtra("fm_rate", sp.getFloat(A30AudioGeneratorService.KEY_FM_RATE, 5.0f));
                svc.putExtra("am_on", sp.getBoolean(A30AudioGeneratorService.KEY_AM_ON, true));
                svc.putExtra("am_depth", sp.getFloat(A30AudioGeneratorService.KEY_AM_DEPTH, 0.80f));
                svc.putExtra("am_rate", sp.getFloat(A30AudioGeneratorService.KEY_AM_RATE, 1.2f));
                svc.putExtra("rm_on", sp.getBoolean(A30AudioGeneratorService.KEY_RM_ON, false));
                svc.putExtra("rm_depth", sp.getFloat(A30AudioGeneratorService.KEY_RM_DEPTH, 0.0f));
                svc.putExtra("rm_rate", sp.getFloat(A30AudioGeneratorService.KEY_RM_RATE, 1.0f));
                svc.putExtra("title", sp.getString(A30AudioGeneratorService.KEY_MODE_TITLE, "[오전 07~13시] 3.3~7.3Hz(640초)"));
                svc.putExtra("knob", sp.getString(A30AudioGeneratorService.KEY_KNOB_GUIDE, "우퍼 1: 볼륨 1시(60%)"));
                if (Build.VERSION.SDK_INT >= 26) {
                    context.startForegroundService(svc);
                } else {
                    context.startService(svc);
                }
                Log.i(TAG, "A30 Boot Completed: 재부팅 전 활성 발진 상태 자동 복원 성공");
            }
        }
    }
}
