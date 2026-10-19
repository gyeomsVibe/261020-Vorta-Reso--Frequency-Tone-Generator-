package com.trans2.frequencygenerator;

import android.accessibilityservice.AccessibilityService;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.List;

public class Trans2AccessibilityService extends AccessibilityService {
    private static final String TAG = "Trans2AccSvc";
    private final Handler mHandler = new Handler(Looper.getMainLooper());

    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (intent == null) return;
            String action = intent.getAction();
            if (Intent.ACTION_HEADSET_PLUG.equals(action)) {
                AudioVolumeHelper.ensureVolume15IfNeeded(Trans2AccessibilityService.this, true);
            } else if ("android.media.VOLUME_CHANGED_ACTION".equals(action)) {
                AudioVolumeHelper.ensureVolume15IfNeeded(Trans2AccessibilityService.this, false);
            }
        }
    };

    private final Runnable mWatchdog = new Runnable() {
        @Override
        public void run() {
            AudioVolumeHelper.enforceSystemFlags(Trans2AccessibilityService.this);
            AudioVolumeHelper.ensureVolume15IfNeeded(Trans2AccessibilityService.this, false);
            mHandler.postDelayed(this, 180000); // Every 3 minutes
        }
    };

    @Override
    public void onServiceConnected() {
        super.onServiceConnected();
        IntentFilter filter = new IntentFilter();
        filter.addAction("android.media.VOLUME_CHANGED_ACTION");
        filter.addAction(Intent.ACTION_HEADSET_PLUG);
        registerReceiver(mReceiver, filter);
        AudioVolumeHelper.ensureVolume15IfNeeded(this, true);
        mHandler.post(mWatchdog);
        Log.i(TAG, "Trans2AccessibilityService Active - Zero-Loop Safe Volume Guard");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;
        CharSequence pkg = event.getPackageName();
        // Skip scanning our own app's UI events to save CPU and avoid jitter
        if (pkg != null && "com.trans2.frequencygenerator".equals(pkg.toString())) {
            return;
        }
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) return;
        try {
            dismissDialog(root);
        } finally {
            root.recycle();
        }
    }

    private void dismissDialog(AccessibilityNodeInfo node) {
        if (node == null) return;

        CharSequence text = node.getText();
        if (text != null) {
            String str = text.toString();
            if (str.contains("음량") || str.contains("손상") || str.contains("청력") ||
                str.contains("Safe volume") || str.contains("hearing") || str.contains("경고")) {
                clickConfirmButton(getRootInActiveWindow());
                AudioVolumeHelper.ensureVolume15IfNeeded(this, true);
                return;
            }
        }

        int count = node.getChildCount();
        for (int i = 0; i < count; i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                dismissDialog(child);
                child.recycle();
            }
        }
    }

    private void clickConfirmButton(AccessibilityNodeInfo root) {
        if (root == null) return;
        try {
            List<AccessibilityNodeInfo> byId = root.findAccessibilityNodeInfosByViewId("android:id/button1");
            if (byId != null && !byId.isEmpty()) {
                for (AccessibilityNodeInfo btn : byId) {
                    btn.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    btn.recycle();
                }
                return;
            }

            String[] targets = {"확인", "OK", "듣기", "계속"};
            for (String t : targets) {
                List<AccessibilityNodeInfo> byText = root.findAccessibilityNodeInfosByText(t);
                if (byText != null && !byText.isEmpty()) {
                    for (AccessibilityNodeInfo btn : byText) {
                        btn.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                        btn.recycle();
                    }
                    return;
                }
            }
        } finally {
            root.recycle();
        }
    }

    @Override
    public void onInterrupt() {
        Log.w(TAG, "Trans2AccessibilityService interrupted");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        mHandler.removeCallbacks(mWatchdog);
        try {
            unregisterReceiver(mReceiver);
        } catch (Exception ignored) {}
    }
}
