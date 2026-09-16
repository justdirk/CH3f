# CH3F

Multilingual restaurant equipment catalogue, built with Python's standard library. Italian and German are the initial markets; English, Turkish, French, Spanish and Portuguese are also available.

## Build and preview

```sh
python3 build.py
python3 scripts/validate.py
python3 -m http.server 4173 --directory dist
```

Edit `content.py`, `refined.py` and `conversion.py` for translations and sales copy. `product_depth.py` and `guide_depth.py` contain expanded Italian and German buying guidance. Edit `build.py` for templates and `assets/style.css` / `assets/app.js` for presentation and interaction. Generated files in `dist/` are disposable; do not edit them.

## Cloudflare Pages

Connect the `justdirk/CH3f` GitHub repository to Cloudflare Pages. Use:

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Framework preset | None |
| Build command | `python3 build.py && python3 scripts/validate.py` |
| Build output directory | `dist` |
| Root directory | Repository root |

For production, set `SITE_ORIGIN` to the verified public HTTPS origin, with no path, and `SITE_INDEXABLE=true`. Leave `SITE_INDEXABLE` unset in preview environments. Builds from branches other than `main` stay noindex even if this variable is inherited. The quote pages and 404 always remain noindex. A new deployment is required after changing build environment variables.

When a custom domain is connected, update `SITE_ORIGIN` and rebuild. Redirect the old public hostname to the new domain before submitting the new sitemap to Search Console. Canonical URLs, reciprocal hreflang, sitemap and structured data all use this single origin.

Assets have content-hashed filenames, responsive WebP variants, self-hosted WOFF2 fonts and immutable cache headers. No package installation is needed to build. Python 3.9 or later is sufficient.

## Contact activation

The catalogue can be published, but quote delivery is **not active**. The form creates a downloadable summary on the visitor's device and explicitly says it has not been sent. There is no lead inbox, database or analytics integration.

Set `whatsapp` in `contact.json` to the confirmed business WhatsApp number, including country code, and rebuild. A blank value displays an availability notice. A configured number opens WhatsApp with a localized product enquiry; the visitor still chooses whether to send it.

Before promoting the site to buyers, connect and test the real quote inbox, replace the preview notices, provide the business identity and applicable customer/privacy information, and confirm model specifications and supply terms. No email address or phone number is invented.

## Content and assets

TOROS Italia is the reference manufacturer. Supplier product photographs are included under the project owner's authorization. The hero is an AI background and lighting edit of the electric machine photo; detail photos retain the supplier imagery. Optimized files preserve that artwork. The 120 mm knife source is low resolution and should be replaced when a better supplier file is available.

Technical information was reviewed on 16 September 2026. Source links appear on the expanded product pages. Missing capacity, power, compatibility, prices, stock, warranty and delivery details must be confirmed in the actual offer. Do not add fabricated reviews, ratings, offers, certifications or performance claims. Product structured data does not by itself qualify these pages for Google's product rich results.

Manrope is self-hosted under the included `assets/manrope-LICENSE.txt`. Other assets are not granted an open-source license by this repository.

## Search measurement

The build checks internal links, asset references, language alternatives, canonicals, structured data and indexing settings. These are technical checks, not ranking or Core Web Vitals measurements. After launch, verify the production domain in Search Console, submit `/sitemap.xml`, and monitor indexing and Italian/German queries. Original product evidence and business authority still need to be developed.
