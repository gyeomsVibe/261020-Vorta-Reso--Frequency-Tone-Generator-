package com.vorta.s6frequency;

import android.accessibilityservice.AccessibilityService;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.List;

public class S6AccessibilityService extends AccessibilityService {
    private static final String TAG = "S6AccessService";

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) return;

        try {
            // Check for Safe Volume Dialog keywords
            String[] keywords = {"높은 볼륨", "청력", "안전 볼륨", "High volume", "hearing", "Hearing"};
            boolean foundWarning = false;

            for (String kw : keywords) {
                List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(kw);
                if (nodes != null && !nodes.isEmpty()) {
                    foundWarning = true;
                    for (AccessibilityNodeInfo n : nodes) {
                        n.recycle();
                    }
                    break;
                }
            }

            if (foundWarning) {
                Log.i(TAG, "Samsung safe volume dialog detected -> auto-dismissing");
                String[] okButtons = {"확인", "OK", "동의", "허용", "Yes"};
                for (String btnText : okButtons) {
                    List<AccessibilityNodeInfo> btnNodes = root.findAccessibilityNodeInfosByText(btnText);
                    if (btnNodes != null && !btnNodes.isEmpty()) {
                        for (AccessibilityNodeInfo btn : btnNodes) {
                            if (btn.isClickable()) {
                                btn.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                                Log.i(TAG, "Clicked confirm button: " + btnText);
                            }
                            btn.recycle();
                        }
                    }
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "Accessibility scan error: " + e.getMessage());
        } finally {
            root.recycle();
        }
    }

    @Override
    public void onInterrupt() {
        Log.i(TAG, "S6AccessibilityService onInterrupt");
    }
}
