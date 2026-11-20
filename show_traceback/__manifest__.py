{
    'name': 'Current Error Traceback',
    'version': '18.0.7.2.0',
    'summary': 'View the latest captured Odoo error at a configurable URL',
    'description': """
Current Error Traceback for Odoo 18
================================================================================
View the complete traceback of the latest captured request error.

Configure the viewer URL in Settings while developer mode is enabled.
Authorized browsers can use the standalone emergency viewer after the
addon has loaded, including during subsequent database registry failures.

Only the latest captured error is retained per database. No
server_wide_modules configuration is required. Browser authorization
expires after eight hours. See read.md for setup and limitations.
""",
    'author': 'shuhaife binhamza',
    'website': 'https://shuhaife.pages.dev/',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/remove_history_menu.xml',
    ],
    'images': ['static/description/traceback_preview.png'],
    'sequence': 100,
    'installable': True,
    'application': False,
    'auto_install': False,
}
