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
            Log.i(TAG, "Event " + action + " -> Applying S6 safe volume bypass flags (user controls volume freely)");
            S6VolumeHelper.enforceSystemFlags(context);
        } else if ("android.media.VOLUME_CHANGED_ACTION".equals(action)) {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                int cur = am.getStreamVolume(AudioManager.STREAM_MUSIC);
                Log.i(TAG, "S6 Volume changed by user: " + cur + "/15 (no override)");
            }
        }
    }
}
