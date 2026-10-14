# Boxmello support

Public support and legal website for Boxmello, developed by Bayram Baş.

- English: https://bayrambas255.github.io/boxmello-support/
- Türkçe: https://bayrambas255.github.io/boxmello-support/tr/
- Contact: bayrambas255@icloud.com

## Content and publication

English and Turkish support, privacy/KVKK notice, game use terms, data deletion instructions, and font acknowledgements are included. The application license points to Apple's Standard EULA; this repository does not supply a custom App Store EULA. No App Store listing text or app source is included.

GitHub Pages serves `main:/docs`. Pages are static HTML with local CSS and images, no JavaScript, analytics, cookies, forms, or remote fonts added by this site. GitHub's hosting/security processing is explained in the privacy notice.

Edit `content/pages.py`, then run:

```sh
python3 scripts/build.py
python3 scripts/check.py
```

Review both languages and the effective date before committing generated `docs/` files. Push to `main` to publish. Keep the published notice aligned with the actual app and developer operations when adding accounts, SDKs, ads, sync, new payment products, or organized research.

## Basis of the first version — 14 October 2026

The current Boxmello code was inspected for local persistence, StoreKit products, restore behavior, network/SDK use, permissions, and TestFlight-only study telemetry. The normal game has local saves, no account, no ad/analytics SDK, four consumable coin products, and a permanent Mint Post cosmetic. No cloud synchronization or in-game erase control exists. Device backup copies may exist. No source code or private development evidence is published here.

Primary references used:

- [Apple App Review Guidelines, privacy and contact information](https://developer.apple.com/app-store/review/guidelines/)
- [Apple Standard EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/)
- [Apple EULA configuration](https://developer.apple.com/help/app-store-connect/manage-app-information/provide-a-custom-license-agreement/)
- [Apple refunds](https://support.apple.com/en-us/118223)
- [Apple analytics privacy](https://www.apple.com/legal/privacy/data/en/app-analytics/)
- [KVKK notice requirements](https://www.kvkk.gov.tr/Icerik/4132/aydinlatma-yukumlulugunun-yerine-getirilmesinde-uyulacak-usul-ve-esaslar-hakkinda-teblig)
- [KVKK individual rights](https://www.kvkk.gov.tr/Icerik/2036/Ilgili-Kisinin-Haklari)
- [KVKK law](https://www.kvkk.gov.tr/Icerik/6649/Personal-Data-Protection-Law)
- [GitHub Pages data collection](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection)

The site is a statement of the disclosed practices, not a certification of compliance in every jurisdiction. The developer must implement stated retention/request handling and assess service-provider and international-transfer obligations for the actual operation; no unverified transfer contract is claimed. App Store availability, age rating, App Privacy answers and submission settings remain outside this support-site task. Before release, the app itself must expose an easily accessible link to the published privacy policy and a support contact as required by Apple's guidelines.
