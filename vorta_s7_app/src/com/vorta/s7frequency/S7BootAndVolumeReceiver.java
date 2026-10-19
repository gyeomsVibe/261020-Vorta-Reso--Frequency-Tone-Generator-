package com.vorta.s7frequency;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.media.AudioManager;
import android.util.Log;

public class S7BootAndVolumeReceiver extends BroadcastReceiver {
    private static final String TAG = "S7BootVolRcvr";

    @Override
    public void onReceive(final Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) return;
        String action = intent.getAction();

        if (Intent.ACTION_BOOT_COMPLETED.equals(action)
                || "android.intent.action.LOCKED_BOOT_COMPLETED".equals(action)
                || Intent.ACTION_HEADSET_PLUG.equals(action)) {
            Log.i(TAG, "Event " + action + " -> Enforcing S7 Target Volume " + S7VolumeHelper.sTargetVolumeStep);
            S7VolumeHelper.ensureTargetVolumeIfNeeded(context, true);

            int[] delays = {500, 1500, 3000, 6000, 12000, 20000, 30000};
            android.os.Handler h = new android.os.Handler(android.os.Looper.getMainLooper());
            for (final int d : delays) {
                h.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        S7VolumeHelper.ensureTargetVolumeIfNeeded(context, true);
                    }
                }, d);
            }
        } else if ("android.media.VOLUME_CHANGED_ACTION".equals(action)) {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                int cur = am.getStreamVolume(AudioManager.STREAM_MUSIC);
                Log.i(TAG, "S7 Volume event observed: cur=" + cur + "/15");
            }
        }
    }
}
