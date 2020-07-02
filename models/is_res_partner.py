# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime
import pytz


class is_res_partner(models.Model):
    _name='is.res.partner'
    _order='parent_id,name'
    _auto = False

    parent_id  = fields.Many2one('res.partner', u'Société')
    name       = fields.Char(u'Contact')
    is_company = fields.Boolean(u'Société')
    street     = fields.Char(u'Rue')
    zip        = fields.Char(u'CP')
    city       = fields.Char(u'Ville')
    phone      = fields.Char(u'Téléphone')
    fax        = fields.Char(u'Fax')
    mobile     = fields.Char(u'Mobile')
    email      = fields.Char(u'Mail')
    website    = fields.Char(u'Site')
    function   = fields.Char(u'Fonction')
    is_type_partenaire = fields.Selection([
        ('Client'      , 'Client'),
        ('Prospect'    , 'Prospect'),
        ('Prescripteur', 'Prescripteur'),
    ], u'Type de partenaire')
    is_region_id           = fields.Many2one('is.region'          , u'Région')
    is_secteur_activite_id = fields.Many2one('is.secteur.activite', u"Secteur d'activité")

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'is_res_partner')
        cr.execute("""
            CREATE OR REPLACE view is_res_partner AS (
                select * 
                from (

                    select 
                        id,
                        parent_id,
                        name,
                        is_company,
                        street,
                        zip,
                        city,
                        phone,
                        fax,
                        mobile,
                        email,
                        website,
                        function,
                        is_type_partenaire,
                        is_region_id,
                        is_secteur_activite_id 
                    from res_partner
                    where parent_id is not null and active='t'

                    union

                    select 
                        id,
                        id as parent_id,
                        '' as name,
                        is_company,
                        street,
                        zip,
                        city,
                        phone,
                        fax,
                        mobile,
                        email,
                        website,
                        function,
                        is_type_partenaire,
                        is_region_id,
                        is_secteur_activite_id 
                    from res_partner 
                    where parent_id is null and active='t'
                ) rp
            );
        """)



