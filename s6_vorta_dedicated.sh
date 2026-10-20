#!/system/bin/sh
# Galaxy S6 (SM-G920*, Android 7.0) -> Vorta Reso v3.0 + Trans2 (Lepy LP-168S) dedicated device.
# Approved by user 2026-10-20. Rule (hang receipt 2026-10-20): every pm call is wrapped in
# `timeout`, because `pm uninstall com.samsung.android.spayfw` blocked forever on SM-G920K.
T=8   # seconds per pm call; a normal pm call measured 0.95 s on this S6
log() { echo "[S6] $*"; }

# 1) Remove: user-requested (gallery/camera/music/video/Galaxy Store) + previous list remainder.
RM="
com.sec.android.gallery3d
com.sec.android.app.camera
com.sec.android.app.music
com.samsung.android.app.music
com.samsung.android.video
com.sec.android.app.videoplayer
com.sec.android.app.samsungapps
com.google.android.youtube
com.google.android.videos
com.google.android.music
com.google.android.apps.photos
com.samsung.android.samsungpass
com.samsung.svoice.sync
com.sec.svoice.lang.ko_KR
com.sec.svoice.lang.en_US
com.samsung.android.voicewakeup
com.samsung.android.scloud
com.samsung.android.fmm
com.samsung.android.game.gamehome
com.enhance.gameservice
flipboard.boxer.app
com.sec.android.service.health
com.sec.android.daemonapp
com.google.android.googlequicksearchbox
com.google.android.talk
com.sec.hearingadjust
com.skt.skaf.OA00018282
com.kt.wificm
com.samsung.android.themestore
com.sec.android.gallery3d.panorama360view
com.sec.android.app.camera.plb
com.sec.android.widgetapp.samsungapps
com.samsung.android.videolist
com.skms.android.agent
"
# 2) Disable only (uninstall hangs): Samsung Pay and its frameworks.
DIS="
com.samsung.android.spay
com.samsung.android.spayfw
com.samsung.android.authfw
"
n=0
for p in $RM; do
  n=$((n+1))
  pm path "$p" >/dev/null 2>&1 || { log "$n skip(absent) $p"; continue; }
  r=$(timeout $T pm uninstall --user 0 "$p" 2>&1)
  case "$r" in *Success*) log "$n removed $p";; *) timeout $T pm disable-user --user 0 "$p" >/dev/null 2>&1; log "$n disabled $p ($r)";; esac
done
for p in $DIS; do
  pm path "$p" >/dev/null 2>&1 || continue
  timeout $T pm disable-user --user 0 "$p" >/dev/null 2>&1 && log "disabled $p" || log "disable-failed-or-timeout $p"
done

# 3) 24 h stability: screen sleeps, no animations, no system sounds, app exempt from Doze.
# Principle 2/3: stay_on stays 0 and screen_off_timeout is never touched.
settings put global stay_on_while_plugged_in 0
# Principle 9/10: 24 h charging protection (85 % cap, no fast-charge heat), safe-volume warning off.
settings put global protect_battery 1
settings put system protect_battery 1
settings put system adaptive_fast_charging 0
settings put global audio_safe_volume_state 2
settings put system volume_limiter_enable 0
for p in com.sec.android.app.soundalive com.sec.hearingadjust com.enhance.gameservice com.samsung.android.game.gos; do
  pm path "$p" >/dev/null 2>&1 && timeout $T pm disable-user --user 0 "$p" >/dev/null 2>&1 && log "frozen $p"
done
settings put global window_animation_scale 0
settings put global transition_animation_scale 0
settings put global animator_duration_scale 0
settings put system sound_effects_enabled 0
settings put system haptic_feedback_enabled 0
settings put system dtmf_tone 0
settings put global charging_sounds_enabled 0
dumpsys deviceidle whitelist +com.vorta.s6frequency >/dev/null 2>&1

# 4) Principle 1/8: media volume is never forced (user sets it; 11-12 suggested per preset);
#    only system/ring/notification streams are muted.
media volume --stream 1 --set 0 >/dev/null 2>&1
media volume --stream 2 --set 0 >/dev/null 2>&1
media volume --stream 5 --set 0 >/dev/null 2>&1
log "done"
exit 0
