/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CashNowButton extends Component {
    static template = "ejad_pos_extend.CashNowButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.printer = useService("printer");
        this.report = useService("report");
        this.hardwareProxy = useService("hardware_proxy");
    }

    async click() {
        const order = this.pos.get_order();

        if (!order || order.get_orderlines().length === 0) {
            await this.popup.add(ErrorPopup, {
                title: _t("Empty Order"),
                body: _t("Please add products before paying."),
            });
            return;
        }

        // 1- Set customer to Administrator (partner id = 3 is base.partner_admin)
        const adminPartner = this.pos.db.get_partner_by_id(3);
        if (!adminPartner) {
            await this.popup.add(ErrorPopup, {
                title: _t("Customer Not Found"),
                body: _t("Administrator customer not found. Please load it in the POS."),
            });
            return;
        }
        order.set_partner(adminPartner);

        // 2- Set order to be invoiced
        order.set_to_invoice(true);

        // 3- Add cash payment line for the full amount
        const cashMethod = this.pos.payment_methods.find(
            (pm) => pm.type === "cash"
        );
        if (!cashMethod) {
            await this.popup.add(ErrorPopup, {
                title: _t("No Cash Method"),
                body: _t("No cash payment method is configured for this POS."),
            });
            return;
        }

        // Clear existing payment lines
        const existingLines = [...order.get_paymentlines()];
        for (const line of existingLines) {
            order.remove_paymentline(line);
        }

        order.add_paymentline(cashMethod);

        // 4- Finalize: push order to server, print invoice and receipt
        try {
            this.hardwareProxy.openCashbox();
            order.date_order = luxon.DateTime.now();
            order.finalized = true;

            this.env.services.ui.block();
            const syncResult = await this.pos.push_single_order(order);
            if (!syncResult) {
                this.env.services.ui.unblock();
                return;
            }

            // Print the invoice PDF
            if (syncResult[0]?.account_move) {
                await this.report.doAction("account.account_invoices", [
                    syncResult[0].account_move,
                ]);
            }
            this.env.services.ui.unblock();

            // Print the POS receipt
            await this.printer.print(
                OrderReceipt,
                {
                    data: order.export_for_printing(),
                    formatCurrency: this.env.utils.formatCurrency,
                },
                { webPrintFallback: true }
            );

            // Clean up and go back to a new order
            this.pos.db.remove_unpaid_order(order);
            this.pos.removeOrder(order);
            this.pos.add_new_order();
            this.pos.showScreen("ProductScreen");
        } catch (error) {
            this.env.services.ui.unblock();
            await this.popup.add(ErrorPopup, {
                title: _t("Payment Error"),
                body: _t("An error occurred while processing the payment."),
            });
        }
    }
}

ProductScreen.addControlButton({
    component: CashNowButton,
    condition: function () {
        return this.pos.payment_methods.some((pm) => pm.type === "cash");
    },
});
