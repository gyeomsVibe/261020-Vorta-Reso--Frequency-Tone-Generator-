package com.vorta.s7frequency;

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

public class S7AudioGeneratorService extends Service {
    private static final String TAG = "S7AudioSvc";
    private static final String AUDIT_TAG = "S7AudioAudit";
    private static final String CHANNEL_ID = "vorta_reso_s7_channel";
    private static final int NOTIFICATION_ID = 3001;

    // Native hardware mixer rate of Galaxy S7 AudioOut_D (48,000 Hz, HAL frame count 960)
    public static final int SAMPLE_RATE = 48000;
    private static final int HAL_FRAMES = 960;
    private static final int CHUNK_FRAMES = HAL_FRAMES * 4; // 3,840 stereo frames (7,680 shorts)
    private static final int TRACK_BUFFER_BYTES = HAL_FRAMES * 24 * 4; // 23,040 stereo frames (92,160 bytes)

    // Vorta DSP Tactical Suite for S7 + 2-Woofer Stereo (240W RMS)
    public static final String PREF_NAME = "vorta_reso_s7_config";
    public static final String KEY_BASS_BOOST = "bass_boost_db";
    public static final String KEY_LIMITER_MODE = "limiter_mode";
    public static final String KEY_CHANNEL_MODE = "channel_mode";
    public static final String KEY_HARMONIC_EXCITER = "harmonic_exciter";
    public static final String KEY_AUTO_PRESET_DSP = "auto_preset_dsp";

    public static volatile float sBassBoostDb = 0.0f; // 0.0dB(Flat), 3.0dB, 6.0dB, 9.0dB
    public static volatile int sLimiterMode = 0; // 0: True-Peak 0.0dBFS Linear, 1: Normalized Analog tanh Saturator
    public static volatile int sChannelMode = 0; // 0: L=R In-phase, 1: L=-R Out-of-phase (180°), 2: L-only, 3: R-only
    public static volatile boolean sHarmonicExciter = false; // 2nd harmonic slab-coupling exciter
    public static volatile boolean sAutoPresetDsp = true; // Auto-apply schedule-matched Vorta DSP

    // Live shared telemetry for UI sync
    public static volatile boolean sIsPlaying = false;
    public static volatile boolean sIsSweepMode = false;
    public static volatile float sTargetFreq = 55.0f;
    public static volatile float sSubFreq = 0.0f;
    public static volatile float sSweepMin = 52.0f;
    public static volatile float sSweepMax = 58.0f;
    public static volatile float sSweepPeriodSec = 180.0f;
    public static volatile float sInstantFreq = 55.0f;

    // Modulation parameters (FM = Vibrato, AM = Tremolo, RM = RingMod)
    public static volatile boolean sFmEnabled = false;
    public static volatile float sFmDepth = 0.0f;
    public static volatile float sFmRateHz = 5.0f;

    public static volatile boolean sAmEnabled = false;
    public static volatile float sAmDepth = 0.0f;
    public static volatile float sAmRateHz = 1.0f;

    public static volatile boolean sRmEnabled = false;
    public static volatile float sRmDepth = 0.0f;
    public static volatile float sRmRateHz = 1.0f;

    public static volatile String sModeTitle = "보르타 레조 S7 v2.8 대기 중";
    public static volatile String sKnobGuide = "120W 우퍼 앰프: VOL 12~1시(정격 60W 풀파워) | FREQ 80~100Hz | BASS +2dB";
    public static volatile int sLastPeak = 32767;
    public static volatile double sLastRmsDb = -3.01;
    public static volatile double sLastDcOffset = 0.0;

    private PowerManager.WakeLock mWakeLock;
    private AudioTrack mAudioTrack;
    private volatile boolean mIsRunning = false;
    private volatile boolean mPhaseResetRequested = false;
    private volatile boolean mAuditRequested = true;

    private Thread mAudioThread;
    private final Handler mHandler = new Handler(Looper.getMainLooper());

    public static void loadConfig(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        sBassBoostDb = sp.getFloat(KEY_BASS_BOOST, 0.0f);
        sLimiterMode = sp.getInt(KEY_LIMITER_MODE, 0);
        sChannelMode = sp.getInt(KEY_CHANNEL_MODE, 0);
        sHarmonicExciter = sp.getBoolean(KEY_HARMONIC_EXCITER, false);
        sAutoPresetDsp = sp.getBoolean(KEY_AUTO_PRESET_DSP, true);
        Log.i(TAG, String.format("Loaded Persistent DSP Config S7 v2.6: Boost=%.1fdB, Limiter=%d, Ch=%d, Exciter=%b, AutoPreset=%b",
                sBassBoostDb, sLimiterMode, sChannelMode, sHarmonicExciter, sAutoPresetDsp));
    }

    public static void saveConfig(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        sp.edit()
                .putFloat(KEY_BASS_BOOST, sBassBoostDb)
                .putInt(KEY_LIMITER_MODE, sLimiterMode)
                .putInt(KEY_CHANNEL_MODE, sChannelMode)
                .putBoolean(KEY_HARMONIC_EXCITER, sHarmonicExciter)
                .putBoolean(KEY_AUTO_PRESET_DSP, sAutoPresetDsp)
                .apply();
    }

    @Override
    public void onCreate() {
        super.onCreate();
        loadConfig(this);
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        if (pm != null) {
            mWakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "VortaResoS7:BitPerfectAudioLock");
            mWakeLock.acquire();
        }
        S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
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
                S7VolumeHelper.sTargetVolumeStep = intent.getIntExtra("vol_step", 15);
            }

            boolean hasPresetFreq = intent.hasExtra("sweep") || intent.hasExtra("freq") || intent.hasExtra("mode");
            if (hasPresetFreq) {
                boolean sweep = intent.getBooleanExtra("sweep", false)
                        || "sweep".equalsIgnoreCase(intent.getStringExtra("mode"));
                if (sweep) {
                    sSweepMin = intent.getFloatExtra("sweep_min", 52.0f);
                    sSweepMax = intent.getFloatExtra("sweep_max", 58.0f);
                    float sDur = intent.getFloatExtra("sweep_sec", 180.0f);
                    sSweepPeriodSec = (sDur >= 1.0f) ? sDur : 180.0f;
                    sIsSweepMode = true;
                    sSubFreq = intent.getFloatExtra("sub_freq", 0.0f);
                } else {
                    sTargetFreq = intent.getFloatExtra("freq", 55.0f);
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
                        ? String.format("보르타 레조 S7 스윕 (%.1f~%.1fHz / %.0f초)", sSweepMin, sSweepMax, sSweepPeriodSec)
                        : String.format("보르타 레조 S7 단독 (%.2fHz)", sTargetFreq);
            }

            String customKnob = intent.getStringExtra("knob");
            if (customKnob != null && !customKnob.isEmpty()) {
                sKnobGuide = customKnob;
            }

            mAuditRequested = true;
            S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
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
        return res.isEmpty() ? "무변조 순수 사인파" : res;
    }

    public static String buildVortaDspSummary() {
        StringBuilder sb = new StringBuilder();
        if (sBassBoostDb > 0.01f) {
            sb.append(String.format("부스트 +%.0fdB | ", sBassBoostDb));
        } else {
            sb.append("부스트 0dB(원음) | ");
        }

        if (sLimiterMode == 1) {
            sb.append("아날로그 소프트 새추레이터 | ");
        } else {
            sb.append("트루피크 0.0dBFS 리미터 | ");
        }

        if (sChannelMode == 1) {
            sb.append("L=-R 역위상(180°) | ");
        } else if (sChannelMode == 2) {
            sb.append("L 단독(우퍼1) | ");
        } else if (sChannelMode == 3) {
            sb.append("R 단독(우퍼2) | ");
        } else {
            sb.append("L=R 스테레오 동위상 | ");
        }

        if (sHarmonicExciter) {
            sb.append("2차 배음 보강 ON");
        } else {
            sb.append("배음 OFF");
        }
        return sb.toString();
    }

    private void updateNotification() {
        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel chan = new NotificationChannel(
                    CHANNEL_ID,
                    "보르타 레조 S7 주파수 발진",
                    NotificationManager.IMPORTANCE_LOW
            );
            chan.setDescription("갤럭시 S7 우퍼 2기 스테레오 백그라운드 발진 가드");
            chan.setShowBadge(false);
            nm.createNotificationChannel(chan);
        }

        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 0, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= 23 ? PendingIntent.FLAG_IMMUTABLE : 0));

        String contentText = String.format("%.2fHz | 볼륨 %d/15 | %s",
                sInstantFreq, S7VolumeHelper.sTargetVolumeStep, buildVortaDspSummary());

        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }

        Notification n = builder
                .setContentTitle(sModeTitle)
                .setContentText(contentText)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentIntent(pi)
                .setOngoing(true)
                .build();

        startForeground(NOTIFICATION_ID, n);
    }

    public static int fillModulatedChunk(short[] stereoBuffer, int frames, double[] state,
                                         boolean isSweep, float targetFreq, float subFreq,
                                         float sweepMin, float sweepMax, float sweepPeriodSec,
                                         boolean fmOn, float fmDepth, float fmRateHz,
                                         boolean amOn, float amDepth, float amRateHz,
                                         boolean rmOn, float rmDepth, float rmRateHz,
                                         float bassBoostDb, int limiterMode, int channelMode, boolean harmonicExciter) {
        final double twoPi = 2.0 * Math.PI;
        final double invSr = 1.0 / (double) SAMPLE_RATE;

        double carrierPhase = state[0];
        double sweepPos     = state[1];
        double fmPhase      = state[2];
        double amPhase      = state[3];
        double rmPhase      = state[4];
        double subPhase     = state[5];

        final double sweepStep = (sweepPeriodSec > 0.05f) ? (2.0 / (sweepPeriodSec * (double) SAMPLE_RATE)) : 0.0;
        final double fmStep    = twoPi * (double) fmRateHz * invSr;
        final double amStep    = twoPi * (double) amRateHz * invSr;
        final double rmStep    = twoPi * (double) rmRateHz * invSr;
        final double subStep   = (subFreq > 0.1f) ? (twoPi * (double) subFreq * invSr) : 0.0;

        final double exciterNorm = 1.0 / 1.09108945118;
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

            // 1. Frequency Modulation (FM / Vibrato): f_inst = f_base * (1 + d_FM * sin(phi_FM))
            double instFreq = baseFreq;
            if (fmOn && fmDepth > 0.0f) {
                instFreq = baseFreq * (1.0 + (double) fmDepth * Math.sin(fmPhase));
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

            // 3. Amplitude Modulation (AM / Tremolo)
            if (amOn && amDepth > 0.0f) {
                double amEnv = 1.0 - (double) amDepth * 0.5 * (1.0 - Math.cos(amPhase));
                sig *= amEnv;
                amPhase += amStep;
                if (amPhase >= twoPi) amPhase -= twoPi;
            }

            // 4. Ring Modulation (RM)
            if (rmOn && rmDepth > 0.0f) {
                double rmFactor = (1.0 - (double) rmDepth) + (double) rmDepth * Math.cos(rmPhase);
                sig *= rmFactor;
                rmPhase += rmStep;
                if (rmPhase >= twoPi) rmPhase -= twoPi;
            }

            // 5. Vorta DSP Sub-Bass Tuner + True-Peak Limiter / Normalized Analog Saturator
            if (driveK > 1.001) {
                if (limiterMode == 1) {
                    sig = Math.tanh(driveK * sig) * invTanhK;
                } else {
                    sig = Math.tanh(driveK * 0.85 * sig) / Math.tanh(driveK * 0.85);
                }
            } else {
                if (sig > 1.0) sig = 1.0;
                else if (sig < -1.0) sig = -1.0;
            }

            // 6. Symmetric nearest-integer quantization at exact 16-bit full scale (32767 = 0.00 dBFS)
            long quant = Math.round(sig * 32767.0);
            if (quant > 32767L) quant = 32767L;
            if (quant < -32767L) quant = -32767L;
            short sample = (short) quant;

            // 7. Vorta DSP Channel Phase & Balance Matrix (Tailored for S7 L/R 2-Woofer Stereo)
            short sampleL = sample;
            short sampleR = sample;
            if (channelMode == 1) {
                sampleR = (short) (-sample); // 180° out of phase for shearing acoustic waves
            } else if (channelMode == 2) {
                sampleR = 0; // Left Woofer 1 only
            } else if (channelMode == 3) {
                sampleL = 0; // Right Woofer 2 only
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
                "[VORTA_RESO_S7_V26] SR=%dHz | Ch=2(Stereo 240W) | Freq=%.2fHz | Mod=[%s] | DSP=[%s] | Peak=%d/32767(0.00dBFS) | RMS=%.1f(%.2fdBFS) | DC=%.5f | Vol=%d/15",
                SAMPLE_RATE, sInstantFreq, buildModulationSummary(), buildVortaDspSummary(), maxAbs, rms, rmsDb, dcOffset, S7VolumeHelper.sTargetVolumeStep));
    }

    private synchronized void startAudioIfNeeded() {
        if (mIsRunning) {
            return;
        }
        mIsRunning = true;
        sIsPlaying = true;

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
                double[] state = new double[]{0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

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
                    Log.i(TAG, "S7 Vorta Reso v2.6 48kHz Stereo Bit-Perfect AudioTrack started");
                }

                while (mIsRunning) {
                    if (mPhaseResetRequested) {
                        state[0] = 0.0;
                        state[1] = 0.0;
                        state[2] = 0.0;
                        state[3] = 0.0;
                        state[4] = 0.0;
                        state[5] = 0.0;
                        mPhaseResetRequested = false;
                    }

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
        }, "S7VortaResoBitPerfectThreadV26");

        mAudioThread.start();
    }

    private synchronized void stopAudio() {
        mIsRunning = false;
        sIsPlaying = false;
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
        Log.i(TAG, "S7 Vorta Reso AudioTrack stopped cleanly");
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
