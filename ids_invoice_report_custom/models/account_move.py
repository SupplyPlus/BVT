from odoo import api, fields, models, _
from odoo import tools
import logging
from num2words import num2words
import qrcode
import base64
from io import BytesIO
from odoo import models, api, fields, _
import binascii


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")
    amount_tax_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")
    amount_untaxed_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")

    @api.depends('amount_total', 'amount_tax', 'amount_untaxed')
    def _compute_amount_total_words(self):
        for invoice in self:
            invoice.amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_total)
            invoice.amount_tax_words = invoice.currency_id.amount_to_text(invoice.amount_tax)
            invoice.amount_untaxed_words = invoice.currency_id.amount_to_text(invoice.amount_untaxed)

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res

    def _string_to_hex(self, value):
        if value:
            string = str(value)
            string_bytes = string.encode("UTF-8")
            encoded_hex_value = binascii.hexlify(string_bytes)
            hex_value = encoded_hex_value.decode("UTF-8")
            return hex_value

    def _get_hex(self, tag, length, value):
        if tag and length and value:
            hex_string = self._string_to_hex(value)
            length = len(value)
            conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
            hexadecimal = ''
            while (length > 0):
                remainder = length % 16
                hexadecimal = conversion_table[remainder] + hexadecimal
                length = length // 16
            if len(hexadecimal) == 1:
                hexadecimal = "0" + hexadecimal
            return tag + hexadecimal + hex_string

    def get_qr_code_data(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            sellername = str(self.company_id.name)
            seller_vat_no = self.company_id.vat or ''
            if self.partner_id.company_type == 'company':
                customer_name = self.partner_id.name
                customer_vat = self.partner_id.vat
        else:
            sellername = str(self.partner_id.name)
            seller_vat_no = self.partner_id.vat
        seller_hex = self._get_hex("01", "0c", sellername)
        vat_hex = self._get_hex("02", "0f", seller_vat_no) or ""
        time_stamp = str(self.create_date)
        date_hex = self._get_hex("03", "14", time_stamp)
        total_with_vat_hex = self._get_hex("04", "0a", str(round(self.amount_total, 2))) or 0
        total_vat_hex = self._get_hex("05", "09", str(round(self.amount_tax, 2))) or 0
        print(vat_hex)
        qr_hex = seller_hex + vat_hex + date_hex + total_with_vat_hex + total_vat_hex
        encoded_base64_bytes = base64.b64encode(bytes.fromhex(qr_hex)).decode()
        return encoded_base64_bytes

    qr_code = fields.Binary(string="QR Code", attachment=True, store=True)

    @api.onchange('invoice_line_ids.product_id')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_qr_code_data())
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            lang = 'ar_001'
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)
        lang = tools.get_lang(self.env)
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=self.currency_unit_label.replace("Riyal", 'ريال'),
        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + _('و') + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word=self.currency_subunit_label.replace("Halala", 'هللة'),
            )
        return amount_words
