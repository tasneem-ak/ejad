/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(Order.prototype, {
    async pay() {
        if (!this.canPay()) {
            return;
        }

        const productIds = [];
        for (const line of this.orderlines) {
            const productId = line.get_product().id;
            if (!productIds.includes(productId)) {
                productIds.push(productId);
            }
        }

        const pickingTypeId = this.pos.picking_type.id;
        const stockData = await this.env.services.orm.call(
            "product.product",
            "check_stock_for_pos",
            [productIds, pickingTypeId],
        );

        for (const line of this.orderlines) {
            const productId = line.get_product().id;
            const qty = stockData[String(productId)];
            if (qty !== undefined && qty <= 5) {
                await this.env.services.popup.add(ErrorPopup, {
                    title: _t("Stock Warning"),
                    body: _t("This product under of the Re-Order Point measure"),
                });
                return;
            }
        }

        return super.pay();
    },
});
