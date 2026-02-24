from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


class RopController(http.Controller):

    @http.route('/shop/rop', type='http', auth='user', website=True)
    def rop_products(self, **kwargs):
        if not request.env.user.has_group('base.group_system') and \
                not request.env.user.has_group('stock.group_stock_manager') and \
                not request.env.user.has_group('stock.group_stock_user'):
            raise AccessError("You do not have access to this page.")

        products = request.env['product.product'].sudo().search([('qty_available', '<', 5), ('type', '=', 'product'), ])
        return request.render('ejad_ecommerce_extended.rop_products_page', {'products': products})
