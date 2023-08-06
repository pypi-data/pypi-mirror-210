from odoo import tools
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    pos_name = fields.Char('POS Name', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['pos_name'] = ", s.pos_name as pos_name"
        groupby += ', s.pos_name'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
