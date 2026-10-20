#!/system/bin/sh
PKGS="
com.skt.prod.phone
com.skt.prod.phone.phonemodesetupwizard
com.skt.prod.dialer
com.skt.t_smart_charge
com.samsung.android.contacts
com.samsung.android.app.contacts
com.sec.android.widgetapp.easymodecontactswidget
com.sec.phone
com.android.phone
com.samsung.android.dialer
com.samsung.android.incallui
com.samsung.android.messaging
com.sec.android.app.dmb
com.samsung.android.app.dtv.dmb
com.sec.android.app.fm
com.sec.android.app.popupcalculator
com.sec.android.app.sbrowser
com.android.chrome
com.sec.android.app.chromecustomizations
com.samsung.android.email.provider
com.google.android.gm
com.samsung.android.easysetup
com.samsung.android.beaconmanager
com.samsung.android.ststub
com.samsung.android.oneconnect
com.samsung.android.allshare.service.fileshare
com.samsung.android.allshare.service.mediashare
com.samsung.android.spay
com.samsung.android.spayfw
com.google.android.youtube
com.google.android.music
com.google.android.videos
com.google.android.apps.photos
com.samsung.android.video
com.sec.android.gallery3d
com.samsung.android.samsungpass
com.samsung.android.samsungpassautofill
com.samsung.android.svoice
com.samsung.svoice.sync
com.sec.svoice.lang.ko_KR
com.sec.svoice.lang.en_US
com.samsung.android.voicewakeup
com.samsung.android.scloud
com.samsung.android.fmm
com.samsung.android.authfw
com.samsung.android.game.gamehome
com.enhance.gameservice
flipboard.boxer.app
com.sec.android.service.health
com.sec.android.daemonapp
com.google.android.googlequicksearchbox
com.google.android.talk
com.sec.android.app.soundalive
com.sec.hearingadjust
Com.sktelecom.minit
com.skt.skaf.OA00018282
com.skt.skaf.OA00199800
com.skt.skaf.OA00412131
com.skt.skaf.A000Z00040
com.sktelecom.smartcard.SmartcardService
com.kt.olleh.customercare
com.kt.show.cs
com.kt.service.cs
uplus.membership
com.lguplus.mobile.cs
com.lguplus.smartpay
com.sec.android.app.samsungapps
com.sec.android.widgetapp.samsungapps
"

# Hang receipt 2026-10-20: plain `timeout 8` sends TERM only; a pm that ignores it blocks forever.
# -k 2 sends KILL 2 s later; absent packages are skipped without calling pm uninstall.
for p in $PKGS; do echo "[pm] $p"
    pm path "$p" >/dev/null 2>&1 || continue
    timeout -k 2 8 pm uninstall --user 0 "$p" </dev/null >/dev/null 2>&1       || timeout -k 2 8 pm disable-user --user 0 "$p" </dev/null >/dev/null 2>&1
done
echo "[pm] done"
exit 0
