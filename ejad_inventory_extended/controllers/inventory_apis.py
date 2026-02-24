from odoo import http
from odoo.http import request


class InventoryApiController(http.Controller):

    @http.route('/inventory/rop-products', type='json', auth='user')
    def get_rop_products(self):
        products = request.env['product.product'].sudo().search([('rop_count', '>', 0), ('type', '=', 'product'), ])
        return [{
            'id': p.id,
            'display_name': p.display_name,
            'default_code': p.default_code or '',
            'qty_available': p.qty_available,
            'rop_count': p.rop_count,
        } for p in products]

    @http.route('/inventory/product/<int:product_id>/rop-count', type='json', auth='user')
    def get_product_rop_count(self, product_id):
        product = request.env['product.product'].sudo().browse(product_id)
        if not product.exists():
            return {'success': False, 'error': 'Product not found.'}
        return {
            'id': product.id,
            'display_name': product.display_name,
            'rop_count': product.rop_count,
        }
