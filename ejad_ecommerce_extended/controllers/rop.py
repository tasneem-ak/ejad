from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


class RopController(http.Controller):

    def _check_rop_access(self):
        user = request.env.user
        if not user.has_group('base.group_system') and \
                not user.has_group('stock.group_stock_manager') and \
                not user.has_group('stock.group_stock_user'):
            raise AccessError("You do not have access to this page.")

    @http.route('/shop/rop', type='http', auth='user', website=True)
    def rop_products(self, **kwargs):
        self._check_rop_access()
        products = request.env['product.product'].sudo().search([('qty_available', '<', 5), ('type', '=', 'product'), ])
        return request.render('ejad_ecommerce_extended.rop_products_page', {'products': products})

    @http.route('/shop/rop/update_qty', type='json', auth='user', website=True)
    def update_product_qty(self, product_id, new_qty):
        self._check_rop_access()
        product = request.env['product.product'].sudo().browse(int(product_id))
        if not product.exists():
            return {'success': False, 'error': 'Product not found.'}

        quant = request.env['stock.quant'].sudo().with_context(inventory_mode=True)
        warehouse = request.env['stock.warehouse'].sudo().search([], limit=1)
        location = warehouse.lot_stock_id

        new_quant = quant.create({
            'product_id': product.id,
            'location_id': location.id,
            'inventory_quantity': int(new_qty),
        })
        new_quant.action_apply_inventory()

        self._notify_stock_users(product, new_qty)
        return {'success': True}

    def _notify_stock_users(self, product, new_qty):
        user = request.env.user
        groups = ['stock.group_stock_manager', 'stock.group_stock_user', ]
        notified_partners = request.env['res.partner']
        for group_xml_id in groups:
            group = request.env.ref(group_xml_id, raise_if_not_found=False)
            if group:
                notified_partners |= group.sudo().users.filtered(lambda u: u.id != user.id).mapped('partner_id')

        message = ('%s updated the quantity of "%s" to %s.' % (user.name, product.display_name, new_qty))
        bus = request.env['bus.bus'].sudo()
        for partner in notified_partners:
            bus._sendone(partner, 'simple_notification', {
                'title': 'Stock Quantity Updated',
                'message': message,
                'type': 'info',
                'sticky': True, })

    @http.route('/shop/rop/realtime', type='http', auth='user', website=True)
    def rop_realtime_products(self, **kwargs):
        self._check_rop_access()
        products = request.env['product.product'].sudo().search([('qty_available', '>', 5), ('type', '=', 'product'), ])
        return request.render('ejad_ecommerce_extended.rop_realtime_page', {'products': products})

    @http.route('/shop/rop/realtime/data', type='json', auth='user', website=True)
    def rop_realtime_data(self):
        self._check_rop_access()
        products = request.env['product.product'].sudo().search([('qty_available', '>', 5), ('type', '=', 'product'), ])
        return [{
            'id': p.id,
            'display_name': p.display_name,
            'default_code': p.default_code or '',
            'qty_available': p.qty_available,
            'lst_price': p.lst_price,
            'currency_symbol': p.currency_id.symbol,
            'template_id': p.product_tmpl_id.id,
        } for p in products]

    @http.route('/rop-product', type='json', auth='user')
    def rop_product_api(self):
        self._check_rop_access()
        products = request.env['product.product'].sudo().search([('qty_available', '<', 5), ('type', '=', 'product'), ])
        return [{
            'id': p.id,
            'display_name': p.display_name,
            'default_code': p.default_code or '',
            'qty_available': p.qty_available,
            'lst_price': p.lst_price,
            'currency_symbol': p.currency_id.symbol,
        } for p in products]
