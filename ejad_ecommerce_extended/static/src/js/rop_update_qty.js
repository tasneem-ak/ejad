/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.RopUpdateQty = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click .btn_update_qty': '_onClickUpdateQty',
        'click #btnApplyQty': '_onClickApply',
    },

    _onClickUpdateQty(ev) {
        const btn = ev.currentTarget;
        const productId = parseInt(btn.dataset.productId);
        const productName = btn.dataset.productName;
        const productQty = parseFloat(btn.dataset.productQty);

        document.getElementById('modalProductId').value = productId;
        document.getElementById('modalProductName').textContent = productName;
        document.getElementById('modalCurrentQty').textContent = productQty;
        document.getElementById('newQtyInput').value = '';

        $('#updateQtyModal').modal('show');
    },

    async _onClickApply() {
        const productId = parseInt(document.getElementById('modalProductId').value);
        const newQty = parseInt(document.getElementById('newQtyInput').value);

        if (isNaN(newQty) || newQty < 0) {
            alert('Please enter a valid quantity (>= 0).');
            return;
        }

        try {
            const result = await jsonrpc('/shop/rop/update_qty', {
                product_id: productId,
                new_qty: newQty,
            });
            if (result.success) {
                $('#updateQtyModal').modal('hide');
                location.reload();
            } else {
                alert(result.error || 'Failed to update quantity.');
            }
        } catch (err) {
            alert('An error occurred while updating the quantity.');
        }
    },
});
