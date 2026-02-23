from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def check_stock_for_pos(self, product_ids, picking_type_id):
        picking_type = self.env['stock.picking.type'].browse(picking_type_id)
        warehouse = picking_type.warehouse_id
        products = self.with_context(warehouse=warehouse.id).browse(product_ids)
        return {str(p.id): p.qty_available for p in products}
