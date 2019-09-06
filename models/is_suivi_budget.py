# -*- coding: utf-8 -*-
from openerp import models,fields,api
import datetime


class IsSuiviBudget(models.Model):
    _name='is.suivi.budget'
    _order='name desc'

    name                = fields.Char(u"Titre du document", required=True)
    commentaire         = fields.Text(u"Commentaires et objectifs")
    taux_transformation = fields.Integer(u"Taux de transformation")
    montant_facture     = fields.Integer(u"Montant facture minimum à prendre en compte")
    mois_ids            = fields.One2many('is.suivi.budget.mois', 'suivi_id', u"Mois du suivi budget", copy=True)
    top_client_ids      = fields.One2many('is.suivi.budget.top.client', 'suivi_id', u"Top Client"    , copy=True)


    @api.multi
    def get_mois(self):
        mois=[]
        for obj in self:
            for m in obj.mois_ids:
                print m
                mois.append(m)
        return mois




class IsSuiviBudgetMois(models.Model):
    _name='is.suivi.budget.mois'
    _order='mois'

    suivi_id        = fields.Many2one('is.suivi.budget', 'Suivi Budget', required=True, ondelete='cascade',index=True)
    mois            = fields.Date(u"Mois", required=True)
    ca_budget       = fields.Integer(u"CA Budget")
    re_previsionnel = fields.Integer(u"RE prévisionnel en valeur")
    re_realise      = fields.Integer(u"RE réalisé en valeur")
    objectif_ca_sud = fields.Integer(u"Objectif CA Sud Ouest et Sud Est")

class IsSuiviBudgetTopClient(models.Model):
    _name='is.suivi.budget.top.client'
    _order='partner_id'

    suivi_id   = fields.Many2one('is.suivi.budget', 'Suivi Budget', required=True, ondelete='cascade',index=True)
    partner_id = fields.Many2one('res.partner', u"Client")
    objectif   = fields.Integer(u"Objectif")

