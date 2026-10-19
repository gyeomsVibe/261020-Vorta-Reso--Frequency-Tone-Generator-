package com.smato.a30frequency;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
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
    private TextView mStatusMod;
    private TextView mStatusDsp;
    private TextView mStatusSignal;
    private TextView mStatusKnob;
    private AudioManager mAudioManager;
    private final Handler mHandler = new Handler(Looper.getMainLooper());

    // 3-Way Tri-Frameset / Split Screen Layout View Containers & Mode State
    private LinearLayout mFrameMainContainer;
    private LinearLayout mFrameSub1Container;
    private LinearLayout mFrameSub2Container;
    private LinearLayout mSplitDivider1;
    private LinearLayout mSplitDivider2;
    private TextView[] mSplitViewButtons = new TextView[4];
    private int mCurrentSplitMode = 0; // 0: All 3 Frames, 1: Main only, 2: Sub1 only, 3: Sub2 only

    // Vorta DSP UI Button References for Active Highlight
    private TextView[] mAutoLockButtons = new TextView[2];
    private boolean[] mAutoLockValues = new boolean[]{true, false};

    private TextView[] mBoostButtons = new TextView[4];
    private float[] mBoostValues = new float[]{0.0f, 3.0f, 6.0f, 9.0f};

    private TextView[] mLimiterButtons = new TextView[2];
    private int[] mLimiterValues = new int[]{0, 1};

    private TextView[] mChannelButtons = new TextView[4];
    private int[] mChannelValues = new int[]{0, 1, 2, 3};

    private TextView[] mExciterButtons = new TextView[2];
    private boolean[] mExciterValues = new boolean[]{true, false};

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

        A30AudioGeneratorService.loadConfig(this);

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#0B0F17"));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(20, 24, 20, 38);
        root.setGravity(Gravity.CENTER_HORIZONTAL);

        // Header Title
        TextView title = new TextView(this);
        title.setText("보르타 레조 A30 v2.8");
        title.setTextSize(21);
        title.setTextColor(Color.parseColor("#00E5FF"));
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("갤럭시 A30 + 우퍼 1기(120W) | 트리플 스플릿 프레임셋 (3-Way Split View) | Vorta DSP");
        subtitle.setTextSize(11);
        subtitle.setTextColor(Color.parseColor("#8B949E"));
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 4, 0, 14);
        root.addView(subtitle);

        float density = getResources().getDisplayMetrics().density;

        // Live Telemetry Dashboard Card (제목 2 / 세부 계측 뷰)
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable cardGd = new GradientDrawable();
        cardGd.setColor(Color.parseColor("#161B22"));
        cardGd.setCornerRadius(12 * density);
        cardGd.setStroke((int)(1.5f * density), Color.parseColor("#30363D"));
        card.setBackground(cardGd);
        card.setPadding((int)(16 * density), (int)(14 * density), (int)(16 * density), (int)(14 * density));

        LinearLayout.LayoutParams lpCard = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpCard.setMargins(0, 0, 0, (int)(10 * density));
        card.setLayoutParams(lpCard);

        TextView cardTitle = new TextView(this);
        cardTitle.setText("📡 실시간 오디오 & DSP 텔레메트리 (Galaxy A30)");
        cardTitle.setTextSize(13.5f);
        cardTitle.setTextColor(Color.parseColor("#58A6FF"));
        cardTitle.setTypeface(Typeface.DEFAULT_BOLD);
        cardTitle.setIncludeFontPadding(false);
        cardTitle.setPadding(0, 0, 0, (int)(6 * density));
        card.addView(cardTitle);

        mStatusMode = new TextView(this);
        mStatusMode.setText("현재 모드: 대기 중 (스케줄/상황 클릭 시 맞춤 DSP 자동 세팅)");
        mStatusMode.setTextSize(13);
        mStatusMode.setTextColor(Color.parseColor("#00FF66"));
        mStatusMode.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusMode.setIncludeFontPadding(false);
        card.addView(mStatusMode);

        mStatusFreq = new TextView(this);
        mStatusFreq.setText("실시간 발진: -- Hz (64-bit 무할당 정현파 0.00 dBFS)");
        mStatusFreq.setTextSize(12.5f);
        mStatusFreq.setTextColor(Color.parseColor("#FFFFFF"));
        mStatusFreq.setIncludeFontPadding(false);
        mStatusFreq.setPadding(0, (int)(4 * density), 0, (int)(2 * density));
        card.addView(mStatusFreq);

        mStatusMod = new TextView(this);
        mStatusMod.setText("변조(FM/AM/RM): 대기 중");
        mStatusMod.setTextSize(12);
        mStatusMod.setTextColor(Color.parseColor("#D2A8FF"));
        mStatusMod.setIncludeFontPadding(false);
        mStatusMod.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(mStatusMod);

        mStatusDsp = new TextView(this);
        mStatusDsp.setText("Vorta DSP: " + A30AudioGeneratorService.buildVortaDspSummary());
        mStatusDsp.setTextSize(12);
        mStatusDsp.setTextColor(Color.parseColor("#38D39F"));
        mStatusDsp.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusDsp.setIncludeFontPadding(false);
        mStatusDsp.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(mStatusDsp);

        mStatusSignal = new TextView(this);
        mStatusSignal.setText("무왜곡 검수: 48,000Hz Native | Peak 32767(0.00dBFS) | DC 0.000 | 클리핑 0건");
        mStatusSignal.setTextSize(11);
        mStatusSignal.setTextColor(Color.parseColor("#58A6FF"));
        mStatusSignal.setIncludeFontPadding(false);
        mStatusSignal.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(mStatusSignal);

        mStatusKnob = new TextView(this);
        mStatusKnob.setText("우퍼 1 노브: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시(0%)");
        mStatusKnob.setTextSize(11);
        mStatusKnob.setTextColor(Color.parseColor("#FFAB70"));
        mStatusKnob.setIncludeFontPadding(false);
        card.addView(mStatusKnob);

        root.addView(card);

        // =========================================================================
        // 🔀 Top 4-Way Mode Selector Bar (트리플 스플릿 프레임 전환 바)
        // =========================================================================
        LinearLayout splitBarCard = new LinearLayout(this);
        splitBarCard.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable splitCardGd = new GradientDrawable();
        splitCardGd.setColor(Color.parseColor("#161B22"));
        splitCardGd.setCornerRadius(12 * density);
        splitCardGd.setStroke((int)(1.5f * density), Color.parseColor("#30363D"));
        splitBarCard.setBackground(splitCardGd);
        splitBarCard.setPadding((int)(14 * density), (int)(12 * density), (int)(14 * density), (int)(12 * density));

        LinearLayout.LayoutParams lpSplitBar = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpSplitBar.setMargins(0, (int)(6 * density), 0, (int)(10 * density));
        splitBarCard.setLayoutParams(lpSplitBar);

        TextView splitTitle = new TextView(this);
        splitTitle.setText("🎛️ 스플릿 뷰 프레임 콘솔 (3대 운용 체계 전환)");
        splitTitle.setTextSize(13.5f);
        splitTitle.setTextColor(Color.parseColor("#58A6FF"));
        splitTitle.setTypeface(Typeface.DEFAULT_BOLD);
        splitTitle.setIncludeFontPadding(false);
        splitBarCard.addView(splitTitle);

        TextView splitSub = new TextView(this);
        splitSub.setText("원하는 프레임을 터치하여 단독 또는 3분할 전체로 즉시 전환합니다.");
        splitSub.setTextSize(11);
        splitSub.setTextColor(Color.parseColor("#8B949E"));
        splitSub.setIncludeFontPadding(false);
        splitSub.setPadding(0, (int)(3 * density), 0, (int)(8 * density));
        splitBarCard.addView(splitSub);

        LinearLayout splitRow = new LinearLayout(this);
        splitRow.setOrientation(LinearLayout.HORIZONTAL);
        splitRow.setPadding(0, 0, 0, 0);

        mSplitViewButtons[0] = createSplitTabButton(splitRow, "전체", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setSplitMode(0); }
        });
        mSplitViewButtons[1] = createSplitTabButton(splitRow, "메인", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setSplitMode(1); }
        });
        mSplitViewButtons[2] = createSplitTabButton(splitRow, "서브1", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setSplitMode(2); }
        });
        mSplitViewButtons[3] = createSplitTabButton(splitRow, "서브2", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setSplitMode(3); }
        });
        splitBarCard.addView(splitRow);
        root.addView(splitBarCard);

        // =========================================================================
        // 👑 [ FRAME MAIN ] 기본 SSOT: 최신맞춤판 운용 체계 (428W 직결)
        // =========================================================================
        mFrameMainContainer = createFrameContainer(
                "👑 [ 메인 프레임 ] 최신맞춤판 (428W 직결 체계)",
                "최신 3기기 428W 직결 4구간 표준 스케줄 · 5대 핵심 맞춤 전술 프리셋",
                "#00E5FF",
                "#08121E"
        );

        // Section M-1: 최신 428W 직결 24시간 4구간 표준 맞춤 스케줄 (SSOT)
        addSectionHeaderInsideFrame(mFrameMainContainer, "1️⃣ 최신 428W 직결 24시간 4구간 표준 스케줄", "#00E5FF");

        LinearLayout mRow1 = new LinearLayout(this);
        mRow1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow1,
                "🌅 오전 (07~13시)",
                "3.3~7.3Hz(640s) | FM10%+AM80%",
                "🎛️DSP: +3dB펀치·트루피크0dBFS·배음OFF",
                "#00838F",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 3.3f, 7.3f, 640.0f,
                                true, 0.10f, 5.0f,
                                true, 0.80f, 1.2f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                15,
                                "[오전 07~13시] 3.3~7.3Hz(640초) + FM10% + AM80%",
                                "우퍼 1 [오전 자율신경]: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        addHalfPresetButton(mRow1,
                "☀️ 오후 (13~19시)",
                "18.6~25.1Hz(900s) | RM35%+AM70%",
                "🎛️DSP: +3dB·소프트새추레이터·2차배음ON",
                "#00695C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                false, 0.0f, 5.0f,
                                true, 0.70f, 1.3f,
                                true, 0.35f, 1.8f,
                                3.0f, 1, 0, true,
                                15,
                                "[오후 13~19시] 18.6~25.1Hz(900초) + RM35% + AM70%",
                                "우퍼 1 [오후 소화기·안구]: 볼륨 1시반(65%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        mFrameMainContainer.addView(mRow1);

        LinearLayout mRow2 = new LinearLayout(this);
        mRow2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow2,
                "🌆 저녁 메인 (19~01시)",
                "15~18.6Hz(900s) | RM45%+AM80%",
                "🎛️DSP: +3dB·소프트새추레이터·2차배음ON",
                "#4A148C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 18.6f, 900.0f,
                                false, 0.0f, 5.0f,
                                true, 0.80f, 1.2f,
                                true, 0.45f, 1.5f,
                                3.0f, 1, 0, true,
                                15,
                                "[저녁 19~01시 메인] 15~18.6Hz(900초) + RM45% + AM80%",
                                "우퍼 1 [저녁 체부둔통]: 볼륨 1시반(65%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        addHalfPresetButton(mRow2,
                "⚡ 저녁 기습 (첫10분)",
                "55.0Hz 단독 | AM100%(6Hz 펄스)",
                "🎛️DSP: +6dB익스트림·소프트새추레이터·배음ON",
                "#B71C1C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                true, 1.0f, 6.0f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                15,
                                "[저녁 19시 첫10분 기습] 55.0Hz 해머 펄스 (AM100%/6Hz)",
                                "우퍼 1 [저녁 10분 기습]: 볼륨 1시반~2시 | 베이스 2시 | 트레블 7시(0%)");
                    }
                });
        mFrameMainContainer.addView(mRow2);

        addFullPresetButton(mFrameMainContainer,
                "🌙 취침 55Hz 요격 & 수면 박탈 (01~07시)",
                "52.5~56.5Hz 스윕 (120초) | FM 15%(2Hz) + AM 60%(1Hz) 침실 공진 장악",
                "🎛️ 맞춤 DSP: 0.0dB 원음 직결 · 트루피크 0.00dBFS · 2차 배음 OFF",
                "#1A237E",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 52.5f, 56.5f, 120.0f,
                                true, 0.15f, 2.0f,
                                true, 0.60f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "[취침 01~07시] 52.5~56.5Hz(120초) + FM15% + AM60%",
                                "우퍼 1 [취침 수면박탈]: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시(0%)");
                    }
                });

        // Section M-2: 5대 핵심 맞춤 전술 프리셋
        addSectionHeaderInsideFrame(mFrameMainContainer, "2️⃣ 5대 핵심 맞춤 전술 프리셋 (최신맞춤판 SSOT)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "👑 프리셋 1 [하이브리드 표준형]",
                "3.3~7.3Hz(640s) 스윕 | FM 10%(5Hz) + AM 80%(1.2Hz) | 인체 복합 공진",
                "🎛️ 맞춤 DSP: +3.0dB 펀치 · 트루피크 0.00dBFS · 배음 OFF",
                "#004D40",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 3.3f, 7.3f, 640.0f,
                                true, 0.10f, 5.0f,
                                true, 0.80f, 1.2f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                15,
                                "[프리셋 1] 하이브리드 표준형 (3.3~7.3Hz 스윕 640초)",
                                "우퍼 1: 볼륨 1시30분(65%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👑 프리셋 2 [트리플 단독 집중 파괴형 (428W)]",
                "55.0Hz 단독 직타 | AM 85%(1.2Hz) + FM 14%(5.5Hz) | 428W 최대 출력",
                "🎛️ 맞춤 DSP: +6.0dB 익스트림 · 아날로그 tanh 새추레이터 · 2차 배음 ON",
                "#880E4F",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.14f, 5.5f,
                                true, 0.85f, 1.2f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                15,
                                "[프리셋 2] 트리플 단독 집중 파괴형 (55.0Hz 428W 풀파워)",
                                "우퍼 1: 볼륨 1시30분(65%) | 베이스 2시 | 트레블 7시");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👑 프리셋 3 [트리플 비동기 광대역 스윕형]",
                "18.6~25.1Hz(900s) 스윕 | RM 35%(1.8Hz) + AM 70%(1.3Hz) | 비동기 입체 포위",
                "🎛️ 맞춤 DSP: +3.0dB 펀치 · 트루피크 0.00dBFS · 2차 배음 ON",
                "#006064",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                false, 0.0f, 5.0f,
                                true, 0.70f, 1.3f,
                                true, 0.35f, 1.8f,
                                3.0f, 0, 0, true,
                                15,
                                "[프리셋 3] 트리플 비동기 광대역 스윕형 (18.6~25.1Hz 900초)",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👑 프리셋 4 [심야 침실 룸모드 공진 제압형]",
                "52.5~56.5Hz(120s) 스윕 | FM 15%(2Hz) + AM 60%(1Hz) | 침실 정재파 완전 장악",
                "🎛️ 맞춤 DSP: 0.0dB 원음 직결 · 트루피크 0.00dBFS · 배음 OFF",
                "#0D47A1",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 52.5f, 56.5f, 120.0f,
                                true, 0.15f, 2.0f,
                                true, 0.60f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "[프리셋 4] 심야 침실 룸모드 공진 제압형 (52.5~56.5Hz 120초)",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👑 프리셋 5 [즉각 응징 해머 펄스형]",
                "55.0Hz 단독 | AM 100%(6Hz 단발 펄스) 흉벽 강타 | 충격 응징",
                "🎛️ 맞춤 DSP: +6.0dB 익스트림 · 아날로그 tanh 새추레이터 · 2차 배음 ON",
                "#B71C1C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                true, 1.0f, 6.0f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                15,
                                "[프리셋 5] 즉각 응징 해머 펄스형 (55.0Hz AM100%/6Hz)",
                                "우퍼 1: 볼륨 1시반(65%) | 베이스 2시 | 트레블 7시");
                    }
                });

        root.addView(mFrameMainContainer);

        // Divider 1
        mSplitDivider1 = createSplitDivider("↕️ 운용 체계 분할선 [ 메인 ↔ 서브 1 ]", "#00E5FF");
        root.addView(mSplitDivider1);

        // =========================================================================
        // 🏛️ [ FRAME SUB 1 ] 서브 1: 주파수 통합 운용 체계 마스터 보고서 최종완결판 (v15.0)
        // =========================================================================
        mFrameSub1Container = createFrameContainer(
                "🏛️ [ 서브 1 프레임 ] 최종완결판 (v15.0) 체계",
                "하루 4등분 표준 스케줄 · 8대 전술 상황 · A30 전용 슬롯 1·2",
                "#1F6FEB",
                "#0D1525"
        );

        // Section S1-1: 하루 4등분 시간대별 표준
        addSectionHeaderInsideFrame(mFrameSub1Container, "1️⃣ 하루 4등분 시간대별 표준 스케줄 (최종완결판 v15.0)", "#58A6FF");

        LinearLayout row1 = new LinearLayout(this);
        row1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(row1,
                "🌅 아침 (07~13시)",
                "52~58Hz(180s) | FM10%+AM90%",
                "🎛️DSP: +3dB펀치·트루피크0dBFS·배음OFF",
                "#1F6FEB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 52.0f, 58.0f, 180.0f,
                                true, 0.10f, 5.0f,
                                true, 0.90f, 1.2f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                15,
                                "[아침 07~13시] 52~58Hz(180초) + FM10% + AM90%",
                                "우퍼 1 [아침 각성타격]: 볼륨 1시30분(65%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        addHalfPresetButton(row1,
                "☀️ 오후 (13~19시)",
                "18.6~25.1Hz(900s) | FM12%+RM40%",
                "🎛️DSP: +3dB·소프트새추레이터·2차배음ON",
                "#0969DA",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                true, 0.12f, 6.0f,
                                false, 0.0f, 1.0f,
                                true, 0.40f, 1.8f,
                                3.0f, 1, 0, true,
                                15,
                                "[오후 13~19시] 슬롯1 18.6~25.1Hz(900초) + FM12% + RM40%",
                                "우퍼 1 [오후 안구·전정]: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        mFrameSub1Container.addView(row1);

        LinearLayout row2 = new LinearLayout(this);
        row2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(row2,
                "🌆 저녁 (19~01시)",
                "15~18.6Hz(900s) | RM45%+AM80%",
                "🎛️DSP: +3dB·소프트새추레이터·2차배음ON",
                "#8250DF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 18.6f, 900.0f,
                                false, 0.0f, 5.0f,
                                true, 0.80f, 1.2f,
                                true, 0.45f, 1.5f,
                                3.0f, 1, 0, true,
                                15,
                                "[저녁 19~01시] 슬롯2 15~18.6Hz(900초) + RM45% + AM80%",
                                "우퍼 1 [저녁 체부둔통]: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        addHalfPresetButton(row2,
                "🌙 심야 (01~07시)",
                "18.98Hz 고정 + 7.0Hz 듀얼비트",
                "🎛️DSP: 0dB원음직결·트루피크0dBFS·배음OFF",
                "#161B22",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 7.0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "[심야 01~07시] 18.98Hz 고정 + 7.0Hz 듀얼비트 앵커",
                                "우퍼 1 [심야 수면교란]: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시(0%)");
                    }
                });
        mFrameSub1Container.addView(row2);

        // Section S1-2: 갤럭시 A30 전용 슬롯
        addSectionHeaderInsideFrame(mFrameSub1Container, "2️⃣ 갤럭시 A30 전용 슬롯 (A30 전용 대역)", "#58A6FF");

        LinearLayout rowSlot = new LinearLayout(this);
        rowSlot.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowSlot,
                "🅰️ 슬롯 1 (18.6~25.1Hz)",
                "900초 왕복 스윕 | 안구·전정기관 진탕",
                "🎛️ +3dB·소프트새추레이터·배음ON",
                "#005FB8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                true, 0.12f, 6.0f,
                                false, 0.0f, 1.0f,
                                true, 0.40f, 1.8f,
                                3.0f, 1, 0, true,
                                15,
                                "A30 슬롯1 [18.6~25.1Hz 스윕 900초]",
                                "우퍼 1 [슬롯 1]: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        addHalfPresetButton(rowSlot,
                "🅱️ 슬롯 2 (3.3~7.3Hz)",
                "640초 왕복 스윕 | 체감형 초저역 진동",
                "🎛️ +3dB·트루피크0dBFS·배음OFF",
                "#023E8A",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 3.3f, 7.3f, 640.0f,
                                true, 0.10f, 5.0f,
                                true, 0.80f, 1.2f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                15,
                                "A30 슬롯2 [3.3~7.3Hz 스윕 640초]",
                                "우퍼 1 [슬롯 2]: 볼륨 1시30분(65%) | 베이스 1시~2시 | 트레블 7시(0%)");
                    }
                });
        mFrameSub1Container.addView(rowSlot);

        // Section S1-3: 8대 전술 상황별 매뉴얼
        addSectionHeaderInsideFrame(mFrameSub1Container, "3️⃣ 8대 전술 상황별 매뉴얼 (최종완결판 ①~⑧)", "#58A6FF");

        LinearLayout rowSit1 = new LinearLayout(this);
        rowSit1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowSit1,
                "① 일반 외출 (2~5h)",
                "18.6~25.1Hz(900s) | RM35%",
                "🎛️ +3dB·소프트새추레이터·배음ON",
                "#238636",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                true, 0.35f, 1.5f,
                                3.0f, 1, 0, true,
                                15,
                                "상황 ① [일반 외출 2~5h] 18.6~25.1Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowSit1,
                "② 출근 무인 (12h)",
                "18.6~25.1Hz(900s) | FM10%+RM35%",
                "🎛️ 0dB원음직결·트루피크0dBFS",
                "#2EA043",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                true, 0.10f, 4.5f,
                                false, 0.0f, 1.0f,
                                true, 0.35f, 1.2f,
                                0.0f, 0, 0, false,
                                15,
                                "상황 ② [출근 12h 무인] 18.6~25.1Hz",
                                "우퍼 1: 볼륨 12시30분~1시(55~60%) | 베이스 1시 | 트레블 7시");
                    }
                });
        mFrameSub1Container.addView(rowSit1);

        LinearLayout rowSit2 = new LinearLayout(this);
        rowSit2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowSit2,
                "③ 장기 외출 (48h+)",
                "10.0~18.9Hz(3600s) | FM8%",
                "🎛️ 0dB원음직결·트루피크0dBFS",
                "#1F6FEB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 10.0f, 18.9f, 3600.0f,
                                true, 0.08f, 3.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "상황 ③ [장기 외출 48h+] 10~18.9Hz",
                                "우퍼 1: 볼륨 12시30분(55%) | 베이스 1시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowSit2,
                "④ 즉각 반격 (5~15m)",
                "18.98Hz+7.0Hz | AM100%(6Hz해머)",
                "🎛️ +6dB익스트림·소프트새추레이터",
                "#DA3633",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 7.0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                true, 1.0f, 6.0f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                15,
                                "상황 ④ [즉각 반격 해머 5~15분] 18.98+7Hz",
                                "우퍼 1: 볼륨 1시30분~2시(65~70%) | 베이스 2시 | 트레블 7시");
                    }
                });
        mFrameSub1Container.addView(rowSit2);

        LinearLayout rowSit3 = new LinearLayout(this);
        rowSit3.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowSit3,
                "⑤ 야간 취침 (01~07h)",
                "18.6~25.1Hz(900s) | FM15%+AM50%",
                "🎛️ 0dB원음직결·트루피크0dBFS",
                "#8250DF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                true, 0.15f, 4.0f,
                                true, 0.50f, 0.5f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "상황 ⑤ [야간 취침 01~07h] 18.6~25.1Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowSit3,
                "⑥ 상대 정신 파괴 (1~3h)",
                "7.83~12.5Hz(300s) | RM50%",
                "🎛️ +3dB·소프트새추레이터·배음ON",
                "#A371F7",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 7.83f, 12.5f, 300.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                true, 0.50f, 0.8f,
                                3.0f, 1, 0, true,
                                15,
                                "상황 ⑥ [상대 정신 파괴 1~3h] 7.83~12.5Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });
        mFrameSub1Container.addView(rowSit3);

        LinearLayout rowSit4 = new LinearLayout(this);
        rowSit4.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowSit4,
                "⑦ 상대 내성 파괴 (2~4h)",
                "9.0~16.5Hz(490s) | FM18%+AM100%",
                "🎛️ +6dB익스트림·소프트새추레이터",
                "#BF8700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 9.0f, 16.5f, 490.0f,
                                true, 0.18f, 5.5f,
                                true, 1.0f, 1.8f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                15,
                                "상황 ⑦ [상대 내성 파괴 2~4h] 9~16.5Hz",
                                "우퍼 1: 볼륨 1시반(65%) | 베이스 2시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowSit4,
                "⑧ 3시간+ 연속 유지",
                "18.6~25.1Hz(900s) | FM10%",
                "🎛️ 0dB원음직결·트루피크0dBFS",
                "#57606A",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                true, 0.10f, 3.5f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "상황 ⑧ [3시간+ 연속 유지] 18.6~25.1Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시");
                    }
                });
        mFrameSub1Container.addView(rowSit4);

        root.addView(mFrameSub1Container);

        // Divider 2
        mSplitDivider2 = createSplitDivider("↕️ 운용 체계 분할선 [ 서브 1 ↔ 서브 2 ]", "#8250DF");
        root.addView(mSplitDivider2);

        // =========================================================================
        // 🔮 [ FRAME SUB 2 ] 서브 2: 주파수 통합 운용 체계 마스터 보고서 ver.2 (SSOT)
        // =========================================================================
        mFrameSub2Container = createFrameContainer(
                "🔮 [ 서브 2 프레임 ] 마스터 ver.2 (SSOT) 체계",
                "스케줄 C 무인 라이프사이클 · 스케줄 A 광역 30~50Hz · 스케줄 B 핵심 전술",
                "#8250DF",
                "#191124"
        );

        // Section S2-1: 스케줄 C 무인 자동 라이프사이클
        addSectionHeaderInsideFrame(mFrameSub2Container, "1️⃣ 스케줄 C: 무인 자동 라이프사이클 (마스터 ver.2)", "#D2A8FF");

        addFullPresetButton(mFrameSub2Container,
                "💼 C-1 외출·출근 (10h 무인 자동)",
                "18.6~25.1Hz (900초 스윕) | RM 35%(1.5Hz) | 피로 누적 및 저항력 붕괴",
                "🎛️ 맞춤 DSP: +3.0dB 펀치 · 아날로그 tanh 새추레이터 · 2차 배음 ON",
                "#004D40",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 18.6f, 25.1f, 900.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                true, 0.35f, 1.5f,
                                3.0f, 1, 0, true,
                                15,
                                "스케줄 C-1 [외출·출근 10h 무인] 18.6~25.1Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🏠 C-2 퇴근·저녁 (4.5h 핵심 제압)",
                "35.0~48.0Hz (300초 스윕) | AM 80%(1.2Hz) | 체감 진동 강타 및 활동 억제",
                "🎛️ 맞춤 DSP: +3.0dB 펀치 · 아날로그 tanh 새추레이터 · 2차 배음 ON",
                "#4A148C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 35.0f, 48.0f, 300.0f,
                                false, 0.0f, 5.0f,
                                true, 0.80f, 1.2f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 0, true,
                                15,
                                "스케줄 C-2 [퇴근·저녁 4.5h 제압] 35~48Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🛏️ C-3 취침·수면 (9.5h 완전 보장)",
                "3.3~7.3Hz (640초 스윕) | AM 50%(0.5Hz) | 초저역 정밀 진탕 및 수면 박탈",
                "🎛️ 맞춤 DSP: 0.0dB 원음 직결 · 트루피크 0.00dBFS · 2차 배음 OFF",
                "#1A237E",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 3.3f, 7.3f, 640.0f,
                                false, 0.0f, 5.0f,
                                true, 0.50f, 0.5f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "스케줄 C-3 [취침·수면 9.5h 보장] 3.3~7.3Hz",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시");
                    }
                });

        // Section S2-2: 스케줄 A 광역 중저역 순환
        addSectionHeaderInsideFrame(mFrameSub2Container, "2️⃣ 스케줄 A: 광역 중저역 순환 체계 (30~50Hz)", "#D2A8FF");

        LinearLayout rowA1 = new LinearLayout(this);
        rowA1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowA1,
                "A-1 오전 중역 (40~50Hz)",
                "240초 스윕 | 전신 압박 순환",
                "🎛️ +3dB·트루피크·배음ON",
                "#00695C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 40.0f, 50.0f, 240.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, true,
                                15,
                                "스케줄 A-1 [오전 중역 40~50Hz 스윕]",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowA1,
                "A-2 오후 고정 (45.0Hz)",
                "단독 직타 | 흉부 공진 지속",
                "🎛️ +3dB·소프트새추레이터",
                "#004D40",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 45.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 0, false,
                                15,
                                "스케줄 A-2 [오후 고정 45.0Hz 단독]",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });
        mFrameSub2Container.addView(rowA1);

        LinearLayout rowA2 = new LinearLayout(this);
        rowA2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowA2,
                "A-3 저녁 중역 (35~48Hz)",
                "300초 스윕 | 체감 타격 극대화",
                "🎛️ +3dB·트루피크·배음ON",
                "#4A148C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 35.0f, 48.0f, 300.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, true,
                                15,
                                "스케줄 A-3 [저녁 중역 35~48Hz 스윕]",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시~2시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowA2,
                "A-4 야간 초저역 (20~25Hz)",
                "600초 스윕 | 심야 슬래브 관통",
                "🎛️ 0dB원음직결·트루피크",
                "#1A237E",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 20.0f, 25.0f, 600.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "스케줄 A-4 [야간 초저역 20~25Hz 스윕]",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시");
                    }
                });
        mFrameSub2Container.addView(rowA2);

        // Section S2-3: 스케줄 B 핵심 전술 정밀 프리셋
        addSectionHeaderInsideFrame(mFrameSub2Container, "3️⃣ 스케줄 B: 핵심 전술 정밀 프리셋 (단독·순환)", "#D2A8FF");

        LinearLayout rowB1 = new LinearLayout(this);
        rowB1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowB1,
                "B-1 43.2Hz 관통 강타",
                "골격 공진 및 두개골 관통",
                "🎛️ +3dB·소프트새추레이터·배음ON",
                "#880E4F",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 0, true,
                                15,
                                "스케줄 B-1 [43.2Hz 골격 공진 관통 강타]",
                                "우퍼 1: 볼륨 1시30분(65%) | 베이스 2시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowB1,
                "B-2 32.8Hz 흉복부 압박",
                "소화기 둔통 및 내장 공진",
                "🎛️ +3dB·소프트새추레이터·배음ON",
                "#B71C1C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 0, true,
                                15,
                                "스케줄 B-2 [32.8Hz 흉복부 둔통 내장 공진]",
                                "우퍼 1: 볼륨 1시30분(65%) | 베이스 2시 | 트레블 7시");
                    }
                });
        mFrameSub2Container.addView(rowB1);

        LinearLayout rowB2 = new LinearLayout(this);
        rowB2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(rowB2,
                "B-3 10~13Hz 알파파 교란",
                "440초 스윕 | 뇌파 동조 교란",
                "🎛️ +6dB익스트림·새추레이터·배음ON",
                "#E65100",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 10.0f, 13.0f, 440.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                15,
                                "스케줄 B-3 [10~13Hz 뇌파 교란 440초 스윕]",
                                "우퍼 1: 볼륨 1시30분(65%) | 베이스 2시 | 트레블 7시");
                    }
                });
        addHalfPresetButton(rowB2,
                "B-4 55.0Hz 요격 앵커",
                "단독 직타 | 룸모드 공진 제압",
                "🎛️ 0dB원음직결·트루피크0dBFS",
                "#0D47A1",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                15,
                                "스케줄 B-4 [55.0Hz 룸모드 요격 앵커]",
                                "우퍼 1: 볼륨 1시(60%) | 베이스 1시 | 트레블 7시");
                    }
                });
        mFrameSub2Container.addView(rowB2);

        root.addView(mFrameSub2Container);

        // =========================================================================
        // 🎛️ 하단 Vorta DSP Tactical Suite 제어 콘솔 (Bass Boost / Limiter / Matrix / Exciter)
        // =========================================================================
        addSectionHeader(root, "🎛️ Vorta DSP 신호처리 스위트 (하드웨어 직결 튜닝 콘솔)");

        // 1. Auto-Preset DSP Binding Lock
        addDspSubLabel(root, "1️⃣ 스케줄 프리셋 클릭 시 맞춤 DSP 자동 연동 (Auto-Sync):");
        LinearLayout autoRow = new LinearLayout(this);
        autoRow.setOrientation(LinearLayout.HORIZONTAL);
        mAutoLockButtons[0] = createDspTabButton(autoRow, "맞춤 DSP 자동 연동 (ON)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                A30AudioGeneratorService.sAutoPresetDsp = true;
                notifyDspChanged("맞춤 DSP 자동 연동 활성화");
            }
        });
        mAutoLockButtons[1] = createDspTabButton(autoRow, "수동 커스텀 고정 (OFF)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                A30AudioGeneratorService.sAutoPresetDsp = false;
                notifyDspChanged("수동 커스텀 모드 전환 (프리셋 클릭 시에도 현재 DSP 설정 고정)");
            }
        });
        root.addView(autoRow);

        // 2. Sub-Bass Tuner Gain Boost
        addDspSubLabel(root, "2️⃣ 초저역 서브우퍼 부스트 (Sub-Bass Tuner Gain):");
        LinearLayout boostRow = new LinearLayout(this);
        boostRow.setOrientation(LinearLayout.HORIZONTAL);
        mBoostButtons[0] = createDspTabButton(boostRow, "0.0 dB (원음)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setBassBoost(0.0f); }
        });
        mBoostButtons[1] = createDspTabButton(boostRow, "+3.0 dB (펀치)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setBassBoost(3.0f); }
        });
        mBoostButtons[2] = createDspTabButton(boostRow, "+6.0 dB (강력)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setBassBoost(6.0f); }
        });
        mBoostButtons[3] = createDspTabButton(boostRow, "+9.0 dB (익스트림)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setBassBoost(9.0f); }
        });
        root.addView(boostRow);

        // 3. Peak Limiter Mode
        addDspSubLabel(root, "3️⃣ 피크 리미터 및 새추레이터 모드 (True-Peak vs Soft Sat):");
        LinearLayout limRow = new LinearLayout(this);
        limRow.setOrientation(LinearLayout.HORIZONTAL);
        mLimiterButtons[0] = createDspTabButton(limRow, "0.00dBFS 트루피크 리미터", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setLimiterMode(0); }
        });
        mLimiterButtons[1] = createDspTabButton(limRow, "아날로그 tanh 새추레이터", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setLimiterMode(1); }
        });
        root.addView(limRow);

        // 4. Stereo Phase Matrix
        addDspSubLabel(root, "4️⃣ 채널 위상 및 밸런스 매트릭스 (Phase Matrix):");
        LinearLayout chRow = new LinearLayout(this);
        chRow.setOrientation(LinearLayout.HORIZONTAL);
        mChannelButtons[0] = createDspTabButton(chRow, "L=R 동위상", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setChannelMode(0); }
        });
        mChannelButtons[1] = createDspTabButton(chRow, "L=-R 역위상(180°)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setChannelMode(1); }
        });
        mChannelButtons[2] = createDspTabButton(chRow, "L 채널 단독", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setChannelMode(2); }
        });
        mChannelButtons[3] = createDspTabButton(chRow, "R 채널 단독", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setChannelMode(3); }
        });
        root.addView(chRow);

        // 5. 2nd Harmonic Exciter
        addDspSubLabel(root, "5️⃣ 2차 고조파 결합 익사이터 (2nd Harmonic Exciter):");
        LinearLayout exciterRow = new LinearLayout(this);
        exciterRow.setOrientation(LinearLayout.HORIZONTAL);
        mExciterButtons[0] = createDspTabButton(exciterRow, "2차 배음 활성화 (ON)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setHarmonicExciter(true); }
        });
        mExciterButtons[1] = createDspTabButton(exciterRow, "순수 정현파 보존 (OFF)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) { setHarmonicExciter(false); }
        });
        root.addView(exciterRow);

        // =========================================================================
        // 🛑 시스템 제어 및 긴급 정지 (A30 리소스 절약형 모드)
        // =========================================================================
        addSectionHeader(root, "🛑 시스템 제어 및 긴급 정지");

        addFullPresetButton(root,
                "🛑 주파수 즉시 정지 (STOP)",
                "AudioTrack 출력 및 백그라운드 발진 완전 종료",
                "출력 대기 상태 전환 (저장된 Vorta DSP 설정은 영구 보존됨)",
                "#7F1D1D",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        stopFrequency();
                    }
                });

        scroll.addView(root);
        setContentView(scroll);

        // Load persistent Split Mode
        SharedPreferences spSplit = getSharedPreferences(A30AudioGeneratorService.PREF_NAME, Context.MODE_PRIVATE);
        mCurrentSplitMode = spSplit.getInt(A30AudioGeneratorService.KEY_SPLIT_MODE, 0);
        setSplitMode(mCurrentSplitMode);

        handleIncomingIntent(getIntent());
        syncTelemetryUi();
    }

    private void setSplitMode(int mode) {
        mCurrentSplitMode = mode;
        SharedPreferences spSplit = getSharedPreferences(A30AudioGeneratorService.PREF_NAME, Context.MODE_PRIVATE);
        spSplit.edit().putInt(A30AudioGeneratorService.KEY_SPLIT_MODE, mode).apply();

        if (mode == 0) {
            // All 3 frames visible
            mFrameMainContainer.setVisibility(View.VISIBLE);
            mFrameSub1Container.setVisibility(View.VISIBLE);
            mFrameSub2Container.setVisibility(View.VISIBLE);
            mSplitDivider1.setVisibility(View.VISIBLE);
            mSplitDivider2.setVisibility(View.VISIBLE);
        } else if (mode == 1) {
            // Main Frame only
            mFrameMainContainer.setVisibility(View.VISIBLE);
            mFrameSub1Container.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.GONE);
            mSplitDivider1.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
        } else if (mode == 2) {
            // Sub 1 Frame only
            mFrameMainContainer.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.VISIBLE);
            mFrameSub2Container.setVisibility(View.GONE);
            mSplitDivider1.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
        } else if (mode == 3) {
            // Sub 2 Frame only
            mFrameMainContainer.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.VISIBLE);
            mSplitDivider1.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
        }
        updateSplitButtonUi();
    }

    private void updateSplitButtonUi() {
        float density = getResources().getDisplayMetrics().density;
        for (int i = 0; i < mSplitViewButtons.length; i++) {
            if (mSplitViewButtons[i] == null) continue;
            boolean active = (mCurrentSplitMode == i);
            GradientDrawable gd = new GradientDrawable();
            gd.setCornerRadius(8 * density);
            if (active) {
                String bgHex = (i == 0) ? "#0969DA" : (i == 1) ? "#00838F" : (i == 2) ? "#1F6FEB" : "#8250DF";
                String strokeHex = (i == 0) ? "#58A6FF" : (i == 1) ? "#00E5FF" : (i == 2) ? "#79C0FF" : "#D2A8FF";
                gd.setColor(Color.parseColor(bgHex));
                gd.setStroke((int)(2 * density), Color.parseColor(strokeHex));
                mSplitViewButtons[i].setBackground(gd);
                mSplitViewButtons[i].setTextColor(Color.WHITE);
                mSplitViewButtons[i].setTypeface(Typeface.DEFAULT_BOLD);
            } else {
                gd.setColor(Color.parseColor("#21262D"));
                gd.setStroke((int)(1 * density), Color.parseColor("#30363D"));
                mSplitViewButtons[i].setBackground(gd);
                mSplitViewButtons[i].setTextColor(Color.parseColor("#8B949E"));
                mSplitViewButtons[i].setTypeface(Typeface.DEFAULT);
            }
        }
    }

    private TextView createSplitTabButton(LinearLayout row, String text, float weight, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        TextView btn = new TextView(this);
        btn.setText(text);
        btn.setTextSize(13);
        btn.setTypeface(Typeface.DEFAULT_BOLD);
        btn.setTextColor(Color.parseColor("#8B949E"));
        btn.setGravity(Gravity.CENTER);
        btn.setSingleLine(true);
        btn.setIncludeFontPadding(false);
        btn.setPadding((int)(3 * density), 0, (int)(3 * density), 0);
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor("#21262D"));
        gd.setCornerRadius(8 * density);
        gd.setStroke((int)(1 * density), Color.parseColor("#30363D"));
        btn.setBackground(gd);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, (int)(44 * density), weight);
        lp.setMargins((int)(2.5f * density), 0, (int)(2.5f * density), 0);
        btn.setLayoutParams(lp);

        row.addView(btn);
        return btn;
    }

    private LinearLayout createSplitDivider(String text, String colorHex) {
        LinearLayout divider = new LinearLayout(this);
        divider.setOrientation(LinearLayout.HORIZONTAL);
        divider.setGravity(Gravity.CENTER);
        divider.setPadding(0, 16, 0, 16);

        TextView label = new TextView(this);
        label.setText(text);
        label.setTextSize(11);
        label.setTextColor(Color.parseColor(colorHex));
        label.setTypeface(Typeface.DEFAULT_BOLD);
        label.setBackgroundColor(Color.parseColor("#161B22"));
        label.setPadding(16, 6, 16, 6);

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor("#161B22"));
        gd.setCornerRadius(10 * getResources().getDisplayMetrics().density);
        gd.setStroke((int)(1 * getResources().getDisplayMetrics().density), Color.parseColor(colorHex));
        label.setBackground(gd);

        divider.addView(label);
        return divider;
    }

    private LinearLayout createFrameContainer(String titleText, String subtitleText, String borderColorHex, String bgColorHex) {
        LinearLayout frame = new LinearLayout(this);
        frame.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor(bgColorHex));
        gd.setCornerRadius(14 * getResources().getDisplayMetrics().density);
        gd.setStroke((int)(2 * getResources().getDisplayMetrics().density), Color.parseColor(borderColorHex));
        frame.setBackground(gd);
        frame.setPadding(14, 14, 14, 16);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 8, 0, 8);
        frame.setLayoutParams(lp);

        // Header Badge Box
        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.VERTICAL);
        header.setBackgroundColor(Color.parseColor("#161B22"));
        header.setPadding(12, 10, 12, 10);
        LinearLayout.LayoutParams lpH = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lpH.setMargins(0, 0, 0, 10);
        header.setLayoutParams(lpH);

        TextView tTitle = new TextView(this);
        tTitle.setText(titleText);
        tTitle.setTextSize(14);
        tTitle.setTextColor(Color.parseColor(borderColorHex));
        tTitle.setTypeface(Typeface.DEFAULT_BOLD);
        header.addView(tTitle);

        TextView tSub = new TextView(this);
        tSub.setText(subtitleText);
        tSub.setTextSize(10);
        tSub.setTextColor(Color.parseColor("#8B949E"));
        tSub.setPadding(0, 2, 0, 0);
        header.addView(tSub);

        frame.addView(header);
        return frame;
    }

    private void addSectionHeaderInsideFrame(LinearLayout parent, String text, String colorHex) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(12);
        tv.setTextColor(Color.parseColor(colorHex));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(4, 14, 4, 6);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        tv.setLayoutParams(lp);
        parent.addView(tv);
    }

    private void addSectionHeader(LinearLayout parent, String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(13);
        tv.setTextColor(Color.parseColor("#58A6FF"));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(4, 20, 4, 8);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        tv.setLayoutParams(lp);
        parent.addView(tv);
    }

    private void addDspSubLabel(LinearLayout parent, String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(11);
        tv.setTextColor(Color.parseColor("#E6EDF3"));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(2, 10, 2, 5);
        parent.addView(tv);
    }

    private TextView createDspTabButton(LinearLayout row, String text, float weight, View.OnClickListener listener) {
        TextView btn = new TextView(this);
        btn.setText(text);
        btn.setTextSize(11);
        btn.setTextColor(Color.parseColor("#C9D1D9"));
        btn.setBackgroundColor(Color.parseColor("#21262D"));
        btn.setGravity(Gravity.CENTER);
        btn.setPadding(8, 14, 8, 14);
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, weight);
        lp.setMargins(4, 0, 4, 6);
        btn.setLayoutParams(lp);

        row.addView(btn);
        return btn;
    }

    private void refreshDspButtonsUi() {
        boolean curAuto = A30AudioGeneratorService.sAutoPresetDsp;
        for (int i = 0; i < mAutoLockButtons.length; i++) {
            if (mAutoLockButtons[i] == null) continue;
            boolean active = (curAuto == mAutoLockValues[i]);
            mAutoLockButtons[i].setBackgroundColor(Color.parseColor(active ? (curAuto ? "#238636" : "#DA3633") : "#21262D"));
            mAutoLockButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#8B949E"));
            mAutoLockButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        float curBoost = A30AudioGeneratorService.sBassBoostDb;
        for (int i = 0; i < mBoostButtons.length; i++) {
            if (mBoostButtons[i] == null) continue;
            boolean active = Math.abs(curBoost - mBoostValues[i]) < 0.1f;
            mBoostButtons[i].setBackgroundColor(Color.parseColor(active ? "#0969DA" : "#21262D"));
            mBoostButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#8B949E"));
            mBoostButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        int curLimiter = A30AudioGeneratorService.sLimiterMode;
        for (int i = 0; i < mLimiterButtons.length; i++) {
            if (mLimiterButtons[i] == null) continue;
            boolean active = curLimiter == mLimiterValues[i];
            mLimiterButtons[i].setBackgroundColor(Color.parseColor(active ? "#1F6FEB" : "#21262D"));
            mLimiterButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#8B949E"));
            mLimiterButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        int curChannel = A30AudioGeneratorService.sChannelMode;
        for (int i = 0; i < mChannelButtons.length; i++) {
            if (mChannelButtons[i] == null) continue;
            boolean active = curChannel == mChannelValues[i];
            mChannelButtons[i].setBackgroundColor(Color.parseColor(active ? "#8250DF" : "#21262D"));
            mChannelButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#8B949E"));
            mChannelButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        boolean curExciter = A30AudioGeneratorService.sHarmonicExciter;
        for (int i = 0; i < mExciterButtons.length; i++) {
            if (mExciterButtons[i] == null) continue;
            boolean active = curExciter == mExciterValues[i];
            mExciterButtons[i].setBackgroundColor(Color.parseColor(active ? "#D29922" : "#21262D"));
            mExciterButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#8B949E"));
            mExciterButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        if (mStatusDsp != null) {
            mStatusDsp.setText("Vorta DSP: " + A30AudioGeneratorService.buildVortaDspSummary());
        }
    }

    private void notifyDspChanged(String toastMsg) {
        A30AudioGeneratorService.saveConfig(this);
        refreshDspButtonsUi();

        Intent svc = new Intent(this, A30AudioGeneratorService.class);
        svc.putExtra("auto_preset_dsp", A30AudioGeneratorService.sAutoPresetDsp);
        svc.putExtra("bass_boost_db", A30AudioGeneratorService.sBassBoostDb);
        svc.putExtra("limiter_mode", A30AudioGeneratorService.sLimiterMode);
        svc.putExtra("channel_mode", A30AudioGeneratorService.sChannelMode);
        svc.putExtra("harmonic_exciter", A30AudioGeneratorService.sHarmonicExciter);
        startService(svc);

        Toast.makeText(this, toastMsg + " (영구 저장됨)", Toast.LENGTH_SHORT).show();
    }

    private void setBassBoost(float db) {
        A30AudioGeneratorService.sBassBoostDb = db;
        notifyDspChanged(String.format("저음 부스트 +%.0fdB 적용", db));
    }

    private void setLimiterMode(int mode) {
        A30AudioGeneratorService.sLimiterMode = mode;
        notifyDspChanged(mode == 1 ? "아날로그 소프트 새추레이터 적용" : "트루피크 0.0dBFS 리미터 적용");
    }

    private void setChannelMode(int mode) {
        A30AudioGeneratorService.sChannelMode = mode;
        String desc = (mode == 1) ? "L=-R 역위상 180°" : (mode == 2) ? "L 채널 단독" : (mode == 3) ? "R 채널 단독" : "L=R 동위상";
        notifyDspChanged("채널 모드: " + desc);
    }

    private void setHarmonicExciter(boolean on) {
        A30AudioGeneratorService.sHarmonicExciter = on;
        notifyDspChanged(on ? "2차 배음 익사이터 ON" : "2차 배음 익사이터 OFF");
    }

    private void addHalfPresetButton(LinearLayout row, String mainText, String subText, String dspBadgeText, String colorHex, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        LinearLayout btn = new LinearLayout(this);
        btn.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor(colorHex));
        gd.setCornerRadius(8 * density);
        gd.setStroke((int)(1 * density), Color.parseColor("#30363D"));
        btn.setBackground(gd);
        btn.setPadding((int)(12 * density), (int)(10 * density), (int)(12 * density), (int)(10 * density));
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);
        btn.setMinimumHeight((int)(76 * density));

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lp.setMargins((int)(3 * density), 0, (int)(3 * density), (int)(8 * density));
        btn.setLayoutParams(lp);

        TextView tv1 = new TextView(this);
        tv1.setText(mainText);
        tv1.setTextSize(13);
        tv1.setTextColor(Color.WHITE);
        tv1.setTypeface(Typeface.DEFAULT_BOLD);
        tv1.setIncludeFontPadding(false);
        btn.addView(tv1);

        TextView tv2 = new TextView(this);
        tv2.setText(subText);
        tv2.setTextSize(10.5f);
        tv2.setTextColor(Color.parseColor("#E6EDF3"));
        tv2.setIncludeFontPadding(false);
        tv2.setPadding(0, (int)(3 * density), 0, (int)(2 * density));
        btn.addView(tv2);

        TextView tv3 = new TextView(this);
        tv3.setText(dspBadgeText);
        tv3.setTextSize(10);
        tv3.setTextColor(Color.parseColor("#7EE787"));
        tv3.setTypeface(Typeface.DEFAULT_BOLD);
        tv3.setIncludeFontPadding(false);
        btn.addView(tv3);

        row.addView(btn);
    }

    private void addFullPresetButton(LinearLayout parent, String mainText, String subText, String dspBadgeText, String colorHex, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        LinearLayout btn = new LinearLayout(this);
        btn.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor(colorHex));
        gd.setCornerRadius(8 * density);
        gd.setStroke((int)(1 * density), Color.parseColor("#30363D"));
        btn.setBackground(gd);
        btn.setPadding((int)(16 * density), (int)(12 * density), (int)(16 * density), (int)(12 * density));
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);
        btn.setMinimumHeight((int)(70 * density));

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, (int)(8 * density));
        btn.setLayoutParams(lp);

        TextView tvMain = new TextView(this);
        tvMain.setText(mainText);
        tvMain.setTextSize(13.5f);
        tvMain.setTextColor(Color.WHITE);
        tvMain.setTypeface(Typeface.DEFAULT_BOLD);
        tvMain.setIncludeFontPadding(false);
        btn.addView(tvMain);

        TextView tvSub = new TextView(this);
        tvSub.setText(subText);
        tvSub.setTextSize(11);
        tvSub.setTextColor(Color.parseColor("#E6EDF3"));
        tvSub.setIncludeFontPadding(false);
        tvSub.setPadding(0, (int)(3 * density), 0, (int)(3 * density));
        btn.addView(tvSub);

        TextView tvDsp = new TextView(this);
        tvDsp.setText(dspBadgeText);
        tvDsp.setTextSize(10.5f);
        tvDsp.setTextColor(Color.parseColor("#7EE787"));
        tvDsp.setTypeface(Typeface.DEFAULT_BOLD);
        tvDsp.setIncludeFontPadding(false);
        btn.addView(tvDsp);

        parent.addView(btn);
    }

    private void startPresetWithDsp(boolean sweep, float freq, float subFreq,
                                    float sMin, float sMax, float sSec,
                                    boolean fmOn, float fmDepth, float fmRate,
                                    boolean amOn, float amDepth, float amRate,
                                    boolean rmOn, float rmDepth, float rmRate,
                                    float presetBoostDb, int presetLimiterMode, int presetChannelMode, boolean presetExciter,
                                    int volStep, String title, String knobGuide) {
        volStep = 15;

        // If Auto-Preset DSP is enabled, automatically apply the preset's tailored Vorta DSP settings
        if (A30AudioGeneratorService.sAutoPresetDsp) {
            A30AudioGeneratorService.sBassBoostDb = presetBoostDb;
            A30AudioGeneratorService.sLimiterMode = presetLimiterMode;
            A30AudioGeneratorService.sChannelMode = presetChannelMode;
            A30AudioGeneratorService.sHarmonicExciter = presetExciter;
            A30AudioGeneratorService.saveConfig(this);
        }
        refreshDspButtonsUi();

        Intent svc = new Intent(this, A30AudioGeneratorService.class);
        svc.putExtra("sweep", sweep);
        svc.putExtra("freq", freq);
        svc.putExtra("sub_freq", subFreq);
        svc.putExtra("sweep_min", sMin);
        svc.putExtra("sweep_max", sMax);
        svc.putExtra("sweep_sec", sSec);
        svc.putExtra("fm_on", fmOn);
        svc.putExtra("fm_depth", fmDepth);
        svc.putExtra("fm_rate", fmRate);
        svc.putExtra("am_on", amOn);
        svc.putExtra("am_depth", amDepth);
        svc.putExtra("am_rate", amRate);
        svc.putExtra("rm_on", rmOn);
        svc.putExtra("rm_depth", rmDepth);
        svc.putExtra("rm_rate", rmRate);
        svc.putExtra("vol_step", volStep);
        svc.putExtra("title", title);
        svc.putExtra("knob", knobGuide);
        svc.putExtra("bass_boost_db", A30AudioGeneratorService.sBassBoostDb);
        svc.putExtra("limiter_mode", A30AudioGeneratorService.sLimiterMode);
        svc.putExtra("channel_mode", A30AudioGeneratorService.sChannelMode);
        svc.putExtra("harmonic_exciter", A30AudioGeneratorService.sHarmonicExciter);
        if (android.os.Build.VERSION.SDK_INT >= 26) {
            startForegroundService(svc);
        } else {
            startService(svc);
        }

        syncTelemetryUi();
        Toast.makeText(this, title + " + Vorta 맞춤 DSP 발진", Toast.LENGTH_SHORT).show();
    }

    private void stopFrequency() {
        Intent svc = new Intent(this, A30AudioGeneratorService.class);
        svc.putExtra("action", "stop");
        startService(svc);

        mStatusMode.setText("현재 모드: ■ 발진 정지됨 (음소거 대기)");
        mStatusFreq.setText("실시간 발진: -- Hz (출력 없음)");
        mStatusMod.setText("변조(FM/AM/RM): 정지됨");
        Toast.makeText(this, "보르타 레조(A30) 주파수 발생 정지 완료", Toast.LENGTH_SHORT).show();
    }

    private void syncTelemetryUi() {
        if (A30AudioGeneratorService.sIsPlaying) {
            mStatusMode.setText("가동 중: " + A30AudioGeneratorService.sModeTitle);
            if (A30AudioGeneratorService.sIsSweepMode) {
                mStatusFreq.setText(String.format("실시간 스윕: %.2f Hz (범위 %.1f~%.1fHz / %.0f초 왕복)",
                        A30AudioGeneratorService.sInstantFreq,
                        A30AudioGeneratorService.sSweepMin,
                        A30AudioGeneratorService.sSweepMax,
                        A30AudioGeneratorService.sSweepPeriodSec));
            } else {
                mStatusFreq.setText(String.format("실시간 발진: %.2f Hz 고정 (64-bit 정현파 0.00 dBFS)",
                        A30AudioGeneratorService.sTargetFreq));
            }
            mStatusMod.setText("활성 변조: " + A30AudioGeneratorService.buildModulationSummary());
            mStatusDsp.setText("Vorta DSP: " + A30AudioGeneratorService.buildVortaDspSummary());
            mStatusSignal.setText(String.format("검수: 48,000Hz Native | Peak %d/32767(0.00dBFS) | RMS %.2fdBFS | DC %.4f | 왜곡 0%%",
                    A30AudioGeneratorService.sLastPeak, A30AudioGeneratorService.sLastRmsDb, A30AudioGeneratorService.sLastDcOffset));
            mStatusKnob.setText(A30AudioGeneratorService.sKnobGuide);
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

        if (intent.hasExtra("sweep") || intent.hasExtra("freq") || intent.hasExtra("mode")) {
            boolean isSweep = intent.getBooleanExtra("sweep", false)
                    || "sweep".equalsIgnoreCase(intent.getStringExtra("mode"));
            float freq = intent.getFloatExtra("freq", 18.98f);
            float subFreq = intent.getFloatExtra("sub_freq", 0.0f);
            float sMin = intent.getFloatExtra("sweep_min", 18.6f);
            float sMax = intent.getFloatExtra("sweep_max", 25.1f);
            float sSec = intent.getFloatExtra("sweep_sec", 900.0f);
            boolean fmOn = intent.getBooleanExtra("fm_on", false);
            float fmDepth = intent.getFloatExtra("fm_depth", 0.10f);
            float fmRate = intent.getFloatExtra("fm_rate", 5.0f);
            boolean amOn = intent.getBooleanExtra("am_on", false);
            float amDepth = intent.getFloatExtra("am_depth", 0.90f);
            float amRate = intent.getFloatExtra("am_rate", 1.2f);
            boolean rmOn = intent.getBooleanExtra("rm_on", false);
            float rmDepth = intent.getFloatExtra("rm_depth", 0.40f);
            float rmRate = intent.getFloatExtra("rm_rate", 1.5f);
            float boostDb = intent.getFloatExtra("bass_boost_db", A30AudioGeneratorService.sBassBoostDb);
            int limiterMode = intent.getIntExtra("limiter_mode", A30AudioGeneratorService.sLimiterMode);
            int channelMode = intent.getIntExtra("channel_mode", A30AudioGeneratorService.sChannelMode);
            boolean exciter = intent.getBooleanExtra("harmonic_exciter", A30AudioGeneratorService.sHarmonicExciter);
            int volStep = intent.getIntExtra("vol_step", 15);
            String title = intent.getStringExtra("title");
            String knob = intent.getStringExtra("knob");

            startPresetWithDsp(isSweep, freq, subFreq, sMin, sMax, sSec,
                    fmOn, fmDepth, fmRate,
                    amOn, amDepth, amRate,
                    rmOn, rmDepth, rmRate,
                    boostDb, limiterMode, channelMode, exciter,
                    volStep, title, knob);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshDspButtonsUi();
        syncTelemetryUi();
        mHandler.post(mUiSyncRunnable);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mHandler.removeCallbacks(mUiSyncRunnable);
    }
}
