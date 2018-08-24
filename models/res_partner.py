# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime


def _date_creation():
    now  = datetime.date.today()
    return now.strftime('%Y-%m-%d')


class IsRegion(models.Model):
    _name='is.region'
    _order='name'

    name = fields.Char(u'Région')


class IsSecteurActivite(models.Model):
    _name='is.secteur.activite'
    _order='name'

    name = fields.Char(u"Secteur d'activité")


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_code_client_ebp = fields.Char('Code Client EBP')
    is_date_creation   = fields.Date(u'Date de création', default=lambda *a: _date_creation())
    is_siren           = fields.Char('SIREN')
    is_afacturage      = fields.Selection([
        ('Oui', 'Oui'),
        ('Non', 'Non'),
    ], 'Afacturage')
    is_validation_financiere = fields.Selection([
        ('Oui', 'Oui'),
        ('Non', 'Non'),
    ], u'Validation financière')
    is_type_partenaire = fields.Selection([
        ('Client'      , 'Client'),
        ('Prospect'    , 'Prospect'),
        ('Prescripteur', 'Prescripteur'),
    ], 'Type de partenaire')
    is_region_id           = fields.Many2one('is.region'          , u'Région')
    is_secteur_activite_id = fields.Many2one('is.secteur.activite', u"Secteur d'activité")



