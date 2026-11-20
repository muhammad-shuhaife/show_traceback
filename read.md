# Current Error Traceback · Odoo 20

![Module icon](static/description/icon.png)

View the **full traceback of the latest captured request error** at a URL you choose in Odoo Settings.

**Author:** shuhaife binhamza  
**Portfolio:** [shuhaife.pages.dev](https://shuhaife.pages.dev/)  
**Version:** `20.0.7.2.0` · **Technical name:** `show_traceback` · **License:** LGPL-3

## What it does

- Adds a controller-name field and **Open traceback** button to Settings, visible in developer mode.
- Displays the exception type, message, request path, UTC timestamp, and complete Python traceback.
- Keeps only the latest captured error for each database; each new error replaces the previous one.
- Serves an authorized emergency viewer before normal database routing, once the addon has loaded.
- Captures unexpected HTTP and JSON-RPC request errors, with a fallback for HTTP-layer registry errors.
- Uses the existing Odoo data directory and requires no `server_wide_modules` entry or environment token.

![Traceback viewer with example data](static/description/traceback_preview.png)

*Preview uses illustrative example data, not an error from your database.*

## Requirements

- Odoo **20**, with the standard `base` and `web` addons.
- A deployment environment that permits custom Python addons and reloading Odoo workers.
- A writable Odoo `data_dir`. Workers for the same instance must share it.
- A Settings administrator account to configure the URL and authorize a browser.

This package is specifically for Odoo 20. Use the separate packages for Odoo 18 or 19.

## Installation and upgrade

1. Extract the ZIP and place its **`show_traceback`** folder in your custom addons directory. The parent directory must be on your existing `addons_path`.
2. For an update, replace the entire existing addon folder to avoid leaving obsolete files behind.
3. Restart/reload **all** Odoo workers so the new Python code is imported.
4. Open Apps, update the apps list, and search for **Current Error Traceback**. Remove the default Apps filter if necessary: this is a technical addon, not a standalone application.
5. Install it, or choose **Upgrade** if it is already installed.
6. Configure and save the URL as described below, even if you used an earlier package.

An Apps upgrade alone cannot reliably replace Python code already loaded in a worker. If you cannot deploy or reload Python addons, ask the hosting administrator to perform the installation. No server-wide module setting is required.

## Configure the viewer

1. Log in as a Settings administrator and enable **developer mode**.
2. Go to **Settings → Error Traceback**.
3. Enter a name such as `my_error` or `/my_error` and click **Save**.
4. Click **Open traceback** to open the exact saved URL for the current database.
5. Reproduce the failing request, then refresh the traceback page in the **same browser and hostname**.

Example: `my_error` opens **`http://localhost:8069/my_error`**. The default is `/traceback`.

Use a single name starting with a letter, followed by letters, digits, underscores or hyphens, up to 80 characters. Reserved or already registered controller names are rejected when changing the setting. Saving a new name does not require another restart.

## Browser access

Only a Settings administrator can authorize a browser. Saving the setting or opening the viewer while Odoo is healthy issues a separate random, HttpOnly, SameSite=Strict cookie. On HTTPS, the cookie is also marked Secure.

- Emergency access lasts **up to eight hours**.
- It intentionally survives rotation or removal of the normal Odoo session cookie, including logout, so a registry failure does not lock out the prepared browser.
- To revoke this browser's access early, delete its `odoo_traceback_*` cookie in browser settings.
- To renew access, authenticate as an administrator while Odoo is healthy and save the setting or use **Open traceback** again.
- Switching browser, using incognito mode, or changing between `localhost` and `127.0.0.1` requires separate authorization.
- The configuration controls require debug mode; the authorized viewer itself does not.

No secret is placed in the viewer URL. If several databases share a URL, **Open traceback** includes `?db=DATABASE_NAME` to select the correct database. Do not use a shared browser profile for emergency access.

## Meaning of “current error”

The page shows the most recently **captured unexpected request exception**, not a live health check. Successful requests do not clear the latest error; check its timestamp. Refresh the page to see a newly captured error.

Expected validation/user/access errors and HTTP 4xx responses are excluded. An error in the viewer does not overwrite the original error. A raw 500 response without a Python exception has no traceback to capture.

## Storage

Data is stored beneath `data_dir/show_traceback_current/`:

| File | Purpose |
| --- | --- |
| `<database-hash>.json` | One complete latest traceback, replaced atomically |
| `<database-hash>.json.endpoint` | Configured URL and hashed, expiring browser grants |
| `<database-hash>.json.endpoint.lock` | Serializes endpoint updates across local workers |

Files are created with owner-only permissions. Separate databases have separate records. Normal Odoo server logging remains unchanged.

The legacy history menu is hidden and no new `traceback.log` records are created. Existing historical database rows or old log files from earlier versions are not deleted or displayed.

## Limits

The addon must have loaded successfully **in each serving worker** before the emergency wrapper can run. A fresh worker that fails before importing it cannot serve the emergency page. A stopped Odoo process cannot serve any page.

Authorize the browser **before** a database failure. A new or expired browser grant cannot be safely authorized through an already broken database. Errors from before installation, background jobs, and other processes may still require the normal server log. Multiple hosts without shared storage will not share captured errors.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Settings option is missing | Addon installed, workers reloaded, Settings administrator, developer mode enabled |
| Custom URL returns 404 | Save the controller name, then use **Open traceback** from the correct database |
| No error captured | Reproduce an unexpected request failure after addon loading, then refresh |
| Viewer also returns 500 | Browser authorized in advance, cookie still valid, same hostname, addon loaded in that worker |
| Saved traceback cannot be read | Odoo OS user's permissions on its data directory |
| `Invalid field name 'perm_read'` during installation | Replace the entire addon folder: Odoo 20 uses `security/ir.access.csv` with an `operation` field |

## Package contents

```text
show_traceback/
├── __manifest__.py
├── read.md
├── README.rst
├── compat.py
├── emergency.py
├── page.py
├── settings.py
├── store.py
├── controllers/
├── models/
├── security/ir.access.csv
├── views/
└── static/description/
    ├── index.html
    ├── icon.png
    ├── icon.svg
    └── traceback_preview.png
```

## Validation

The corrected module imports against the available local Odoo 20 source. Its access CSV has been checked against the real `ir.access` fields and operation values; data XML passes Odoo's import schema. The behavioral regression suite contains 23 isolated tests using framework stubs. These checks do **not** replace installing and verifying the addon in a staging database.

## Changelog

- **20.0.7.2.0:** Added this README, Apps description, original module icon, author/portfolio metadata, and complete manifest description.
- **20.0.7.1.1:** Fixed the Odoo 20 access CSV and README underline warning.
- **20.0.7.1.0:** Ported the HTTP imports and typed configuration API to Odoo 20; emergency authorization survives Odoo session rotation.

## Author and license

Created by **shuhaife binhamza**. Visit [the author's portfolio](https://shuhaife.pages.dev/).

Distributed under **LGPL-3**, as declared in the manifest.
