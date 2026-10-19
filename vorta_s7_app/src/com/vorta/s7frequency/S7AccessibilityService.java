package com.vorta.s7frequency;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.util.Log;
import java.util.List;

public class S7AccessibilityService extends AccessibilityService {
    private static final String TAG = "S7AccService";

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        Log.i(TAG, "S7 Safe Volume Guard AccessibilityService Connected");
        S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);

        int[] delays = {1000, 3000, 7000, 15000, 30000};
        android.os.Handler h = new android.os.Handler(android.os.Looper.getMainLooper());
        for (final int d : delays) {
            h.postDelayed(new Runnable() {
                @Override
                public void run() {
                    S7VolumeHelper.ensureTargetVolumeIfNeeded(S7AccessibilityService.this, true);
                }
            }, d);
        }
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;
        CharSequence pkg = event.getPackageName();
        String pkgStr = (pkg != null) ? pkg.toString() : "";

        if (!pkgStr.contains("systemui") && !pkgStr.equals("android") && !pkgStr.contains("settings") && !pkgStr.contains("soundalive")) {
            return;
        }

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) return;

        try {
            if (containsSafeVolumeWarning(root)) {
                Log.i(TAG, "Detected Safe Volume Warning Dialog on S7! Auto-clicking OK...");
                clickPositiveButton(root);
                S7VolumeHelper.ensureTargetVolumeIfNeeded(this, true);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error processing accessibility node: " + e.getMessage());
        } finally {
            root.recycle();
        }
    }

    private boolean containsSafeVolumeWarning(AccessibilityNodeInfo node) {
        if (node == null) return false;
        CharSequence text = node.getText();
        if (text != null) {
            String t = text.toString();
            if (t.contains("청력") || t.contains("높은 음량") || t.contains("안전 음량")
                    || t.contains("음량을 높이시겠습니까") || t.contains("귀가 손상") || t.contains("손상")
                    || t.contains("High volume") || t.contains("hearing") || t.contains("Safe volume")) {
                return true;
            }
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                boolean found = containsSafeVolumeWarning(child);
                child.recycle();
                if (found) return true;
            }
        }
        return false;
    }

    private boolean clickPositiveButton(AccessibilityNodeInfo root) {
        String[] targets = {"확인", "OK", "예", "동의", "Allow"};
        for (String label : targets) {
            List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(label);
            if (nodes != null) {
                for (AccessibilityNodeInfo n : nodes) {
                    if (n.isClickable()) {
                        n.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                        return true;
                    }
                    AccessibilityNodeInfo parent = n.getParent();
                    if (parent != null && parent.isClickable()) {
                        parent.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                        return true;
                    }
                }
            }
        }
        List<AccessibilityNodeInfo> btn1 = root.findAccessibilityNodeInfosByViewId("android:id/button1");
        if (btn1 != null && !btn1.isEmpty()) {
            for (AccessibilityNodeInfo n : btn1) {
                if (n.isClickable()) {
                    n.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    return true;
                }
            }
        }
        return false;
    }

    @Override
    public void onInterrupt() {}
}
