# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class IsAccountInvoiceLine(models.Model):
    _name='is.account.invoice.line'
    _order='id desc'
    _auto = False

    invoice_id             = fields.Many2one('account.invoice', u'Facture')
    date_invoice           = fields.Date(u'Date facture')
    partner_id             = fields.Many2one('res.partner', u'Client')
    is_type_partenaire = fields.Selection([
        ('Client'      , 'Client'),
        ('Prospect'    , 'Prospect'),
        ('Prescripteur', 'Prescripteur'),
    ], u'Type de partenaire')
    is_region_id           = fields.Many2one('is.region'          , u'Région')
    is_secteur_activite_id = fields.Many2one('is.secteur.activite', u"Secteur d'activité")
    product_id             = fields.Many2one('product.template', u'Article')
    default_code           = fields.Char(u'Référence interne')
    description            = fields.Text(u'Description')
    quantity               = fields.Float(u"Quantité"     , digits=(14,2))
    price_unit             = fields.Float(u"Prix unitaire", digits=(14,2))
    price_subtotal         = fields.Float(u"Total HT"     , digits=(14,2))
    state = fields.Selection([
        ('draft' , 'Brouillon'),
        ('open'  , 'Ouverte'),
        ('paid'  , 'Payé'),
        ('cancel', 'Annulé'),
    ], u'État')


    def init(self):
        cr=self._cr
        tools.drop_view_if_exists(cr, 'is_account_invoice_line')
        cr.execute("""
            CREATE OR REPLACE view is_account_invoice_line AS (
                select
                    ail.id,
                    ail.invoice_id,
                    ai.date_invoice,
                    ai.partner_id,
                    rp.is_type_partenaire,
                    rp.is_region_id,
                    rp.is_secteur_activite_id,
                    pt.id product_id,
                    pt.default_code,
                    ail.name description,
                    ail.quantity,
                    ail.price_unit,
                    ail.price_subtotal,
                    ai.state
                from account_invoice ai inner join account_invoice_line ail on ai.id=ail.invoice_id
                                   inner join res_partner      rp on ai.partner_id=rp.id
                                   inner join product_product  pp on ail.product_id=pp.id
                                   inner join product_template pt on pp.product_tmpl_id=pt.id
                where ai.state<>'cancel'
            )
        """)

