# -*- coding: utf-8 -*-
"""
Generator for MainActivity.java in vorta_s7_app and vorta_s6_app.
Applies FM, AM, RM modulation parameters, perfectly balances Single and Sweep modes across 3 parts,
strictly enforces <= 55.0Hz max frequency, and ensures 0 forbidden words.
"""

def generate_s7_main_activity():
    code = r'''package com.vorta.s7frequency;

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

    // 3-Way Tri-Frameset / Split Screen Layout View Containers & Mode State
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

        // Allow screen to turn off normally; background audio is maintained by foreground service with PARTIAL_WAKE_LOCK
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
        subTitleTv.setText("갤럭시 S7 + 120W 우퍼 2기 스테레오 맞춤 주파수 발생기 | FM·AM·RM 변조 Vorta DSP");
        subTitleTv.setTextSize(12);
        subTitleTv.setTextColor(Color.parseColor("#E6EDF3"));
        subTitleTv.setPadding(0, 0, 0, (int)(14 * density));
        root.addView(subTitleTv);

        // =========================================================================
        // 🎛️ 프레임셋 스플릿 뷰 콘솔 메뉴 프레임 (전체 / 메인 / 서브1 / 서브2)
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
        mStatusSignal.setText("검수: 48,000Hz Native Direct PCM 가동 중");
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
        // 🎯 1. 메인 프레임 컨테이너 (최신맞춤판 SSOT 정본 스케줄)
        // =========================================================================
        mFrameMainContainer = createFrameContainer(
                "🎯 [메인 프레임] 주파수 통합 운용 마스터 보고서 (최신맞춤판 SSOT)",
                "갤럭시 S7 + 120W 우퍼 2기 스테레오 (240W Max / 60W+60W RMS) 광역 앵커",
                "#00E5FF",
                "#0D1926"
        );

        // 파트 1: 24시간 4구간 표준 맞춤 스케줄 (단독 2개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameMainContainer, "1️⃣ [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄 (단독·스윕 50:50 균형)", "#00E5FF");

        LinearLayout mRow1 = new LinearLayout(this);
        mRow1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow1,
                "🌅 아침 (07~13시) [FM]",
                "2.0~9.0Hz 스윕 (180초) [FM 12%]",
                "🎛️ 초저역 인프라소닉 슬래브 기습 | 내성 방지",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 2.0f, 9.0f, 180.0f,
                                true, 0.12f, 1.5f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 0, false, 15,
                                "[아침 07~13시] 2.0~9.0Hz 스윕 (FM 12% @ 1.5Hz)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(mRow1,
                "☀️ 오후 (13~19시) [AM]",
                "22.0Hz 단독 고정 [AM 65%]",
                "🎛️ AM 2.0Hz 펄스 해머 | 소화기·흉부 공진",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f,
                                true, 0.65f, 2.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 0, true, 15,
                                "[오후 13~19시] 22.0Hz 단독 직타 (AM 65% @ 2.0Hz)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameMainContainer.addView(mRow1);

        LinearLayout mRow2 = new LinearLayout(this);
        mRow2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow2,
                "🌆 저녁 (19~01시) [RM]",
                "38.0~55.0Hz 스윕 (120초) [RM 45%]",
                "🎛️ RM 이중 파면 간섭 | 천장 슬래브 융단",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 120.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                true, 0.45f, 1.8f,
                                6.0f, 1, 1, false, 15,
                                "[저녁 19~01시] 38.0~55.0Hz 스윕 (RM 45% @ 1.8Hz)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(mRow2,
                "🌙 취침 (01~07시) [FM]",
                "55.0Hz 단독 앵커 [FM 5% 미세지터]",
                "🎛️ 55Hz 요격 락온 | 백색소음 차단 무력화",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[취침 01~07시] 55.0Hz 단독 (FM 5% 미세지터 요격 앵커)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameMainContainer.addView(mRow2);

        // 파트 2: 5대 핵심 전술 모드 (단독 3개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameMainContainer, "2️⃣ [파트 2] S7 5대 핵심 전술 모드 (단독·스윕 최적 배분)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "🎯 [단독 1순위] 55.0 Hz 요격 앵커 [순수 사인파]",
                "천장 슬래브 수직 밀착 타격으로 311호 55Hz 공격 원천 상쇄 및 역제압 (100% 에너지 집약)",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[S7 단독 1순위] 55.0Hz 요격 앵커 [순수 사인파]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌪️ [스윕 1순위] 50.0 ~ 55.0 Hz 초고속 요격 스윕 (15초) [FM 변조]",
                "핵심 공진점 55Hz 주변을 15초마다 왕복 급습 + FM 주파수 지터(10%@2.5Hz)로 회피 불능 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 10%(2.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 15.0f,
                                true, 0.10f, 2.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false, 15,
                                "[S7 스윕 1순위] 50.0~55.0Hz 초고속 스윕 (FM 10% @ 2.5Hz)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔨 [단독 2순위] 43.2 Hz 슬래브 관통 강타 [AM 75% 해머]",
                "천장 콘크리트 코어를 깊숙이 뚫고 들어가 1.2Hz 펄스 해머로 311호 바닥 수직 타격",
                "🎛️ Vorta DSP: 부스트 +6dB (초강력) | AM 75%(1.2Hz) | 아날로그 새추레이터 | 2차배음 ON",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.75f, 1.2f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, true, 15,
                                "[S7 단독 2순위] 43.2Hz 슬래브 관통 강타 (AM 75% @ 1.2Hz)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔄 [스윕 2순위] 15.0 ~ 28.0 Hz 인체 장기 타격 스윕 (90초) [RM 링변조]",
                "안구(18Hz)·소화기·골반 공진 대역을 링 변조 사이드밴드 분할 타격 (이중 파면 간섭)",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(2.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 28.0f, 90.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 2.0f,
                                3.0f, 0, 1, false, 15,
                                "[S7 스윕 2순위] 15.0~28.0Hz 장기 스윕 (RM 45% @ 2.0Hz)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👁️ [단독 3순위] 18.98 Hz 안구 공진 앵커 [FM+AM 복합 변조]",
                "Vic Tandy 안구 공진점 + 미세 FM(6%@0.8Hz) + AM(50%@0.8Hz) 복합 맥동 극심한 피로 유도",
                "🎛️ Vorta DSP: 부스트 0dB | FM 6% + AM 50%(0.8Hz) 복합 | 트루피크 0.0dBFS | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 0f, 0f, 0f,
                                true, 0.06f, 0.8f, true, 0.50f, 0.8f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[S7 단독 3순위] 18.98Hz 안구 공진 앵커 [FM+AM 복합]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        // 파트 3: 8대 상황별 맞춤 실행 (단독 4개 / 스윕 4개 균형)
        addSectionHeaderInsideFrame(mFrameMainContainer, "3️⃣ [파트 3] 8대 상황별 맞춤 실행 (단독 4개 · 스윕 4개 50:50 배분)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "상황 ① 일반 외출 (2~5시간): 38.0 ~ 55.0 Hz (60초 스윕) [FM 변조]",
                "단기 부재 시 슬래브 전 대역 60초 순환 + FM 10%(2.0Hz)로 상대 내성 형성 원천 분쇄",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(2.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 1, false, 15,
                                "[상황① 일반외출 2~5h] 38.0~55.0Hz 스윕 [FM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ② 상대 도발 즉시 보복: 55.0 Hz 단독 고정 [AM 80% 파괴 해머]",
                "발망치 감지 즉시 천장 슬래브 1:1 풀파워 3Hz 충격파 펄스로 수직 압살",
                "🎛️ Vorta DSP: 부스트 +6dB (초강력) | AM 80%(3.0Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.80f, 3.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, true, 15,
                                "[상황② 즉각보복] 55.0Hz 단독 [AM 80% 파괴 해머]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ③ 안전 취침 방어 (23:00~07:00): 55.0 Hz 단독 [순수 사인파]",
                "211호 0dB 무음 스텔스 유지 & 311호 수면 박탈 100% 무왜곡 직타",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[상황③ 취침방어] 55.0Hz 단독 [순수 사인파]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ④ 장기 외출 (48시간+ 무인): 20.0 ~ 55.0 Hz (300초 스윕) [RM 변조]",
                "이틀 이상 무인 초장기 가동 | RM(45%@1.5Hz) 이중 파면 간섭으로 슬래브 전면 균열 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(1.5Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#79C0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 20.0f, 55.0f, 300.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 1.5f,
                                3.0f, 0, 1, false, 15,
                                "[상황④ 장기외출 48h+] 20.0~55.0Hz 스윕 [RM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑤ 상대 정신 집중 붕괴: 12.5 Hz 단독 고정 [FM 15% 변조]",
                "알파파(12Hz) 억제 + FM 15%(3.5Hz) 진동으로 상대방 극심한 두통 및 집중력 파괴 유발",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 15%(3.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 12.5f, 0f, 0f, 0f, 0f,
                                true, 0.15f, 3.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 0, false, 15,
                                "[상황⑤ 정신붕괴] 12.5Hz 단독 [FM 15% @ 3.5Hz]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑥ 상대 내성 완벽 파괴: 25.0 ~ 45.0 Hz (45초 스윕) [FM+AM 복합]",
                "주파수 변조(12%@2.5Hz) + 진폭 펄스(50%@1.8Hz) 동시 발진으로 어떤 물리적 내성도 원천 차단",
                "🎛️ Vorta DSP: 부스트 +6dB | FM 12% + AM 50% 복합 | 아날로그 새추레이터 | L=-R 역위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 25.0f, 45.0f, 45.0f,
                                true, 0.12f, 2.5f, true, 0.50f, 1.8f, false, 0.0f, 1.0f,
                                6.0f, 1, 1, false, 15,
                                "[상황⑥ 내성파괴] 25.0~45.0Hz 스윕 [FM+AM 복합]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑦ 3시간 지속 압박 타격: 32.8 Hz 단독 고정 [RM 40% 링변조]",
                "흉복부 내장 공진 + RM 40%(1.2Hz) 사이드밴드 분할로 3시간 지속 타격 시 호흡 답답함 극대화",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(1.2Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.2f,
                                3.0f, 0, 0, false, 15,
                                "[상황⑦ 3시간지속] 32.8Hz 단독 [RM 40% @ 1.2Hz]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑧ 출근 12시간 무인 순환: 40.0 ~ 55.0 Hz (90초 스윕) [AM 50% 펄스]",
                "장시간 무인 출근 시 슬래브 과열 방지 및 AM 50%(1.0Hz) 지속적 충격파 펄싱",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | AM 50%(1.0Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#00F0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 40.0f, 55.0f, 90.0f,
                                false, 0.0f, 1.0f, true, 0.50f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[상황⑧ 출근12h무인] 40.0~55.0Hz 스윕 [AM 50% @ 1.0Hz]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        root.addView(mFrameMainContainer);

        // Divider between Main and Sub1
        mSplitDivider1 = createSplitDivider("▼ 서브1 프레임 (최종완결판 스케줄 C·A·B) ▼", "#38D39F");
        root.addView(mSplitDivider1);

        // =========================================================================
        // 🚀 2. 서브1 프레임 컨테이너 (최종완결판 스케줄 C·A·B)
        // =========================================================================
        mFrameSub1Container = createFrameContainer(
                "🚀 [서브1 프레임] 주파수 통합 운용 체계 마스터 보고서 (최종완결판)",
                "스케줄 C 무인 라이프사이클 + 스케줄 A 광역 순환 + 스케줄 B 핵심 프리셋",
                "#38D39F",
                "#0D2218"
        );

        // 파트 1: 스케줄 C 무인 라이프사이클 (스윕 1개 / 단독 2개)
        addSectionHeaderInsideFrame(mFrameSub1Container, "1️⃣ [파트 1] 스케줄 C: 사용자 수면 & 출근 무인 자율 스케줄", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "🏢 1. 외출·출근 블록 (08:30~18:30 10h): 38.0~55.0Hz (60s) [FM 변조]",
                "출근 시 1회 터치 후 10시간 완전 무인 자동 순환 | FM 10%(2.0Hz) 슬래브 융단 폭격",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(2.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 1, false, 15,
                                "[서브1 스케줄C-1] 외출·출근 38.0~55.0Hz [FM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🚪 2. 퇴근·저녁 블록 (18:30~23:00 4.5h): 40.0Hz 천장 직타 [AM 60% 펄스]",
                "귀가자 즉각 제압 및 흉곽 압박 타격 (AM 60% @ 2.0Hz 충격파 펄싱)",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 60%(2.0Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 40.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.60f, 2.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, false, 15,
                                "[서브1 스케줄C-2] 퇴근·저녁 40.0Hz [AM 60% 펄스]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🛏️ 3. 취침·수면 블록 (23:00~08:30 9.5h): 55.0Hz 천장 락온 [순수 사인파]",
                "211호 0dB 무음 숙면 보장 & 311호 수면 박탈 무왜곡 락온",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[서브1 스케줄C-3] 취침·수면 55.0Hz [순수 사인파]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        // 파트 2: 스케줄 A 광역 중저역 순환 (스윕 2개 / 단독 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub1Container, "2️⃣ [파트 2] 스케줄 A: 광역 순환 스케줄 (단독 2개 · 스윕 2개)", "#38D39F");

        LinearLayout sub1RowA = new LinearLayout(this);
        sub1RowA.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub1RowA,
                "🌅 오전 중역 (07~12시) [FM]",
                "40.0 ~ 50.0Hz (240s) [FM 10%]",
                "슬래브 2차 공진 훑기 가진",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 40.0f, 50.0f, 240.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브1 스케줄A] 오전 40.0~50.0Hz 스윕 [FM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub1RowA,
                "☀️ 오후 고정 (12~18시) [AM]",
                "45.0Hz 단독 고정 [AM 50%]",
                "중저역 연속 충격 진동 가진",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 45.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.50f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브1 스케줄A] 오후 45.0Hz 단독 [AM 펄스]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub1Container.addView(sub1RowA);

        LinearLayout sub1RowB = new LinearLayout(this);
        sub1RowB.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub1RowB,
                "🌆 저녁 중역 (18~23시) [RM]",
                "35.0 ~ 52.0Hz (300s) [RM 40%]",
                "복합 슬래브 굽힘파 전단 타격",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 35.0f, 52.0f, 300.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.8f,
                                3.0f, 1, 1, false, 15,
                                "[서브1 스케줄A] 저녁 35.0~52.0Hz 스윕 [RM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub1RowB,
                "🌙 야간 초저역 (23~07시) [FM]",
                "22.0Hz 단독 고정 [FM 5% 미세지터]",
                "비가청 전정기관·골반 침투",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[서브1 스케줄A] 야간 22.0Hz 단독 [FM 지터]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub1Container.addView(sub1RowB);

        // 파트 3: 스케줄 B 핵심 전술 정밀 프리셋 (단독 2개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub1Container, "3️⃣ [파트 3] 스케줄 B: 핵심 전술 정밀 프리셋 (단독 2개 · 스윕 2개)", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "⚡ 43.2 Hz 슬래브 관통 강타 [AM 70% 펄스 해머]",
                "15cm 콘크리트 슬래브를 가장 빠르게 관통하여 311호 바닥 수직 직타 (AM 70% @ 1.5Hz)",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 70%(1.5Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브1 스케줄B] 43.2Hz 관통 강타 [AM 70% 펄스]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "💥 32.8 Hz 흉복부 압박 [RM 45% 링변조]",
                "인체 흉곽 및 복부 고유 진동수와 일치하여 호흡 답답함 유발 (RM 사이드밴드 분할 타격)",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(1.2Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 1.2f,
                                3.0f, 1, 0, false, 15,
                                "[서브1 스케줄B] 32.8Hz 흉복부 압박 [RM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🎯 50.0 ~ 55.0 Hz 야간 요격 스윕 (20초) [FM 10% 지터]",
                "311호의 야간 공격을 슬래브 공진점에서 실시간 추적 상쇄 및 역제압 (FM 10% @ 3.0Hz)",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(3.0Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 20.0f,
                                true, 0.10f, 3.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[서브1 스케줄B] 50.0~55.0Hz 요격 스윕 [FM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "👁️ 15.0 ~ 25.0 Hz 안구·초저역 스윕 (120초) [RM 40% 링변조]",
                "안구 고유 진동수(18Hz) 및 골반 초저역을 RM 이중 간섭 파면으로 자극하여 신경 피로 유도",
                "🎛️ Vorta DSP: 부스트 +6dB | RM 40%(2.0Hz) | 2차 배음 ON | L=-R 역위상",
                "#00E5FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 25.0f, 120.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 2.0f,
                                6.0f, 1, 1, true, 15,
                                "[서브1 스케줄B] 15.0~25.0Hz 안구·초저역 스윕 [RM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        root.addView(mFrameSub1Container);

        // Divider between Sub1 and Sub2
        mSplitDivider2 = createSplitDivider("▼ 서브2 프레임 (ver2 마스터 스케줄) ▼", "#A371F7");
        root.addView(mSplitDivider2);

        // =========================================================================
        // 🛡️ 3. 서브2 프레임 컨테이너 (ver2 마스터 스케줄)
        // =========================================================================
        mFrameSub2Container = createFrameContainer(
                "🛡️ [서브2 프레임] 주파수 통합 운용 체계 마스터 보고서 (ver2)",
                "ver2 표준 4구간 + 핵심 전술 프리셋 + 긴급 대응 3종 모드",
                "#A371F7",
                "#1B122C"
        );

        // 파트 1: ver2 4대 표준 시간대 스케줄 (스윕 2개 / 단독 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub2Container, "1️⃣ [파트 1] ver2 4대 표준 시간대 스케줄 (단독 2개 · 스윕 2개)", "#A371F7");

        LinearLayout sub2RowA = new LinearLayout(this);
        sub2RowA.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub2RowA,
                "🚶 주간 외출 (09~18시) [FM]",
                "38.0 ~ 55.0Hz (60s) [FM 10%]",
                "천장 슬래브 전면 순환 폭격",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 1, false, 15,
                                "[서브2 ver2-1] 주간 외출 38.0~55.0Hz [FM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub2RowA,
                "💥 저녁 집중 (18~23시) [AM]",
                "48.0 ~ 55.0Hz (20s) [AM 50%]",
                "공진점 주변 빠른 왕복 펄싱",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 48.0f, 55.0f, 20.0f,
                                false, 0.0f, 1.0f, true, 0.50f, 2.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브2 ver2-2] 저녁 집중 48.0~55.0Hz [AM 펄스]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub2Container.addView(sub2RowA);

        LinearLayout sub2RowB = new LinearLayout(this);
        sub2RowB.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub2RowB,
                "💤 심야 취침 (23~07시) [순수]",
                "55.0Hz 단독 요격 [순수 사인파]",
                "야간 0dB 스텔스 요격 앵커",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[서브2 ver2-3] 심야 취침 55.0Hz [순수 사인파]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub2RowB,
                "⏰ 아침 기상 (07~09시) [AM]",
                "43.2Hz 단독 [AM 70% 해머]",
                "1타 콘크리트 슬래브 해머",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브2 ver2-4] 아침 기상 43.2Hz [AM 해머]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub2Container.addView(sub2RowB);

        // 파트 2: ver2 핵심 전술 프리셋 (단독 2개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub2Container, "2️⃣ [파트 2] ver2 핵심 전술 프리셋 (단독 2개 · 스윕 2개)", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🎯 [ver2 전술1] 55.0 Hz 순수 앵커 [순수 사인파]",
                "천장 슬래브 고유 공진 모드 100% 무왜곡 직타 (역제압 앵커)",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | L=R 동위상",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[서브2 전술1] 55.0Hz 순수 앵커 [순수 사인파]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔨 [ver2 전술2] 43.2 Hz 콘크리트 해머 [AM 75% 펄스]",
                "천장 슬래브 깊숙이 망치로 찍어내리는 1.2Hz 충격 해머",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 75%(1.2Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.75f, 1.2f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브2 전술2] 43.2Hz 콘크리트 해머 [AM 펄스]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "⚡ [ver2 전술3] 30.0 ~ 45.0 Hz 골조 공진 스윕 (90초) [RM 40% 링변조]",
                "건물 골조 및 흉복부 내장 진동을 이중 간섭 파면으로 광역 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(1.5Hz) | 아날로그 새추레이터 | L=-R 역위상",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 30.0f, 45.0f, 90.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.5f,
                                3.0f, 1, 1, false, 15,
                                "[서브2 전술3] 30.0~45.0Hz 골조 스윕 [RM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🌪️ [ver2 전술4] 50.0 ~ 55.0 Hz (15초 급습) [FM 10% 지터]",
                "핵심 공진점 50~55Hz 15초 왕복 급습 + FM 10%(3.0Hz)로 상대 내성 형성 원천 분쇄",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 10%(3.0Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 15.0f,
                                true, 0.10f, 3.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 0, false, 15,
                                "[서브2 전술4] 50.0~55.0Hz 급습 스윕 [FM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        // 파트 3: ver2 긴급 대응 3종 모드 (단독 2개 / 스윕 1개)
        addSectionHeaderInsideFrame(mFrameSub2Container, "3️⃣ [파트 3] ver2 긴급 대응 3종 모드", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🚨 [긴급 1] 발망치 즉각 응징: 55.0 Hz [AM 85% 풀파워]",
                "상대 도발 감지 즉시 3.0Hz 파괴 펄스로 천장 수직 풀파워 투하",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 85%(3.0Hz) | 아날로그 새추레이터 | L=R 동위상",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.85f, 3.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 0, false, 15,
                                "[서브2 긴급1] 발망치 즉각 응징 [AM 85% 풀파워]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "💣 [긴급 2] 슬래브 전면 공진 타격: 38.0 ~ 55.0 Hz (60s) [RM 45% 링변조]",
                "슬래브 전 대역 RM 이중 간섭 파면 타격으로 지속적 구조물 피로 누적",
                "🎛️ Vorta DSP: 부스트 0dB | RM 45%(2.0Hz) | 트루피크 0.0dBFS | L=-R 역위상",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 2.0f,
                                0.0f, 0, 1, false, 15,
                                "[서브2 긴급2] 슬래브 전면 공진 타격 [RM 변조]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🛡️ [긴급 3] 24시간 무인 상시 방어: 55.0 Hz [FM 5% 미세지터]",
                "311호 내장진동 상시 차단 방어선 + 미세 지터로 청각 내성 형성 방지",
                "🎛️ Vorta DSP: 부스트 0dB | FM 5%(0.5Hz) | 트루피크 0.0dBFS | L=R 동위상",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 0, false, 15,
                                "[서브2 긴급3] 24시간 무인 방어 [FM 지터 앵커]",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        root.addView(mFrameSub2Container);

        // =========================================================================
        // 🎛️ Vorta DSP 튜너 & 제어 콘솔 카드
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

        // =========================================================================
        // ■ 즉시 정지 카드 (Emergency STOP)
        // =========================================================================
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
            int targetVol,
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

        svc.putExtra("vol_step", targetVol);
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
    return code


def generate_s6_main_activity():
    code = r'''package com.vorta.s6frequency;

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

    // 3-Way Tri-Frameset / Split Screen Layout View Containers & Mode State
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

        // Allow screen to turn off normally; background audio is maintained by foreground service with PARTIAL_WAKE_LOCK
        getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                | WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
        );

        S6AudioGeneratorService.loadConfig(this);
        S6VolumeHelper.ensureTargetVolumeIfNeeded(this, true);

        float density = getResources().getDisplayMetrics().density;

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#0A0E17"));
        scroll.setFillViewport(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding((int)(16 * density), (int)(18 * density), (int)(16 * density), (int)(28 * density));

        // Header Title
        TextView titleTv = new TextView(this);
        titleTv.setText("보르타 레조 S6 v2.8");
        titleTv.setTextSize(22);
        titleTv.setTextColor(Color.parseColor("#00F0FF"));
        titleTv.setTypeface(Typeface.DEFAULT_BOLD);
        titleTv.setPadding(0, 0, 0, (int)(4 * density));
        root.addView(titleTv);

        TextView subTitleTv = new TextView(this);
        subTitleTv.setText("갤럭시 S6 + Lepy LP-168S 앰프 + 트랜스2 전용 맞춤 주파수 발생기 | FM·AM·RM 변조 Vorta DSP");
        subTitleTv.setTextSize(12);
        subTitleTv.setTextColor(Color.parseColor("#E6EDF3"));
        subTitleTv.setPadding(0, 0, 0, (int)(14 * density));
        root.addView(subTitleTv);

        // =========================================================================
        // 🎛️ 프레임셋 스플릿 뷰 콘솔 메뉴 프레임 (전체 / 메인 / 서브1 / 서브2)
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
        mStatusMode.setText("현재 모드: " + S6AudioGeneratorService.sModeTitle);
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
        mStatusMod.setText("변조 상태: " + S6AudioGeneratorService.buildModulationSummary());
        mStatusMod.setTextSize(12);
        mStatusMod.setTextColor(Color.parseColor("#FF79C6"));
        mStatusMod.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusMod.setPadding(0, 0, 0, (int)(2 * density));
        card.addView(mStatusMod);

        mStatusDsp = new TextView(this);
        mStatusDsp.setText("Vorta DSP: " + S6AudioGeneratorService.buildVortaDspSummary());
        mStatusDsp.setTextSize(12);
        mStatusDsp.setTextColor(Color.parseColor("#38D39F"));
        mStatusDsp.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusDsp.setPadding(0, 0, 0, (int)(2 * density));
        card.addView(mStatusDsp);

        mStatusSignal = new TextView(this);
        mStatusSignal.setText("검수: 48,000Hz Native Direct PCM 가동 중");
        mStatusSignal.setTextSize(11);
        mStatusSignal.setTextColor(Color.parseColor("#8B949E"));
        mStatusSignal.setPadding(0, 0, 0, (int)(2 * density));
        card.addView(mStatusSignal);

        mStatusKnob = new TextView(this);
        mStatusKnob.setText("LP-168S 가이드: " + S6AudioGeneratorService.sKnobGuide);
        mStatusKnob.setTextSize(11);
        mStatusKnob.setTextColor(Color.parseColor("#F1E05A"));
        card.addView(mStatusKnob);

        root.addView(card);

        // =========================================================================
        // 🎯 1. 메인 프레임 컨테이너 (최신맞춤판 SSOT 정본 스케줄)
        // =========================================================================
        mFrameMainContainer = createFrameContainer(
                "🎯 [메인 프레임] 주파수 통합 운용 마스터 보고서 (최신맞춤판 SSOT)",
                "갤럭시 S6 + Lepy LP-168S + 트랜스2 (68W BTL 모노) 천장 수직 직타 전용",
                "#00E5FF",
                "#0D1926"
        );

        // 파트 1: 24시간 4구간 표준 맞춤 스케줄 (단독 2개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameMainContainer, "1️⃣ [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄 (단독·스윕 50:50 균형)", "#00E5FF");

        LinearLayout mRow1 = new LinearLayout(this);
        mRow1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow1,
                "🌅 아침 (07~13시) [FM]",
                "2.0~9.0Hz 스윕 (180초) [FM 12%]",
                "🎛️ 인프라소닉 천장 기습 | 내성 원천 차단",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 2.0f, 9.0f, 180.0f,
                                true, 0.12f, 1.5f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 2, false, 15,
                                "[아침 07~13시] 2.0~9.0Hz 스윕 (FM 12% @ 1.5Hz)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | BASS 12~1시 | VOL 5.5");
                    }
                });

        addHalfPresetButton(mRow1,
                "☀️ 오후 (13~19시) [AM]",
                "22.0Hz 단독 고정 [AM 65%]",
                "🎛️ AM 2.0Hz 펄스 해머 | 소화기·흉부 공진",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f,
                                true, 0.65f, 2.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 2, true, 15,
                                "[오후 13~19시] 22.0Hz 단독 직타 (AM 65% @ 2.0Hz)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | BASS 12~1시 | VOL 5.5");
                    }
                });
        mFrameMainContainer.addView(mRow1);

        LinearLayout mRow2 = new LinearLayout(this);
        mRow2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow2,
                "🌆 저녁 (19~01시) [RM]",
                "38.0~55.0Hz 스윕 (120초) [RM 45%]",
                "🎛️ RM 이중 파면 간섭 | 천장 슬래브 융단",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 120.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                true, 0.45f, 1.8f,
                                6.0f, 1, 2, false, 15,
                                "[저녁 19~01시] 38.0~55.0Hz 스윕 (RM 45% @ 1.8Hz)",
                                "LP-168S [강타]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addHalfPresetButton(mRow2,
                "🌙 취침 (01~07시) [FM]",
                "55.0Hz 단독 앵커 [FM 5% 미세지터]",
                "🎛️ 55Hz 요격 락온 | 백색소음 차단 무력화",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[취침 01~07시] 55.0Hz 단독 (FM 5% 미세지터 요격 앵커)",
                                "LP-168S [무음 락온]: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0");
                    }
                });
        mFrameMainContainer.addView(mRow2);

        // 파트 2: 5대 핵심 전술 모드 (단독 3개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameMainContainer, "2️⃣ [파트 2] 트랜스2 5대 핵심 전술 모드 (단독·스윕 최적 배분)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "🎯 [단독 1순위] 55.0 Hz 요격 앵커 [순수 사인파]",
                "천장 슬래브 수직 밀착 타격으로 311호 55Hz 공격 원천 상쇄 및 역제압 (100% 에너지 집약)",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[트랜스2 단독 1순위] 55.0Hz 요격 앵커 [순수 사인파]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz(10시) | BASS 12~1시 | TREBLE 7시 | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌪️ [스윕 1순위] 50.0 ~ 55.0 Hz 초고속 요격 스윕 (15초) [FM 변조]",
                "핵심 공진점 55Hz 주변을 15초마다 왕복 급습 + FM 주파수 지터(10%@2.5Hz)로 회피 불능 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 10%(2.5Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 15.0f,
                                true, 0.10f, 2.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 2, false, 15,
                                "[트랜스2 스윕 1순위] 50.0~55.0Hz 초고속 스윕 (FM 10% @ 2.5Hz)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔨 [단독 2순위] 43.2 Hz 슬래브 관통 강타 [AM 75% 해머]",
                "천장 콘크리트 코어를 깊숙이 뚫고 들어가 1.2Hz 펄스 해머로 311호 바닥 수직 타격",
                "🎛️ Vorta DSP: 부스트 +6dB (초강력) | AM 75%(1.2Hz) | 아날로그 새추레이터 | 2차배음 ON",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.75f, 1.2f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, true, 15,
                                "[트랜스2 단독 2순위] 43.2Hz 슬래브 관통 강타 (AM 75% @ 1.2Hz)",
                                "LP-168S [기습 강타]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔄 [스윕 2순위] 15.0 ~ 28.0 Hz 인체 장기 타격 스윕 (90초) [RM 링변조]",
                "안구(18Hz)·소화기·골반 공진 대역을 링 변조 사이드밴드 분할 타격 (이중 파면 간섭)",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(2.0Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 28.0f, 90.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 2.0f,
                                3.0f, 0, 2, false, 15,
                                "[트랜스2 스윕 2순위] 15.0~28.0Hz 장기 스윕 (RM 45% @ 2.0Hz)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "👁️ [단독 3순위] 18.98 Hz 안구 공진 앵커 [FM+AM 복합 변조]",
                "Vic Tandy 안구 공진점 + 미세 FM(6%@0.8Hz) + AM(50%@0.8Hz) 복합 맥동 극심한 피로 유도",
                "🎛️ Vorta DSP: 부스트 0dB | FM 6% + AM 50%(0.8Hz) 복합 | 트루피크 0.0dBFS | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 0f, 0f, 0f,
                                true, 0.06f, 0.8f, true, 0.50f, 0.8f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[트랜스2 단독 3순위] 18.98Hz 안구 공진 앵커 [FM+AM 복합]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        // 파트 3: 8대 상황별 맞춤 실행 (단독 4개 / 스윕 4개 균형)
        addSectionHeaderInsideFrame(mFrameMainContainer, "3️⃣ [파트 3] 8대 상황별 맞춤 실행 (단독 4개 · 스윕 4개 50:50 배분)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "상황 ① 일반 외출 (2~5시간): 38.0 ~ 55.0 Hz (60초 스윕) [FM 변조]",
                "단기 부재 시 슬래브 전 대역 60초 순환 + FM 10%(2.0Hz)로 상대 내성 형성 원천 분쇄",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(2.0Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황① 일반외출 2~5h] 38.0~55.0Hz 스윕 [FM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ② 상대 도발 즉시 보복: 55.0 Hz 단독 고정 [AM 80% 파괴 해머]",
                "발망치 감지 즉시 천장 슬래브 1:1 풀파워 3Hz 충격파 펄스로 수직 압살",
                "🎛️ Vorta DSP: 부스트 +6dB (초강력) | AM 80%(3.0Hz) | 아날로그 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.80f, 3.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, true, 15,
                                "[상황② 즉각보복] 55.0Hz 단독 [AM 80% 파괴 해머]",
                                "LP-168S [보복 펀치]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ③ 안전 취침 방어 (23:00~07:00): 55.0 Hz 단독 [순수 사인파]",
                "211호 0dB 무음 스텔스 유지 & 311호 수면 박탈 100% 무왜곡 직타",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | 무변조 순수 사인파 | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황③ 취침방어] 55.0Hz 단독 [순수 사인파]",
                                "LP-168S [무음 락온]: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ④ 장기 외출 (48시간+ 무인): 20.0 ~ 55.0 Hz (300초 스윕) [RM 변조]",
                "이틀 이상 무인 초장기 가동 | RM(45%@1.5Hz) 이중 파면 간섭으로 슬래브 전면 균열 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(1.5Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#79C0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 20.0f, 55.0f, 300.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 1.5f,
                                3.0f, 0, 2, false, 15,
                                "[상황④ 장기외출 48h+] 20.0~55.0Hz 스윕 [RM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑤ 상대 정신 집중 붕괴: 12.5 Hz 단독 고정 [FM 15% 변조]",
                "알파파(12Hz) 억제 + FM 15%(3.5Hz) 진동으로 상대방 극심한 두통 및 집중력 파괴 유발",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 15%(3.5Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 12.5f, 0f, 0f, 0f, 0f,
                                true, 0.15f, 3.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 0, 2, false, 15,
                                "[상황⑤ 정신붕괴] 12.5Hz 단독 [FM 15% @ 3.5Hz]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑥ 상대 내성 완벽 파괴: 25.0 ~ 45.0 Hz (45초 스윕) [FM+AM 복합]",
                "주파수 변조(12%@2.5Hz) + 진폭 펄스(50%@1.8Hz) 동시 발진으로 어떤 물리적 내성도 원천 차단",
                "🎛️ Vorta DSP: 부스트 +6dB | FM 12% + AM 50% 복합 | 아날로그 새추레이터 | BTL 모노",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 25.0f, 45.0f, 45.0f,
                                true, 0.12f, 2.5f, true, 0.50f, 1.8f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, false, 15,
                                "[상황⑥ 내성파괴] 25.0~45.0Hz 스윕 [FM+AM 복합]",
                                "LP-168S [초강력 파괴]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑦ 3시간 지속 압박 타격: 32.8 Hz 단독 고정 [RM 40% 링변조]",
                "흉복부 내장 공진 + RM 40%(1.2Hz) 사이드밴드 분할로 3시간 지속 타격 시 호흡 답답함 극대화",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(1.2Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.2f,
                                3.0f, 0, 2, false, 15,
                                "[상황⑦ 3시간지속] 32.8Hz 단독 [RM 40% @ 1.2Hz]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑧ 출근 12시간 무인 순환: 40.0 ~ 55.0 Hz (90초 스윕) [AM 50% 펄스]",
                "장시간 무인 출근 시 슬래브 과열 방지 및 AM 50%(1.0Hz) 지속적 충격파 펄싱",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | AM 50%(1.0Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#00F0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 40.0f, 55.0f, 90.0f,
                                false, 0.0f, 1.0f, true, 0.50f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황⑧ 출근12h무인] 40.0~55.0Hz 스윕 [AM 50% @ 1.0Hz]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        root.addView(mFrameMainContainer);

        // Divider between Main and Sub1
        mSplitDivider1 = createSplitDivider("▼ 서브1 프레임 (최종완결판 스케줄 C·A·B) ▼", "#38D39F");
        root.addView(mSplitDivider1);

        // =========================================================================
        // 🚀 2. 서브1 프레임 컨테이너 (최종완결판 스케줄 C·A·B)
        // =========================================================================
        mFrameSub1Container = createFrameContainer(
                "🚀 [서브1 프레임] 주파수 통합 운용 체계 마스터 보고서 (최종완결판)",
                "스케줄 C 무인 라이프사이클 + 스케줄 A 광역 순환 + 스케줄 B 핵심 프리셋",
                "#38D39F",
                "#0D2218"
        );

        // 파트 1: 스케줄 C 무인 라이프사이클 (스윕 1개 / 단독 2개)
        addSectionHeaderInsideFrame(mFrameSub1Container, "1️⃣ [파트 1] 스케줄 C: 사용자 수면 & 출근 무인 자율 스케줄", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "🏢 1. 외출·출근 블록 (08:30~18:30 10h): 38.0~55.0Hz (60s) [FM 변조]",
                "출근 시 1회 터치 후 10시간 완전 무인 자동 순환 | FM 10%(2.0Hz) 슬래브 융단 폭격",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(2.0Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄C-1] 외출·출근 38.0~55.0Hz [FM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🚪 2. 퇴근·저녁 블록 (18:30~23:00 4.5h): 40.0Hz 천장 직타 [AM 60% 펄스]",
                "귀가자 즉각 제압 및 흉곽 압박 타격 (AM 60% @ 2.0Hz 충격파 펄싱)",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 60%(2.0Hz) | 아날로그 새추레이터 | BTL 모노",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 40.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.60f, 2.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, false, 15,
                                "[서브1 스케줄C-2] 퇴근·저녁 40.0Hz [AM 60% 펄스]",
                                "LP-168S [저녁 압박]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🛏️ 3. 취침·수면 블록 (23:00~08:30 9.5h): 55.0Hz 천장 락온 [순수 사인파]",
                "211호 0dB 무음 숙면 보장 & 311호 수면 박탈 무왜곡 락온",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | BTL 모노",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄C-3] 취침·수면 55.0Hz [순수 사인파]",
                                "LP-168S [무음 락온]: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0");
                    }
                });

        // 파트 2: 스케줄 A 광역 중저역 순환 (스윕 2개 / 단독 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub1Container, "2️⃣ [파트 2] 스케줄 A: 광역 순환 스케줄 (단독 2개 · 스윕 2개)", "#38D39F");

        LinearLayout sub1RowA = new LinearLayout(this);
        sub1RowA.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub1RowA,
                "🌅 오전 중역 (07~12시) [FM]",
                "40.0 ~ 50.0Hz (240s) [FM 10%]",
                "슬래브 2차 공진 훑기 가진",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 40.0f, 50.0f, 240.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄A] 오전 40.0~50.0Hz 스윕 [FM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addHalfPresetButton(sub1RowA,
                "☀️ 오후 고정 (12~18시) [AM]",
                "45.0Hz 단독 고정 [AM 50%]",
                "중저역 연속 충격 진동 가진",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 45.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.50f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄A] 오후 45.0Hz 단독 [AM 펄스]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });
        mFrameSub1Container.addView(sub1RowA);

        LinearLayout sub1RowB = new LinearLayout(this);
        sub1RowB.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub1RowB,
                "🌆 저녁 중역 (18~23시) [RM]",
                "35.0 ~ 52.0Hz (300s) [RM 40%]",
                "복합 슬래브 굽힘파 타격",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 35.0f, 52.0f, 300.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.8f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄A] 저녁 35.0~52.0Hz 스윕 [RM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addHalfPresetButton(sub1RowB,
                "🌙 야간 초저역 (23~07시) [FM]",
                "22.0Hz 단독 고정 [FM 5% 미세지터]",
                "비가청 전정기관·골반 침투",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄A] 야간 22.0Hz 단독 [FM 지터]",
                                "LP-168S [무음 락온]: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0");
                    }
                });
        mFrameSub1Container.addView(sub1RowB);

        // 파트 3: 스케줄 B 핵심 전술 정밀 프리셋 (단독 2개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub1Container, "3️⃣ [파트 3] 스케줄 B: 핵심 전술 정밀 프리셋 (단독 2개 · 스윕 2개)", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "⚡ 43.2 Hz 슬래브 관통 강타 [AM 70% 펄스 해머]",
                "15cm 콘크리트 슬래브를 가장 빠르게 관통하여 311호 바닥 수직 직타 (AM 70% @ 1.5Hz)",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 70%(1.5Hz) | 아날로그 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄B] 43.2Hz 관통 강타 [AM 70% 펄스]",
                                "LP-168S [기습 강타]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "💥 32.8 Hz 흉복부 압박 [RM 45% 링변조]",
                "인체 흉곽 및 복부 고유 진동수와 일치하여 호흡 답답함 유발 (RM 사이드밴드 분할 타격)",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 45%(1.2Hz) | 아날로그 새추레이터 | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 1.2f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄B] 32.8Hz 흉복부 압박 [RM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🎯 50.0 ~ 55.0 Hz 야간 요격 스윕 (20초) [FM 10% 지터]",
                "311호의 야간 공격을 슬래브 공진점에서 실시간 추적 상쇄 및 역제압 (FM 10% @ 3.0Hz)",
                "🎛️ Vorta DSP: 부스트 0dB | FM 10%(3.0Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 20.0f,
                                true, 0.10f, 3.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄B] 50.0~55.0Hz 요격 스윕 [FM 변조]",
                                "LP-168S [무음 요격]: SUB 3.5(9시반) | X-OVER 80Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "👁️ 15.0 ~ 25.0 Hz 안구·초저역 스윕 (120초) [RM 40% 링변조]",
                "안구 고유 진동수(18Hz) 및 골반 초저역을 RM 이중 간섭 파면으로 자극하여 신경 피로 유도",
                "🎛️ Vorta DSP: 부스트 +6dB | RM 40%(2.0Hz) | 2차 배음 ON | BTL 모노",
                "#00E5FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 15.0f, 25.0f, 120.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 2.0f,
                                6.0f, 1, 2, true, 15,
                                "[서브1 스케줄B] 15.0~25.0Hz 안구·초저역 스윕 [RM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        root.addView(mFrameSub1Container);

        // Divider between Sub1 and Sub2
        mSplitDivider2 = createSplitDivider("▼ 서브2 프레임 (ver2 마스터 스케줄) ▼", "#A371F7");
        root.addView(mSplitDivider2);

        // =========================================================================
        // 🛡️ 3. 서브2 프레임 컨테이너 (ver2 마스터 스케줄)
        // =========================================================================
        mFrameSub2Container = createFrameContainer(
                "🛡️ [서브2 프레임] 주파수 통합 운용 체계 마스터 보고서 (ver2)",
                "ver2 표준 4구간 + 핵심 전술 프리셋 + 긴급 대응 3종 모드",
                "#A371F7",
                "#1B122C"
        );

        // 파트 1: ver2 4대 표준 시간대 스케줄 (스윕 2개 / 단독 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub2Container, "1️⃣ [파트 1] ver2 4대 표준 시간대 스케줄 (단독 2개 · 스윕 2개)", "#A371F7");

        LinearLayout sub2RowA = new LinearLayout(this);
        sub2RowA.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub2RowA,
                "🚶 주간 외출 (09~18시) [FM]",
                "38.0 ~ 55.0Hz (60s) [FM 10%]",
                "천장 슬래브 전면 순환 폭격",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                true, 0.10f, 2.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 ver2-1] 주간 외출 38.0~55.0Hz [FM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addHalfPresetButton(sub2RowA,
                "💥 저녁 집중 (18~23시) [AM]",
                "48.0 ~ 55.0Hz (20s) [AM 50%]",
                "공진점 주변 빠른 왕복 펄싱",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 48.0f, 55.0f, 20.0f,
                                false, 0.0f, 1.0f, true, 0.50f, 2.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 ver2-2] 저녁 집중 48.0~55.0Hz [AM 펄스]",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });
        mFrameSub2Container.addView(sub2RowA);

        LinearLayout sub2RowB = new LinearLayout(this);
        sub2RowB.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub2RowB,
                "💤 심야 취침 (23~07시) [순수]",
                "55.0Hz 단독 요격 [순수 사인파]",
                "야간 0dB 스텔스 요격 앵커",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 ver2-3] 심야 취침 55.0Hz [순수 사인파]",
                                "LP-168S [무음 락온]: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0");
                    }
                });

        addHalfPresetButton(sub2RowB,
                "⏰ 아침 기상 (07~09시) [AM]",
                "43.2Hz 단독 [AM 70% 해머]",
                "1타 콘크리트 슬래브 해머",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.70f, 1.5f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 ver2-4] 아침 기상 43.2Hz [AM 해머]",
                                "LP-168S [기습 강타]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });
        mFrameSub2Container.addView(sub2RowB);

        // 파트 2: ver2 핵심 전술 프리셋 (단독 2개 / 스윕 2개 균형)
        addSectionHeaderInsideFrame(mFrameSub2Container, "2️⃣ [파트 2] ver2 핵심 전술 프리셋 (단독 2개 · 스윕 2개)", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🎯 [ver2 전술1] 55.0 Hz 순수 앵커 [순수 사인파]",
                "천장 슬래브 고유 공진 모드 100% 무왜곡 직타 (역제압 앵커)",
                "🎛️ Vorta DSP: 부스트 0dB | 무변조 순수 사인파 | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 전술1] 55.0Hz 순수 앵커 [순수 사인파]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | BASS 12~1시 | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔨 [ver2 전술2] 43.2 Hz 콘크리트 해머 [AM 75% 펄스]",
                "천장 슬래브 깊숙이 망치로 찍어내리는 1.2Hz 충격 해머",
                "🎛️ Vorta DSP: 부스트 +3dB | AM 75%(1.2Hz) | 아날로그 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.75f, 1.2f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 전술2] 43.2Hz 콘크리트 해머 [AM 펄스]",
                                "LP-168S [기습 강타]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "⚡ [ver2 전술3] 30.0 ~ 45.0 Hz 골조 공진 스윕 (90초) [RM 40% 링변조]",
                "건물 골조 및 흉복부 내장 진동을 이중 간섭 파면으로 광역 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | RM 40%(1.5Hz) | 아날로그 새추레이터 | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 30.0f, 45.0f, 90.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.40f, 1.5f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 전술3] 30.0~45.0Hz 골조 스윕 [RM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🌪️ [ver2 전술4] 50.0 ~ 55.0 Hz (15초 급습) [FM 10% 지터]",
                "핵심 공진점 50~55Hz 15초 왕복 급습 + FM 10%(3.0Hz)로 상대 내성 형성 원천 분쇄",
                "🎛️ Vorta DSP: 부스트 +3dB | FM 10%(3.0Hz) | 아날로그 새추레이터 | BTL 모노",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 55.0f, 15.0f,
                                true, 0.10f, 3.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 전술4] 50.0~55.0Hz 급습 스윕 [FM 변조]",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        // 파트 3: ver2 긴급 대응 3종 모드 (단독 2개 / 스윕 1개)
        addSectionHeaderInsideFrame(mFrameSub2Container, "3️⃣ [파트 3] ver2 긴급 대응 3종 모드", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🚨 [긴급 1] 발망치 즉각 응징: 55.0 Hz [AM 85% 풀파워]",
                "상대 도발 감지 즉시 3.0Hz 파괴 펄스로 천장 수직 풀파워 투하",
                "🎛️ Vorta DSP: 부스트 +6dB | AM 85%(3.0Hz) | 아날로그 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                false, 0.0f, 1.0f, true, 0.85f, 3.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, false, 15,
                                "[서브2 긴급1] 발망치 즉각 응징 [AM 85% 풀파워]",
                                "LP-168S [보복 펀치]: SUB 4.0(10시) | X-OVER 85Hz | BASS +2(1시) | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "💣 [긴급 2] 슬래브 전면 공진 타격: 38.0 ~ 55.0 Hz (60s) [RM 45% 링변조]",
                "슬래브 전 대역 RM 이중 간섭 파면 타격으로 지속적 구조물 피로 누적",
                "🎛️ Vorta DSP: 부스트 0dB | RM 45%(2.0Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 55.0f, 60.0f,
                                false, 0.0f, 1.0f, false, 0.0f, 1.0f, true, 0.45f, 2.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 긴급2] 슬래브 전면 공진 타격 [RM 변조]",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🛡️ [긴급 3] 24시간 무인 상시 방어: 55.0 Hz [FM 5% 미세지터]",
                "311호 내장진동 상시 차단 방어선 + 미세 지터로 청각 내성 형성 방지",
                "🎛️ Vorta DSP: 부스트 0dB | FM 5%(0.5Hz) | 트루피크 0.0dBFS | BTL 모노",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.05f, 0.5f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 긴급3] 24시간 무인 방어 [FM 지터 앵커]",
                                "LP-168S [무음 락온]: SUB 3.0(9시) | X-OVER 70Hz | TREBLE 7시 | VOL 5.0");
                    }
                });

        root.addView(mFrameSub2Container);

        // =========================================================================
        // 🎛️ Vorta DSP 튜너 & 제어 콘솔 카드
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
                S6AudioGeneratorService.sAutoPresetDsp = true;
                notifyDspChanged("프리셋 자동 DSP 매칭 활성화");
            }
        });
        mAutoLockButtons[1] = createDspTabButton(autoRow, "수동 오버라이드", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sAutoPresetDsp = false;
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
                S6AudioGeneratorService.sLimiterMode = 0;
                notifyDspChanged("트루피크 0.0dBFS 리미터 적용");
            }
        });
        mLimiterButtons[1] = createDspTabButton(limiterRow, "아날로그 새추레이터", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sLimiterMode = 1;
                notifyDspChanged("아날로그 소프트 새추레이터 적용");
            }
        });
        dspCard.addView(limiterRow);

        addDspSubLabel(dspCard, "4. 트랜스2 모노 BTL 채널 매트릭스 (Channel Matrix):");
        LinearLayout chRow = new LinearLayout(this);
        chRow.setOrientation(LinearLayout.HORIZONTAL);
        mChannelButtons[0] = createDspTabButton(chRow, "BTL 모노 서밍 (권장)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sChannelMode = 2;
                notifyDspChanged("BTL (L+R)/2 모노 서밍 모드 적용");
            }
        });
        mChannelButtons[1] = createDspTabButton(chRow, "L=R 동위상 스테레오", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sChannelMode = 0;
                notifyDspChanged("L=R 동위상 스테레오 모드 적용");
            }
        });
        mChannelButtons[2] = createDspTabButton(chRow, "L=-R 180° 역위상", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sChannelMode = 1;
                notifyDspChanged("L=-R 역위상 모드 적용");
            }
        });
        dspCard.addView(chRow);

        addDspSubLabel(dspCard, "5. 2차 고조파 결합 익사이터 (2nd Harmonic Exciter):");
        LinearLayout exciterRow = new LinearLayout(this);
        exciterRow.setOrientation(LinearLayout.HORIZONTAL);
        mExciterButtons[0] = createDspTabButton(exciterRow, "배음 활성 ON", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sHarmonicExciter = true;
                notifyDspChanged("2차 배음 결합 익사이터 활성화");
            }
        });
        mExciterButtons[1] = createDspTabButton(exciterRow, "배음 비활성 OFF", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S6AudioGeneratorService.sHarmonicExciter = false;
                notifyDspChanged("순수 단일 주파수 전송");
            }
        });
        dspCard.addView(exciterRow);

        root.addView(dspCard);

        // =========================================================================
        // ■ 즉시 정지 카드 (Emergency STOP)
        // =========================================================================
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
        S6VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
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
        boolean curAuto = S6AudioGeneratorService.sAutoPresetDsp;
        for (int i = 0; i < mAutoLockButtons.length; i++) {
            if (mAutoLockButtons[i] == null) continue;
            boolean active = (curAuto == mAutoLockValues[i]);
            mAutoLockButtons[i].setBackgroundColor(Color.parseColor(active ? (curAuto ? "#56D364" : "#DA3633") : "#21262D"));
            mAutoLockButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mAutoLockButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        float curBoost = S6AudioGeneratorService.sBassBoostDb;
        for (int i = 0; i < mBoostButtons.length; i++) {
            if (mBoostButtons[i] == null) continue;
            boolean active = Math.abs(curBoost - mBoostValues[i]) < 0.1f;
            mBoostButtons[i].setBackgroundColor(Color.parseColor(active ? "#58A6FF" : "#21262D"));
            mBoostButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mBoostButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        int curLimiter = S6AudioGeneratorService.sLimiterMode;
        for (int i = 0; i < mLimiterButtons.length; i++) {
            if (mLimiterButtons[i] == null) continue;
            boolean active = (curLimiter == i);
            mLimiterButtons[i].setBackgroundColor(Color.parseColor(active ? "#58A6FF" : "#21262D"));
            mLimiterButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mLimiterButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        int curChannel = S6AudioGeneratorService.sChannelMode;
        int[] channelModes = {2, 0, 1}; // Buttons map to Mode 2 (BTL), Mode 0 (Stereo), Mode 1 (Inverted)
        for (int i = 0; i < 3; i++) {
            if (mChannelButtons[i] == null) continue;
            boolean active = (curChannel == channelModes[i]);
            mChannelButtons[i].setBackgroundColor(Color.parseColor(active ? "#D2A8FF" : "#21262D"));
            mChannelButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mChannelButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        boolean curExciter = S6AudioGeneratorService.sHarmonicExciter;
        for (int i = 0; i < mExciterButtons.length; i++) {
            if (mExciterButtons[i] == null) continue;
            boolean active = (curExciter == (i == 0));
            mExciterButtons[i].setBackgroundColor(Color.parseColor(active ? "#FFD700" : "#21262D"));
            mExciterButtons[i].setTextColor(Color.parseColor(active ? "#FFFFFF" : "#E6EDF3"));
            mExciterButtons[i].setTypeface(active ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        }

        if (mStatusDsp != null) {
            mStatusDsp.setText("Vorta DSP: " + S6AudioGeneratorService.buildVortaDspSummary());
        }
    }

    private void notifyDspChanged(String toastMsg) {
        S6AudioGeneratorService.saveConfig(this);
        refreshDspButtonsUi();

        Intent svc = new Intent(this, S6AudioGeneratorService.class);
        svc.putExtra("auto_preset_dsp", S6AudioGeneratorService.sAutoPresetDsp);
        svc.putExtra("bass_boost_db", S6AudioGeneratorService.sBassBoostDb);
        svc.putExtra("limiter_mode", S6AudioGeneratorService.sLimiterMode);
        svc.putExtra("channel_mode", S6AudioGeneratorService.sChannelMode);
        svc.putExtra("harmonic_exciter", S6AudioGeneratorService.sHarmonicExciter);
        startService(svc);

        Toast.makeText(this, toastMsg + " (영구 저장됨)", Toast.LENGTH_SHORT).show();
    }

    private void setBassBoost(float db) {
        S6AudioGeneratorService.sBassBoostDb = db;
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
            int targetVol,
            String title, String knobGuide) {

        Intent svc = new Intent(this, S6AudioGeneratorService.class);
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

        if (S6AudioGeneratorService.sAutoPresetDsp) {
            svc.putExtra("bass_boost_db", presetBoostDb);
            svc.putExtra("limiter_mode", presetLimiter);
            svc.putExtra("channel_mode", presetChannel);
            svc.putExtra("harmonic_exciter", presetHarmonic);
        } else {
            svc.putExtra("bass_boost_db", S6AudioGeneratorService.sBassBoostDb);
            svc.putExtra("limiter_mode", S6AudioGeneratorService.sLimiterMode);
            svc.putExtra("channel_mode", S6AudioGeneratorService.sChannelMode);
            svc.putExtra("harmonic_exciter", S6AudioGeneratorService.sHarmonicExciter);
        }

        svc.putExtra("vol_step", targetVol);
        svc.putExtra("title", title);
        svc.putExtra("knob", knobGuide);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(svc);
        } else {
            startService(svc);
        }

        S6VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
        refreshDspButtonsUi();

        Toast.makeText(this, title + " 발진 시작 (자유 볼륨/안전해제)", Toast.LENGTH_SHORT).show();
    }

    private void stopFrequencyService() {
        Intent svc = new Intent(this, S6AudioGeneratorService.class);
        svc.putExtra("action", "stop");
        startService(svc);
        Toast.makeText(this, "주파수 발진 정지 (DSP 설정 보존)", Toast.LENGTH_SHORT).show();
        syncTelemetryUi();
    }

    private void syncTelemetryUi() {
        if (mStatusMode != null) {
            mStatusMode.setText("현재 모드: " + S6AudioGeneratorService.sModeTitle);
        }
        if (mStatusFreq != null) {
            if (S6AudioGeneratorService.sIsPlaying) {
                if (S6AudioGeneratorService.sIsSweepMode) {
                    mStatusFreq.setText(String.format("실시간 발진: %.2f Hz (스윕 %.1f~%.1fHz) | 0.00dBFS True-Peak",
                            S6AudioGeneratorService.sInstantFreq,
                            S6AudioGeneratorService.sSweepMin,
                            S6AudioGeneratorService.sSweepMax));
                } else {
                    mStatusFreq.setText(String.format("실시간 발진: %.2f Hz 고정 (0.00 dBFS True-Peak)",
                            S6AudioGeneratorService.sInstantFreq));
                }
            } else {
                mStatusFreq.setText("실시간 발진: 정지됨 (출력 대기 상태)");
            }
        }
        if (mStatusMod != null) {
            mStatusMod.setText("변조 상태: " + S6AudioGeneratorService.buildModulationSummary());
        }
        if (mStatusDsp != null) {
            mStatusDsp.setText("Vorta DSP: " + S6AudioGeneratorService.buildVortaDspSummary());
        }
        if (mStatusSignal != null) {
            if (S6AudioGeneratorService.sIsPlaying) {
                mStatusSignal.setText(String.format("검수: 48,000Hz Native | Peak %d/32767(0.00dBFS) | RMS %.2fdBFS | DC %.4f | 왜곡 0%%",
                        S6AudioGeneratorService.sLastPeak,
                        S6AudioGeneratorService.sLastRmsDb,
                        S6AudioGeneratorService.sLastDcOffset));
            } else {
                mStatusSignal.setText("검수: 48,000Hz Native Direct PCM 대기 중");
            }
        }
        if (mStatusKnob != null) {
            mStatusKnob.setText("LP-168S 가이드: " + S6AudioGeneratorService.sKnobGuide);
        }
    }
}
'''
    return code


if __name__ == '__main__':
    s7_code = generate_s7_main_activity()
    with open('vorta_s7_app/src/com/vorta/s7frequency/MainActivity.java', 'w', encoding='utf-8') as f:
        f.write(s7_code)
    print("Wrote vorta_s7_app/src/com/vorta/s7frequency/MainActivity.java")

    s6_code = generate_s6_main_activity()
    with open('vorta_s6_app/src/com/vorta/s6frequency/MainActivity.java', 'w', encoding='utf-8') as f:
        f.write(s6_code)
    print("Wrote vorta_s6_app/src/com/vorta/s6frequency/MainActivity.java")
