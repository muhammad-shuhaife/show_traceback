"""Standalone HTML: no database, QWeb, web assets or JavaScript required."""
from html import escape

HEADERS = {
    'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow',
    'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
    'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'",
}


def render_page(record):
    if record:
        e = lambda key: escape(str(record.get(key, '')))
        summary = e('message') or e('error_type') or 'Unexpected server error'
        content = '''<section class="error"><div class="eyebrow">LATEST CAPTURED ERROR</div>
<h2>{kind}</h2><p class="message">{message}</p>
<div class="metadata"><span><b>REQUEST</b><code>{method} {path}</code></span>
<span><b>CAPTURED AT (UTC)</b><time>{time}</time></span></div></section>
<section class="trace"><div class="trace-head"><h2>Full traceback</h2><span>Python · complete output</span></div>
<pre tabindex="0">{traceback}</pre></section>'''.format(
            kind=e('error_type') or 'Server error', message=summary, method=e('method'),
            path=e('path'), time=e('time'), traceback=e('traceback'))
    else:
        content = '''<section class="empty"><h2>No error has been captured yet</h2>
<p>Reproduce the failing Odoo request, then refresh this page in the same browser.</p>
<p>Only errors captured after this addon loads can appear here.</p></section>'''
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Current error · Odoo</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f6f8;color:#202333;font:15px/1.6 system-ui,sans-serif}
header{background:#fff;border-bottom:1px solid #e1e3e8;padding:18px 5vw;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{font-weight:650;color:#714b67}.badge{font-size:12px;border:1px solid #ddd3da;border-radius:20px;padding:4px 12px;color:#714b67}
main{max-width:1200px;margin:36px auto;padding:0 24px}.title{display:flex;justify-content:space-between;align-items:center;gap:16px}h1{font-size:30px;letter-spacing:-.7px;margin:0}h2{font-size:20px;margin:10px 0}p{margin:8px 0}.intro{color:#657080;margin:6px 0 26px}
a.button{border:1px solid #d2d6dd;background:white;border-radius:6px;padding:8px 16px;color:#34394a;text-decoration:none;white-space:nowrap}
a:focus-visible,pre:focus-visible{outline:3px solid #714b67;outline-offset:3px}
.error,.empty{background:white;border:1px solid #e0e3e8;border-radius:10px;padding:24px}.error{border-top:4px solid #d24c4c}
.eyebrow{font-size:11px;font-weight:750;letter-spacing:1.2px;color:#a83e3e}.message{overflow-wrap:anywhere;color:#733333}
.metadata{display:flex;flex-wrap:wrap;gap:16px 48px;border-top:1px solid #eee;margin-top:22px;padding-top:16px}
.metadata span{display:flex;flex-direction:column;min-width:0}.metadata b{font-size:10px;color:#727c8b;letter-spacing:1px}code{overflow-wrap:anywhere}
.trace{border:1px solid #d8dde6;border-radius:10px;overflow:hidden;margin-top:24px}.trace-head{background:#fff;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;gap:16px}.trace-head h2{font-size:15px;margin:0}.trace-head span{font-size:12px;color:#727c8b}
pre{margin:0;background:#171d2b;color:#e1e7f0;padding:24px;font:13px/1.8 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;tab-size:4}
footer{font-size:12px;color:#737e8e;margin:20px 0 36px}@media(max-width:600px){main{padding:0 16px;margin-top:24px}h1{font-size:24px}.trace-head span{display:none}pre{padding:16px}.error{padding:18px}}
</style></head><body><header><span class="brand">Odoo / Diagnostics</span><span class="badge">Current error only</span></header>
<main><div class="title"><h1>Current error traceback</h1><a class="button" href="">Refresh</a></div>
<p class="intro">The most recent captured error. A new error replaces the previous one.</p>''' + content + '''
<footer>Full traceback preserved · No error history · Emergency access is limited to an authorized browser</footer></main></body></html>'''
