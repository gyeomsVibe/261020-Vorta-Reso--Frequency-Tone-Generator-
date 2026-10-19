package com.trans2.frequencygenerator;

import android.content.Context;
import android.media.AudioManager;
import android.provider.Settings;
import android.util.Log;
import java.lang.reflect.Method;

public class AudioVolumeHelper {
    private static final String TAG = "Trans2VolHelper";
    private static long sLastForceTimeMs = 0;

    public static void enforceSystemFlags(Context context) {
        try {
            Settings.Global.putInt(context.getContentResolver(), "audio_safe_volume_state", 1);
            Settings.Global.putInt(context.getContentResolver(), "safe_media_volume_active", 0);
            Settings.Global.putInt(context.getContentResolver(), "safe_media_volume_enabled", 0);
            Settings.Global.putInt(context.getContentResolver(), "bluetooth_disable_absolute_volume", 1);
            Settings.Secure.putString(context.getContentResolver(), "unsafe_volume_music_active_ms", "0");
        } catch (Exception e) {
            Log.w(TAG, "Global/Secure settings write skipped: " + e.getMessage());
        }

        try {
            if (Settings.System.canWrite(context)) {
                Settings.System.putInt(context.getContentResolver(), "safe_volume_multimedia", 0);
                Settings.System.putInt(context.getContentResolver(), "safe_volume_state", 0);
                Settings.System.putInt(context.getContentResolver(), "volume_limiter_enable", 1);
                Settings.System.putInt(context.getContentResolver(), "volume_limiter_value", 15);
            }
        } catch (Exception ignored) {}
    }

    public static void ensureVolume15IfNeeded(Context context, boolean forceAllDevices) {
        AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
        if (am == null) return;

        int cur = am.getStreamVolume(AudioManager.STREAM_MUSIC);
        long now = System.currentTimeMillis();

        // Idempotent guard: if volume is already 15 and not forced, do zero IPC calls to prevent broadcast loops
        if (!forceAllDevices && cur >= 15) {
            return;
        }

        // Cooldown guard (500ms) to prevent VOLUME_CHANGED_ACTION feedback loop
        if (forceAllDevices && cur >= 15 && (now - sLastForceTimeMs) < 500) {
            return;
        }
        sLastForceTimeMs = now;

        enforceSystemFlags(context);

        try {
            am.setStreamVolume(AudioManager.STREAM_MUSIC, 15, 0);
        } catch (Exception ignored) {}

        try {
            Class<?> audioSystem = Class.forName("android.media.AudioSystem");
            Method setVolume = audioSystem.getMethod("setStreamVolumeIndex", int.class, int.class, int.class);
            int[] devices = {
                0x2,        // DEVICE_OUT_SPEAKER
                0x4,        // DEVICE_OUT_WIRED_HEADSET
                0x8,        // DEVICE_OUT_WIRED_HEADPHONE
                0x80,       // DEVICE_OUT_BLUETOOTH_A2DP
                0x100,      // DEVICE_OUT_BLUETOOTH_A2DP_HEADPHONES
                0x200,      // DEVICE_OUT_BLUETOOTH_A2DP_SPEAKER
                0x40000000  // DEVICE_OUT_DEFAULT
            };
            for (int dev : devices) {
                try {
                    setVolume.invoke(null, 3, 15, dev);
                } catch (Exception ignored) {}
            }
            Log.i(TAG, "Volume 15 enforced cleanly (prev=" + cur + ", forceAll=" + forceAllDevices + ")");
        } catch (Exception e) {
            Log.e(TAG, "AudioSystem reflection error: " + e.getMessage());
        }
    }

    public static void forceAllDevicesVolume15(Context context) {
        ensureVolume15IfNeeded(context, true);
    }
}
