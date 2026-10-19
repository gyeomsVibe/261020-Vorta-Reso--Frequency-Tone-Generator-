import sys

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
    private TextView[] mChannelButtons = new TextView[5];
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

        // Lockscreen bypass flags for emergency & 24/7 boiler room headless operation
        getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                | WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
                | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
                | WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
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
        subTitleTv.setText("갤럭시 S7 + 120W/60W 우퍼 전용 파워 앰프 맞춤 주파수 발생기 | Vorta DSP");
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
        mStatusFreq.setPadding(0, (int)(3 * density), 0, (int)(2 * density));
        card.addView(mStatusFreq);

        mStatusMod = new TextView(this);
        mStatusMod.setText("변조 상태: 무변조 순수 사인파");
        mStatusMod.setTextSize(12);
        mStatusMod.setTextColor(Color.parseColor("#E040FB"));
        mStatusMod.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusMod.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(mStatusMod);

        mStatusDsp = new TextView(this);
        mStatusDsp.setText("Vorta DSP: " + S7AudioGeneratorService.buildVortaDspSummary());
        mStatusDsp.setTextSize(12);
        mStatusDsp.setTextColor(Color.parseColor("#00FF66"));
        mStatusDsp.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusDsp.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(mStatusDsp);

        mStatusSignal = new TextView(this);
        mStatusSignal.setText("무왜곡 검수: 48,000Hz Native | Peak 32767(0.00dBFS) | DC 0.000 | 클리핑 0건");
        mStatusSignal.setTextSize(12);
        mStatusSignal.setTextColor(Color.parseColor("#58A6FF"));
        mStatusSignal.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusSignal.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(mStatusSignal);

        mStatusKnob = new TextView(this);
        mStatusKnob.setText("120W 우퍼 앰프: VOL 12~1시(정격 60W 풀파워) | FREQ 80~100Hz | BASS +2dB");
        mStatusKnob.setTextSize(12);
        mStatusKnob.setTextColor(Color.parseColor("#FFA657"));
        mStatusKnob.setTypeface(Typeface.DEFAULT_BOLD);
        card.addView(mStatusKnob);

        root.addView(card);

        // =========================================================================
        // 🎯 1. 메인 프레임 컨테이너 (최신맞춤판 SSOT 정본 스케줄)
        // =========================================================================
        mFrameMainContainer = createFrameContainer(
                "🎯 [메인 프레임] 주파수 통합 운용 마스터 보고서 (최신맞춤판 SSOT)",
                "갤럭시 S7 + 120W/60W 우퍼 전용 앰프 바닥 슬래브 2점 광역 앵커 전용",
                "#00E5FF",
                "#0D1926"
        );

        // 파트 1: 24시간 4구간 표준 맞춤 스케줄
        addSectionHeaderInsideFrame(mFrameMainContainer, "1️⃣ [파트 1] 하루 4등분 시간대별 표준 맞춤 스케줄", "#00E5FF");

        LinearLayout mRow1 = new LinearLayout(this);
        mRow1.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow1,
                "🌅 아침 (07~13시)",
                "7.0Hz 단독 고정 | 천장 슬래브 직타",
                "🎛️DSP: +3dB펀치·트루피크0dBFS·BTL모노",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 7.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 0, 2, false,
                                15,
                                "[아침 07~13시] 7.0Hz 단독 고정 (천장 슬래브 직타 앵커)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(mRow1,
                "☀️ 오후 (13~19시)",
                "22.0Hz 단독 고정 | 소화기·안구 타격 직타",
                "🎛️DSP: +3dB펀치·새추레이터·2차배음ON",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 22.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                3.0f, 1, 2, true,
                                15,
                                "[오후 13~19시] 22.0Hz 단독 고정 (소화기·안구 타격 직타)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameMainContainer.addView(mRow1);

        LinearLayout mRow2 = new LinearLayout(this);
        mRow2.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(mRow2,
                "🌆 저녁 (19~01시)",
                "첫 10분 55Hz 기습 → 본모드 40.0Hz 직타",
                "🎛️DSP: +6dB초강력·새추레이터·BTL모노",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 40.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                6.0f, 1, 2, false,
                                15,
                                "[저녁 19~01시] 40.0Hz 천장 직타 (첫10분 55Hz 기습 타격)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(mRow2,
                "🌙 취침 (01~07시)",
                "55.0Hz 단독 고정 | 311호 요격 앵커",
                "🎛️DSP: 0dB원음·트루피크0dBFS·BTL모노",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f,
                                false, 0.0f, 1.0f,
                                false, 0.0f, 1.0f,
                                0.0f, 0, 2, false,
                                15,
                                "[취침 01~07시] 55.0Hz 단독 고정 (311호 요격 앵커 천장 직타)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameMainContainer.addView(mRow2);

        // 파트 2: 트랜스2 5대 고유 전술 모드
        addSectionHeaderInsideFrame(mFrameMainContainer, "2️⃣ [파트 2] 트랜스2 5대 고유 전술 모드 (원터치 직접 선택)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "🎯 [단독 1순위] 55.0 Hz 요격 앵커 (천장 수직 직타)",
                "천장 슬래브 수직 밀착 타격으로 311호 55Hz 공격 원천 상쇄 및 역제압",
                "🎛️ Vorta DSP: 부스트 0dB (순수 사인파) | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[트랜스2 단독 1순위] 55.0Hz 요격 앵커 (천장 수직 직타)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔨 [단독 2순위] 43.2 Hz 슬래브 관통 강타 (콘크리트 심층 투과)",
                "천장 콘크리트 코어를 깊숙이 뚫고 들어가 311호 바닥을 망치로 찍듯 수직 타격",
                "🎛️ Vorta DSP: 부스트 +3dB (강타) | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[트랜스2 단독 2순위] 43.2Hz 슬래브 관통 강타",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "⚡ [단독 3순위] 32.8 Hz 흉부·복부 압박 (내장 공명 유도)",
                "체류 시 호흡 답답함·신경 피로·불안감 유발 (인체 내부 공진 대역 타격)",
                "🎛️ Vorta DSP: 부스트 +3dB (펀치) | 아날로그 소프트 새추레이터 | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[트랜스2 단독 3순위] 32.8Hz 흉부·복부 압박",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔄 [스윕 1순위] 38.0 ~ 68.0 Hz (60초 주기 슬래브 순환)",
                "천장 슬래브 1차~4차 고유 공진 모드를 60초마다 전주파 훑으며 융단폭격",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS 리미터 | BTL 모노",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[트랜스2 스윕 1순위] 38.0~68.0Hz (60초 주기 슬래브 순환)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌪️ [스윕 2순위] 50.0 ~ 60.0 Hz (15초 주기 고속 급습)",
                "핵심 공진점 55Hz 주변을 15초마다 초고속 왕복 급습하여 내성 형성 원천 분쇄",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 60.0f, 15.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[트랜스2 스윕 2순위] 50.0~60.0Hz (15초 주기 고속 급습)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        // 파트 3: 8대 상황별 맞춤 실행 (S6 전담 전술)
        addSectionHeaderInsideFrame(mFrameMainContainer, "3️⃣ [파트 3] 8대 상황별 맞춤 실행 (S6 전담 전술)", "#00E5FF");

        addFullPresetButton(mFrameMainContainer,
                "상황 ① 일반 외출 (2~5시간): 38.0 ~ 68.0 Hz (60초 스윕)",
                "단기 부재 시 천장 전 대역 고유 공진 60초 순환 가진",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | 트루피크 0.0dBFS | BTL 모노",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황① 일반외출 2~5h] 38.0~68.0Hz(60초) 슬래브 순환",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ② 출근 (07:00~19:00 12시간): 38.0 ~ 68.0 Hz (60초 스윕)",
                "장시간 무인 출근 시 슬래브 과열 방지 및 연속 타격",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황② 출근 12h] 38.0~68.0Hz(60초) 슬래브 순환",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ③ 장기 외출 (48시간+): 38.0 ~ 68.0 Hz (60초 스윕)",
                "이틀 이상 무인 초장기 가동 안정성 확보",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#79C0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황③ 장기외출 48h+] 38.0~68.0Hz(60초) 슬래브 순환",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ④ 상대 도발 즉시 보복: 55.0 Hz 단독 고정",
                "발망치 직후 천장 슬래브 공진 1:1 즉각 타격",
                "🎛️ Vorta DSP: 부스트 +6dB (초강력) | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, false, 15,
                                "[상황④ 즉각보복] 55.0Hz 단독 고정 (천장 수직 타격)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑤ 주말 낮 체류 (13:00~17:00): 32.8 Hz 단독 고정",
                "주말 휴식 시간대 흉복부 내장 공진 자극",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[상황⑤ 주말낮] 32.8Hz 단독 고정 (흉복부 압박)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑥ 심야 수면 (23:00~07:00): 55.0 Hz 단독 고정",
                "211호 0dB 스텔스 유지 및 311호 수면 박탈",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황⑥ 심야수면] 55.0Hz 단독 고정 (천장 수직 락온)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑦ 천장 골전도 1:1 집중 타격: 43.2 Hz 단독 고정",
                "슬래브 코어 깊숙이 망치로 찍듯 수직 타격",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[상황⑦ 집중타격] 43.2Hz 단독 고정 (슬래브 관통)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "상황 ⑧ 3시간+ 연속 유지 (앰프 보호): 55.0 Hz 단독 고정",
                "장시간 가동 시 120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB",
                "🎛️ Vorta DSP: 부스트 0dB (원음) | 트루피크 0.0dBFS | BTL 모노",
                "#00F0FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[상황⑧ 장시간유지] 55.0Hz 단독 고정 (장비 보호 모드)",
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

        // 파트 1: 스케줄 C 무인 라이프사이클
        addSectionHeaderInsideFrame(mFrameSub1Container, "1️⃣ [파트 1] 스케줄 C: 사용자 수면 & 출근 무인 자율 스케줄", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "🏢 1. 외출·출근 블록 (08:30~18:30 10h): 38.0~68.0Hz (60s)",
                "출근 시 1회 터치 후 10시간 완전 무인 자동 순환 | 슬래브 융단 폭격",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄C-1] 외출·출근 (38.0~68.0Hz 60s 슬래브 융단)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🚪 2. 퇴근·저녁 블록 (18:30~23:00 4.5h): 40.0Hz 천장 직타",
                "귀가자 즉각 제압 및 흉곽 압박 (첫 10분 55Hz 기습 타격 포함)",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 40.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, false, 15,
                                "[서브1 스케줄C-2] 퇴근·저녁 40.0Hz 천장 직타 (흉곽 압박)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🛏️ 3. 취침·수면 블록 (23:00~08:30 9.5h): 55.0Hz 천장 락온",
                "211호 0dB 무음 숙면 보장 & 311호 수면 박탈 락온",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄C-3] 취침·수면 55.0Hz 천장 락온 앵커",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        // 파트 2: 스케줄 A 광역 중저역 순환
        addSectionHeaderInsideFrame(mFrameSub1Container, "2️⃣ [파트 2] 스케줄 A: 광역 중저역 순환 스케줄 (30~50Hz 확장)", "#38D39F");

        LinearLayout sub1RowA = new LinearLayout(this);
        sub1RowA.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub1RowA,
                "🌅 오전 중역 (07~12시)",
                "40.0 ~ 50.0Hz (240s 스윕)",
                "슬래브 2차 공진 훑기 가진",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 40.0f, 50.0f, 240.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄A] 오전 40.0~50.0Hz (240초 스윕)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub1RowA,
                "☀️ 오후 고정 (12~18시)",
                "45.0Hz 단독 고정 직타",
                "중저역 연속 진동 가진",
                "#D2A8FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 45.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄A] 오후 45.0Hz 단독 고정 직타",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub1Container.addView(sub1RowA);

        LinearLayout sub1RowB = new LinearLayout(this);
        sub1RowB.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub1RowB,
                "🌆 저녁 중역 (18~23시)",
                "35.0 ~ 48.0Hz (300s 스윕)",
                "복합 슬래브 굽힘파",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 35.0f, 48.0f, 300.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄A] 저녁 35.0~48.0Hz (300초 스윕)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub1RowB,
                "🌙 야간 초저역 (23~07시)",
                "20.0 ~ 25.0Hz (600s 스윕)",
                "비가청 전정기관 타격",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 20.0f, 25.0f, 600.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄A] 야간 20.0~25.0Hz (600초 초저역 스윕)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub1Container.addView(sub1RowB);

        // 파트 3: 스케줄 B 핵심 전술 정밀 프리셋
        addSectionHeaderInsideFrame(mFrameSub1Container, "3️⃣ [파트 3] 스케줄 B: 핵심 전술 정밀 프리셋", "#38D39F");

        addFullPresetButton(mFrameSub1Container,
                "⚡ 43.2 Hz 슬래브 관통 강타 (콘크리트 1타 해머)",
                "15cm 콘크리트 슬래브를 가장 빠르게 관통하여 311호 바닥 수직 직타",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄B] 43.2Hz 슬래브 관통 강타",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "💥 32.8 Hz 흉복부 압박 (내장 공명 유도)",
                "인체 흉곽 및 복부 고유 진동수와 일치하여 호흡 답답함 유발",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브1 스케줄B] 32.8Hz 흉복부 압박",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🎯 55.0 Hz 야간 요격 앵커 (311호 내장진동 상쇄)",
                "311호의 야간 55Hz 공격을 슬래브 공진점에서 상쇄 및 역제압",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브1 스케줄B] 55.0Hz 야간 요격 앵커",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "👁️ 18.98 Hz 안구 공진 앵커 (비가청 스텔스)",
                "안구 고유 진동수(18Hz) 자극으로 안구 떨림 및 신경 피로 유발",
                "🎛️ Vorta DSP: 부스트 +6dB | 2차 배음 ON | BTL 모노",
                "#00E5FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 18.98f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, true, 15,
                                "[서브1 스케줄B] 18.98Hz 안구 공진 앵커",
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

        // 파트 1: ver2 4대 표준 시간대 스케줄
        addSectionHeaderInsideFrame(mFrameSub2Container, "1️⃣ [파트 1] ver2 4대 표준 시간대 스케줄", "#A371F7");

        LinearLayout sub2RowA = new LinearLayout(this);
        sub2RowA.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub2RowA,
                "🚶 주간 외출 (09~18시)",
                "38.0 ~ 68.0Hz (60s 스윕)",
                "천장 슬래브 전면 순환",
                "#58A6FF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 ver2-1] 주간 외출 38.0~68.0Hz (60s)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub2RowA,
                "💥 저녁 집중 (18~23시)",
                "50.0 ~ 60.0Hz (15s 급습)",
                "공진점 주변 빠른 왕복",
                "#FFD700",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 60.0f, 15.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 ver2-2] 저녁 집중 50.0~60.0Hz (15s 급습)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub2Container.addView(sub2RowA);

        LinearLayout sub2RowB = new LinearLayout(this);
        sub2RowB.setOrientation(LinearLayout.HORIZONTAL);
        addHalfPresetButton(sub2RowB,
                "💤 심야 취침 (23~07시)",
                "55.0Hz 단독 요격 앵커",
                "야간 0dB 스텔스 요격",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 ver2-3] 심야 취침 55.0Hz 단독 요격 앵커",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addHalfPresetButton(sub2RowB,
                "⏰ 아침 기상 (07~09시)",
                "43.2Hz 관통 강타",
                "1타 콘크리트 해머",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 ver2-4] 아침 기상 43.2Hz 슬래브 관통 강타",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });
        mFrameSub2Container.addView(sub2RowB);

        // 파트 2: ver2 핵심 전술 프리셋
        addSectionHeaderInsideFrame(mFrameSub2Container, "2️⃣ [파트 2] ver2 핵심 전술 프리셋", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🎯 [ver2 전술1] 55.0 Hz 순수 앵커",
                "천장 슬래브 고유 공진 모드 100% 무왜곡 직타",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#39FF14",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 전술1] 55.0Hz 순수 앵커",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔨 [ver2 전술2] 43.2 Hz 콘크리트 해머",
                "천장 슬래브 깊숙이 망치로 찍어내리는 1타 강타",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 43.2f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 전술2] 43.2Hz 콘크리트 해머",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "⚡ [ver2 전술3] 32.8 Hz 장기 공명 타격",
                "흉복부 내장 기관 진동 유도",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#E040FB",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 32.8f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 전술3] 32.8Hz 장기 공명 타격",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🌪️ [ver2 전술4] 50.0 ~ 60.0 Hz (15초 급습)",
                "핵심 공진점 15초 왕복 급습",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FFA657",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 50.0f, 60.0f, 15.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                3.0f, 1, 2, false, 15,
                                "[서브2 전술4] 50.0~60.0Hz (15초 급습)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        // 파트 3: ver2 긴급 대응 모드
        addSectionHeaderInsideFrame(mFrameSub2Container, "3️⃣ [파트 3] ver2 긴급 대응 3종 모드", "#A371F7");

        addFullPresetButton(mFrameSub2Container,
                "🚨 [긴급 1] 발망치 즉각 응징: 55.0 Hz 펄스",
                "상대 도발 감지 즉시 천장 수직 풀파워 투하",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FF5252",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                6.0f, 1, 2, false, 15,
                                "[서브2 긴급1] 발망치 즉각 응징 (55.0Hz 풀파워)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "💣 [긴급 2] 슬래브 전면 공진 타격: 38.0 ~ 68.0 Hz (60s)",
                "슬래브 전 대역 광역 타격으로 피로 누적",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#388BFD",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(true, 0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 긴급2] 슬래브 전면 공진 타격 (38~68Hz 60s)",
                                "120W 우퍼 앰프: VOL 12~1시(정격 60W) | FREQ 80~100Hz | BASS +2dB");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🛡️ [긴급 3] 24시간 무인 자동 방어: 55.0 Hz 상시 앵커",
                "311호 내장진동 상시 차단 방어선",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 0.0dBFS | BTL 모노",
                "#56D364",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPresetWithDsp(false, 55.0f, 0f, 38.0f, 68.0f, 60.0f,
                                false, 0.0f, 5.0f, false, 0.0f, 1.0f, false, 0.0f, 1.0f,
                                0.0f, 0, 2, false, 15,
                                "[서브2 긴급3] 24시간 무인 자동 방어 (55.0Hz 상시 앵커)",
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
        dspLp.setMargins(0, 0, 0, (int)(16 * density));
        dspCard.setLayoutParams(dspLp);

        // 0. Auto Preset Lock
        addDspSubLabel(dspCard, "0. 프리셋 실행 시 DSP 최적값 자동 로드 (Auto-Preset DSP Lock):");
        LinearLayout autoRow = new LinearLayout(this);
        autoRow.setOrientation(LinearLayout.HORIZONTAL);
        mAutoLockButtons[0] = createDspTabButton(autoRow, "자동 로드 ON (권장)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sAutoPresetDsp = true;
                notifyDspChanged("프리셋 자동 DSP 로드 활성화");
            }
        });
        mAutoLockButtons[1] = createDspTabButton(autoRow, "수동 유지 (Manual)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sAutoPresetDsp = false;
                notifyDspChanged("수동 DSP 모드 전환");
            }
        });
        dspCard.addView(autoRow);

        // 1. Bass Boost
        addDspSubLabel(dspCard, "1. 초저역 에너지 부스트 (Digital Analog Gain Swing):");
        LinearLayout boostRow = new LinearLayout(this);
        boostRow.setOrientation(LinearLayout.HORIZONTAL);
        mBoostButtons[0] = createDspTabButton(boostRow, "0dB (순수원음)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setBassBoost(0.0f);
            }
        });
        mBoostButtons[1] = createDspTabButton(boostRow, "+3dB (강타 펀치)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setBassBoost(3.0f);
            }
        });
        mBoostButtons[2] = createDspTabButton(boostRow, "+6dB (익스트림 타격)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setBassBoost(6.0f);
            }
        });
        dspCard.addView(boostRow);

        // 2. Limiter / Saturator
        addDspSubLabel(dspCard, "2. 리미터 & 새추레이터 (True-Peak 0.0dBFS 무왜곡 정규화):");
        LinearLayout limiterRow = new LinearLayout(this);
        limiterRow.setOrientation(LinearLayout.HORIZONTAL);
        mLimiterButtons[0] = createDspTabButton(limiterRow, "트루피크 0.0dBFS 리미터", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sLimiterMode = 0;
                notifyDspChanged("트루피크 0.0dBFS 리미터 적용");
            }
        });
        mLimiterButtons[1] = createDspTabButton(limiterRow, "아날로그 소프트 새추레이터", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sLimiterMode = 1;
                notifyDspChanged("아날로그 소프트 새추레이터 적용");
            }
        });
        dspCard.addView(limiterRow);

        // 3. Channel Matrix
        addDspSubLabel(dspCard, "3. 트랜스2 BTL 출력 모드 (Output Matrix):");
        LinearLayout channelRow = new LinearLayout(this);
        channelRow.setOrientation(LinearLayout.HORIZONTAL);
        mChannelButtons[0] = createDspTabButton(channelRow, "BTL 모노 서밍(권장)", 1.2f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sChannelMode = 2;
                notifyDspChanged("BTL 모노 서밍(L+R) 적용");
            }
        });
        mChannelButtons[1] = createDspTabButton(channelRow, "L=R 동위상", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sChannelMode = 0;
                notifyDspChanged("L=R 동위상 적용");
            }
        });
        mChannelButtons[2] = createDspTabButton(channelRow, "L=-R 역위상(180°)", 1.1f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sChannelMode = 1;
                notifyDspChanged("L=-R 역위상(180°) 적용");
            }
        });
        dspCard.addView(channelRow);

        // 4. Harmonic Exciter
        addDspSubLabel(dspCard, "4. 2차 배음 익사이터 (슬래브 전달 효율 & 체감 진동 2배 강화):");
        LinearLayout exciterRow = new LinearLayout(this);
        exciterRow.setOrientation(LinearLayout.HORIZONTAL);
        mExciterButtons[0] = createDspTabButton(exciterRow, "🔥 2차 배음 보강 ON", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sHarmonicExciter = true;
                notifyDspChanged("2차 배음 익사이터 활성화");
            }
        });
        mExciterButtons[1] = createDspTabButton(exciterRow, "배음 OFF (순수 단일 기본파)", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                S7AudioGeneratorService.sHarmonicExciter = false;
                notifyDspChanged("배음 OFF (순수 기본파 모드)");
            }
        });
        dspCard.addView(exciterRow);

        root.addView(dspCard);

        // =========================================================================
        // 🛑 출력 제어 & 즉시 정지
        // =========================================================================
        addSectionHeader(root, "🛑 출력 제어");

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
                String bgHex = (i == 0) ? "#58A6FF" : (i == 1) ? "#00897B" : (i == 2) ? "#2EA043" : "#8A3FFC";
                String strokeHex = (i == 0) ? "#58A6FF" : (i == 1) ? "#00F0FF" : (i == 2) ? "#56D364" : "#D2A8FF";
                gd.setColor(Color.parseColor(bgHex));
                gd.setStroke((int)(2 * density), Color.parseColor(strokeHex));
                mSplitViewButtons[i].setBackground(gd);
                mSplitViewButtons[i].setTextColor(Color.WHITE);
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
        tSub.setTextSize(11);
        tSub.setTextColor(Color.parseColor("#FFFFFF"));
        tSub.setTypeface(Typeface.DEFAULT_BOLD);
        tSub.setPadding(0, 3, 0, 0);
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
        tv.setTextColor(Color.parseColor("#00F0FF"));
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
        int[] chValues = {2, 0, 1}; // Buttons 0, 1, 2 map to channel modes 2, 0, 1
        for (int i = 0; i < 3; i++) {
            if (mChannelButtons[i] == null) continue;
            boolean active = (curChannel == chValues[i]);
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

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor("#161B22"));
        gd.setCornerRadius(8 * density);
        gd.setStroke((int)(1.2f * density), Color.parseColor("#30363D"));
        btn.setBackground(gd);

        btn.setPadding((int)(12 * density), (int)(10 * density), (int)(12 * density), (int)(10 * density));
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lp.setMargins((int)(3 * density), (int)(3 * density), (int)(3 * density), (int)(3 * density));
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
        tSub.setPadding(0, (int)(3 * density), 0, (int)(2 * density));
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

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(Color.parseColor("#161B22"));
        gd.setCornerRadius(8 * density);
        gd.setStroke((int)(1.2f * density), Color.parseColor("#30363D"));
        btn.setBackground(gd);

        btn.setPadding((int)(14 * density), (int)(12 * density), (int)(14 * density), (int)(12 * density));
        btn.setClickable(true);
        btn.setFocusable(true);
        btn.setOnClickListener(listener);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, (int)(4 * density), 0, (int)(4 * density));
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
        tSub.setPadding(0, (int)(3 * density), 0, (int)(2 * density));
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

        Toast.makeText(this, title + " 발진 시작 (15/15 볼륨 고정)", Toast.LENGTH_SHORT).show();
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
            mStatusKnob.setText(S7AudioGeneratorService.sKnobGuide);
        }
    }
}
'''

with open(r'd:\D_Workspace_NB\주파수\vorta_s7_app\src\com\vorta\s7frequency\MainActivity.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("MainActivity.java written successfully!")
