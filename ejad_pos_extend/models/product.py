from odoo import _, api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def check_stock_for_pos(self, product_ids, picking_type_id):
        picking_type = self.env['stock.picking.type'].browse(picking_type_id)
        warehouse = picking_type.warehouse_id
        products = self.with_context(warehouse=warehouse.id).browse(product_ids)
        stock_data = {str(p.id): p.qty_available for p in products}

        low_stock_products = products.filtered(lambda p: p.qty_available <= 5)
        if low_stock_products:
            self._notify_warehouse_admins(low_stock_products, warehouse)

        return stock_data

    def _notify_warehouse_admins(self, products, warehouse):
        admin_group = self.env.ref('stock.group_stock_manager')
        admin_partners = admin_group.users.mapped('partner_id')
        if not admin_partners:
            return
        for product in products:
            product.product_tmpl_id.message_post(
                body=_(
                    "POS Alert: Product <b>%(product)s</b> has low stock "
                    "(%(qty)s units) in warehouse <b>%(warehouse)s</b>. "
                    "Please check the Re-Order Point.",
                    product=product.display_name,
                    qty=product.qty_available,
                    warehouse=warehouse.name,
                ),
                subject=_("Low Stock Alert from POS"),
                partner_ids=admin_partners.ids,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
