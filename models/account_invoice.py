# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    date_due = fields.Date(string=u"Date d'échéance", readonly=False, states={}, index=True, copy=False)

