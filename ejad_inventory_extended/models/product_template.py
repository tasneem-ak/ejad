from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_rop = fields.Boolean(string="Has ROP")
    rop_count = fields.Integer(string="ROP Count")
    same_rop_count = fields.Integer(
        string="Same ROP Products",
        compute='_compute_same_rop_count',
    )

    @api.depends('has_rop', 'rop_count')
    def _compute_same_rop_count(self):
        for record in self:
            if record.has_rop and record.rop_count and isinstance(record.id, int):
                record.same_rop_count = self.search_count([
                    ('has_rop', '=', True),
                    ('rop_count', '=', record.rop_count),
                    ('id', '!=', record.id),
                ])
            else:
                record.same_rop_count = 0

    def action_view_same_rop_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products with ROP Count %s' % self.rop_count,
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'domain': [
                ('has_rop', '=', True),
                ('rop_count', '=', self.rop_count),
                ('id', '!=', self.id),
            ],
        }
