# Getting the app onto an Android phone

Two routes. **Route A takes about thirty seconds and needs nothing built** — try
it first. Route B produces an actual `.apk` file, which is only worth the effort
if you want to put the app on a phone that isn't yours, or keep an offline copy
of a specific version.

Neither route needs a Google Play developer account, and neither costs anything.

---

## Route A — install straight from Chrome (recommended)

1. Open **https://podcast.mingli.world** in **Chrome** on the phone.
   Chrome specifically — Samsung Internet and Firefox make a shortcut, not an app.
2. Sign in. The cookie lasts a year, so this is one-time.
3. Menu **⋮** → **Install app** (older Chrome says *Add to Home screen*).

You get a WebAPK: a real installed Android package with its own launcher icon,
its own entry in the recents switcher, no browser UI, and offline support for
anything the service worker has cached. Google signs it during install, so none
of the developer-verification rules below apply to it.

Uninstall like any app: long-press → Uninstall.

### If "Install app" doesn't appear

Chrome only offers it when the manifest, icons and service worker all load.
All three are verified live, so the usual cause is a stale cached manifest:
Settings → Privacy → Site settings → All sites → podcast.mingli.world → Clear
data, then reload and try again.

---

## Route B — the sideloadable APK

A Trusted Web Activity: a thin native wrapper that renders the same site
full-screen, verified against the domain so no address bar appears.

### Getting the file

The build runs in CI, because it needs a JDK and the Android SDK — about half a
gigabyte of toolchain that would otherwise have to be installed locally.

```bash
gh workflow run build-apk.yml          # takes 3-6 minutes
```

When it finishes the APK is in two places:

- attached to the run as the `mingli-podcast-apk` artifact
- published to **https://podcast.mingli.world/app/mingli.apk**, which is the
  easy one — open that URL in the phone's browser

### Installing it

1. Open **https://podcast.mingli.world/app/mingli.apk** in Chrome on the phone.
2. Chrome warns that this file type can harm your device. That warning appears
   for every APK not from the Play Store. Tap **Download anyway**.
3. Tap the downloaded file. Android will say Chrome isn't allowed to install
   unknown apps → **Settings** → enable **Allow from this source** → back.
4. **Install**.

If you'd rather use a cable: enable Developer options (tap Build number seven
times) → USB debugging, then `adb install app-release-signed.apk`.

### Verifying it before you trust it

The build already does this and fails if anything is off, but to check by hand:

```bash
BT=$ANDROID_HOME/build-tools/$(ls $ANDROID_HOME/build-tools | sort -V | tail -1)

$BT/apksigner verify --print-certs app-release-signed.apk   # signature + fingerprint
$BT/aapt2 dump badging app-release-signed.apk | head        # package id, label, SDK levels
unzip -l app-release-signed.apk | tail -5                   # contents
```

The SHA-256 in `apksigner`'s output **must match** the fingerprint in
`site/.well-known/assetlinks.json`. If it doesn't, Android still installs the
app but shows a browser address bar across the top, because the domain no longer
vouches for that signing key.

Current fingerprint:

```
99:F0:78:DF:47:8D:D3:13:5B:9F:36:D7:0C:27:3D:84:46:F1:AD:A1:FE:81:F8:AA:98:1C:3E:C5:F6:93:78:32
```

### The signing key

`.keys/mingli.keystore`, alias `mingli`, gitignored. CI restores it from the
`ANDROID_KEYSTORE_B64` secret.

**Keep a copy somewhere safe.** Android identifies an app by its signing key, so
losing it means no future build can install over this one — the phone would
reject the update and you'd have to uninstall first, losing local state. It also
means regenerating `assetlinks.json` with the new fingerprint.

---

## Developer verification, and why it doesn't block you

Google is phasing in a rule that apps on certified Android devices must come
from a verified developer, sideloading included. Relevant dates: enforcement
begins **30 September 2026** in Brazil, Indonesia, Singapore and Thailand, and
expands globally during **2027**.

It doesn't affect this app:

- **Route A is unaffected entirely** — Google signs WebAPKs during install.
- **ADB installs are explicitly exempt**; Google's guidance says the ADB
  workflow is unchanged.
- There is a **free limited-distribution tier** — no identity check, no fee, up
  to 20 devices — which is exactly the personal-use case.
- Non-certified devices are out of scope.

The $25 verified account only matters for general public distribution.

Sources: [developer verification guide](https://developer.android.com/developer-verification/guides),
[rollout timeline](https://android-developers.googleblog.com/2026/03/android-developer-verification-rolling-out-to-all-developers.html).

---

## Which route should you actually use?

Route A, unless you have a specific reason not to. It produces the same
experience — same icon, same full-screen app, same offline behaviour — with no
build, no signing key to protect, and no security warnings to click through.

Route B earns its keep when you want to hand the app to someone else's phone, or
pin a known-good version offline.
