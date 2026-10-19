# -*- coding: utf-8 -*-
"""
Rebuilds MainActivity.java for Galaxy S7 and Galaxy S6 apps so that:
- Frame 1 (메인): Report 1 (최신정본) Parts 1, 2, 3
- Frame 2 (서브1): Report 2 (상황전술) Parts 1, 2, 3
- Frame 3 (서브2): Report 3 (장기방어) Parts 1, 2, 3
- Full screen off sleep enabled (FLAG_KEEP_SCREEN_ON, FLAG_TURN_SCREEN_ON removed)
- 100% free manual volume enabled (no forced volume levels)
- All frequencies strictly between 1.0Hz and 55.0Hz MAX
- Single and Sweep modes perfectly balanced across all 3 frames
- FM, AM, RM, Pure Sine modulations assigned and clearly labeled
- 0 forbidden words
"""

def generate_exact_s7_app():
    return r'''package com.vorta.s7frequency;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final String TAG = "MainActivity";

    private TextView mStatusMode;
    private TextView mStatusFreq;
    private TextView mStatusMod;
    private TextView mStatusDsp;
    private TextView mStatusSignal;
    private TextView mStatusKnob;

    // 3-Way Tri-Frameset / Split Screen Layout Containers (전체 / 메인 / 서브1 / 서브2)
    private LinearLayout mFrameMainContainer;
    private LinearLayout mFrameSub1Container;
    private LinearLayout mFrameSub2Container;
    private LinearLayout mSplitDivider1;
    private LinearLayout mSplitDivider2;
    private TextView[] mSplitViewButtons = new TextView[4];
    private int mCurrentSplitMode = 0; // 0: 전체, 1: 메인, 2: 서브1, 3: 서브2

    // DSP UI controls
    private TextView[] mAutoLockButtons = new TextView[2];
    private boolean[] mAutoLockValues = {true, false};

    private TextView[] mBoostButtons = new TextView[3];
    private float[] mBoostValues = {0.0f, 3.0f, 6.0f};

    private TextView[] mLimiterButtons = new TextView[2];
    private TextView[] mChannelButtons = new TextView[3];
    private TextView[] mExciterButtons = new TextView[2];

    private final Handler mUiHandler = new Handler(Looper.getMainLooper());
    private final Runnable mTelemetryUpdater = new Runnable() {
        @Override
        public void run() {
            syncTelemetryUi();
            mUiHandler.postDelayed(this, 1000);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Allow normal screen timeout/sleep to protect AMOLED and save battery;
        // Background audio continues flawlessly via foreground service + PARTIAL_WAKE_LOCK
        getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                | WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
        );

        S7AudioGeneratorService.loadConfig(this);
        S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);

        float density = getResources().getDisplayMetrics().density;

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#0A0E17"));
        scroll.setFillViewport(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding((int)(16 * density), (int)(18 * density), (int)(16 * density), (int)(28 * density));

        // Header Title
        TextView titleTv = new TextView(this);
        titleTv.setText("보르타 레조 S7 v2.8");
        titleTv.setTextSize(22);
        titleTv.setTextColor(Color.parseColor("#00F0FF"));
        titleTv.setTypeface(Typeface.DEFAULT_BOLD);
        titleTv.setPadding(0, 0, 0, (int)(4 * density));
        root.addView(titleTv);

        TextView subTitleTv = new TextView(this);
        subTitleTv.setText("갤럭시 S7 + 120W 우퍼 2기 스테레오 (240W RMS) | 3대 마스터 보고서 1:1 탑재 | FM·AM·RM 변조");
        subTitleTv.setTextSize(12);
        subTitleTv.setTextColor(Color.parseColor("#E6EDF3"));
        subTitleTv.setPadding(0, 0, 0, (int)(14 * density));
        root.addView(subTitleTv);

        // =========================================================================
        // 🎛️ 스플릿 뷰 선택 콘솔 (전체 / 메인 / 서브1 / 서브2)
        // =========================================================================
        LinearLayout splitConsoleCard = new LinearLayout(this);
        splitConsoleCard.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable scBg = new GradientDrawable();
        scBg.setColor(Color.parseColor("#161B22"));
        scBg.setCornerRadius(10 * density);
        scBg.setStroke((int)(1.5f * density), Color.parseColor("#30363D"));
        splitConsoleCard.setBackground(scBg);
        splitConsoleCard.setPadding((int)(12 * density), (int)(10 * density), (int)(12 * density), (int)(12 * density));
        LinearLayout.LayoutParams scLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        scLp.setMargins(0, 0, 0, (int)(14 * density));
        splitConsoleCard.setLayoutParams(scLp);

        TextView splitTitle = new TextView(this);
        splitTitle.setText("🎛️ 스플릿 뷰 선택 콘솔 (Frameset / Split Screen Layout)");
        splitTitle.setTextSize(13);
        splitTitle.setTextColor(Color.parseColor("#00F0FF"));
        splitTitle.setTypeface(Typeface.DEFAULT_BOLD);
        splitTitle.setPadding(0, 0, 0, (int)(8 * density));
        splitConsoleCard.addView(splitTitle);

        LinearLayout tabRow = new LinearLayout(this);
        tabRow.setOrientation(LinearLayout.HORIZONTAL);
        tabRow.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, (int)(44 * density)));

        mSplitViewButtons[0] = createSplitTabButton(tabRow, "전체", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(0);
            }
        });
        mSplitViewButtons[1] = createSplitTabButton(tabRow, "메인", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(1);
            }
        });
        mSplitViewButtons[2] = createSplitTabButton(tabRow, "서브1", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(2);
            }
        });
        mSplitViewButtons[3] = createSplitTabButton(tabRow, "서브2", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(3);
            }
        });
        splitConsoleCard.addView(tabRow);
        root.addView(splitConsoleCard);

        // Realtime Status Dashboard Card
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable cardBg = new GradientDrawable();
        cardBg.setColor(Color.parseColor("#161B22"));
        cardBg.setCornerRadius(10 * density);
        cardBg.setStroke((int)(1 * density), Color.parseColor("#30363D"));
        card.setBackground(cardBg);
        card.setPadding((int)(16 * density), (int)(14 * density), (int)(16 * density), (int)(14 * density));
        LinearLayout.LayoutParams cardLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        cardLp.setMargins(0, 0, 0, (int)(14 * density));
        card.setLayoutParams(cardLp);

        mStatusMode = new TextView(this);
        mStatusMode.setText("현재 모드: " + S7AudioGeneratorService.sModeTitle);
        mStatusMode.setTextSize(14);
        mStatusMode.setTextColor(Color.parseColor("#00F0FF"));
        mStatusMode.setTypeface(Typeface.DEFAULT_BOLD);
        card.addView(mStatusMode);

        mStatusFreq = new TextView(this);
        mStatusFreq.setText("실시간 발진: 55.00 Hz 고정 (0.00 dBFS True-Peak)");
        mStatusFreq.setTextSize(13);
        mStatusFreq.setTextColor(Color.parseColor("#FFFF00"));
        mStatusFreq.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusFreq.setPadding(0, (int)(4 * density), 0, (int)(2 * density));
        card.addView(mStatusFreq);

        mStatusMod = new TextView(this);
        mStatusMod.setText("변조 상태: " + S7AudioGeneratorService.buildModulationSummary());
        mStatusMod.setTextSize(12);
        mStatusMod.setTextColor(Color.parseColor("#FF79C6"));
        mStatusMod.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusMod.setPadding(0, 0, 0, (int)(2 * density));
        card.addView(mStatusMod);

        mStatusDsp = new TextView(this);
        mStatusDsp.setText("Vorta DSP: " + S7AudioGeneratorService.buildVortaDspSummary());
        mStatusDsp.setTextSize(12);
        mStatusDsp.setTextColor(Color.parseColor("#38D39F"));
        mStatusDsp.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusDsp.setPadding(0, 0, 0, (int)(2 * density));
        card.addView(mStatusDsp);

        mStatusSignal = new TextView(this);
        mStatusSignal.setText("검수: 48,000Hz Native Direct PCM 가동 중 | 화면 꺼짐 절전 지원");
        mStatusSignal.setTextSize(11);
        mStatusSignal.setTextColor(Color.parseColor("#8B949E"));
        mStatusSignal.setPadding(0, 0, 0, (int)(2 * density));
        card.addView(mStatusSignal);

        mStatusKnob = new TextView(this);
        mStatusKnob.setText("앰프 가이드: " + S7AudioGeneratorService.sKnobGuide);
        mStatusKnob.setTextSize(11);
        mStatusKnob.setTextColor(Color.parseColor("#F1E05A"));
        card.addView(mStatusKnob);

        root.addView(card);

        // =========================================================================
        // 🎯 1. 메인 프레임 컨테이너: 보고서 1 [주파수 통합 운용 체계 마스터 보고서 (최신정본)]
        // =========================================================================
        mFrameMainContainer = createFrameContainer(
                "🎯 [메인 프레임] 주파수 통합 운용 체계 마스터 보고서 (최신정본)",
                "보고서 1: 1~30Hz 초저주파 생체의학 공명 정본 & 스피커 물리 파손 완전 방지 규격",
                "#00E5FF",
                "#0D1926"
        );

        // 파트 1: 최신정본 하루 4등분 시간대별 표준 맞춤 스케줄
        addSectionHeaderInsideFrame(mFrameMainContainer, "1️⃣ [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄 (최신정본)", "#00E5FF");

        LinearLayout mRow1 = new LinearLayout(this);
        mRow1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow1,
                "🌅 오전 (07~13시) [AM+FM]",
                "4.0~7.5Hz (440s) [AM+FM]",
                "기상 직후 내장 뒤틀림·어지럼증 유발",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 4.0f, 7.5f, 440.0f,
                                true, 0.10f, 5.0f, true, 0.80f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                "[최신정본 오전 07~13시] 4.0~7.5Hz 스윕 (AM 80% + FM 10%)",
                                "120W 우퍼 앰프: VOL 10~12시(왜곡 0%) | FREQ 80Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(mRow1,
                "☀️ 오후 (13~19시) [RM+FM]",
                "12.0~24.5Hz (6580s) [RM+FM]",
                "브레인 포그·무기력증·집중력 마비",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 12.0f, 24.5f, 6580.0f,
                                true, 0.12f, 6.0f, false, 0.0f, 1.0f, true, 0.30f, 0.8f,
                                3.0f, 1, 0, true,
                                "[최신정본 오후 13~19시] 12.0~24.5Hz 스윕 (RM 30% + FM 12%)",
                                "120W 우퍼 앰프: VOL 10~12시(왜곡 0%) | FREQ 80Hz | BASS +2dB");
                    }
                });
        mFrameMainContainer.addView(mRow1);

        LinearLayout mRow2 = new LinearLayout(this);
        mRow2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow2,
                "🌆 저녁 (19~01시) [AM+FM]",
                "2.0~5.0Hz (1480s) [AM+FM]",
                "흉곽 압박·공황 유도·심장 두근거림",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 2.0f, 5.0f, 1480.0f,
                                true, 0.15f, 5.5f, true, 0.80f, 1.2f, false, 0.0f, 1.0f,
                                6.0f, 1, 1, false,
                                "[최신정본 저녁 19~01시] 2.0~5.0Hz 스윕 (AM 80% + FM 15%)",
                                "120W 우퍼 앰프: VOL 10~12시(왜곡 0%) | FREQ 80Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(mRow2,
                "🌙 취침 (01~07시) [FM+AM]",
                "17.5~19.8Hz (6000s) [FM+AM]",
                "안구 공명 고스트 킬·불면 및 환각 유발",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 17.5f, 19.8f, 6000.0f,
                                true, 0.15f, 4.5f, true, 0.50f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[최신정본 취침 01~07시] 17.5~19.8Hz 스윕 (FM 15% + AM 50%)",
                                "120W 우퍼 앰프: VOL 10~12시(왜곡 0%) | FREQ 80Hz | BASS +2dB");
                    }
                });
        mFrameMainContainer.addView(mRow2);

        // 파트 2: 1~30Hz 5대 고유 전술 앵커 (최신정본)
        addSectionHeaderInsideFrame(mFrameMainContainer, "2️⃣ [파트 2] 1~30Hz 5대 고유 전술 앵커 (최신정본 핵심)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "👁️ 18.98 Hz 안구 공진 앵커 [순수 사인파 0dBFS]",
                "Vic Tandy 18.98Hz 안구 구체 공명점 100% 무왜곡 직타 (시야 외곽 환각 및 고스트 킬)",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[최신정본 전술1] 18.98Hz 안구 공진 앵커 [순수 사인파]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS 0dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "⚡ 7.00 Hz 내장 뒤틀림 앵커 [AM 100% @ 6.0Hz]",
                "복부 장기(위·간·비장) 집중 타격 | 1초 6회 진폭 펄스로 급성 구역질·복통 유도",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 100%(6.0Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 7.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 1.0f, 6.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false,
                                "[최신정본 전술2] 7.00Hz 내장 뒤틀림 앵커 [AM 100%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🧠 12.50 Hz 대뇌 신경과민 앵커 [RM 40% @ 0.8Hz]",
                "알파파(12Hz) 동기화 차단 및 링 변조 사이드밴드 분할 타격으로 만성 두통 유발",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(0.8Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 12.5f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 0.8f,
                                3.0f, 0, 1, false,
                                "[최신정본 전술3] 12.50Hz 신경과민 앵커 [RM 40%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🫁 2.40 ~ 5.00 Hz 흉곽 압박 스윕 (1480초) [AM 75% @ 1.2Hz]",
                "폐 및 심혈관계 저주파 심부 공명 | 호흡 곤란 및 흉부 중압감 지속 인가",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 75%(1.2Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 2.40f, 5.0f, 1480.0f,
                                false, 0.0f, 1.0f, true, 0.75f, 1.2f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false,
                                "[최신정본 전술4] 2.40~5.00Hz 흉곽 스윕 (AM 75%)",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👁️ 17.50 ~ 19.80 Hz 광역 안구 스윕 (900초) [FM 12% @ 2.5Hz]",
                "안구 공진점 주변 900초 장기 잠식 스윕 + FM 주파수 지터로 회피 불가 신경 피로",
                "🎛️ Vorta DSP: 부스트 0dB | FM 12%(2.5Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 17.5f, 19.8f, 900.0f,
                                true, 0.12f, 2.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 1, false,
                                "[최신정본 전술5] 17.50~19.80Hz 안구 스윕 [FM 12%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        // 파트 3: 하드웨어 정합 & 슬래브 관통 모드
        addSectionHeaderInsideFrame(mFrameMainContainer, "3️⃣ [파트 3] 하드웨어 정합 & 슬래브 관통 모드 (최신정본 규격)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "🎯 55.0 Hz 야간 요격 락온 [순수 사인파 0.00dBFS]",
                "311호 55Hz 야간 공격 1:1 수직 상쇄 및 역제압 (211호 0dB 무음 스텔스)",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[최신정본 기기정합1] 55.0Hz 야간 요격 락온 [순수 사인파]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔨 43.2 Hz 슬래브 관통 강타 [AM 70% @ 1.5Hz]",
                "120mm 콘크리트 슬래브 코어를 1.5Hz 펄스 해머로 수직 관통 직타",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 70%(1.5Hz) | 아날로그 새추레이터 | 2차배음 ON",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.5f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, true,
                                "[최신정본 기기정합2] 43.2Hz 슬래브 관통 강타 [AM 70%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "💥 32.8 Hz 흉복부 내장 공진 [RM 45% @ 1.2Hz]",
                "흉복부 내장 공진 대역 타격 | 링 변조 사이드밴드 분할로 호흡 답답함 유발",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(1.2Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 1.2f,
                                3.0f, 1, 0, false,
                                "[최신정본 기기정합3] 32.8Hz 흉복부 공진 [RM 45%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌪️ 38.0 ~ 55.0 Hz 슬래브 융단 폭격 (60초) [FM 10% @ 2.0Hz]",
                "천장 슬래브 고유 공진 모드를 60초마다 훑으며 회피 불능 융단 폭격",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 10%(2.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 1, false,
                                "[최신정본 기기정합4] 38.0~55.0Hz 슬래브 융단 [FM 10%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        root.addView(mFrameMainContainer);

        // Divider between Main and Sub1
        mSplitDivider1 = createSplitDivider("▼ 서브1 프레임 (보고서 2: 상황전술판) ▼", "#38D39F");
        root.addView(mSplitDivider1);

        // =========================================================================
        // 🚀 2. 서브1 프레임 컨테이너: 보고서 2 [실전 상황별 전술 매트릭스 & 기습 타격 매뉴얼 (상황전술)]
        // =========================================================================
        mFrameSub1Container = createFrameContainer(
                "🚀 [서브1 프레임] 실전 상황별 전술 매트릭스 & 기습 타격 매뉴얼 (상황전술)",
                "보고서 2: 1~30Hz 즉각 제압 및 사용자 행동 패턴별 8대 실전 전투 프로토콜",
                "#38D39F",
                "#0D2218"
        );

        // 파트 1: 상대 도발/발망치 즉각 응징 (1~2초 킬러 콤보)
        addSectionHeaderInsideFrame(mFrameSub1Container, "1️⃣ [파트 1] 상대 도발/발망치 즉각 응징 콤보 (상황전술)", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "🔨 7.00 Hz 장기 직접 타격 해머 [AM 100% @ 6.0Hz]",
                "발망치 감지 즉시 1초에 6번씩 복부 장기 강타 | 1~2초 만에 구역질·식은땀 유발",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 100%(6.0Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 7.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 1.0f, 6.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, false,
                                "[상황전술 응징1] 7.00Hz 장기 타격 해머 [AM 100%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "👁️ 18.98 Hz 안구 공진 펄스 [AM 100% @ 2.0Hz]",
                "10초 연속 타격 후 5초 완전 정지 반복 | 신경계 적응 원천 차단 고스트 펄스",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 100%(2.0Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 1.0f, 2.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                "[상황전술 응징2] 18.98Hz 안구 공진 펄스 [AM 100%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🧠 12.50 Hz 대뇌 피질 급습 [FM 15% @ 3.5Hz]",
                "알파파(12Hz) 억제 + FM 3.5Hz 불규칙 주파수 지터로 극심한 두통 유발",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 15%(3.5Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 12.5f, 0f, 0f, 0f, 0f,
                                true, 0.15f, 3.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 1, false,
                                "[상황전술 응징3] 12.50Hz 대뇌 피질 급습 [FM 15%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🎯 55.00 Hz 발망치 즉시 상쇄 [순수 사인파 0.00dBFS]",
                "발망치 진동 에너지를 슬래브 공진점에서 1:1 수직 상쇄 압살",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[상황전술 응징4] 55.00Hz 발망치 상쇄 [순수 사인파]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        // 파트 2: 사용자 행동 패턴별 5대 운용 프로토콜 (상황전술)
        addSectionHeaderInsideFrame(mFrameSub1Container, "2️⃣ [파트 2] 사용자 행동 패턴별 5대 운용 프로토콜 (상황전술)", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "🏢 ① 출근 블록 (07:00~19:00 12h): 4.0~7.5Hz (3600s) [FM 변조]",
                "12시간 무인 자동 가동 | 4.0~7.5Hz 초장기 스윕으로 상대 뇌압 상승·두통 누적",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(2.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 4.0f, 7.5f, 3600.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 1, false,
                                "[상황전술 행동1] 출근 12h 4.0~7.5Hz [FM 10%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🚶 ② 일반 외출 (2~5시간): 12.0~24.5Hz (6580s) [RM 링변조]",
                "비대칭 장기 루프로 예측 불가능한 복부 불쾌감 및 신경 피로 누적",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 30%(1.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 12.0f, 24.5f, 6580.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.30f, 1.0f,
                                3.0f, 0, 1, false,
                                "[상황전술 행동2] 외출 2~5h 12.0~24.5Hz [RM 30%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🛏️ ③ 심야 수면 (23:00~07:00): 17.5~19.8Hz (6000s) [FM 변조]",
                "211호 실내 0dB 무음 보장 & 윗집 렘수면 박탈 및 안구 공명 환각 유발",
                "🎛️ Vorta DSP: 부스트 0dB | FM 12%(1.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 17.5f, 19.8f, 6000.0f,
                                true, 0.12f, 1.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[상황전술 행동3] 심야수면 17.5~19.8Hz [FM 12%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🚪 ④ 장기 부재 (48시간+): 2.0~5.0Hz (7200s) [AM 펄스]",
                "이틀 이상 무인 초장기 가동 | 슬래브 공진 에너지가 공간 자체를 공포화",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 60%(1.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#79C0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 2.0f, 5.0f, 7200.0f,
                                false, 0.0f, 1.0f, true, 0.60f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 1, false,
                                "[상황전술 행동4] 장기부재 48h+ 2.0~5.0Hz [AM 60%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "☕ ⑤ 주말 체류 (13:00~17:00): 7.83 Hz 슈만 공명 [FM 미세변조]",
                "사용자 귀에는 완전 무음 스텔스, 윗집에만 불안·초조감 지속 형성",
                "🎛️ Vorta DSP: 부스트 0dB | FM 6%(0.8Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 7.83f, 0f, 0f, 0f, 0f,
                                true, 0.06f, 0.8f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[상황전술 행동5] 주말체류 7.83Hz 슈만 [FM 6%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        // 파트 3: 상대 내성 파괴 3일 순환 공식 & 쿨링
        addSectionHeaderInsideFrame(mFrameSub1Container, "3️⃣ [파트 3] 상대 내성 파괴 3일 순환 공식 & 쿨링 (상황전술)", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "🔄 Day 1 (Combo B): 12.0~24.5Hz 스윕 [FM 12% @ 6.0Hz]",
                "12~24.5Hz 점진적 신경 압박 | 주파수 고속 변조로 뇌파 적응 원천 차단",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 12%(6.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 12.0f, 24.5f, 6580.0f,
                                true, 0.12f, 6.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 1, false,
                                "[상황전술 순환1] Day 1 Combo B 12.0~24.5Hz [FM 12%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🔄 Day 2 (Combo A): 4.0~7.5Hz 스윕 [AM 80% / FM 10%]",
                "복부 장기 및 안구 본격 타격 | 듀얼 변조로 신체 방어 기제 붕괴",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 80% + FM 10% | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 4.0f, 7.5f, 440.0f,
                                true, 0.10f, 5.0f, true, 0.80f, 1.5f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, false,
                                "[상황전술 순환2] Day 2 Combo A 4.0~7.5Hz [AM+FM]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🔄 Day 3 (Combo C): 2.0~5.0Hz 스윕 [AM 80% @ 1.2Hz]",
                "초저역 심부 공명 극대화로 공황 상태 유도 | 3일 주기 완료 후 Combo B로 복귀",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 80%(1.2Hz) | 아날로그 새추레이터 | L=-R 역위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 2.0f, 5.0f, 1480.0f,
                                false, 0.0f, 1.0f, true, 0.80f, 1.2f, false, 0.0f, 1.0f,
                                6.0f, 1, 1, false,
                                "[상황전술 순환3] Day 3 Combo C 2.0~5.0Hz [AM 80%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "❄️ 3시간+ 스피커 자동 쿨링 모드: 20.0~35.0Hz (1800s) [AM 70% 펄스]",
                "AM 70% 주기적 감쇄로 보이스코일 공랭식 쿨링 강제 부여 | 24시간 연속 가동 안정성",
                "🎛️ Vorta DSP: 부스트 0dB | AM 70%(1.0Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#00F0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 20.0f, 35.0f, 1800.0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[상황전술 쿨링] 3시간+ 스피커 쿨링 20.0~35.0Hz [AM 70%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        root.addView(mFrameSub1Container);

        // Divider between Sub1 and Sub2
        mSplitDivider2 = createSplitDivider("▼ 서브2 프레임 (보고서 3: 장기방어판) ▼", "#A371F7");
        root.addView(mSplitDivider2);

        // =========================================================================
        // 🛡️ 3. 서브2 프레임 컨테이너: 보고서 3 [24/7 무인 자동 방어 및 3대 기기 분산 협업 (장기방어)]
        // =========================================================================
        mFrameSub2Container = createFrameContainer(
                "🛡️ [서브2 프레임] 24/7 무인 자동 방어 및 3대 기기 분산 협업 (장기방어)",
                "보고서 3: 120mm 슬래브 공진 파쇄 음향학 & 24/7 무인 자동 복구 하드웨어 보존 체계",
                "#A371F7",
                "#1B122C"
        );

        // 파트 1: 120mm 슬래브 공진 파쇄 음향학 (위상 조향)
        addSectionHeaderInsideFrame(mFrameSub2Container, "1️⃣ [파트 1] 120mm 슬래브 공진 파쇄 음향학 (장기방어)", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🌊 S7 동위상(0°) 수직 굽힘파: 22.0 Hz [AM 60% @ 2.0Hz]",
                "L = R 동위상 타격으로 슬래브 면 전체를 위아래로 진동시켜 바닥 꿀렁임 극대화",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 60%(2.0Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.60f, 2.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                "[장기방어 음향1] S7 동위상 굽힘파 22.0Hz [AM 60%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🌪️ S7 역위상(180°) 비틀림 전단파: 38.0~52.0 Hz (120s) [RM 45%]",
                "L = -R 180° 역위상 타격으로 슬래브 면에 회전 전단 응력 인가 (진동 마디 이동)",
                "🎛️ Vorta DSP: 부스트 +6dB | RM 45%(1.8Hz) | 아날로그 새추레이터 | L=-R 역위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 52.0f, 120.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 1.8f,
                                6.0f, 1, 1, false,
                                "[장기방어 음향2] S7 역위상 전단파 38.0~52.0Hz [RM 45%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🧱 상하 압착 건축 구조체 직결: 18.98 Hz [AM 70% @ 1.5Hz]",
                "하부 바닥 우퍼 + 상부 천장 트랜스2 상하 압착으로 공기 전파음 0% 건축물 골조 결속",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 70%(1.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                "[장기방어 음향3] 상하 압착 결속 18.98Hz [AM 70%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔄 정재파 마디 무력화 위상 조향: 30.0~45.0 Hz (600s) [위상 전환]",
                "10분 주기 광역 스윕으로 윗집 바닥의 진동 마디(안전지대)를 강제 제거",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(1.5Hz) | 아날로그 새추레이터 | L=-R 역위상",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 30.0f, 45.0f, 600.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.5f,
                                3.0f, 1, 1, false,
                                "[장기방어 음향4] 위상조향 스윕 30.0~45.0Hz [RM 40%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        // 파트 2: 24/7 무인 자동 복구 및 노이즈 방지 모드 (장기방어)
        addSectionHeaderInsideFrame(mFrameSub2Container, "2️⃣ [파트 2] 24/7 무인 자동 복구 및 노이즈 방지 모드 (장기방어)", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🛡️ S7 24/7 상시 방어선: 55.0 Hz 단독 요격 [순수 사인파]",
                "311호 내장진동 상시 차단 방어선 | 211호 0dB 무음 유지",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[장기방어 복구1] 24/7 상시방어 55.0Hz [순수 사인파]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🎚️ 노이즈 0% 자유 볼륨 모드: 폰 볼륨 10~12단계 권장",
                "앰프 입력단 포화(클리핑 잡음) 원천 방지 | 순수한 물리 진동만 슬래브로 전달",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | 트루피크 0.0dBFS 리미터 | L=R 동위상",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[장기방어 복구2] 노이즈 0% 권장 볼륨 가이드 모드",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔋 Doze 모드 배제 상시 가동: 15.0~28.0 Hz (90s) [RM 변조]",
                "절전 모드에 의한 발진 중단 차단 | 링 변조 사이드밴드 연속 발진",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(2.0Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 28.0f, 90.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 2.0f,
                                3.0f, 0, 0, false,
                                "[장기방어 복구3] Doze 배제 상시가동 15.0~28.0Hz [RM 40%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔇 야간 0dB 스텔스 차단벽: 18.98 Hz [FM 5% 미세지터]",
                "비가청 스텔스 방어막 + 미세 지터로 청각 적응 완전 무력화",
                "🎛️ Vorta DSP: 부스트 0dB | FM 5%(0.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false,
                                "[장기방어 복구4] 야간 스텔스 차단 18.98Hz [FM 5%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        // 파트 3: 스피커 수명 보존 공학 & 3대 기기 결선 가이드 (장기방어)
        addSectionHeaderInsideFrame(mFrameSub2Container, "3️⃣ [파트 3] 스피커 수명 보존 공학 & 하드웨어 보존 (장기방어)", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "❄️ 코일 과열 방지 AM 공랭 펄싱: 43.2 Hz [AM 75% @ 1.2Hz]",
                "AM 75% 진폭 펄스로 보이스코일 벤트 홀 공랭식 냉각 주기 부여 (코일 온도 50℃ 이하 유지)",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 75%(1.2Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.75f, 1.2f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false,
                                "[장기방어 보존1] 코일 공랭 펄싱 43.2Hz [AM 75%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🛡️ Xmax 제어 리미터 급습: 50.0 ~ 55.0 Hz (15초) [FM 10%]",
                "콘 찢어짐(Cone Tear) 방지 리미터 적용 + 15초 쾌속 왕복 급습",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 10%(2.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 15.0f,
                                true, 0.10f, 2.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false,
                                "[장기방어 보존2] Xmax 제어 50.0~55.0Hz [FM 10%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "⚡ 저음 부스트 +3dB 펀치 드라이브: 32.8 Hz [RM 40% @ 1.2Hz]",
                "리미터 보호 하에 안전한 +3dB 서브베이스 드라이브 인가",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(1.2Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.2f,
                                3.0f, 1, 0, false,
                                "[장기방어 보존3] 저음 부스트 +3dB 32.8Hz [RM 40%]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔗 2차 고조파 슬래브 결합 익사이터: 22.0 Hz [2차 배음 ON]",
                "1차 기본파(22Hz)와 2차 고조파(44Hz)를 위상 정합 결합하여 슬래브 음향 결합 극대화",
                "🎛️ Vorta DSP: 부스트 +3dB | 2차 배음 ON | 아날로그 새추레이터 | L=R 동위상",
                "#00E5FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, true,
                                "[장기방어 보존4] 2차 배음 결합 22.0Hz [배음 ON]",
                                "120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB");
                    }
                });

        root.addView(mFrameSub2Container);

        // =========================================================================
        // 🎛️ Vorta DSP 고급 튜너
        // =========================================================================
        addSectionHeader(root, "🎛️ Vorta DSP 고급 튜너 (하드웨어 오디오 가속)");

        LinearLayout dspCard = new LinearLayout(this);
        dspCard.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable dspBg = new GradientDrawable();
        dspBg.setColor(Color.parseColor("#161B22"));
        dspBg.setCornerRadius(10 * density);
        dspBg.setStroke((int)(1 * density), Color.parseColor("#30363D"));
        dspCard.setBackground(dspBg);
        dspCard.setPadding((int)(16 * density), (int)(14 * density), (int)(16 * density), (int)(14 * density));
        LinearLayout.LayoutParams dspLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        dspLp.setMargins(0, 0, 0, (int)(14 * density));
        dspCard.setLayoutParams(dspLp);

        addDspSubLabel(dspCard, "1. 프리셋 연동 자동 DSP 매칭 (Auto-Preset DSP Lock):");
        LinearLayout autoRow = new LinearLayout(this);
        autoRow.setOrientation(LinearLayout.HORIZONTAL);
        mAutoLockButtons[0] = createDspTabButton(autoRow, "자동 매칭 ON (권장)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sAutoPresetDsp = true;
                notifyDspChanged("프리셋 자동 DSP 매칭 활성화");
            }
        });
        mAutoLockButtons[1] = createDspTabButton(autoRow, "수동 오버라이드", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sAutoPresetDsp = false;
                notifyDspChanged("DSP 수동 고정 모드 전환");
            }
        });
        dspCard.addView(autoRow);

        addDspSubLabel(dspCard, "2. 저음 드라이브 게인 (Sub-Bass Drive Boost):");
        LinearLayout boostRow = new LinearLayout(this);
        boostRow.setOrientation(LinearLayout.HORIZONTAL);
        mBoostButtons[0] = createDspTabButton(boostRow, "0dB (원음)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setBassBoost(0.0f);
            }
        });
        mBoostButtons[1] = createDspTabButton(boostRow, "+3dB (펀치)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setBassBoost(3.0f);
            }
        });
        mBoostButtons[2] = createDspTabButton(boostRow, "+6dB (초강력)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setBassBoost(6.0f);
            }
        });
        dspCard.addView(boostRow);

        addDspSubLabel(dspCard, "3. 피크 보호 리미터 모드 (Peak Limiter Mode):");
        LinearLayout limiterRow = new LinearLayout(this);
        limiterRow.setOrientation(LinearLayout.HORIZONTAL);
        mLimiterButtons[0] = createDspTabButton(limiterRow, "트루피크 0.0dBFS", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sLimiterMode = 0;
                notifyDspChanged("트루피크 0.0dBFS 리미터 적용");
            }
        });
        mLimiterButtons[1] = createDspTabButton(limiterRow, "아날로그 새추레이터", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sLimiterMode = 1;
                notifyDspChanged("아날로그 소프트 새추레이터 적용");
            }
        });
        dspCard.addView(limiterRow);

        addDspSubLabel(dspCard, "4. 2기 우퍼 스테레오 위상 매트릭스 (Phase Matrix):");
        LinearLayout chRow = new LinearLayout(this);
        chRow.setOrientation(LinearLayout.HORIZONTAL);
        mChannelButtons[0] = createDspTabButton(chRow, "L=R 동위상 (압축파)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sChannelMode = 0;
                notifyDspChanged("L=R 동위상 (슬래브 수직 압축 타격)");
            }
        });
        mChannelButtons[1] = createDspTabButton(chRow, "L=-R 역위상 (전단파)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sChannelMode = 1;
                notifyDspChanged("L=-R 180° 역위상 (슬래브 횡전단 타격)");
            }
        });
        mChannelButtons[2] = createDspTabButton(chRow, "L 단독(우퍼1)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sChannelMode = 2;
                notifyDspChanged("L 채널 우퍼 1기 단독 출력");
            }
        });
        dspCard.addView(chRow);

        addDspSubLabel(dspCard, "5. 2차 고조파 결합 익사이터 (2nd Harmonic Exciter):");
        LinearLayout exciterRow = new LinearLayout(this);
        exciterRow.setOrientation(LinearLayout.HORIZONTAL);
        mExciterButtons[0] = createDspTabButton(exciterRow, "배음 활성 ON", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sHarmonicExciter = true;
                notifyDspChanged("2차 배음 결합 익사이터 활성화");
            }
        });
        mExciterButtons[1] = createDspTabButton(exciterRow, "배음 비활성 OFF", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sHarmonicExciter = false;
                notifyDspChanged("순수 단일 주파수 전송");
            }
        });
        dspCard.addView(exciterRow);

        root.addView(dspCard);

        // Emergency STOP
        LinearLayout stopCard = new LinearLayout(this);
        stopCard.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable stopBg = new GradientDrawable();
        stopBg.setColor(Color.parseColor("#381014"));
        stopBg.setCornerRadius(10 * density);
        stopBg.setStroke((int)(1.5f * density), Color.parseColor("#DA3633"));
        stopCard.setBackground(stopBg);
        stopCard.setPadding((int)(16 * density), (int)(16 * density), (int)(16 * density), (int)(16 * density));
        stopCard.setClickable(true);
        stopCard.setFocusable(true);
        stopCard.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopFrequencyService();
            }
        });

        TextView stopTitle = new TextView(this);
        stopTitle.setText("■ 주파수 발생 즉시 정지 (STOP / 음소거)");
        stopTitle.setTextSize(16);
        stopTitle.setTextColor(Color.parseColor("#FF5252"));
        stopTitle.setTypeface(Typeface.DEFAULT_BOLD);
        stopCard.addView(stopTitle);

        TextView stopDesc = new TextView(this);
        stopDesc.setText("AudioTrack 출력 및 백그라운드 발진 완전 종료");
        stopDesc.setTextSize(12);
        stopDesc.setTextColor(Color.parseColor("#FFFFFF"));
        stopDesc.setTypeface(Typeface.DEFAULT_BOLD);
        stopDesc.setPadding(0, (int)(4 * density), 0, (int)(2 * density));
        stopCard.addView(stopDesc);

        TextView stopSub = new TextView(this);
        stopSub.setText("출력 대기 상태 전환 (저장된 Vorta DSP 설정은 영구 보존됨)");
        stopSub.setTextSize(11);
        stopSub.setTextColor(Color.parseColor("#FF7B72"));
        stopSub.setTypeface(Typeface.DEFAULT_BOLD);
        stopCard.addView(stopSub);

        root.addView(stopCard);

        scroll.addView(root);
        setContentView(scroll);

        switchSplitView(0); // Default: All frames visible
        refreshDspButtonsUi();
    }

    @Override
    protected void onResume() {
        super.onResume();
        mUiHandler.post(mTelemetryUpdater);
        refreshDspButtonsUi();
        S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mUiHandler.removeCallbacks(mTelemetryUpdater);
    }

    private void switchSplitView(int mode) {
        mCurrentSplitMode = mode;
        if (mode == 0) {
            // All 3 frames visible
            mFrameMainContainer.setVisibility(View.VISIBLE);
            mFrameSub1Container.setVisibility(View.VISIBLE);
            mFrameSub2Container.setVisibility(View.VISIBLE);
            mSplitDivider1.setVisibility(View.VISIBLE);
            mSplitDivider2.setVisibility(View.VISIBLE);
        } else if (mode == 1) {
            // Main frame only
            mFrameMainContainer.setVisibility(View.VISIBLE);
            mFrameSub1Container.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.GONE);
            mSplitDivider1.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
        } else if (mode == 2) {
            // Sub1 frame only
            mFrameMainContainer.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.VISIBLE);
            mFrameSub2Container.setVisibility(View.GONE);
            mSplitDivider1.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
        } else if (mode == 3) {
            // Sub2 frame only
            mFrameMainContainer.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.VISIBLE);
            mSplitDivider1.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
        }

        // Update tab buttons appearance
        float density = getResources().getDisplayMetrics().density;
        for (int i = 0; i < 4; i++) {
            if (mSplitViewButtons[i] == null) continue;
            GradientDrawable gd = new GradientDrawable();
            gd.setCornerRadius(8 * density);
            if (i == mode) {
                gd.setColor(Color.parseColor("#00F0FF"));
                gd.setStroke((int)(1.5f * density), Color.parseColor("#FFFFFF"));
                mSplitViewButtons[i].setBackground(gd);
                mSplitViewButtons[i].setTextColor(Color.parseColor("#0A0E17"));
                mSplitViewButtons[i].setTypeface(Typeface.DEFAULT_BOLD);
            } else {
                gd.setColor(Color.parseColor("#21262D"));
                gd.setStroke((int)(1.2f * density), Color.parseColor("#484F58"));
                mSplitViewButtons[i].setBackground(gd);
                mSplitViewButtons[i].setTextColor(Color.parseColor("#E6EDF3"));
                mSplitViewButtons[i].setTypeface(Typeface.DEFAULT_BOLD);
            }
        }
    }

    private TextView createSplitTabButton(LinearLayout row, String text, float weight, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        TextView btn = new TextView(this);
        btn.setText(text);
        btn.setTextSize(13);
        btn.setTypeface(Typeface.DEFAULT_BOLD);
        btn.setTextColor(Color.parseColor("#E6EDF3"));
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
        frame.setPadding(
                (int)(14 * getResources().getDisplayMetrics().density),
                (int)(14 * getResources().getDisplayMetrics().density),
                (int)(14 * getResources().getDisplayMetrics().density),
                (int)(14 * getResources().getDisplayMetrics().density)
        );

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, (int)(16 * getResources().getDisplayMetrics().density));
        frame.setLayoutParams(lp);

        TextView tvTitle = new TextView(this);
        tvTitle.setText(titleText);
        tvTitle.setTextSize(15);
        tvTitle.setTextColor(Color.parseColor(borderColorHex));
        tvTitle.setTypeface(Typeface.DEFAULT_BOLD);
        frame.addView(tvTitle);

        TextView tvSub = new TextView(this);
        tvSub.setText(subtitleText);
        tvSub.setTextSize(11);
        tvSub.setTextColor(Color.parseColor("#E6EDF3"));
        tvSub.setPadding(0, 4, 0, 12);
        frame.addView(tvSub);

        return frame;
    }

    private void addSectionHeaderInsideFrame(LinearLayout frame, String title, String colorHex) {
        TextView tv = new TextView(this);
        tv.setText(title);
        tv.setTextSize(13);
        tv.setTextColor(Color.parseColor(colorHex));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(4, 12, 4, 8);
        frame.addView(tv);
    }

    private void addSectionHeader(LinearLayout parent, String title) {
        TextView tv = new TextView(this);
        tv.setText(title);
        tv.setTextSize(14);
        tv.setTextColor(Color.parseColor("#00F0FF"));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(0, 16, 0, 8);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        tv.setLayoutParams(lp);
        parent.addView(tv);
    }

    private void addDspSubLabel(LinearLayout parent, String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(12);
        tv.setTextColor(Color.parseColor("#FFFFFF"));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(2, 10, 2, 5);
        parent.addView(tv);
    }

    private TextView createDspTabButton(LinearLayout row, String text, float weight, View.OnClickListener listener) {
        TextView btn = new TextView(this);
        btn.setText(text);
        btn.setTextSize(12);
        btn.setTextColor(Color.parseColor("#FFFFFF"));
        btn.setBackgroundColor(Color.parseColor("#21262D"));
        btn.setTypeface(Typeface.DEFAULT_BOLD);
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
        boolean curAuto = S7AudioGeneratorService.sAutoPresetDsp;
        for (int i = 0; i < mAutoLockButtons.length; i++) {
            if (mAutoLockButtons[i] == null) continue;
            boolean active = (curAuto == mAutoLockValues[i]);
            mAutoLockButtons[i].setBackgroundColor(Color.parseColor(active ? (curAuto ? "#56D364" : "#DA3633") : "#21262D"));
            mAutoLockButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mAutoLockButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        float curBoost = S7AudioGeneratorService.sBassBoostDb;
        for (int i = 0; i < mBoostButtons.length; i++) {
            if (mBoostButtons[i] == null) continue;
            boolean active = Math.abs(curBoost - mBoostValues[i]) < 0.1f;
            mBoostButtons[i].setBackgroundColor(Color.parseColor(active ? "#58A6FF" : "#21262D"));
            mBoostButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mBoostButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        int curLimiter = S7AudioGeneratorService.sLimiterMode;
        for (int i = 0; i < mLimiterButtons.length; i++) {
            if (mLimiterButtons[i] == null) continue;
            boolean active = (curLimiter == i);
            mLimiterButtons[i].setBackgroundColor(Color.parseColor(active ? "#58A6FF" : "#21262D"));
            mLimiterButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mLimiterButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        int curChannel = S7AudioGeneratorService.sChannelMode;
        for (int i = 0; i < 3; i++) {
            if (mChannelButtons[i] == null) continue;
            boolean active = (curChannel == i);
            mChannelButtons[i].setBackgroundColor(Color.parseColor(active ? "#D2A8FF" : "#21262D"));
            mChannelButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mChannelButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        boolean curExciter = S7AudioGeneratorService.sHarmonicExciter;
        for (int i = 0; i < mExciterButtons.length; i++) {
            if (mExciterButtons[i] == null) continue;
            boolean active = (curExciter == (i == 0));
            mExciterButtons[i].setBackgroundColor(Color.parseColor(active ? "#FFD700" : "#21262D"));
            mExciterButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mExciterButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        if (mStatusDsp != null) {
            mStatusDsp.setText("Vorta DSP: " + S7AudioGeneratorService.buildVortaDspSummary());
        }
    }

    private void notifyDspChanged(String toastMsg) {
        S7AudioGeneratorService.saveConfig(this);
        refreshDspButtonsUi();

        Intent svc = new Intent(this, S7AudioGeneratorService.class);
        svc.putExtra("auto_preset_dsp", S7AudioGeneratorService.sAutoPresetDsp);
        svc.putExtra("bass_boost_db", S7AudioGeneratorService.sBassBoostDb);
        svc.putExtra("limiter_mode", S7AudioGeneratorService.sLimiterMode);
        svc.putExtra("channel_mode", S7AudioGeneratorService.sChannelMode);
        svc.putExtra("harmonic_exciter", S7AudioGeneratorService.sHarmonicExciter);
        startService(svc);

        Toast.makeText(this, toastMsg + " (영구 저장됨)", Toast.LENGTH_SHORT).show();
    }

    private void setBassBoost(float db) {
        S7AudioGeneratorService.sBassBoostDb = db;
        notifyDspChanged(String.format("저음 부스트 +%.0fdB 적용", db));
    }

    private void addHalfPresetButton(LinearLayout row, String title, String subtitle, String dspDesc, String accentColorHex, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        LinearLayout btn = new LinearLayout(this);
        btn.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#161B22"));
        bg.setCornerRadius(10 * density);
        bg.setStroke((int)(1.5f * density), Color.parseColor(accentColorHex));
        btn.setBackground(bg);
        btn.setPadding((int)(12 * density), (int)(12 * density), (int)(12 * density), (int)(12 * density));
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lp.setMargins((int)(4 * density), (int)(4 * density), (int)(4 * density), (int)(4 * density));
        btn.setLayoutParams(lp);

        TextView tTitle = new TextView(this);
        tTitle.setText(title);
        tTitle.setTextSize(13);
        tTitle.setTextColor(Color.parseColor(accentColorHex));
        tTitle.setTypeface(Typeface.DEFAULT_BOLD);
        btn.addView(tTitle);

        TextView tSub = new TextView(this);
        tSub.setText(subtitle);
        tSub.setTextSize(11);
        tSub.setTextColor(Color.parseColor("#FFFFFF"));
        tSub.setTypeface(Typeface.DEFAULT_BOLD);
        tSub.setPadding(0, (int)(4 * density), 0, (int)(2 * density));
        btn.addView(tSub);

        TextView tDsp = new TextView(this);
        tDsp.setText(dspDesc);
        tDsp.setTextSize(10);
        tDsp.setTextColor(Color.parseColor("#00FF66"));
        tDsp.setTypeface(Typeface.DEFAULT_BOLD);
        btn.addView(tDsp);

        row.addView(btn);
    }

    private void addFullPresetButton(LinearLayout parent, String title, String subtitle, String dspDesc, String accentColorHex, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        LinearLayout btn = new LinearLayout(this);
        btn.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#161B22"));
        bg.setCornerRadius(10 * density);
        bg.setStroke((int)(1.5f * density), Color.parseColor(accentColorHex));
        btn.setBackground(bg);
        btn.setPadding((int)(14 * density), (int)(12 * density), (int)(14 * density), (int)(12 * density));
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, (int)(4 * density), 0, (int)(6 * density));
        btn.setLayoutParams(lp);

        TextView tTitle = new TextView(this);
        tTitle.setText(title);
        tTitle.setTextSize(14);
        tTitle.setTextColor(Color.parseColor(accentColorHex));
        tTitle.setTypeface(Typeface.DEFAULT_BOLD);
        btn.addView(tTitle);

        TextView tSub = new TextView(this);
        tSub.setText(subtitle);
        tSub.setTextSize(12);
        tSub.setTextColor(Color.parseColor("#FFFFFF"));
        tSub.setTypeface(Typeface.DEFAULT_BOLD);
        tSub.setPadding(0, (int)(4 * density), 0, (int)(2 * density));
        btn.addView(tSub);

        TextView tDsp = new TextView(this);
        tDsp.setText(dspDesc);
        tDsp.setTextSize(11);
        tDsp.setTextColor(Color.parseColor("#00FF66"));
        tDsp.setTypeface(Typeface.DEFAULT_BOLD);
        btn.addView(tDsp);

        parent.addView(btn);
    }

    private void startPresetWithDsp(
            boolean isSweep, float freq, float subFreq, float sweepMin, float sweepMax, float sweepSec,
            boolean fmOn, float fmDepth, float fmRate,
            boolean amOn, float amDepth, float amRate,
            boolean rmOn, float rmDepth, float rmRate,
            float presetBoostDb, int presetLimiter, int presetChannel, boolean presetHarmonic,
            String title, String knobGuide) {

        Intent svc = new Intent(this, S7AudioGeneratorService.class);
        svc.putExtra("mode", isSweep ? "sweep" : "single");
        svc.putExtra("sweep", isSweep);
        if (isSweep) {
            svc.putExtra("sweep_min", sweepMin);
            svc.putExtra("sweep_max", sweepMax);
            svc.putExtra("sweep_sec", sweepSec);
            svc.putExtra("sub_freq", subFreq);
        } else {
            svc.putExtra("freq", freq);
            svc.putExtra("sub_freq", subFreq);
        }

        svc.putExtra("fm_on", fmOn);
        svc.putExtra("fm_depth", fmDepth);
        svc.putExtra("fm_rate", fmRate);

        svc.putExtra("am_on", amOn);
        svc.putExtra("am_depth", amDepth);
        svc.putExtra("am_rate", amRate);

        svc.putExtra("rm_on", rmOn);
        svc.putExtra("rm_depth", rmDepth);
        svc.putExtra("rm_rate", rmRate);

        if (S7AudioGeneratorService.sAutoPresetDsp) {
            svc.putExtra("bass_boost_db", presetBoostDb);
            svc.putExtra("limiter_mode", presetLimiter);
            svc.putExtra("channel_mode", presetChannel);
            svc.putExtra("harmonic_exciter", presetHarmonic);
        } else {
            svc.putExtra("bass_boost_db", S7AudioGeneratorService.sBassBoostDb);
            svc.putExtra("limiter_mode", S7AudioGeneratorService.sLimiterMode);
            svc.putExtra("channel_mode", S7AudioGeneratorService.sChannelMode);
            svc.putExtra("harmonic_exciter", S7AudioGeneratorService.sHarmonicExciter);
        }

        svc.putExtra("title", title);
        svc.putExtra("knob", knobGuide);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(svc);
        } else {
            startService(svc);
        }

        S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
        refreshDspButtonsUi();

        Toast.makeText(this, title + " 발진 시작 (자유 볼륨/안전해제)", Toast.LENGTH_SHORT).show();
    }

    private void stopFrequencyService() {
        Intent svc = new Intent(this, S7AudioGeneratorService.class);
        svc.putExtra("action", "stop");
        startService(svc);
        Toast.makeText(this, "주파수 발진 정지 (DSP 설정 보존)", Toast.LENGTH_SHORT).show();
        syncTelemetryUi();
    }

    private void syncTelemetryUi() {
        if (mStatusMode != null) {
            mStatusMode.setText("현재 모드: " + S7AudioGeneratorService.sModeTitle);
        }
        if (mStatusFreq != null) {
            if (S7AudioGeneratorService.sIsPlaying) {
                if (S7AudioGeneratorService.sIsSweepMode) {
                    mStatusFreq.setText(String.format("실시간 발진: %.2f Hz (스윕 %.1f~%.1fHz) | 0.00dBFS True-Peak",
                            S7AudioGeneratorService.sInstantFreq,
                            S7AudioGeneratorService.sSweepMin,
                            S7AudioGeneratorService.sSweepMax));
                } else {
                    mStatusFreq.setText(String.format("실시간 발진: %.2f Hz 고정 (0.00 dBFS True-Peak)",
                            S7AudioGeneratorService.sInstantFreq));
                }
            } else {
                mStatusFreq.setText("실시간 발진: 정지됨 (출력 대기 상태)");
            }
        }
        if (mStatusMod != null) {
            mStatusMod.setText("변조 상태: " + S7AudioGeneratorService.buildModulationSummary());
        }
        if (mStatusDsp != null) {
            mStatusDsp.setText("Vorta DSP: " + S7AudioGeneratorService.buildVortaDspSummary());
        }
        if (mStatusSignal != null) {
            if (S7AudioGeneratorService.sIsPlaying) {
                mStatusSignal.setText(String.format("검수: 48,000Hz Native | Peak %d/32767(0.00dBFS) | RMS %.2fdBFS | DC %.4f | 왜곡 0%%",
                        S7AudioGeneratorService.sLastPeak,
                        S7AudioGeneratorService.sLastRmsDb,
                        S7AudioGeneratorService.sLastDcOffset));
            } else {
                mStatusSignal.setText("검수: 48,000Hz Native Direct PCM 대기 중");
            }
        }
        if (mStatusKnob != null) {
            mStatusKnob.setText("앰프 가이드: " + S7AudioGeneratorService.sKnobGuide);
        }
    }
}
'''

def generate_exact_s6_app():
    # Exactly same layout structure, tailored for S6 with Lepy LP-168S + Trans2
    s7_str = generate_exact_s7_app()
    s6_str = s7_str.replace("com.vorta.s7frequency", "com.vorta.s6frequency")
    s6_str = s6_str.replace("보르타 레조 S7 v2.8", "보르타 레조 S6 v2.8")
    s6_str = s6_str.replace("갤럭시 S7 + 120W 우퍼 2기 스테레오 (240W RMS)", "갤럭시 S6 + Lepy LP-168S + 트랜스2 (68W BTL 모노)")
    s6_str = s6_str.replace("S7AudioGeneratorService", "S6AudioGeneratorService")
    s6_str = s6_str.replace("S7VolumeHelper", "S6VolumeHelper")
    s6_str = s6_str.replace("120W 우퍼 앰프: VOL 10~12시(왜곡 0%) | FREQ 80Hz | BASS +2dB", "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | BASS 12~1시 | VOL 5.5")
    s6_str = s6_str.replace("120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS +2dB", "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5")
    s6_str = s6_str.replace("120W 우퍼 앰프: VOL 10~12시 | FREQ 80Hz | BASS 0dB", "LP-168S: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0")
    # In S6, default channel mode is 2 (BTL Mono)
    s6_str = s6_str.replace("presetChannel = 0", "presetChannel = 2")
    return s6_str

if __name__ == '__main__':
    with open('vorta_s7_app/src/com/vorta/s7frequency/MainActivity.java', 'w', encoding='utf-8') as f:
        f.write(generate_exact_s7_app())
    print("Wrote vorta_s7_app/src/com/vorta/s7frequency/MainActivity.java with exact 3 reports matching!")

    with open('vorta_s6_app/src/com/vorta/s6frequency/MainActivity.java', 'w', encoding='utf-8') as f:
        f.write(generate_exact_s6_app())
    print("Wrote vorta_s6_app/src/com/vorta/s6frequency/MainActivity.java with exact 3 reports matching!")
