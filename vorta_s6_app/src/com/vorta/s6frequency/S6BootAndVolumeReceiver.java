package com.vorta.s6frequency;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.media.AudioManager;
import android.util.Log;

public class S6BootAndVolumeReceiver extends BroadcastReceiver {
    private static final String TAG = "S6BootVolRcvr";

    @Override
    public void onReceive(final Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) return;
        String action = intent.getAction();

        if (Intent.ACTION_BOOT_COMPLETED.equals(action)
                || "android.intent.action.LOCKED_BOOT_COMPLETED".equals(action)
                || Intent.ACTION_HEADSET_PLUG.equals(action)) {
            Log.i(TAG, "Event " + action + " -> Enforcing S6 Target Volume " + S6VolumeHelper.sTargetVolumeStep);
            S6VolumeHelper.ensureTargetVolumeIfNeeded(context, true);

            int[] delays = {500, 1500, 3000, 6000, 12000, 20000, 30000};
            android.os.Handler h = new android.os.Handler(android.os.Looper.getMainLooper());
            for (final int d : delays) {
                h.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        S6VolumeHelper.ensureTargetVolumeIfNeeded(context, true);
                    }
                }, d);
            }
        } else if ("android.media.VOLUME_CHANGED_ACTION".equals(action)) {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                int cur = am.getStreamVolume(AudioManager.STREAM_MUSIC);
                Log.i(TAG, "S6 Volume event observed: cur=" + cur + "/15");
                if (cur < 15) {
                    S6VolumeHelper.ensureTargetVolumeIfNeeded(context, true);
                }
            }
        }
    }
}
