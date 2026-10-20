package com.vorta.s6frequency;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.ImageView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final String TAG = "MainActivity";

    // Pinned Status Telemetry
    private LinearLayout mStatusCardLayout;
    private ImageView mStatusTrafficLight;
    private TextView mStatusMode;
    private TextView mStatusScenario;
    private TextView mStatusFreq;
    private TextView mStatusMod;
    private TextView mStatusKnob;

    // Split Screen Layout Containers
    private LinearLayout mFrameMainContainer;
    private LinearLayout mFrameSub1Container;
    private LinearLayout mFrameSub2Container;
    private LinearLayout mSplitDivider1;
    private LinearLayout mSplitDivider2;
    private TextView[] mSplitViewButtons = new TextView[4];
    private int mCurrentSplitMode = 0; // 0: 전체, 1: 메인, 2: 서브1, 3: 서브2

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

        // Load DSP Config & unlock safe volume without locking volume level
        S6AudioGeneratorService.loadConfig(this);
        S6VolumeHelper.ensureTargetVolumeIfNeeded(this, true);

        float density = getResources().getDisplayMetrics().density;

        // Unified Full-Screen ScrollView: The entire screen scrolls naturally with wide, expansive visibility!
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#0A0E17"));
        scroll.setFillViewport(true);
        scroll.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.MATCH_PARENT));

        LinearLayout contentPane = new LinearLayout(this);
        contentPane.setOrientation(LinearLayout.VERTICAL);
        contentPane.setPadding((int)(14 * density), (int)(14 * density), (int)(14 * density), (int)(28 * density));

        // Header Title 1 (H1) & Subtitle
        TextView titleTv = new TextView(this);
        titleTv.setText("보르타 레조 S6 v3.0");
        titleTv.setTextSize(20);
        titleTv.setTextColor(Color.parseColor("#00F0FF"));
        titleTv.setTypeface(Typeface.DEFAULT_BOLD);
        contentPane.addView(titleTv);

        TextView subTitleTv = new TextView(this);
        subTitleTv.setText("갤럭시 S6 + 트랜스2(68W BTL) 맞춤 주파수 발생기 | Vorta DSP");
        subTitleTv.setTextSize(11);
        subTitleTv.setTextColor(Color.parseColor("#E2E8F0"));
        subTitleTv.setPadding(0, (int)(2 * density), 0, (int)(8 * density));
        contentPane.addView(subTitleTv);

        // Realtime Telemetry Status Card
        LinearLayout statusCard = new LinearLayout(this);
        mStatusCardLayout = statusCard;
        statusCard.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable scBg = new GradientDrawable();
        scBg.setColor(Color.parseColor("#1E293B"));
        scBg.setCornerRadius(8 * density);
        scBg.setStroke((int)(1.5f * density), Color.parseColor("#EF4444"));
        statusCard.setBackground(scBg);
        statusCard.setPadding((int)(14 * density), (int)(10 * density), (int)(14 * density), (int)(10 * density));
        LinearLayout.LayoutParams scLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        scLp.setMargins(0, 0, 0, (int)(8 * density));
        statusCard.setLayoutParams(scLp);

        // Principle 12: Android 7 renders emoji as tofu, so the traffic light is a 16dp oval drawable.
        LinearLayout statusRow = new LinearLayout(this);
        statusRow.setOrientation(LinearLayout.HORIZONTAL);
        statusRow.setGravity(Gravity.CENTER_VERTICAL);
        mStatusTrafficLight = new ImageView(this);
        int dotSize = (int)(16 * density);
        LinearLayout.LayoutParams dotLp = new LinearLayout.LayoutParams(dotSize, dotSize);
        dotLp.setMargins(0, 0, (int)(8 * density), 0);
        mStatusTrafficLight.setLayoutParams(dotLp);
        GradientDrawable redDot = new GradientDrawable();
        redDot.setShape(GradientDrawable.OVAL);
        redDot.setColor(Color.parseColor("#FF3366"));
        mStatusTrafficLight.setImageDrawable(redDot);
        statusRow.addView(mStatusTrafficLight);

        mStatusMode = new TextView(this);
        mStatusMode.setText("상태: [작동 중지] 멈춤 (대기 상태)");
        mStatusMode.setTextSize(14);
        mStatusMode.setTextColor(Color.parseColor("#FF3366"));
        mStatusMode.setTypeface(Typeface.DEFAULT_BOLD);
        statusRow.addView(mStatusMode);
        statusCard.addView(statusRow);

        mStatusScenario = new TextView(this);
        mStatusScenario.setText("시나리오: 대기 중 (선택 없음)");
        mStatusScenario.setTextSize(13);
        mStatusScenario.setTextColor(Color.parseColor("#64748B"));
        mStatusScenario.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusScenario.setPadding(0, (int)(4 * density), 0, 0);
        statusCard.addView(mStatusScenario);

        mStatusFreq = new TextView(this);
        mStatusFreq.setText("발진: 0.00 Hz (출력 차단 / MUTE)");
        mStatusFreq.setTextSize(12);
        mStatusFreq.setTextColor(Color.parseColor("#94A3B8"));
        mStatusFreq.setTypeface(Typeface.DEFAULT_BOLD);
        mStatusFreq.setPadding(0, (int)(2 * density), 0, (int)(1 * density));
        statusCard.addView(mStatusFreq);

        mStatusMod = new TextView(this);
        mStatusMod.setText("변조: 비활성 (주파수 신호 멈춤) | BTL 대기");
        mStatusMod.setTextSize(11);
        mStatusMod.setTextColor(Color.parseColor("#64748B"));
        mStatusMod.setTypeface(Typeface.DEFAULT_BOLD);
        statusCard.addView(mStatusMod);

        mStatusKnob = new TextView(this);
        mStatusKnob.setText("앰프 노브: Lepy LP-168S [5개 다이얼] SUB VOL 3~5시 (정격 68W 골전도 풀파워) | X-OVER 80Hz | BASS 0dB");
        mStatusKnob.setTextSize(10);
        mStatusKnob.setTextColor(Color.parseColor("#94A3B8"));
        mStatusKnob.setPadding(0, (int)(2 * density), 0, 0);
        statusCard.addView(mStatusKnob);

        contentPane.addView(statusCard);

        // Emergency Stop Button
        TextView stopBtn = new TextView(this);
        stopBtn.setText("🛑 즉각 정지 (Mute / Stop)");
        stopBtn.setTextSize(14);
        stopBtn.setTextColor(Color.parseColor("#FFFFFF"));
        stopBtn.setTypeface(Typeface.DEFAULT_BOLD);
        stopBtn.setGravity(Gravity.CENTER);
        GradientDrawable stopBg = new GradientDrawable();
        stopBg.setColor(Color.parseColor("#DC2626"));
        stopBg.setCornerRadius(6 * density);
        stopBtn.setBackground(stopBg);
        stopBtn.setPadding(0, (int)(9 * density), 0, (int)(9 * density));
        LinearLayout.LayoutParams stopLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        stopLp.setMargins(0, 0, 0, (int)(8 * density));
        stopBtn.setLayoutParams(stopLp);
        stopBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent it = new Intent(MainActivity.this, S6AudioGeneratorService.class);
                it.putExtra("action", "stop");
                startService(it);
                S6AudioGeneratorService.sIsPlaying = false;
                S6AudioGeneratorService.sModeTitle = "🛑 [작동 중지] 발진 멈춤 (대기 상태)";
                S6AudioGeneratorService.sInstantFreq = 0.0f;
                syncTelemetryUi();
                Toast.makeText(MainActivity.this, "🛑 주파수 발진 정지 완료 (작동 중지)", Toast.LENGTH_SHORT).show();
            }
        });
        contentPane.addView(stopBtn);

        // 🎛️ Split View Console Menu Frame: Exactly [전체 / 메인 / 서브1 / 서브2]
        LinearLayout tabRow = new LinearLayout(this);
        tabRow.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams tabLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, (int)(42 * density));
        tabLp.setMargins(0, 0, 0, (int)(12 * density));
        tabRow.setLayoutParams(tabLp);

        mSplitViewButtons[0] = createSplitTabButton(tabRow, "🌐 전체", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(0);
            }
        });
        mSplitViewButtons[1] = createSplitTabButton(tabRow, "🎯 메인", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(1);
            }
        });
        mSplitViewButtons[2] = createSplitTabButton(tabRow, "⚡ 서브1", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(2);
            }
        });
        mSplitViewButtons[3] = createSplitTabButton(tabRow, "🛡️ 서브2", 1.0f, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                switchSplitView(3);
            }
        });
        contentPane.addView(tabRow);

        // -------------------------------------------------------------------------
        // 🎯 [메인 프레임] 통합운용 시나리오 버전1 (총 17개 프리셋)
        // -------------------------------------------------------------------------
        mFrameMainContainer = createFrameContainer(
                "🎯 [메인 프레임] 통합운용 시나리오 버전1 (최신 정본)",
                "24시간 4대 스케줄 + 9대 실전 맞춤 + 전술 요격 프리셋",
                "#00F0FF",
                "#082F49"
        );

        // [파트 1] 24시간 4대 시간대별 룸모드 직타 스케줄
        addSectionHeaderInsideFrame(mFrameMainContainer, "1️⃣ [파트 1] 🌅 24시간 4대 시간대별 룸모드 직타 스케줄", "#00F0FF");

        addFullPresetButton(mFrameMainContainer,
                "🌅 1. 아침 (07:00~13:00): 55.0 Hz 직타",
                "53.1~55Hz 룸모드 피크 관통 | FM 3.5% (1.50Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.035f, 1.50f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[메인 스케줄-1] 아침 55.0Hz 직타 (FM 3.5%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "☀️ 2. 오후 (13:00~19:00): 31.0 ~ 40.0 Hz (360초 스윕)",
                "흉벽 관통 불규칙 이중 파면 | RM 20% (12.50Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#FACC15",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(true, 0f, 0f, 31.0f, 40.0f, 360.0f,
                                false, 0f, 0f, false, 0f, 0f, true, 0.20f, 12.50f,
                                0f, 0, 2, false, 11,
                                "[메인 스케줄-2] 오후 31.0~40.0Hz 스윕 (RM 20%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌆 3. 저녁 (19:00~01:00): 43.2 Hz 직타",
                "120mm 슬래브 1타 기계 해머 직타 | AM 18% (2.80Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +3dB | 트루피크 -1.5dBFS | BTL 모노",
                "#FB923C",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.18f, 2.80f, false, 0f, 0f,
                                3.0f, 1, 2, false, 12,
                                "[메인 스케줄-3] 저녁 43.2Hz 슬래브 해머 (AM 18%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌙 4. 취침 (01:00~07:00): 55.0 Hz 락온",
                "침실 1차 정상파 초밀착 락온 | FM 2.5% (0.80Hz) | Vol 10",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#34D399",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.025f, 0.80f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 10,
                                "[메인 스케줄-4] 취침 55.0Hz 락온 (FM 2.5% 스텔스)",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        // [파트 2] 사용자 행동별 9대 실전 맞춤 시나리오
        addSectionHeaderInsideFrame(mFrameMainContainer, "2️⃣ [파트 2] 🎯 사용자 행동별 9대 실전 맞춤 시나리오", "#00F0FF");

        addFullPresetButton(mFrameMainContainer,
                "⚡ 1. 상대 공격 즉각 요격: 55.0 Hz 직타 (복합 변조)",
                "쿵쾅거림 즉시 룸모드 충격파 반격 | FM 3.5% + AM 15% | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#EF4444",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.035f, 1.50f, true, 0.15f, 2.00f, false, 0f, 0f,
                                6.0f, 1, 2, false, 12,
                                "[메인 행동-1] 상대공격 즉각요격 55.0Hz (복합변조)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🔨 2. 벌주기 (보복 타격): 40.0 Hz 두경부 직타",
                "1~2시간 강력 집중 응징 | RM 25% (15.00Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#F87171",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 40.0f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, false, 0f, 0f, true, 0.25f, 15.00f,
                                6.0f, 1, 2, false, 12,
                                "[메인 행동-2] 벌주기 40.0Hz 두경부 타격 (RM 25%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🏢 3. 출근 12시간 무인방어: 24.0 Hz / 43.2 Hz 교대 (600초)",
                "07~19시 부재중 자동 방어 | AM 15% / FM 4% 교대 | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 43.2f, 24.0f, 0f, 0f, 0f,
                                true, 0.04f, 1.20f, true, 0.15f, 2.50f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[메인 행동-3] 출근 12h 무인방어 24/43.2Hz 교대",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🚶 4. 일상 외출 자동 순항: 31.0 Hz 상복부 직타",
                "2~4시간 외출 시 기저 둔통 유지 | AM 12% (1.80Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#60A5FA",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 31.0f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.12f, 1.80f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[메인 행동-4] 일상외출 31.0Hz 상복부 직타 (AM 12%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🏰 5. 초장기 외출 (48h+): 55.0 Hz 인터벌 락온",
                "무인 요새화 | 30분 발진 / 15분 휴지 | FM 2.5% | Vol 10",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#818CF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.025f, 0.80f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 10,
                                "[메인 행동-5] 초장기 48h+ 55.0Hz 인터벌 락온",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "💥 6. 상대 내성 파괴: 24.0 Hz ↔ 55.0 Hz 급변 도약",
                "비선형 변조 도약으로 상대 신경 적응 무효화 | AM 20% | Vol 12",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#C084FC",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 55.0f, 24.0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.20f, 3.00f, false, 0f, 0f,
                                3.0f, 1, 2, false, 12,
                                "[메인 행동-6] 상대 내성파괴 24↔55Hz 급변 (AM 20%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🧠 7. 상대 정신 집중 차단: 40.0 Hz 뇌파 공진 직타",
                "재택/공부 방해, 인지 저하 유도 | RM 20% (10.00Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#A78BFA",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 40.0f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, false, 0f, 0f, true, 0.20f, 10.00f,
                                0f, 0, 2, false, 11,
                                "[메인 행동-7] 정신집중차단 40.0Hz 뇌파직타 (RM 20%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🛌 8. 수면 시간 집중 압박: 55.0 Hz 룸모드 락온",
                "새벽 1~5시 수면 단계 파괴 | FM 3.0% (0.80Hz) | Vol 10",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#34D399",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 55.0f, 0f, 0f, 0f, 0f,
                                true, 0.030f, 0.80f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 10,
                                "[메인 행동-8] 수면시간 집중압박 55.0Hz 락온 (FM 3%)",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🛡️ 9. 3시간 이상 기기 보호: 43.2 Hz 보호 모드",
                "보이스코일 발열 억제 운용 | AM 12% (1.50Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#2DD4BF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.12f, 1.50f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[메인 행동-9] 3시간+ 기기보호 43.2Hz (AM 12%)",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        // [파트 3] 전술 요격 및 룸모드 특수 프리셋
        addSectionHeaderInsideFrame(mFrameMainContainer, "3️⃣ [파트 3] 📊 전술 요격 및 룸모드 특수 프리셋", "#00F0FF");

        addFullPresetButton(mFrameMainContainer,
                "🔨 슬래브 120mm 1타 굽힘파: 43.2 Hz 단독 직타",
                "원음 무변조 수직 관통 해머 | Vol 12",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#F59E0B",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 43.2f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, false, 0f, 0f, false, 0f, 0f,
                                3.0f, 1, 2, false, 12,
                                "[메인 특수-1] 슬래브 120mm 굽힘파 43.2Hz 단독",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🎯 침실 1차 정상파 스텔스: 53.6 Hz 단독 직타",
                "침실 고유 공진 초밀착 락온 | FM 2.0% (0.50Hz) | Vol 10",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#10B981",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 53.6f, 0f, 0f, 0f, 0f,
                                true, 0.020f, 0.50f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 10,
                                "[메인 특수-2] 침실 1차 정상파 53.6Hz 직타 (FM 2%)",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌊 흉복부 중저역 스윕: 24.0 ~ 38.0 Hz (480초 스윕)",
                "흉복부 내장 공진 광역 훑기 | AM 15% (2.20Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(true, 0f, 0f, 24.0f, 38.0f, 480.0f,
                                false, 0f, 0f, true, 0.15f, 2.20f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[메인 특수-3] 흉복부 24.0~38.0Hz 스윕 (AM 15%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameMainContainer,
                "🌪️ 룸모드 고차 훑기: 40.0 ~ 55.0 Hz (300초 스윕)",
                "천장 전 대역 고유 공진 순환 가진 | FM 4.0% (1.00Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#6366F1",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(true, 0f, 0f, 40.0f, 55.0f, 300.0f,
                                true, 0.040f, 1.00f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[메인 특수-4] 룸모드 40.0~55.0Hz 스윕 (FM 4%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        contentPane.addView(mFrameMainContainer);

        // Divider between Main and Sub1
        mSplitDivider1 = createSplitDivider("▼ ⚡ 서브1 프레임 (통합운용 시나리오 버전2) ▼", "#10B981");
        contentPane.addView(mSplitDivider1);

        // -------------------------------------------------------------------------
        // ⚡ [서브1 프레임] 통합운용 시나리오 버전2 (총 11개 프리셋)
        // -------------------------------------------------------------------------
        mFrameSub1Container = createFrameContainer(
                "⚡ [서브1 프레임] 통합운용 시나리오 버전2 (상황 전술)",
                "하악골 골도 공진 + 2차 정상파 + 1Hz 맥놀이 충격파",
                "#10B981",
                "#064E3B"
        );

        // [파트 1] 24시간 4대 시간대별 마스터 스케줄 (v2)
        addSectionHeaderInsideFrame(mFrameSub1Container, "1️⃣ [파트 1] 🌅 24시간 4대 시간대별 룸모드 직타 스케줄 (v2)", "#10B981");

        addFullPresetButton(mFrameSub1Container,
                "🌅 1. 아침 (07:00~13:00 v2): 46.8 Hz 직타",
                "하악골 골도 공진 수직 해머 직타 | AM 16% (2.40Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 +3dB | 트루피크 -1.5dBFS | BTL 모노",
                "#34D399",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 46.8f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.16f, 2.40f, false, 0f, 0f,
                                3.0f, 1, 2, false, 11,
                                "[서브1 스케줄-1] 아침 46.8Hz 골도해머 (AM 16%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "☀️ 2. 오후 (13:00~19:00 v2): 51.5 Hz 직타",
                "311호 룸모드 2차 정상파 공진 추적 | FM 4.0% (1.20Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#2DD4BF",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 51.5f, 0f, 0f, 0f, 0f,
                                true, 0.040f, 1.20f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브1 스케줄-2] 오후 51.5Hz 2차정상파 (FM 4%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🌆 3. 저녁 (19:00~01:00 v2): 54.0 Hz 직타",
                "55Hz 인접 1.0Hz 맥놀이 충격파 직타 | RM 25% (1.00Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#FACC15",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 54.0f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, false, 0f, 0f, true, 0.25f, 1.00f,
                                6.0f, 1, 2, false, 12,
                                "[서브1 스케줄-3] 저녁 54.0Hz 1Hz맥놀이 (RM 25%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🌙 4. 취침 (01:00~07:00 v2): 36.5 ~ 44.5 Hz (600초 스윕)",
                "흉골/갈비뼈 수직 미세 펄스 훑기 | AM 12% (1.50Hz) | Vol 10",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(true, 0f, 0f, 36.5f, 44.5f, 600.0f,
                                false, 0f, 0f, true, 0.12f, 1.50f, false, 0f, 0f,
                                0f, 0, 2, false, 10,
                                "[서브1 스케줄-4] 취침 36.5~44.5Hz 흉골스윕 (AM 12%)",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        // [파트 2] 사용자 행동별 실전 맞춤 시나리오 (v2)
        addSectionHeaderInsideFrame(mFrameSub1Container, "2️⃣ [파트 2] 🎯 사용자 행동별 실전 맞춤 시나리오 (v2)", "#10B981");

        addFullPresetButton(mFrameSub1Container,
                "⚡ 1. 상대 공격 즉각 반격 (v2): 54.0 Hz 직타",
                "하향 충격파 동시 발진 | RM 25% + AM 15% | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#EF4444",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 54.0f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.15f, 2.00f, true, 0.25f, 1.00f,
                                6.0f, 1, 2, false, 12,
                                "[서브1 행동-1] 즉각반격 54.0Hz 충격파 (RM+AM)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🔨 2. 벌주기 (미로기관 파쇄): 46.8 Hz 두개골 직타",
                "안구/두개골 공진 입체 파쇄 | FM 5.0% (2.00Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#F87171",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 46.8f, 0f, 0f, 0f, 0f,
                                true, 0.050f, 2.00f, false, 0f, 0f, false, 0f, 0f,
                                6.0f, 1, 2, false, 12,
                                "[서브1 행동-2] 벌주기 46.8Hz 두개골파쇄 (FM 5%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🏢 3. 출근 12시간 무인방어 (v2): 36.5 Hz / 51.5 Hz 교대 (720초)",
                "v2 독자 대역 순환 신경 피로 극대화 | AM 12% / FM 4% | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 51.5f, 36.5f, 0f, 0f, 0f,
                                true, 0.040f, 1.20f, true, 0.12f, 1.50f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브1 행동-3] 출근 12h 36.5/51.5Hz 교대 (AM/FM)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "💥 4. 상대 내성 완전파괴 (v2): 33.0 Hz ↔ 54.0 Hz 급변 도약",
                "주파수 비선형 도약 예측 불허 타격 | AM 20% (3.50Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#C084FC",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 54.0f, 33.0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.20f, 3.50f, false, 0f, 0f,
                                3.0f, 1, 2, false, 12,
                                "[서브1 행동-4] 내성완전파괴 33↔54Hz 급변 (AM 20%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🧠 5. 상대 정신 집중차단 (v2): 46.8 Hz 뇌파 공진 직타",
                "골도 공진으로 두통 및 인지 마비 유도 | RM 20% (8.00Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#A78BFA",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 46.8f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, false, 0f, 0f, true, 0.20f, 8.00f,
                                0f, 0, 2, false, 11,
                                "[서브1 행동-5] 정신집중차단 46.8Hz 뇌파직타 (RM 20%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        // [파트 3] v2 고유 음향역학 변조 전술 프리셋
        addSectionHeaderInsideFrame(mFrameSub1Container, "3️⃣ [파트 3] 📊 v2 고유 음향역학 변조 전술 프리셋", "#10B981");

        addFullPresetButton(mFrameSub1Container,
                "🦴 하악골 골도 공진 단독: 46.8 Hz 단독 직타",
                "골도 공진 순수 타격 해머 | AM 16% (2.40Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 +3dB | 트루피크 -1.5dBFS | BTL 모노",
                "#10B981",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 46.8f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.16f, 2.40f, false, 0f, 0f,
                                3.0f, 1, 2, false, 11,
                                "[서브1 특수-1] 하악골 골도공진 46.8Hz 단독 (AM 16%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub1Container,
                "🎯 2차 정상파 수직 관통: 51.5 Hz 단독 직타",
                "침실 2차 정상파 수직 관통 락온 | FM 4.0% (1.20Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#14B8A6",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 51.5f, 0f, 0f, 0f, 0f,
                                true, 0.040f, 1.20f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브1 특수-2] 2차 정상파 51.5Hz 관통 (FM 4%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        contentPane.addView(mFrameSub1Container);

        // Divider between Sub1 and Sub2
        mSplitDivider2 = createSplitDivider("▼ 🛡️ 서브2 프레임 (통합운용 시나리오 버전3) ▼", "#A855F7");
        contentPane.addView(mSplitDivider2);

        // -------------------------------------------------------------------------
        // 🛡️ [서브2 프레임] 통합운용 시나리오 버전3 (총 10개 프리셋)
        // -------------------------------------------------------------------------
        mFrameSub2Container = createFrameContainer(
                "🛡️ [서브2 프레임] 통합운용 시나리오 버전3 (장기 방어)",
                "슬래브 전단파 + 고차 굽힘파 + 1차 정상파 초정밀 락온",
                "#A855F7",
                "#3B0764"
        );

        // [파트 1] 24시간 4대 시간대별 마스터 스케줄 (v3)
        addSectionHeaderInsideFrame(mFrameSub2Container, "1️⃣ [파트 1] 🌅 24시간 4대 시간대별 룸모드 직타 스케줄 (v3)", "#A855F7");

        addFullPresetButton(mFrameSub2Container,
                "🌅 1. 아침 (07:00~13:00 v3): 37.0 Hz 직타",
                "슬래브 전단파 요동 수직 관통 | FM 5.0% (1.60Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#C084FC",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 37.0f, 0f, 0f, 0f, 0f,
                                true, 0.050f, 1.60f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브2 스케줄-1] 아침 37.0Hz 전단파 직타 (FM 5%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "☀️ 2. 오후 (13:00~19:00 v3): 48.5 Hz 직타",
                "슬래브 고차 굽힘파 기계 해머 직타 | AM 18% (3.10Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 +3dB | 트루피크 -1.5dBFS | BTL 모노",
                "#E879F9",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 48.5f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.18f, 3.10f, false, 0f, 0f,
                                3.0f, 1, 2, false, 11,
                                "[서브2 스케줄-2] 오후 48.5Hz 고차굽힘파 (AM 18%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🌆 3. 저녁 (19:00~01:00 v3): 53.2 Hz 직타",
                "311호 1차 정상파(53.6Hz) 초정밀 락온 | FM 3.0% (0.80Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#F472B6",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 53.2f, 0f, 0f, 0f, 0f,
                                true, 0.030f, 0.80f, false, 0f, 0f, false, 0f, 0f,
                                6.0f, 1, 2, false, 12,
                                "[서브2 스케줄-3] 저녁 53.2Hz 정상파 락온 (FM 3%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🌙 4. 취침 (01:00~07:00 v3): 42.0 ~ 47.5 Hz (580초 스윕)",
                "침대 프레임 골도 미세 펄스 훑기 | AM 10% (1.20Hz) | Vol 10",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(true, 0f, 0f, 42.0f, 47.5f, 580.0f,
                                false, 0f, 0f, true, 0.10f, 1.20f, false, 0f, 0f,
                                0f, 0, 2, false, 10,
                                "[서브2 스케줄-4] 취침 42.0~47.5Hz 골도스윕 (AM 10%)",
                                "LP-168S: SUB 3.0(9시) | X-OVER 65Hz | VOL 5.0");
                    }
                });

        // [파트 2] 사용자 행동별 실전 맞춤 시나리오 (v3)
        addSectionHeaderInsideFrame(mFrameSub2Container, "2️⃣ [파트 2] 🎯 사용자 행동별 실전 맞춤 시나리오 (v3)", "#A855F7");

        addFullPresetButton(mFrameSub2Container,
                "⚡ 1. 상대 공격 즉각 반격 (v3): 53.2 Hz 정상파 직타",
                "침실 룸모드 즉각 현기증 유발 | FM 3.0% + AM 18% | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#EF4444",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 53.2f, 0f, 0f, 0f, 0f,
                                true, 0.030f, 0.80f, true, 0.18f, 2.00f, false, 0f, 0f,
                                6.0f, 1, 2, false, 12,
                                "[서브2 행동-1] 즉각반격 53.2Hz 정상파 직타 (FM+AM)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🔨 2. 벌주기 (흉곽 슐만 파쇄): 37.0 Hz 슬래브 직타",
                "슐만 2차 고조파 연동 흉곽/척추 집중 타격 | AM 18% (2.50Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +6dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#F87171",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 37.0f, 0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.18f, 2.50f, false, 0f, 0f,
                                6.0f, 1, 2, false, 12,
                                "[서브2 행동-2] 벌주기 37.0Hz 흉곽슐만파쇄 (AM 18%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🏢 3. 출근 12시간 무인방어 (v3): 37.0 Hz / 53.2 Hz 교대 (600초)",
                "3주차 고유 주파수 및 3기기 변조 조화 | FM 5% / FM 3% | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#38BDF8",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 53.2f, 37.0f, 0f, 0f, 0f,
                                true, 0.050f, 1.60f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브2 행동-3] 출근 12h 37.0/53.2Hz 교대 (FM)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "💥 4. 상대 내성 완전파괴 (v3): 37.0 Hz ↔ 53.2 Hz 급변",
                "광대역 카오스 도약 복합 조화 | AM 20% (3.20Hz) | Vol 12",
                "🎛️ Vorta DSP: 부스트 +3dB | 아날로그 소프트 새추레이터 | BTL 모노",
                "#C084FC",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 53.2f, 37.0f, 0f, 0f, 0f,
                                false, 0f, 0f, true, 0.20f, 3.20f, false, 0f, 0f,
                                3.0f, 1, 2, false, 12,
                                "[서브2 행동-4] 내성완전파괴 37↔53.2Hz 급변 (AM 20%)",
                                "LP-168S: SUB 4.0(10시) | X-OVER 85Hz | VOL 6.0");
                    }
                });

        // [파트 3] v3 고유 전단파/정상파 특수 프리셋
        addSectionHeaderInsideFrame(mFrameSub2Container, "3️⃣ [파트 3] 📊 v3 고유 전단파/정상파 특수 프리셋", "#A855F7");

        addFullPresetButton(mFrameSub2Container,
                "🌊 슬래브 전단파 수직 관통: 37.0 Hz 단독 직타",
                "전단파 요동 단독 관통 | FM 5.0% (1.60Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#A855F7",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 37.0f, 0f, 0f, 0f, 0f,
                                true, 0.050f, 1.60f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브2 특수-1] 슬래브 전단파 37.0Hz 단독 (FM 5%)",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        addFullPresetButton(mFrameSub2Container,
                "🎯 침실 1차 정상파 초정밀 락온: 53.2 Hz 단독 직타",
                "침실 룸모드 피크 극점 단독 직타 | FM 3.0% (0.80Hz) | Vol 11",
                "🎛️ Vorta DSP: 부스트 0dB | 트루피크 -1.5dBFS | BTL 모노",
                "#EC4899",
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        startPreset(false, 53.2f, 0f, 0f, 0f, 0f,
                                true, 0.030f, 0.80f, false, 0f, 0f, false, 0f, 0f,
                                0f, 0, 2, false, 11,
                                "[서브2 특수-2] 1차 정상파 53.2Hz 초정밀 락온",
                                "LP-168S: SUB 3.5(9시반) | X-OVER 65~85Hz | VOL 5.5");
                    }
                });

        contentPane.addView(mFrameSub2Container);

        scroll.addView(contentPane);
        setContentView(scroll);
        switchSplitView(0); // Default: 전체
    }

    @Override
    protected void onResume() {
        super.onResume();
        mUiHandler.post(mTelemetryUpdater);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mUiHandler.removeCallbacks(mTelemetryUpdater);
    }

    // =========================================================================
    // 🎛️ Split View Switching Logic: Exactly [전체 / 메인 / 서브1 / 서브2]
    // =========================================================================
    private void switchSplitView(int modeIndex) {
        mCurrentSplitMode = modeIndex;
        float density = getResources().getDisplayMetrics().density;

        for (int i = 0; i < 4; i++) {
            GradientDrawable tabBg = new GradientDrawable();
            if (i == modeIndex) {
                tabBg.setColor(Color.parseColor("#0284C7")); // Active Sky Blue
                tabBg.setCornerRadius(6 * density);
                mSplitViewButtons[i].setTextColor(Color.parseColor("#FFFFFF"));
                mSplitViewButtons[i].setTypeface(Typeface.DEFAULT_BOLD);
            } else {
                tabBg.setColor(Color.parseColor("#1E293B")); // Inactive Slate
                tabBg.setCornerRadius(6 * density);
                mSplitViewButtons[i].setTextColor(Color.parseColor("#94A3B8"));
                mSplitViewButtons[i].setTypeface(Typeface.DEFAULT);
            }
            mSplitViewButtons[i].setBackground(tabBg);
        }

        if (modeIndex == 0) { // 전체
            mFrameMainContainer.setVisibility(View.VISIBLE);
            mSplitDivider1.setVisibility(View.VISIBLE);
            mFrameSub1Container.setVisibility(View.VISIBLE);
            mSplitDivider2.setVisibility(View.VISIBLE);
            mFrameSub2Container.setVisibility(View.VISIBLE);
        } else if (modeIndex == 1) { // 메인
            mFrameMainContainer.setVisibility(View.VISIBLE);
            mSplitDivider1.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.GONE);
        } else if (modeIndex == 2) { // 서브1
            mFrameMainContainer.setVisibility(View.GONE);
            mSplitDivider1.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.VISIBLE);
            mSplitDivider2.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.GONE);
        } else if (modeIndex == 3) { // 서브2
            mFrameMainContainer.setVisibility(View.GONE);
            mSplitDivider1.setVisibility(View.GONE);
            mFrameSub1Container.setVisibility(View.GONE);
            mSplitDivider2.setVisibility(View.GONE);
            mFrameSub2Container.setVisibility(View.VISIBLE);
        }
    }

    private TextView createSplitTabButton(LinearLayout parent, String text, float weight, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;
        TextView btn = new TextView(this);
        btn.setText(text);
        btn.setTextSize(13);
        btn.setGravity(Gravity.CENTER);
        btn.setSingleLine(true);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, weight);
        lp.setMargins((int)(2 * density), 0, (int)(2 * density), 0);
        btn.setLayoutParams(lp);
        btn.setOnClickListener(listener);
        parent.addView(btn);
        return btn;
    }

    private LinearLayout createFrameContainer(String title, String desc, String accentColor, String cardBgColor) {
        float density = getResources().getDisplayMetrics().density;
        LinearLayout frame = new LinearLayout(this);
        frame.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#0F172A"));
        bg.setCornerRadius(10 * density);
        bg.setStroke((int)(1.5f * density), Color.parseColor(accentColor));
        frame.setBackground(bg);
        frame.setPadding((int)(14 * density), (int)(12 * density), (int)(14 * density), (int)(14 * density));

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, (int)(16 * density));
        frame.setLayoutParams(lp);

        TextView tvTitle = new TextView(this);
        tvTitle.setText(title);
        tvTitle.setTextSize(16);
        tvTitle.setTextColor(Color.parseColor(accentColor));
        tvTitle.setTypeface(Typeface.DEFAULT_BOLD);
        frame.addView(tvTitle);

        TextView tvDesc = new TextView(this);
        tvDesc.setText(desc);
        tvDesc.setTextSize(11);
        tvDesc.setTextColor(Color.parseColor("#CBD5E1"));
        tvDesc.setPadding(0, (int)(2 * density), 0, (int)(10 * density));
        frame.addView(tvDesc);

        return frame;
    }

    private void addSectionHeaderInsideFrame(LinearLayout frame, String sectionTitle, String color) {
        float density = getResources().getDisplayMetrics().density;
        TextView header = new TextView(this);
        header.setText(sectionTitle);
        header.setTextSize(13);
        header.setTextColor(Color.parseColor(color));
        header.setTypeface(Typeface.DEFAULT_BOLD);
        header.setPadding(0, (int)(10 * density), 0, (int)(6 * density));
        frame.addView(header);
    }

    private LinearLayout createSplitDivider(String text, String color) {
        float density = getResources().getDisplayMetrics().density;
        LinearLayout divider = new LinearLayout(this);
        divider.setOrientation(LinearLayout.VERTICAL);
        divider.setGravity(Gravity.CENTER);
        divider.setPadding(0, (int)(4 * density), 0, (int)(12 * density));

        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(12);
        tv.setTextColor(Color.parseColor(color));
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        divider.addView(tv);

        return divider;
    }

    private void addFullPresetButton(LinearLayout parent, String mainText, String subText, String dspText,
                                     String accentColor, View.OnClickListener listener) {
        float density = getResources().getDisplayMetrics().density;

        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#1E293B"));
        bg.setCornerRadius(8 * density);
        bg.setStroke((int)(1 * density), Color.parseColor("#334155"));
        card.setBackground(bg);
        card.setPadding((int)(12 * density), (int)(10 * density), (int)(12 * density), (int)(10 * density));

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, (int)(3 * density), 0, (int)(5 * density));
        card.setLayoutParams(lp);

        TextView tvMain = new TextView(this);
        tvMain.setText(mainText);
        tvMain.setTextSize(13);
        tvMain.setTextColor(Color.parseColor("#FFFFFF"));
        tvMain.setTypeface(Typeface.DEFAULT_BOLD);
        card.addView(tvMain);

        TextView tvSub = new TextView(this);
        tvSub.setText(subText);
        tvSub.setTextSize(11);
        tvSub.setTextColor(Color.parseColor("#CBD5E1"));
        tvSub.setPadding(0, (int)(2 * density), 0, (int)(2 * density));
        card.addView(tvSub);

        TextView tvDsp = new TextView(this);
        tvDsp.setText(dspText);
        tvDsp.setTextSize(10);
        tvDsp.setTextColor(Color.parseColor(accentColor));
        tvDsp.setTypeface(Typeface.DEFAULT_BOLD);
        card.addView(tvDsp);

        card.setOnClickListener(listener);
        parent.addView(card);
    }

    private void startPreset(boolean sweep, float freq, float subFreq, float sMin, float sMax, float sSec,
                             boolean fmOn, float fmDepth, float fmRate,
                             boolean amOn, float amDepth, float amRate,
                             boolean rmOn, float rmDepth, float rmRate,
                             float boostDb, int limiterMode, int channelMode, boolean exciter, int volStep,
                             String title, String knobGuide) {
        Intent it = new Intent(this, S6AudioGeneratorService.class);
        it.putExtra("action", "start");
        it.putExtra("sweep", sweep);
        if (sweep) {
            it.putExtra("sweep_min", sMin);
            it.putExtra("sweep_max", sMax);
            it.putExtra("sweep_sec", sSec);
        } else {
            it.putExtra("freq", freq);
            it.putExtra("sub_freq", subFreq);
        }
        it.putExtra("fm_on", fmOn);
        it.putExtra("fm_depth", fmDepth);
        it.putExtra("fm_rate", fmRate);

        it.putExtra("am_on", amOn);
        it.putExtra("am_depth", amDepth);
        it.putExtra("am_rate", amRate);

        it.putExtra("rm_on", rmOn);
        it.putExtra("rm_depth", rmDepth);
        it.putExtra("rm_rate", rmRate);

        it.putExtra("bass_boost_db", boostDb);
        it.putExtra("limiter_mode", limiterMode);
        it.putExtra("channel_mode", channelMode);
        it.putExtra("harmonic_exciter", exciter);
        it.putExtra("vol_step", volStep);

        String partTag = "[메인 파트]";
        if (mCurrentSplitMode == 2 || title.contains("서브1") || title.contains("상황") || title.contains("보복") || title.contains("심리")) {
            partTag = "[서브1 파트]";
        } else if (mCurrentSplitMode == 3 || title.contains("서브2") || title.contains("장기") || title.contains("취침") || title.contains("출근")) {
            partTag = "[서브2 파트]";
        } else if (mCurrentSplitMode == 1) {
            partTag = "[메인 파트]";
        }
        S6AudioGeneratorService.sActivePart = partTag;
        S6AudioGeneratorService.sScenarioName = title;

        it.putExtra("title", title);
        it.putExtra("part", partTag);
        it.putExtra("scenario", title);
        it.putExtra("knob_guide", knobGuide);

        S6AudioGeneratorService.sIsPlaying = true;
        S6AudioGeneratorService.sModeTitle = title;
        if (sweep) {
            S6AudioGeneratorService.sIsSweepMode = true;
            S6AudioGeneratorService.sSweepMin = sMin;
            S6AudioGeneratorService.sSweepMax = sMax;
            S6AudioGeneratorService.sInstantFreq = sMin;
        } else {
            S6AudioGeneratorService.sIsSweepMode = false;
            S6AudioGeneratorService.sTargetFreq = freq;
            S6AudioGeneratorService.sInstantFreq = freq;
        }

        startService(it);
        Toast.makeText(this, title + " 발진 시작", Toast.LENGTH_SHORT).show();
        syncTelemetryUi();
    }

    private void syncTelemetryUi() {
        boolean isPlaying = S6AudioGeneratorService.sIsPlaying;
        float density = getResources().getDisplayMetrics().density;

        if (mStatusCardLayout != null) {
            GradientDrawable scBg = new GradientDrawable();
            scBg.setCornerRadius(8 * density);
            scBg.setColor(Color.parseColor("#111827")); // AMOLED Deep Slate (Never green background!)
            if (isPlaying) {
                scBg.setStroke((int)(2 * density), Color.parseColor("#10B981")); // Vivid Emerald Green border
            } else {
                scBg.setStroke((int)(2 * density), Color.parseColor("#EF4444")); // Warning Crimson Red border
            }
            mStatusCardLayout.setBackground(scBg);
        }

        if (mStatusTrafficLight != null) {
            GradientDrawable trafficDot = new GradientDrawable();
            trafficDot.setShape(GradientDrawable.OVAL);
            if (isPlaying) {
                trafficDot.setColor(Color.parseColor("#00E676")); // Neon Green Traffic Light
            } else {
                trafficDot.setColor(Color.parseColor("#FF3366")); // Neon Red Traffic Light
            }
            mStatusTrafficLight.setImageDrawable(trafficDot);
        }

        if (mStatusMode != null) {
            if (isPlaying) {
                mStatusMode.setText("상태: [발진 중] " + S6AudioGeneratorService.sActivePart);
                mStatusMode.setTextColor(Color.parseColor("#00E676")); // Neon Traffic Light Green
            } else {
                mStatusMode.setText("상태: [작동 중지] 멈춤 (대기 상태)");
                mStatusMode.setTextColor(Color.parseColor("#FF3366")); // Neon Traffic Light Red
            }
        }

        if (mStatusScenario != null) {
            if (isPlaying) {
                mStatusScenario.setText("시나리오: " + S6AudioGeneratorService.sScenarioName);
                mStatusScenario.setTextColor(Color.parseColor("#00F0FF")); // Electric Cyan
            } else {
                mStatusScenario.setText("시나리오: 대기 중 (선택 없음)");
                mStatusScenario.setTextColor(Color.parseColor("#64748B"));
            }
        }

        if (mStatusFreq != null) {
            if (!isPlaying) {
                mStatusFreq.setText("발진: 0.00 Hz (출력 차단 / MUTE)");
                mStatusFreq.setTextColor(Color.parseColor("#94A3B8")); // Muted Gray
            } else if (S6AudioGeneratorService.sIsSweepMode) {
                mStatusFreq.setText(String.format("발진: %.2f Hz 실시간 (%.1f~%.1fHz 스윕)",
                        S6AudioGeneratorService.sInstantFreq, S6AudioGeneratorService.sSweepMin, S6AudioGeneratorService.sSweepMax));
                mStatusFreq.setTextColor(Color.parseColor("#FFD700")); // High-brightness & saturation Green
            } else {
                mStatusFreq.setText(String.format("발진: %.2f Hz 직타 고정 (-1.5dBFS True-Peak)",
                        S6AudioGeneratorService.sTargetFreq));
                mStatusFreq.setTextColor(Color.parseColor("#FFD700")); // High-brightness & saturation Green
            }
        }

        if (mStatusMod != null) {
            if (!isPlaying) {
                mStatusMod.setText("변조: 비활성 (주파수 신호 멈춤) | BTL 대기");
                mStatusMod.setTextColor(Color.parseColor("#64748B"));
            } else {
                StringBuilder sb = new StringBuilder("변조: ");
                boolean hasMod = false;
                if (S6AudioGeneratorService.sFmEnabled) {
                    sb.append(String.format("FM %.1f%%(%.2fHz) ", S6AudioGeneratorService.sFmDepth * 100f, S6AudioGeneratorService.sFmRateHz));
                    hasMod = true;
                }
                if (S6AudioGeneratorService.sAmEnabled) {
                    sb.append(String.format("AM %.1f%%(%.2fHz) ", S6AudioGeneratorService.sAmDepth * 100f, S6AudioGeneratorService.sAmRateHz));
                    hasMod = true;
                }
                if (S6AudioGeneratorService.sRmEnabled) {
                    sb.append(String.format("RM %.1f%%(%.2fHz) ", S6AudioGeneratorService.sRmDepth * 100f, S6AudioGeneratorService.sRmRateHz));
                    hasMod = true;
                }
                if (!hasMod) sb.append("무변조 순수 사인파 ");
                sb.append("| BTL 모노");
                mStatusMod.setText(sb.toString());
                mStatusMod.setTextColor(Color.parseColor("#F472B6"));
            }
        }

        if (mStatusKnob != null) {
            mStatusKnob.setText("앰프 노브: Lepy LP-168S [5개 다이얼] SUB VOL 3~5시 (정격 68W 골전도 풀파워) | X-OVER 80Hz | BASS 0dB");
        }
    }
}
