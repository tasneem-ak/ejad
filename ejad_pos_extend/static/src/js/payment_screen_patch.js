/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    async _isOrderValid(isForceValidate) {
        const partner = this.currentOrder.get_partner();

        // 1- Customer must be selected
        if (!partner) {
            this.popup.add(ErrorPopup, {
                title: _t("Customer Required"),
                body: _t("Please select a customer before proceeding to payment."),
            });
            return false;
        }

        // 2- Customer must have a phone number
        const phone = partner.phone || partner.mobile || "";
        if (!phone) {
            this.popup.add(ErrorPopup, {
                title: _t("Customer Phone Required"),
                body: _t("The selected customer must have a phone number."),
            });
            return false;
        }

        // 3- Phone must start with +2
        if (!phone.startsWith("+2")) {
            this.popup.add(ErrorPopup, {
                title: _t("Invalid Phone Number"),
                body: _t("The customer phone number must start with +2."),
            });
            return false;
        }

        return super._isOrderValid(isForceValidate);
    },
});
