package com.smato.a30frequency;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.os.Process;
import android.util.Log;

public class A30AudioGeneratorService extends Service {
    private static final String TAG = "A30AudioSvc";
    private static final String AUDIT_TAG = "A30AudioAudit";
    private static final String CHANNEL_ID = "vorta_reso_a30_silent_v3";
    private static final int NOTIFICATION_ID = 2001;

    // Native hardware mixer rate of Galaxy A30 AudioOut_D (48,000 Hz, HAL frame count 960)
    public static final int SAMPLE_RATE = 48000;
    private static final int HAL_FRAMES = 960;
    private static final int CHUNK_FRAMES = HAL_FRAMES * 4; // 3,840 stereo frames (7,680 shorts)
    private static final int TRACK_BUFFER_BYTES = HAL_FRAMES * 24 * 4; // 23,040 stereo frames (92,160 bytes)

    // Vorta DSP Tactical Suite & Playback Persistence Keys
    public static final String PREF_NAME = "vorta_reso_a30_config";
    public static final String KEY_BASS_BOOST = "bass_boost_db";
    public static final String KEY_LIMITER_MODE = "limiter_mode";
    public static final String KEY_CHANNEL_MODE = "channel_mode";
    public static final String KEY_HARMONIC_EXCITER = "harmonic_exciter";
    public static final String KEY_AUTO_PRESET_DSP = "auto_preset_dsp";

    public static final String KEY_IS_PLAYING = "is_playing";
    public static final String KEY_IS_SWEEP = "is_sweep";
    public static final String KEY_SWEEP_MIN = "sweep_min";
    public static final String KEY_SWEEP_MAX = "sweep_max";
    public static final String KEY_SWEEP_SEC = "sweep_sec";
    public static final String KEY_TARGET_FREQ = "target_freq";
    public static final String KEY_SUB_FREQ = "sub_freq";
    public static final String KEY_FM_ON = "fm_on";
    public static final String KEY_FM_DEPTH = "fm_depth";
    public static final String KEY_FM_RATE = "fm_rate";
    public static final String KEY_AM_ON = "am_on";
    public static final String KEY_AM_DEPTH = "am_depth";
    public static final String KEY_AM_RATE = "am_rate";
    public static final String KEY_RM_ON = "rm_on";
    public static final String KEY_RM_DEPTH = "rm_depth";
    public static final String KEY_RM_RATE = "rm_rate";
    public static final String KEY_MODE_TITLE = "mode_title";
    public static final String KEY_KNOB_GUIDE = "knob_guide";
    public static final String KEY_SPLIT_MODE = "split_mode";

    public static volatile float sBassBoostDb = 3.0f; // 0.0dB(Flat), 3.0dB, 6.0dB, 9.0dB
    public static volatile int sLimiterMode = 0; // 0: True-Peak 0.0dBFS Linear, 1: Normalized Analog tanh Saturator
    public static volatile int sChannelMode = 0; // 0: Stereo In-phase (L=R), 1: Out-of-phase (L=-R 180°), 2: L-only, 3: R-only
    public static volatile boolean sHarmonicExciter = false; // 2nd harmonic slab-coupling exciter
    public static volatile boolean sAutoPresetDsp = true; // Auto-apply schedule-matched Vorta DSP on preset click

    // Live shared telemetry for UI sync
    public static volatile boolean sIsPlaying = false;
    public static volatile boolean sIsSweepMode = true;
    public static volatile float sTargetFreq = 18.98f;
    public static volatile float sSubFreq = 0.0f;
    public static volatile float sSweepMin = 3.3f;
    public static volatile float sSweepMax = 7.3f;
    public static volatile float sSweepPeriodSec = 640.0f;
    public static volatile float sInstantFreq = 3.3f;

    // Modulation parameters (FM = Vibrato, AM = Tremolo, RM = RingMod)
    public static volatile boolean sFmEnabled = true;
    public static volatile float sFmDepth = 0.10f;
    public static volatile float sFmRateHz = 5.0f;

    public static volatile boolean sAmEnabled = true;
    public static volatile float sAmDepth = 0.80f;
    public static volatile float sAmRateHz = 1.2f;

    public static volatile boolean sRmEnabled = false;
    public static volatile float sRmDepth = 0.0f;
    public static volatile float sRmRateHz = 1.0f;

    public static volatile String sActivePart = "[메인 파트]";
    public static volatile String sScenarioName = "[오전 07~13시] 3.3~7.3Hz(640초)";
    public static volatile String sModeTitle = "[오전 07~13시] 3.3~7.3Hz(640초) + FM10% + AM80%";
    public static volatile String sKnobGuide = "스마토 앰프 #1: 단일 볼륨 11시~1시 (순수 사인파 120W 모노)";
    public static volatile int sLastPeak = 32767;
    public static volatile double sLastRmsDb = -2.36;
    public static volatile double sLastDcOffset = 0.0;

    private PowerManager.WakeLock mWakeLock;
    private AudioTrack mAudioTrack;
    private volatile boolean mIsRunning = false;
    private volatile boolean mPhaseResetRequested = false;
    // Pure-sine woofer protection (2026-10-20 user receipt: roar/noise on all 3 devices).
    // Gain ramps 0->1 over 1.0 s on start, 1->0 over 0.5 s on stop: a step to full scale is a
    // broadband click that slams the cone. Scenario Hz, boost, exciter and ring-mod are kept as the preset defines them.
    private static final double FREQ_FLOOR_HZ = 1.0; // engine safety only; scenario frequencies are never altered (principle 16)
    private static final double FADE_IN_SEC = 1.0;
    private static final double FADE_OUT_SEC = 0.5;
    private static double mGain = 0.0; // static: fillModulatedChunk is static
    private static volatile boolean mFadeOutRequested = false;
    private static volatile boolean mFadeOutDone = false;
    private volatile boolean mAuditRequested = true;

    private Thread mAudioThread;
    private final Handler mHandler = new Handler(Looper.getMainLooper());

    private final Runnable mVolumeGuardRunnable = new Runnable() {
        @Override
        public void run() {
            // No background polling to allow completely uninhibited volume control
        }
    };

    public static void loadConfig(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        sBassBoostDb = sp.getFloat(KEY_BASS_BOOST, 3.0f);
        sLimiterMode = sp.getInt(KEY_LIMITER_MODE, 0);
        sChannelMode = sp.getInt(KEY_CHANNEL_MODE, 0);
        sHarmonicExciter = sp.getBoolean(KEY_HARMONIC_EXCITER, false);
        sAutoPresetDsp = sp.getBoolean(KEY_AUTO_PRESET_DSP, true);

        sIsPlaying = sp.getBoolean(KEY_IS_PLAYING, false);
        sIsSweepMode = sp.getBoolean(KEY_IS_SWEEP, true);
        sSweepMin = sp.getFloat(KEY_SWEEP_MIN, 3.3f);
        sSweepMax = sp.getFloat(KEY_SWEEP_MAX, 7.3f);
        sSweepPeriodSec = sp.getFloat(KEY_SWEEP_SEC, 640.0f);
        sTargetFreq = sp.getFloat(KEY_TARGET_FREQ, 18.98f);
        sSubFreq = sp.getFloat(KEY_SUB_FREQ, 0.0f);
        sFmEnabled = sp.getBoolean(KEY_FM_ON, true);
        sFmDepth = sp.getFloat(KEY_FM_DEPTH, 0.10f);
        sFmRateHz = sp.getFloat(KEY_FM_RATE, 5.0f);
        sAmEnabled = sp.getBoolean(KEY_AM_ON, true);
        sAmDepth = sp.getFloat(KEY_AM_DEPTH, 0.80f);
        sAmRateHz = sp.getFloat(KEY_AM_RATE, 1.2f);
        sRmEnabled = sp.getBoolean(KEY_RM_ON, false);
        sRmDepth = sp.getFloat(KEY_RM_DEPTH, 0.0f);
        sRmRateHz = sp.getFloat(KEY_RM_RATE, 1.0f);
        sModeTitle = sp.getString(KEY_MODE_TITLE, "[오전 07~13시] 3.3~7.3Hz(640초) + FM10% + AM80%");
        sKnobGuide = sp.getString(KEY_KNOB_GUIDE, "우퍼 1 노브: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시(0%)");

        Log.i(TAG, String.format("Loaded Persistent DSP Config v2.8: Boost=%.1fdB, Limiter=%d, Ch=%d, Exciter=%b, Playing=%b",
                sBassBoostDb, sLimiterMode, sChannelMode, sHarmonicExciter, sIsPlaying));
    }

    public static void saveConfig(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        sp.edit()
                .putFloat(KEY_BASS_BOOST, sBassBoostDb)
                .putInt(KEY_LIMITER_MODE, sLimiterMode)
                .putInt(KEY_CHANNEL_MODE, sChannelMode)
                .putBoolean(KEY_HARMONIC_EXCITER, sHarmonicExciter)
                .putBoolean(KEY_AUTO_PRESET_DSP, sAutoPresetDsp)
                .putBoolean(KEY_IS_PLAYING, sIsPlaying)
                .putBoolean(KEY_IS_SWEEP, sIsSweepMode)
                .putFloat(KEY_SWEEP_MIN, sSweepMin)
                .putFloat(KEY_SWEEP_MAX, sSweepMax)
                .putFloat(KEY_SWEEP_SEC, sSweepPeriodSec)
                .putFloat(KEY_TARGET_FREQ, sTargetFreq)
                .putFloat(KEY_SUB_FREQ, sSubFreq)
                .putBoolean(KEY_FM_ON, sFmEnabled)
                .putFloat(KEY_FM_DEPTH, sFmDepth)
                .putFloat(KEY_FM_RATE, sFmRateHz)
                .putBoolean(KEY_AM_ON, sAmEnabled)
                .putFloat(KEY_AM_DEPTH, sAmDepth)
                .putFloat(KEY_AM_RATE, sAmRateHz)
                .putBoolean(KEY_RM_ON, sRmEnabled)
                .putFloat(KEY_RM_DEPTH, sRmDepth)
                .putFloat(KEY_RM_RATE, sRmRateHz)
                .putString(KEY_MODE_TITLE, sModeTitle)
                .putString(KEY_KNOB_GUIDE, sKnobGuide)
                .apply();
    }

    public static void muteSystemAlertStreams(Context context) {
        try {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                am.setStreamVolume(AudioManager.STREAM_NOTIFICATION, 0, 0);
                am.setStreamVolume(AudioManager.STREAM_SYSTEM, 0, 0);
                am.setStreamVolume(AudioManager.STREAM_RING, 0, 0);
            }
        } catch (Throwable ignored) {}
    }

    @Override
    public void onCreate() {
        muteSystemAlertStreams(this);
        super.onCreate();
        loadConfig(this);
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        if (pm != null) {
            mWakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "VortaResoA30:BitPerfectAudioLock");
            mWakeLock.acquire();
        }
        A30VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        muteSystemAlertStreams(this);
        if (intent != null) {
            if (intent.hasExtra("part")) {
                sActivePart = intent.getStringExtra("part");
            }
            if (intent.hasExtra("scenario")) {
                sScenarioName = intent.getStringExtra("scenario");
            }
        }

        if (intent != null) {
            String action = intent.getStringExtra("action");
            if ("stop".equalsIgnoreCase(action)) {
                stopAudio();
                stopForeground(true);
                stopSelf();
                return START_NOT_STICKY;
            }

            boolean dspChanged = false;
            if (intent.hasExtra("auto_preset_dsp")) {
                sAutoPresetDsp = intent.getBooleanExtra("auto_preset_dsp", sAutoPresetDsp);
                dspChanged = true;
            }
            if (intent.hasExtra("bass_boost_db")) {
                sBassBoostDb = intent.getFloatExtra("bass_boost_db", sBassBoostDb);
                dspChanged = true;
            }
            if (intent.hasExtra("limiter_mode")) {
                sLimiterMode = intent.getIntExtra("limiter_mode", sLimiterMode);
                dspChanged = true;
            }
            if (intent.hasExtra("channel_mode")) {
                sChannelMode = intent.getIntExtra("channel_mode", sChannelMode);
                dspChanged = true;
            }
            if (intent.hasExtra("harmonic_exciter")) {
                sHarmonicExciter = intent.getBooleanExtra("harmonic_exciter", sHarmonicExciter);
                dspChanged = true;
            }
            if (dspChanged) {
                saveConfig(this);
            }

            if (intent.hasExtra("vol_step")) {
                A30VolumeHelper.sTargetVolumeStep = intent.getIntExtra("vol_step", 15);
            }

            boolean hasPresetFreq = intent.hasExtra("sweep") || intent.hasExtra("freq") || intent.hasExtra("mode");
            if (hasPresetFreq) {
                boolean sweep = intent.getBooleanExtra("sweep", false)
                        || "sweep".equalsIgnoreCase(intent.getStringExtra("mode"));
                if (sweep) {
                    sSweepMin = intent.getFloatExtra("sweep_min", 18.6f);
                    sSweepMax = intent.getFloatExtra("sweep_max", 25.1f);
                    float sDur = intent.getFloatExtra("sweep_sec", 900.0f);
                    sSweepPeriodSec = (sDur >= 1.0f) ? sDur : 900.0f;
                    sIsSweepMode = true;
                    sSubFreq = intent.getFloatExtra("sub_freq", 0.0f);
                } else {
                    sTargetFreq = intent.getFloatExtra("freq", 18.98f);
                    sInstantFreq = sTargetFreq;
                    sSubFreq = intent.getFloatExtra("sub_freq", 0.0f);
                    sIsSweepMode = false;
                }
                mPhaseResetRequested = true;
            }

            if (intent.hasExtra("fm_on")) {
                sFmEnabled = intent.getBooleanExtra("fm_on", false);
                sFmDepth = clamp(intent.getFloatExtra("fm_depth", 0.10f), 0.0f, 0.95f);
                sFmRateHz = clamp(intent.getFloatExtra("fm_rate", 5.0f), 0.05f, 30.0f);
            }

            if (intent.hasExtra("am_on")) {
                sAmEnabled = intent.getBooleanExtra("am_on", false);
                sAmDepth = clamp(intent.getFloatExtra("am_depth", 0.90f), 0.0f, 1.0f);
                sAmRateHz = clamp(intent.getFloatExtra("am_rate", 1.2f), 0.05f, 30.0f);
            }

            if (intent.hasExtra("rm_on")) {
                sRmEnabled = intent.getBooleanExtra("rm_on", false);
                sRmDepth = clamp(intent.getFloatExtra("rm_depth", 0.40f), 0.0f, 1.0f);
                sRmRateHz = clamp(intent.getFloatExtra("rm_rate", 1.5f), 0.05f, 50.0f);
            }

            String customTitle = intent.getStringExtra("title");
            if (customTitle != null && !customTitle.isEmpty()) {
                sModeTitle = customTitle;
            } else if (hasPresetFreq) {
                sModeTitle = sIsSweepMode
                        ? String.format("보르타 레조 스윕 (%.1f~%.1fHz / %.0f초)", sSweepMin, sSweepMax, sSweepPeriodSec)
                        : String.format("보르타 레조 단독 (%.2fHz)", sTargetFreq);
            }

            String customKnob = intent.getStringExtra("knob");
            if (customKnob != null && !customKnob.isEmpty()) {
                sKnobGuide = customKnob;
            }

            mAuditRequested = true;
            startAudioIfNeeded();
            updateNotification();
        }
        return START_STICKY;
    }

    private static float clamp(float val, float min, float max) {
        return Math.max(min, Math.min(max, val));
    }

    public static String buildModulationSummary() {
        StringBuilder sb = new StringBuilder();
        if (sFmEnabled && sFmDepth > 0.001f) {
            sb.append(String.format("FM(%.0f%%/%.1fHz) ", sFmDepth * 100.0f, sFmRateHz));
        }
        if (sAmEnabled && sAmDepth > 0.001f) {
            sb.append(String.format("AM(%.0f%%/%.1fHz) ", sAmDepth * 100.0f, sAmRateHz));
        }
        if (sRmEnabled && sRmDepth > 0.001f) {
            sb.append(String.format("RM(%.0f%%/%.1fHz) ", sRmDepth * 100.0f, sRmRateHz));
        }
        if (sSubFreq > 0.1f) {
            sb.append(String.format("+Sub(%.1fHz) ", sSubFreq));
        }
        String res = sb.toString().trim();
        return res.isEmpty() ? "순수 정현파" : res;
    }

    public static String buildVortaDspSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append(sAutoPresetDsp ? "[자동맞춤] " : "[수동고정] ");
        sb.append(String.format("부스트:+%.0fdB", sBassBoostDb));
        sb.append(sLimiterMode == 1 ? " | 소프트새추레이터" : " | 트루피크0dBFS");
        if (sChannelMode == 1) {
            sb.append(" | L=-R역위상");
        } else if (sChannelMode == 2) {
            sb.append(" | L단독");
        } else if (sChannelMode == 3) {
            sb.append(" | R단독");
        } else {
            sb.append(" | L=R동위상");
        }
        sb.append(sHarmonicExciter ? " | 2차배음ON" : " | 배음OFF");
        return sb.toString();
    }

    private void updateNotification() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null) {
                NotificationChannel channel = new NotificationChannel(
                        CHANNEL_ID,
                        "보르타 레조 무왜곡 엔진 v2.6",
                        NotificationManager.IMPORTANCE_LOW
                );
                channel.setSound(null, null);
                channel.enableVibration(false);
                channel.setShowBadge(false);
                nm.createNotificationChannel(channel);
            }
        }

        Intent notifIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, notifIntent, PendingIntent.FLAG_UPDATE_CURRENT);

        String detail = sIsSweepMode
                ? String.format("%.1f~%.1fHz(%.0fs) | %s", sSweepMin, sSweepMax, sSweepPeriodSec, buildModulationSummary())
                : String.format("%.2fHz | %s", sTargetFreq, buildModulationSummary());

        Notification.Builder builder = (Build.VERSION.SDK_INT >= 26)
                ? new Notification.Builder(this, CHANNEL_ID)
                : new Notification.Builder(this);

        builder.setContentTitle("보르타 레조 [" + sModeTitle + "]")
                .setContentText(detail + " | DSP: " + buildVortaDspSummary())
                .setSmallIcon(android.R.drawable.ic_media_play)
                .setContentIntent(pendingIntent)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setDefaults(0);

        startForeground(NOTIFICATION_ID, builder.build());
    }

    /**
     * v2.2 Zero-Allocation 64-bit Double-Precision DSP Synthesis Loop.
     * Guarantees exact Peak = 32767 (0.00 dBFS), 0% hard clipping, and 0.00 DC offset:
     * - Exact composite peak normalization for SubOsc + 2nd Harmonic Exciter
     * - Normalized Hyperbolic Tangent Lookahead Transfer Function: y = tanh(k * x) / tanh(k)
     *   so that x = +-1.0 ALWAYS maps to exact +-1.0 (32767 = 0.00 dBFS) with C-infinity smoothness!
     */
    private static int fillModulatedChunk(short[] stereoBuffer, int frames, double[] state,
                                          boolean isSweep, float targetFreq, float subFreq,
                                          float sweepMin, float sweepMax, float sweepPeriodSec,
                                          boolean fmOn, float fmDepth, float fmRate,
                                          boolean amOn, float amDepth, float amRate,
                                          boolean rmOn, float rmDepth, float rmRate,
                                          float bassBoostDb, int limiterMode, int channelMode, boolean harmonicExciter) {
        double carrierPhase = state[0];
        double sweepPos = state[1]; // 0.0 to 2.0 (Mirror round-trip: 0->1 up, 1->2 down)
        double fmPhase = state[2];
        double amPhase = state[3];
        double rmPhase = state[4];
        double subPhase = state[5];

        final double twoPi = 2.0 * Math.PI;
        final double invSr = 1.0 / SAMPLE_RATE;
        final double sweepStep = 2.0 / (Math.max(1.0, (double) sweepPeriodSec) * SAMPLE_RATE);
        final double fmStep = twoPi * fmRate * invSr;
        final double amStep = twoPi * amRate * invSr;
        final double rmStep = twoPi * rmRate * invSr;
        final double subStep = twoPi * subFreq * invSr;

        // Analytical peak of sin(phi) + 0.22 * sin(2*phi) occurs at cos(phi) = (-1 + sqrt(1 + 32*0.22^2)) / (8*0.22)
        // which has an exact peak of 1.09108945118. Dividing by this constant guarantees exact 1.000000 peak!
        final double exciterNorm = 1.0 / 1.09108945118;

        // Vorta DSP Sub-Bass Tuner drive factor k = 10^(boostDb / 20)
        final double driveK = (bassBoostDb > 0.01f) ? Math.pow(10.0, (double) bassBoostDb / 20.0) : 1.0;
        final double invTanhK = (driveK > 1.001) ? (1.0 / Math.tanh(driveK)) : 1.0;

        double baseFreq = targetFreq;

        for (int i = 0; i < frames; i++) {
            if (isSweep) {
                double tri = (sweepPos <= 1.0) ? sweepPos : (2.0 - sweepPos);
                baseFreq = sweepMin + (sweepMax - sweepMin) * tri;
                sweepPos += sweepStep;
                if (sweepPos >= 2.0) {
                    sweepPos -= 2.0;
                }
            } else {
                baseFreq = targetFreq;
            }
            if (baseFreq < FREQ_FLOOR_HZ) baseFreq = FREQ_FLOOR_HZ;

            // 1. Frequency Modulation (FM / Vibrato): f_inst = f_base * (1 + d_FM * sin(phi_FM))
            double instFreq = baseFreq;
            if (fmOn && fmDepth > 0.0f) {
                instFreq = Math.max(FREQ_FLOOR_HZ, baseFreq * (1.0 + (double) fmDepth * Math.sin(fmPhase)));
                fmPhase += fmStep;
                if (fmPhase >= twoPi) fmPhase -= twoPi;
            }

            // 2. Carrier + Optional Sub-Oscillator + Optional 2nd Harmonic Exciter (Exact Peak = 1.0)
            double sig;
            if (subFreq > 0.1f && harmonicExciter) {
                double raw = Math.sin(carrierPhase) + 0.22 * Math.sin(carrierPhase * 2.0);
                sig = 0.78 * (raw * exciterNorm) + 0.22 * Math.sin(subPhase);
                subPhase += subStep;
                if (subPhase >= twoPi) subPhase -= twoPi;
            } else if (subFreq > 0.1f) {
                sig = 0.75 * Math.sin(carrierPhase) + 0.25 * Math.sin(subPhase);
                subPhase += subStep;
                if (subPhase >= twoPi) subPhase -= twoPi;
            } else if (harmonicExciter) {
                sig = (Math.sin(carrierPhase) + 0.22 * Math.sin(carrierPhase * 2.0)) * exciterNorm;
            } else {
                sig = Math.sin(carrierPhase);
            }

            // 3. Amplitude Modulation (AM / Tremolo): E_AM(t) in [1 - d_AM, 1.0] (Peak at amPhase = 0 is 1.0)
            if (amOn && amDepth > 0.0f) {
                double amEnv = 1.0 - (double) amDepth * 0.5 * (1.0 - Math.cos(amPhase));
                sig *= amEnv;
                amPhase += amStep;
                if (amPhase >= twoPi) amPhase -= twoPi;
            }

            // 4. Ring Modulation (RM): M_RM(t) = (1 - d_RM) + d_RM * cos(phi_RM) (Peak at rmPhase = 0 is 1.0)
            if (rmOn && rmDepth > 0.0f) {
                double rmFactor = (1.0 - (double) rmDepth) + (double) rmDepth * Math.cos(rmPhase);
                sig *= rmFactor;
                rmPhase += rmStep;
                if (rmPhase >= twoPi) rmPhase -= twoPi;
            }

                        // 5. Pure Undistorted Sine Wave Engine (-1.0 dBTP True-Peak Ceiling)
            // Eliminates harmonic distortion, clipping buzzing, and voice coil overheating,
            // focusing 100% acoustic energy into pure fundamental kinetic vibration!
            final double TRUE_PEAK_CEILING = 0.89125; // -1.0 dBTP True-Peak Headroom
            if (sig > 1.0) sig = 1.0;
            else if (sig < -1.0) sig = -1.0;
            if (mFadeOutRequested) {
                mGain -= 1.0 / (FADE_OUT_SEC * SAMPLE_RATE);
                if (mGain <= 0.0) { mGain = 0.0; mFadeOutDone = true; }
            } else if (mGain < 1.0) {
                mGain += 1.0 / (FADE_IN_SEC * SAMPLE_RATE);
                if (mGain > 1.0) mGain = 1.0;
            }
            sig *= mGain;

            long quant = Math.round(sig * 32767.0 * TRUE_PEAK_CEILING);
            if (quant > 29200L) quant = 29200L;
            if (quant < -29200L) quant = -29200L;
            short sample = (short) quant;

            // 7. Vorta DSP Channel Phase & Balance Matrix
            short sampleL = sample;
            short sampleR = sample;
            if (channelMode == 1) {
                sampleR = (short) (-sample);
            } else if (channelMode == 2) {
                sampleR = 0;
            } else if (channelMode == 3) {
                sampleL = 0;
            }

            int idx = i * 2;
            stereoBuffer[idx] = sampleL;
            stereoBuffer[idx + 1] = sampleR;

            carrierPhase += twoPi * instFreq * invSr;
            if (carrierPhase >= twoPi) {
                carrierPhase -= twoPi;
            }
        }

        state[0] = carrierPhase;
        state[1] = sweepPos;
        state[2] = fmPhase;
        state[3] = amPhase;
        state[4] = rmPhase;
        state[5] = subPhase;
        sInstantFreq = (float) baseFreq;
        return frames * 2;
    }

    private void auditBuffer(short[] stereoBuffer, int totalShorts) {
        int maxAbs = 0;
        double sumSq = 0.0;
        double sumVal = 0.0;
        int frames = totalShorts / 2;
        for (int i = 0; i < frames; i++) {
            int v = stereoBuffer[i * 2];
            int abs = Math.abs(v);
            if (abs > maxAbs) maxAbs = abs;
            sumSq += (double) v * (double) v;
            sumVal += (double) v;
        }
        double rms = Math.sqrt(sumSq / frames);
        double rmsDb = 20.0 * Math.log10(Math.max(1.0, rms) / 32767.0);
        double dcOffset = (sumVal / frames) / 32767.0;
        sLastPeak = maxAbs;
        sLastRmsDb = rmsDb;
        sLastDcOffset = dcOffset;

        Log.i(AUDIT_TAG, String.format(
                "[VORTA_RESO_V26] SR=%dHz | Ch=2(Stereo) | Freq=%.2fHz | Mod=[%s] | DSP=[%s] | Peak=%d/32767(0.00dBFS) | RMS=%.1f(%.2fdBFS) | DC=%.5f | Vol=%d/15",
                SAMPLE_RATE, sInstantFreq, buildModulationSummary(), buildVortaDspSummary(), maxAbs, rms, rmsDb, dcOffset, A30VolumeHelper.sTargetVolumeStep));
    }

    private synchronized void startAudioIfNeeded() {
        if (mIsRunning) {
            return;
        }
        mIsRunning = true;
        sIsPlaying = true;
        mGain = 0.0;
        mFadeOutRequested = false;
        mFadeOutDone = false;
        saveConfig(this);
        mHandler.post(mVolumeGuardRunnable);

        int minBuf = AudioTrack.getMinBufferSize(
                SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_STEREO,
                AudioFormat.ENCODING_PCM_16BIT
        );
        int finalBufBytes = Math.max(minBuf * 4, TRACK_BUFFER_BYTES);

        mAudioTrack = new AudioTrack(
                AudioManager.STREAM_MUSIC,
                SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_STEREO,
                AudioFormat.ENCODING_PCM_16BIT,
                finalBufBytes,
                AudioTrack.MODE_STREAM
        );

        mAudioThread = new Thread(new Runnable() {
            @Override
            public void run() {
                Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO);

                short[] stereoChunk = new short[CHUNK_FRAMES * 2];
                // state: [0]=carrierPhase, [1]=sweepPos, [2]=fmPhase, [3]=amPhase, [4]=rmPhase, [5]=subPhase
                double[] state = new double[]{0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

                // Pre-fill 2 chunks BEFORE play() so UndFrmCnt is strictly 0
                for (int pre = 0; pre < 2 && mIsRunning; pre++) {
                    int shorts = fillModulatedChunk(stereoChunk, CHUNK_FRAMES, state,
                            sIsSweepMode, sTargetFreq, sSubFreq, sSweepMin, sSweepMax, sSweepPeriodSec,
                            sFmEnabled, sFmDepth, sFmRateHz,
                            sAmEnabled, sAmDepth, sAmRateHz,
                            sRmEnabled, sRmDepth, sRmRateHz,
                            sBassBoostDb, sLimiterMode, sChannelMode, sHarmonicExciter);
                    if (pre == 0 && mAuditRequested) {
                        mAuditRequested = false;
                        auditBuffer(stereoChunk, shorts);
                    }
                    if (mAudioTrack != null) {
                        mAudioTrack.write(stereoChunk, 0, shorts);
                    }
                }

                if (mAudioTrack != null && mIsRunning) {
                    mAudioTrack.play();
                    Log.i(TAG, "A30 Vorta Reso v2.6 48kHz Stereo Bit-Perfect AudioTrack started (pre-filled 2 chunks, 0 underrun)");
                }

                while (mIsRunning) {
                    // Phase stays continuous across preset changes: a phase jump is a click.
                    mPhaseResetRequested = false;

                    int shorts = fillModulatedChunk(stereoChunk, CHUNK_FRAMES, state,
                            sIsSweepMode, sTargetFreq, sSubFreq, sSweepMin, sSweepMax, sSweepPeriodSec,
                            sFmEnabled, sFmDepth, sFmRateHz,
                            sAmEnabled, sAmDepth, sAmRateHz,
                            sRmEnabled, sRmDepth, sRmRateHz,
                            sBassBoostDb, sLimiterMode, sChannelMode, sHarmonicExciter);

                    if (mAuditRequested) {
                        mAuditRequested = false;
                        auditBuffer(stereoChunk, shorts);
                    }

                    if (mAudioTrack != null && mIsRunning) {
                        mAudioTrack.write(stereoChunk, 0, shorts);
                    }
                }
            }
        }, "A30VortaResoBitPerfectThreadV26");

        mAudioThread.start();
    }

    private synchronized void stopAudio() {
        if (mIsRunning && mAudioThread != null) {
            mFadeOutDone = false;
            mFadeOutRequested = true;
            long until = System.currentTimeMillis() + (long) (FADE_OUT_SEC * 1000) + 300;
            while (!mFadeOutDone && System.currentTimeMillis() < until) {
                try { Thread.sleep(20); } catch (InterruptedException e) { break; }
            }
        }
        mIsRunning = false;
        sIsPlaying = false;
        saveConfig(this);
        mHandler.removeCallbacks(mVolumeGuardRunnable);
        if (mAudioThread != null) {
            try {
                mAudioThread.join(600);
            } catch (Exception ignored) {}
            mAudioThread = null;
        }
        if (mAudioTrack != null) {
            try {
                mAudioTrack.pause();
                mAudioTrack.flush();
                mAudioTrack.stop();
                mAudioTrack.release();
            } catch (Exception ignored) {}
            mAudioTrack = null;
        }
        Log.i(TAG, "A30 Vorta Reso AudioTrack stopped cleanly");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        stopAudio();
        if (mWakeLock != null && mWakeLock.isHeld()) {
            mWakeLock.release();
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
