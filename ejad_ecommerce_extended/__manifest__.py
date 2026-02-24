{
    'name': 'Ecommerce Extended',
    'version': '17.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Ecommerce Technical Task',
    'depends': ['website_sale', 'stock', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/rop_templates.xml',
        'data/menu_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ejad_ecommerce_extended/static/src/js/rop_update_qty.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
