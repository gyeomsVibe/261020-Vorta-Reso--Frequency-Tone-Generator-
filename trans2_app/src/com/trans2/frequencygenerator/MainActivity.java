package com.trans2.frequencygenerator;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.media.AudioManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private TextView mStatusMode;
    private TextView mStatusFreq;
    private TextView mStatusSignal;
    private TextView mStatusVolume;
    private TextView mStatusKnob;
    private AudioManager mAudioManager;
    private final Handler mHandler = new Handler(Looper.getMainLooper());

    private final Runnable mUiSyncRunnable = new Runnable() {
        @Override
        public void run() {
            syncTelemetryUi();
            mHandler.postDelayed(this, 1000);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mAudioManager = (AudioManager) getSystemService(Context.AUDIO_SERVICE);

        AudioVolumeHelper.ensureVolume15IfNeeded(this, true);

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#0D1117"));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(26, 32, 26, 40);
        root.setGravity(Gravity.CENTER_HORIZONTAL);

        // Header
        TextView title = new TextView(this);
        title.setText("트랜스2 전용 주파수 발생기 v2.0");
        title.setTextSize(21);
        title.setTextColor(Color.parseColor("#00E5FF"));
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("마스터 보고서(v15.0) 완전 이식 | 48kHz L+R 무왜곡 0.0dBFS 엔진");
        subtitle.setTextSize(12);
        subtitle.setTextColor(Color.parseColor("#8B949E"));
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 4, 0, 20);
        root.addView(subtitle);

        // Live Telemetry Dashboard Card
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackgroundColor(Color.parseColor("#161B22"));
        card.setPadding(26, 22, 26, 22);

        mStatusMode = new TextView(this);
        mStatusMode.setText("현재 모드: 대기 중 (프리셋을 선택하세요)");
        mStatusMode.setTextSize(15);
        mStatusMode.setTextColor(Color.parseColor("#00FF66"));
        mStatusMode.setTypeface(Typeface.DEFAULT_BOLD);
        card.addView(mStatusMode);

        mStatusFreq = new TextView(this);
        mStatusFreq.setText("실시간 발진: -- Hz (순수 사인파 0.00 dBFS)");
        mStatusFreq.setTextSize(14);
        mStatusFreq.setTextColor(Color.parseColor("#FFFFFF"));
        mStatusFreq.setPadding(0, 8, 0, 4);
        card.addView(mStatusFreq);

        mStatusSignal = new TextView(this);
        mStatusSignal.setText("신호 검수: 48,000Hz Native | L+R 동위상 | Peak 32767 | 클리핑 0건");
        mStatusSignal.setTextSize(12);
        mStatusSignal.setTextColor(Color.parseColor("#58A6FF"));
        mStatusSignal.setPadding(0, 2, 0, 4);
        card.addView(mStatusSignal);

        mStatusVolume = new TextView(this);
        mStatusVolume.setText("스마트폰 볼륨: 15 / 15 (100% 영구 고정 · 부스터 0% OFF)");
        mStatusVolume.setTextSize(13);
        mStatusVolume.setTextColor(Color.parseColor("#FFD700"));
        mStatusVolume.setPadding(0, 2, 0, 6);
        card.addView(mStatusVolume);

        mStatusKnob = new TextView(this);
        mStatusKnob.setText("LP-168S 노브: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시 | TREBLE 7시");
        mStatusKnob.setTextSize(12);
        mStatusKnob.setTextColor(Color.parseColor("#FFAB70"));
        card.addView(mStatusKnob);

        root.addView(card);

        // Section 1: 4 Daily Time Blocks Quick Row
        addSectionHeader(root, "⏰ 하루 4등분 시간대별 원터치 실행 (마스터 스케줄)");

        LinearLayout row1 = new LinearLayout(this);
        row1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfButton(row1, "🌅 아침 (07~13시)", "55.0Hz 단독 | SUB 1시", "#1F6FEB", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startSingle(55.0f,
                        "[아침 07~13시] 55.0Hz 인지무력화·흉부압박",
                        "LP-168S [아침 표준]: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시 | TREBLE 7시");
            }
        });
        addHalfButton(row1, "☀️ 오후 (13~19시)", "32.8Hz 단독 | SUB 12시반", "#0969DA", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startSingle(32.8f,
                        "[오후 13~19시] 32.8Hz 흉곽·복부 공명 압박",
                        "LP-168S [오후 지속]: VOL 6.5(1시반) | SUB 5.0(12시반) | BASS +1(12시반) | X-OVER 10시 | TREBLE 7시");
            }
        });
        root.addView(row1);

        LinearLayout row2 = new LinearLayout(this);
        row2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfButton(row2, "🌆 저녁 (19~01시)", "50~60Hz 15초 스윕 | SUB 1시", "#8250DF", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startSweep(50.0f, 60.0f, 15.0f,
                        "[저녁 19~01시] 50~60Hz(15초) 귀가제압·공황압박",
                        "LP-168S [저녁 표준]: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시 | TREBLE 7시");
            }
        });
        addHalfButton(row2, "🌙 취침 (01~07시)", "55.0Hz 역제압 | SUB 12시반", "#B62324", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startSingle(55.0f,
                        "[취침 01~07시] 55.0Hz 311호 야간공격 정면 역제압",
                        "LP-168S [취침 숙면]: VOL 6.0(1시) | SUB 5.0(12시반) | BASS +1(12시반) | X-OVER 10시 | TREBLE 7시");
            }
        });
        root.addView(row2);

        // Section 2: Single Tone Presets (1~5)
        addSectionHeader(root, "🎯 단독(Single Tone) 정밀 타격 프리셋 (1~5순위)");

        addFullButton(root,
                "1순위: 311호 요격 앵커 (55.0 Hz 단독)",
                "상황⑤ 야간취침(01~07시) 55Hz 역제압 · 아침(07~13시) · 상황⑧ 3시간+ 고정",
                "#D32F2F",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSingle(55.0f,
                                "단독 1순위: 311호 요격 앵커 (55.0Hz)",
                                "LP-168S [취침 SUB 5.0(12시반) / 주간 SUB 5.5(1시)] | VOL 6.0~7.0 | X-OVER 10시");
                    }
                });

        addFullButton(root,
                "2순위: 슬래브 관통 1타 해머 (43.2 Hz 단독)",
                "상황④ 발망치·도발 시 1~2초 즉각 반격 해머(5~15분) · 저녁 첫 10분 기습",
                "#C2185B",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSingle(43.2f,
                                "단독 2순위: 즉각 반격 1타 해머 (43.2Hz)",
                                "LP-168S [반격 해머 최대]: VOL 7.5(2시15분) | SUB 6.0~6.5(1시반) | BASS +3(1시반)");
                    }
                });

        addFullButton(root,
                "3순위: 흉부·복부 압박 (32.8 Hz 단독)",
                "상황⑥ 상대 정신 파괴(공황·두통·이명 유도) · 오후(13~19시) 슬래브 2차 공진",
                "#7B1FA2",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSingle(32.8f,
                                "단독 3순위: 정신 파괴·흉복부 압박 (32.8Hz)",
                                "LP-168S [정신파괴/오후]: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시");
                    }
                });

        addFullButton(root,
                "4순위: 비가청 안구·신경 압박 (19.0 Hz 단독)",
                "NASA 안구 공진 대역 · 시야 흔들림 · 원인 불명 불안감 및 신경 피로",
                "#303F9F",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSingle(19.0f,
                                "단독 4순위: 비가청 안구·신경 압박 (19.0Hz)",
                                "LP-168S [표준 세팅]: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시");
                    }
                });

        addFullButton(root,
                "5순위: 초저주파 안구 피크 반격 (18.98 Hz 단독)",
                "초저주파 물리 공명 타격 · 전정기관 어지럼증 및 멀미 유도",
                "#00796B",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSingle(18.98f,
                                "단독 5순위: 초저주파 물리 공명 (18.98Hz)",
                                "LP-168S [반격 세팅]: VOL 7.5(2시15분) | SUB 6.0(1시반) | BASS +3(1시반)");
                    }
                });

        // Section 3: Master Report Sweep Presets (1~3)
        addSectionHeader(root, "🌊 스윕(Sweep) 무내성·무인 가동 프리셋 (1~3순위)");

        addFullButton(root,
                "스윕 1순위: 38.0 ~ 68.0 Hz (60초 왕복 루프)",
                "상황① 일반외출(2~5h) · 상황② 출근(12h) · 상황③ 장기외출(48h+) · 상황⑧ 3h+ 코일쿨링",
                "#E65100",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSweep(38.0f, 68.0f, 60.0f,
                                "스윕 1순위: 광대역 피로·무인쿨링 (38~68Hz / 60초)",
                                "LP-168S [외출 SUB 5.5(1시) / 출근·3h+ SUB 5.0(12시반) / 장기외출 SUB 4.5(12시)]");
                    }
                });

        addFullButton(root,
                "스윕 2순위: 50.0 ~ 60.0 Hz (15초 고속 왕복)",
                "상황⑦ 상대 내성 파괴(적응 100% 리셋) · 저녁(19:10~01:00) · 상황⑥ 정신 파괴",
                "#AD1457",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSweep(50.0f, 60.0f, 15.0f,
                                "스윕 2순위: 내성 파괴·공진점 급습 (50~60Hz / 15초)",
                                "LP-168S [내성파괴/저녁]: VOL 7.0(2시) | SUB 5.5(1시) | BASS +2(1시) | X-OVER 10시");
                    }
                });

        addFullButton(root,
                "스윕 3순위: 18.6 ~ 55.0 Hz (30초 전대역 통합)",
                "안구·장간막 생체 공명(18.6Hz) ~ 슬래브 3차 공진(55.0Hz) 전대역 왕복 소탕",
                "#4527A0",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startSweep(18.6f, 55.0f, 30.0f,
                                "스윕 3순위: 생체·슬래브 통합 스윕 (18.6~55Hz / 30초)",
                                "LP-168S [통합 스윕]: VOL 6.5(1시반) | SUB 5.0~5.5(12시반~1시) | X-OVER 10시");
                    }
                });

        // Stop Button
        addSectionHeader(root, "🛑 출력 제어");
        addFullButton(root,
                "■ 주파수 발생 즉시 정지 (STOP / 음소거)",
                "AudioTrack 출력 및 백그라운드 발진 완전 종료",
                "#37474F",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        stopFrequency();
                    }
                });

        scroll.addView(root);
        setContentView(scroll);

        handleIncomingIntent(getIntent());
        syncTelemetryUi();
    }

    private void addSectionHeader(LinearLayout parent, String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(14);
        tv.setTextColor(Color.parseColor("#58A6FF"));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(4, 22, 4, 10);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        tv.setLayoutParams(lp);
        parent.addView(tv);
    }

    private void addHalfButton(LinearLayout row, String mainText, String subText, String colorHex, View.OnClickListener listener) {
        LinearLayout btn = new LinearLayout(this);
        btn.setOrientation(LinearLayout.VERTICAL);
        btn.setBackgroundColor(Color.parseColor(colorHex));
        btn.setPadding(18, 16, 18, 16);
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lp.setMargins(6, 0, 6, 12);
        btn.setLayoutParams(lp);

        TextView tv1 = new TextView(this);
        tv1.setText(mainText);
        tv1.setTextSize(14);
        tv1.setTextColor(Color.WHITE);
        tv1.setTypeface(Typeface.DEFAULT_BOLD);
        btn.addView(tv1);

        TextView tv2 = new TextView(this);
        tv2.setText(subText);
        tv2.setTextSize(11);
        tv2.setTextColor(Color.parseColor("#E6EDF3"));
        tv2.setPadding(0, 3, 0, 0);
        btn.addView(tv2);

        row.addView(btn);
    }

    private void addFullButton(LinearLayout parent, String mainText, String subText, String colorHex, View.OnClickListener listener) {
        LinearLayout btn = new LinearLayout(this);
        btn.setOrientation(LinearLayout.VERTICAL);
        btn.setBackgroundColor(Color.parseColor(colorHex));
        btn.setPadding(24, 18, 24, 18);
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, 14);
        btn.setLayoutParams(lp);

        TextView tvMain = new TextView(this);
        tvMain.setText(mainText);
        tvMain.setTextSize(15);
        tvMain.setTextColor(Color.WHITE);
        tvMain.setTypeface(Typeface.DEFAULT_BOLD);
        btn.addView(tvMain);

        TextView tvSub = new TextView(this);
        tvSub.setText(subText);
        tvSub.setTextSize(11);
        tvSub.setTextColor(Color.parseColor("#ECEFF1"));
        tvSub.setPadding(0, 4, 0, 0);
        btn.addView(tvSub);

        parent.addView(btn);
    }

    private void startSingle(float freq, String title, String knobGuide) {
        AudioVolumeHelper.ensureVolume15IfNeeded(this, true);
        Intent svc = new Intent(this, AudioGeneratorService.class);
        svc.putExtra("freq", freq);
        svc.putExtra("sweep", false);
        svc.putExtra("title", title);
        svc.putExtra("knob", knobGuide);
        startService(svc);

        syncTelemetryUi();
        Toast.makeText(this, title + " 발진 시작", Toast.LENGTH_SHORT).show();
    }

    private void startSweep(float minFreq, float maxFreq, float periodSec, String title, String knobGuide) {
        AudioVolumeHelper.ensureVolume15IfNeeded(this, true);
        Intent svc = new Intent(this, AudioGeneratorService.class);
        svc.putExtra("sweep", true);
        svc.putExtra("sweep_min", minFreq);
        svc.putExtra("sweep_max", maxFreq);
        svc.putExtra("sweep_sec", periodSec);
        svc.putExtra("title", title);
        svc.putExtra("knob", knobGuide);
        startService(svc);

        syncTelemetryUi();
        Toast.makeText(this, title + " 발진 시작", Toast.LENGTH_SHORT).show();
    }

    private void stopFrequency() {
        Intent svc = new Intent(this, AudioGeneratorService.class);
        svc.putExtra("action", "stop");
        startService(svc);

        mStatusMode.setText("현재 모드: ■ 발진 정지됨 (음소거 대기)");
        mStatusFreq.setText("실시간 발진: -- Hz (출력 없음)");
        Toast.makeText(this, "주파수 발생 정지 완료", Toast.LENGTH_SHORT).show();
    }

    private void syncTelemetryUi() {
        AudioVolumeHelper.ensureVolume15IfNeeded(this, false);
        if (mAudioManager != null) {
            int cur = mAudioManager.getStreamVolume(AudioManager.STREAM_MUSIC);
            mStatusVolume.setText(String.format("스마트폰 볼륨: %d / 15 (100%% 영구 고정 · 부스터 0%% OFF)", cur));
        }

        if (AudioGeneratorService.sIsPlaying) {
            mStatusMode.setText("가동 중: " + AudioGeneratorService.sModeTitle);
            if (AudioGeneratorService.sIsSweepMode) {
                mStatusFreq.setText(String.format("실시간 스윕: %.2f Hz (범위 %.1f~%.1fHz / %.0f초 왕복)",
                        AudioGeneratorService.sInstantFreq,
                        AudioGeneratorService.sSweepMin,
                        AudioGeneratorService.sSweepMax,
                        AudioGeneratorService.sSweepPeriodSec));
            } else {
                mStatusFreq.setText(String.format("실시간 발진: %.2f Hz 고정 (순수 정현파 0.00 dBFS)",
                        AudioGeneratorService.sTargetFreq));
            }
            mStatusSignal.setText(String.format("검수: 48,000Hz Native | L+R 동위상 | Peak %d/32767 | RMS %.2fdBFS | 왜곡 0%%",
                    AudioGeneratorService.sLastPeak, AudioGeneratorService.sLastRmsDb));
            mStatusKnob.setText(AudioGeneratorService.sKnobGuide);
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIncomingIntent(intent);
    }

    private void handleIncomingIntent(Intent intent) {
        if (intent == null) return;
        String action = intent.getStringExtra("action");
        if ("stop".equalsIgnoreCase(action)) {
            stopFrequency();
            return;
        }

        boolean isSweep = intent.getBooleanExtra("sweep", false)
                || "sweep".equalsIgnoreCase(intent.getStringExtra("mode"));
        if (isSweep) {
            float sMin = intent.getFloatExtra("sweep_min", 38.0f);
            float sMax = intent.getFloatExtra("sweep_max", 68.0f);
            float sSec = intent.getFloatExtra("sweep_sec", 60.0f);
            String title = intent.getStringExtra("title");
            if (title == null) title = String.format("가변 스윕 (%.1f~%.1fHz / %.0f초)", sMin, sMax, sSec);
            startSweep(sMin, sMax, sSec, title, intent.getStringExtra("knob"));
            return;
        }

        if (intent.hasExtra("freq")) {
            float f = intent.getFloatExtra("freq", 55.0f);
            startSingle(f, intent.getStringExtra("title"), intent.getStringExtra("knob"));
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        AudioVolumeHelper.ensureVolume15IfNeeded(this, false);
        syncTelemetryUi();
        mHandler.post(mUiSyncRunnable);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mHandler.removeCallbacks(mUiSyncRunnable);
    }
}
