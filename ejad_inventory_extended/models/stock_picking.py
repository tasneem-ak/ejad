from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        today = fields.Date.today()
        for picking in self:
            if (picking.picking_type_code == 'outgoing'
                    and picking.scheduled_date
                    and picking.scheduled_date.date() >= today):
                raise ValidationError(
                    _("You cannot validate outgoing transfer '%(name)s' with a "
                      "scheduled date of today or in the future.",
                      name=picking.name)
                )
        return super().button_validate()
