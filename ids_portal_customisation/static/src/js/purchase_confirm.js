odoo.define('ids_portal_customisation.confirm_rfq', function (require) {
    'use strict';

    var rpc = require('web.rpc');

    function confirmRFQ(button) {
        var rfq_id = button.getAttribute('data-id');
        console.log('rfq_id',rfq_id)
        if (rfq_id) {
            rpc.query({
                model: 'purchase.order',
                method: 'action_rfq_confirm',
                args: [parseInt(rfq_id)],
            })
            .then(function (result) {
//                alert('RFQ confirmed successfully!');
                location.reload();
            })
            .catch(function (error) {
                alert('Failed to confirm RFQ: ' + (error.message || 'Unknown error'));
                console.error('RPC error:', error);
            });
        } else {
            console.log('RFQ ID is missing');
        }
    }

    function viewReceipt(button) {
        var purchase_order_id = button.getAttribute('data-id');
        if (purchase_order_id) {
            window.location.href = '/my/receipt/' + purchase_order_id;
        } else {
            console.log('Purchase ID is missing for receipt view');
        }
    }

    window.confirmRFQ = confirmRFQ;
    window.viewReceipt = viewReceipt;
});
