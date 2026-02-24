from odoo import http, fields
from odoo.http import request


class PosSessionController(http.Controller):

    @http.route('/pos/session/<int:session_id>/orders', type='json', auth='user')
    def get_session_orders(self, session_id):
        session = request.env['pos.session'].sudo().browse(session_id)
        if not session.exists():
            return {'success': False, 'error': 'Session not found.'}

        orders = session.order_ids
        return [{
            'id': order.id,
            'name': order.name,
            'pos_reference': order.pos_reference,
            'partner_id': order.partner_id.name or '',
            'date_order': str(order.date_order),
            'state': order.state,
            'amount_total': order.amount_total,
            'amount_paid': order.amount_paid,
            'amount_tax': order.amount_tax,
            'lines': [{
                'product': line.product_id.display_name,
                'qty': line.qty,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'price_subtotal_incl': line.price_subtotal_incl,
            } for line in order.lines],
        } for order in orders]

    @http.route('/pos/orders/by-date', type='json', auth='user')
    def get_orders_by_date(self, start_date, end_date):
        """Dates should be in YYYY-MM-DD format"""
        start = fields.Datetime.to_datetime(start_date)
        end = fields.Datetime.to_datetime(end_date)
        if not start or not end:
            return {'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD.'}

        # Set end to end of day
        end = end.replace(hour=23, minute=59, second=59)

        orders = request.env['pos.order'].sudo().search([
            ('date_order', '>=', start),
            ('date_order', '<=', end),
        ])
        return [{
            'id': order.id,
            'name': order.name,
            'pos_reference': order.pos_reference,
            'session': order.session_id.name,
            'partner_id': order.partner_id.name or '',
            'date_order': str(order.date_order),
            'state': order.state,
            'amount_total': order.amount_total,
            'amount_paid': order.amount_paid,
            'amount_tax': order.amount_tax,
            'lines': [{
                'product': line.product_id.display_name,
                'qty': line.qty,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'price_subtotal_incl': line.price_subtotal_incl,
            } for line in order.lines],
        } for order in orders]
