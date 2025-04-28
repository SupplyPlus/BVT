from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
	_inherit = "sale.report"

	is_return = fields.Boolean(string='Is Return')
	
	# def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
	# 	with_ = ("WITH %s" % with_clause) if with_clause else ""
	# 	print(fields)
	# 	fields['is_return'] = ",s.is_return as is_return"
	# 	groupby += ",s.is_return"
	# 	sale_order_id = self.env['sale.order.line'].search([('is_return','=',True)])
	# 	# for lines in sale_order_id:
	# 	# 	lines._get_invoice_qty()
	# 	# 	lines._get_to_invoice_qty()
	# 	map(lambda x:x._get_invoice_qty(),sale_order_id)
	# 	map(lambda x:x._get_to_invoice_qty(),sale_order_id)
	# 	res = super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
	# 	replace_res = res.replace("sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,","sum(Case When is_return = true Then -product_uom_qty Else product_uom_qty End / u.factor * u2.factor) as product_uom_qty,")
	# 	print(res)
	# 	return replace_res