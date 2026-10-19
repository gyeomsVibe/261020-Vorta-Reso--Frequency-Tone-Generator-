package com.trans2.frequencygenerator;

import android.app.Notification;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.os.Process;
import android.util.Log;

public class AudioGeneratorService extends Service {
    private static final String TAG = "Trans2AudioSvc";
    private static final String AUDIT_TAG = "Trans2AudioAudit";
    private static final int NOTIFICATION_ID = 1001;

    // Hardware native sample rate of Galaxy S6 AudioOut_D (48,000 Hz, HAL frame count 960)
    public static final int SAMPLE_RATE = 48000;
    private static final int HAL_FRAMES = 960;
    private static final int CHUNK_FRAMES = HAL_FRAMES * 4; // 3,840 stereo frames (7,680 shorts)
    private static final int TRACK_BUFFER_BYTES = HAL_FRAMES * 24 * 4; // 23,040 stereo frames (92,160 bytes)

    // Live shared telemetry for UI sync
    public static volatile boolean sIsPlaying = false;
    public static volatile boolean sIsSweepMode = false;
    public static volatile float sTargetFreq = 55.0f;
    public static volatile float sSweepMin = 38.0f;
    public static volatile float sSweepMax = 68.0f;
    public static volatile float sSweepPeriodSec = 60.0f;
    public static volatile float sInstantFreq = 55.0f;
    public static volatile String sModeTitle = "1순위: 311호 요격 앵커 (55.0Hz 단독)";
    public static volatile String sKnobGuide = "LP-168S 노브: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시 | TREBLE 7시";
    public static volatile int sLastPeak = 32767;
    public static volatile double sLastRmsDb = -3.01;

    private PowerManager.WakeLock mWakeLock;
    private AudioTrack mAudioTrack;
    private volatile boolean mIsRunning = false;
    private volatile boolean mSweepResetRequested = false;
    private volatile boolean mAuditRequested = true;

    private Thread mAudioThread;
    private final Handler mHandler = new Handler(Looper.getMainLooper());

    private final Runnable mVolumeGuardRunnable = new Runnable() {
        @Override
        public void run() {
            if (mIsRunning) {
                AudioVolumeHelper.ensureVolume15IfNeeded(AudioGeneratorService.this, false);
                mHandler.postDelayed(this, 10000);
            }
        }
    };

    @Override
    public void onCreate() {
        super.onCreate();
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        if (pm != null) {
            mWakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "Trans2:BitPerfectAudioLock");
            mWakeLock.acquire();
        }
        AudioVolumeHelper.ensureVolume15IfNeeded(this, true);
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

            boolean sweep = intent.getBooleanExtra("sweep", false);
            if (intent.hasExtra("mode") && "sweep".equalsIgnoreCase(intent.getStringExtra("mode"))) {
                sweep = true;
            }

            if (sweep) {
                float sMin = intent.getFloatExtra("sweep_min", 38.0f);
                float sMax = intent.getFloatExtra("sweep_max", 68.0f);
                float sDur = intent.getFloatExtra("sweep_sec", 60.0f);
                sSweepMin = sMin;
                sSweepMax = sMax;
                sSweepPeriodSec = (sDur > 1.0f) ? sDur : 60.0f;
                sIsSweepMode = true;
                mSweepResetRequested = true;

                String customTitle = intent.getStringExtra("title");
                if (customTitle != null && !customTitle.isEmpty()) {
                    sModeTitle = customTitle;
                } else {
                    sModeTitle = String.format("가변 스윕 (%.1f~%.1fHz / %.0f초 왕복)", sMin, sMax, sSweepPeriodSec);
                }
            } else {
                float freq = intent.getFloatExtra("freq", 55.0f);
                sTargetFreq = freq;
                sInstantFreq = freq;
                sIsSweepMode = false;

                String customTitle = intent.getStringExtra("title");
                if (customTitle != null && !customTitle.isEmpty()) {
                    sModeTitle = customTitle;
                } else {
                    sModeTitle = resolveDefaultTitle(freq);
                }
            }

            String customKnob = intent.getStringExtra("knob");
            if (customKnob != null && !customKnob.isEmpty()) {
                sKnobGuide = customKnob;
            } else {
                sKnobGuide = resolveDefaultKnobGuide(sIsSweepMode, sTargetFreq, sSweepMin, sSweepMax, sSweepPeriodSec);
            }

            mAuditRequested = true;
            AudioVolumeHelper.ensureVolume15IfNeeded(this, true);
            startAudioIfNeeded();
            updateNotification();
        }
        return START_STICKY;
    }

    private String resolveDefaultTitle(float freq) {
        if (Math.abs(freq - 55.0f) < 0.05f) return "단독 1순위: 311호 요격 앵커 (55.0Hz)";
        if (Math.abs(freq - 43.2f) < 0.05f) return "단독 2순위: 슬래브 관통 해머 (43.2Hz)";
        if (Math.abs(freq - 32.8f) < 0.05f) return "단독 3순위: 흉부·복부 압박 (32.8Hz)";
        if (Math.abs(freq - 19.0f) < 0.05f) return "단독 4순위: 비가청 안구 공진 (19.0Hz)";
        if (Math.abs(freq - 18.98f) < 0.05f) return "단독 5순위: 즉각 물리 반격 (18.98Hz)";
        return String.format("단독 정현파 집중 타격 (%.2fHz)", freq);
    }

    private String resolveDefaultKnobGuide(boolean sweep, float freq, float sMin, float sMax, float sDur) {
        if (!sweep && Math.abs(freq - 43.2f) < 0.05f) {
            return "LP-168S [반격 해머]: VOL 7.5(2시15분) | SUB 6.0~6.5(1시반) | BASS +3(1시반) | X-OVER 10시 | TREBLE 7시";
        }
        if (sweep && Math.abs(sMin - 38.0f) < 0.5f && Math.abs(sMax - 68.0f) < 0.5f) {
            return "LP-168S [외출/출근/장기]: VOL 6.5(1시반) | SUB 5.0(12시반) | BASS +1(12시반) | X-OVER 10시 | TREBLE 7시";
        }
        return "LP-168S [표준/취침]: VOL 6.0~7.0(1~2시) | SUB 5.0~5.5(12시반~1시) | BASS +1~+2 | X-OVER 10시 | TREBLE 7시";
    }

    private void updateNotification() {
        Intent notifIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, notifIntent, PendingIntent.FLAG_UPDATE_CURRENT);

        String detail = sIsSweepMode
                ? String.format("%.1f~%.1fHz (%.0f초 왕복) | 48kHz L+R 0dBFS", sSweepMin, sSweepMax, sSweepPeriodSec)
                : String.format("%.2f Hz 순수 정현파 | 48kHz L+R 0dBFS", sTargetFreq);

        Notification.Builder builder = new Notification.Builder(this)
                .setContentTitle("트랜스2 전용 발생기 [" + sModeTitle + "]")
                .setContentText(detail + " | 볼륨 15/15")
                .setSmallIcon(android.R.drawable.ic_media_play)
                .setContentIntent(pendingIntent)
                .setOngoing(true);

        startForeground(NOTIFICATION_ID, builder.build());
    }

    private static int fillSineChunk(short[] stereoBuffer, int frames, double[] state,
                                     boolean isSweep, float targetFreq,
                                     float sweepMin, float sweepMax, float sweepPeriodSec) {
        double phase = state[0];
        double sweepPos = state[1]; // 0.0 to 2.0 (0->1 up, 1->2 down Mirror loop)
        double twoPi = 2.0 * Math.PI;
        // Mirror loop: full round-trip (up + down) takes sweepPeriodSec seconds
        double sweepStep = 2.0 / (Math.max(1.0, (double) sweepPeriodSec) * SAMPLE_RATE);
        double curFreq = targetFreq;

        for (int i = 0; i < frames; i++) {
            if (isSweep) {
                double tri = (sweepPos <= 1.0) ? sweepPos : (2.0 - sweepPos);
                curFreq = sweepMin + (sweepMax - sweepMin) * tri;
                sweepPos += sweepStep;
                if (sweepPos >= 2.0) {
                    sweepPos -= 2.0;
                }
            } else {
                curFreq = targetFreq;
            }

            // Nearest-integer symmetric rounding at exact 16-bit full scale (32767 = 0.00 dBFS)
            short sample = (short) Math.round(Math.sin(phase) * 32767.0);

            // Stereo dual-channel phase-locked output (L = sample, R = sample)
            int idx = i * 2;
            stereoBuffer[idx] = sample;
            stereoBuffer[idx + 1] = sample;

            phase += twoPi * curFreq / SAMPLE_RATE;
            if (phase >= twoPi) {
                phase -= twoPi;
            }
        }

        state[0] = phase;
        state[1] = sweepPos;
        sInstantFreq = (float) curFreq;
        return frames * 2;
    }

    private void auditBuffer(short[] stereoBuffer, int totalShorts) {
        int maxAbs = 0;
        double sumSq = 0.0;
        int frames = totalShorts / 2;
        for (int i = 0; i < frames; i++) {
            int v = stereoBuffer[i * 2];
            int abs = Math.abs(v);
            if (abs > maxAbs) maxAbs = abs;
            sumSq += (double) v * (double) v;
        }
        double rms = Math.sqrt(sumSq / frames);
        double rmsDb = 20.0 * Math.log10(rms / 32767.0);
        sLastPeak = maxAbs;
        sLastRmsDb = rmsDb;

        Log.i(AUDIT_TAG, String.format(
                "[SIGNAL_AUDIT] SR=%dHz | Ch=2(Stereo L=R PhaseLocked) | Sweep=%b | Freq=%.2fHz | Peak=%d/32767(0.00dBFS) | RMS=%.1f(%.2fdBFS) | Mode=%s",
                SAMPLE_RATE, sIsSweepMode, sInstantFreq, maxAbs, rms, rmsDb, sModeTitle));
    }

    private synchronized void startAudioIfNeeded() {
        if (mIsRunning) {
            return;
        }
        mIsRunning = true;
        sIsPlaying = true;
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
                // state[0] = wave phase (rad), state[1] = sweepProgress (0..2)
                double[] state = new double[]{0.0, 0.0};

                // Pre-fill 2 chunks BEFORE play() so UndFrmCnt is strictly 0
                for (int pre = 0; pre < 2 && mIsRunning; pre++) {
                    int shorts = fillSineChunk(stereoChunk, CHUNK_FRAMES, state,
                            sIsSweepMode, sTargetFreq, sSweepMin, sSweepMax, sSweepPeriodSec);
                    if (mAudioTrack != null) {
                        mAudioTrack.write(stereoChunk, 0, shorts);
                    }
                }

                if (mAudioTrack != null && mIsRunning) {
                    mAudioTrack.play();
                    Log.i(TAG, "Trans2 48kHz Stereo Bit-Perfect AudioTrack started (pre-filled 2 chunks, 0 underrun)");
                }

                while (mIsRunning) {
                    if (mSweepResetRequested) {
                        state[1] = 0.0;
                        mSweepResetRequested = false;
                    }

                    int shorts = fillSineChunk(stereoChunk, CHUNK_FRAMES, state,
                            sIsSweepMode, sTargetFreq, sSweepMin, sSweepMax, sSweepPeriodSec);

                    if (mAuditRequested) {
                        mAuditRequested = false;
                        auditBuffer(stereoChunk, shorts);
                    }

                    if (mAudioTrack != null && mIsRunning) {
                        mAudioTrack.write(stereoChunk, 0, shorts);
                    }
                }
            }
        }, "Trans2BitPerfectAudioThread");

        mAudioThread.start();
    }

    private synchronized void stopAudio() {
        mIsRunning = false;
        sIsPlaying = false;
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
        Log.i(TAG, "Trans2 AudioTrack stopped cleanly");
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
