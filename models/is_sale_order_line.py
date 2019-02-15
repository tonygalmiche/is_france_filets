# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


_TYPE_CHANTIER=[
    ('neuf'           , 'Neuf'),
    ('renovation'     , 'Rénovation'),
    ('neuf_renovation', 'Neuf et Rénovation'),
]


class IsSaleOrderLine(models.Model):
    _name='is.sale.order.line'
    _order='id desc'
    _auto = False

    order_id               = fields.Many2one('sale.order', 'Commande')
    date_order             = fields.Date('Date commande')
    is_date_previsionnelle = fields.Date(u'Date prévisionnelle du chantier')
    is_type_chantier       = fields.Selection(_TYPE_CHANTIER, u'Type de chantier')
    is_type_prestation_id  = fields.Many2one('is.type.prestation', u'Type de prestation')
    partner_id             = fields.Many2one('res.partner', 'Client')
    is_type_partenaire = fields.Selection([
        ('Client'      , 'Client'),
        ('Prospect'    , 'Prospect'),
        ('Prescripteur', 'Prescripteur'),
    ], 'Type de partenaire')
    is_region_id           = fields.Many2one('is.region'          , u'Région')
    is_secteur_activite_id = fields.Many2one('is.secteur.activite', u"Secteur d'activité")
    product_id             = fields.Many2one('product.template', 'Article')
    default_code           = fields.Char(u'Référence interne')
    description            = fields.Text(u'Description')
    product_uom_qty        = fields.Float(u"Qté commandée", digits=(14,2))
    price_unit             = fields.Float(u"Prix unitaire", digits=(14,2))
    price_subtotal         = fields.Float(u"Total HT"     , digits=(14,2))
    state = fields.Selection([
        ('draft' , 'Devis'),
        ('sent'  , 'Devis envoyé'),
        ('sale'  , 'Bon de commande'),
        ('done'  , 'Vérouillé'),
        ('cancel', 'Annulé'),
    ], u'État')



    def init(self):
        cr=self._cr
        tools.drop_view_if_exists(cr, 'is_sale_order_line')
        cr.execute("""
            CREATE OR REPLACE view is_sale_order_line AS (
                select
                    sol.id,
                    sol.order_id,
                    so.date_order::timestamp::date,
                    so.is_date_previsionnelle,
                    so.is_type_chantier,
                    so.is_type_prestation_id,
                    so.partner_id,
                    so.state,
                    rp.is_type_partenaire,
                    rp.is_region_id,
                    rp.is_secteur_activite_id,
                    pt.id product_id,
                    pt.default_code,
                    sol.name description,
                    sol.product_uom_qty,
                    sol.price_unit,
                    sol.price_subtotal
                from sale_order so inner join sale_order_line sol on so.id=sol.order_id
                                   inner join res_partner      rp on so.partner_id=rp.id
                                   inner join product_product  pp on sol.product_id=pp.id
                                   inner join product_template pt on pp.product_tmpl_id=pt.id
            )
        """)

