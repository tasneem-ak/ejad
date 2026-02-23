{
    'name': 'POS',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'POS Tecnical Task',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'ejad_pos_extend/static/src/js/pos_payment_patch.js',
            'ejad_pos_extend/static/src/js/payment_screen_patch.js',
            'ejad_pos_extend/static/src/js/cash_now_button.js',
            'ejad_pos_extend/static/src/xml/cash_now_button.xml',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
