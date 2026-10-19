package com.vorta.s7frequency;

import android.content.Context;
import android.media.AudioManager;
import android.provider.Settings;
import android.util.Log;

public class S7VolumeHelper {
    private static final String TAG = "S7VolHelper";
    private static long sLastForceTimeMs = 0;

    // S7 Maximum Volume Unlocked (15/15 100% Full Power - No Volume Limitation):
    public static volatile int sTargetVolumeStep = 15;

    public static void enforceSystemFlags(Context context) {
        try {
            // Global & Secure system database flags for Samsung Galaxy S7 (Android 8.0.0)
            Settings.Global.putInt(context.getContentResolver(), "audio_safe_volume_state", 2);
            Settings.Global.putInt(context.getContentResolver(), "safe_media_volume_active", 0);
            Settings.Global.putInt(context.getContentResolver(), "safe_media_volume_enabled", 0);
            Settings.Global.putInt(context.getContentResolver(), "bluetooth_disable_absolute_volume", 1);
            Settings.Global.putInt(context.getContentResolver(), "stay_on_while_plugged_in", 0); // Allow screen to sleep normally!
            Settings.Secure.putString(context.getContentResolver(), "unsafe_volume_music_active_ms", "0");
        } catch (Exception e) {
            Log.w(TAG, "Global/Secure settings write skipped: " + e.getMessage());
        }

        try {
            if (Settings.System.canWrite(context)) {
                Settings.System.putInt(context.getContentResolver(), "safe_volume_multimedia", 0);
                Settings.System.putInt(context.getContentResolver(), "safe_volume_state", 0);
                Settings.System.putInt(context.getContentResolver(), "volume_limiter_enable", 0);
                Settings.System.putInt(context.getContentResolver(), "volume_limiter_value", 15);
                Settings.System.putInt(context.getContentResolver(), "volumelimit_on", 0);
                Settings.System.putInt(context.getContentResolver(), "screen_off_timeout", 60000); // 1 minute normal screen timeout
            }
        } catch (Exception ignored) {}
    }

    public static void ensureTargetVolumeIfNeeded(Context context, boolean forceAllDevices) {
        // Enforce safe media volume unlock flags so volume can reach up to 15 without warning dialogs,
        // but NEVER force or lock the volume level - user has 100% free volume control!
        enforceSystemFlags(context);
    }
}
