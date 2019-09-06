# -*- coding: utf-8 -*-
from openerp import models,fields,api
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


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
    def val2html(self,val):
        html=''
        if val:
            html='<span>'+'{:,.0f}'.format(val).replace(","," ").replace(".",",")+' €</span>'
        return html


    @api.multi
    def val2htmlcolor(self,val):
        color='green'
        if val<0:
            color='red'
        html=''
        if val:
            html='<span style="color:'+color+'">'+'{:,.0f}'.format(val).replace(","," ").replace(".",",")+' €</span>'
        return html


    @api.multi
    def get_mois(self):
        mois=[]
        for obj in self:
            for m in obj.mois_ids:
                m.ca_budget_html       = self.val2html(m.ca_budget)
                m.re_previsionnel_html = self.val2htmlcolor(m.re_previsionnel)
                m.re_realise_html      = self.val2htmlcolor(m.re_realise)
                m.objectif_ca_sud_html = self.val2html(m.objectif_ca_sud)
                mois.append(m)
        return mois



    @api.multi
    def get_clients(self):
        clients=[]
        for obj in self:
            for c in obj.top_client_ids:
                clients.append(c)
        return clients


    @api.multi
    def get_periode(self,m):
        d = datetime.strptime(m.mois, '%Y-%m-%d')
        r={}
        r['mois']  = d.strftime('%m/%Y')
        r['debut'] = d - timedelta(days=d.day-1)
        r['fin']   = r['debut'] + relativedelta(months=1)
        return r


    @api.multi
    def get_annee(self):
        r={}
        for obj in self:
            for m in obj.mois_ids:
                d = datetime.strptime(m.mois, '%Y-%m-%d')
                r['debut'] = d - timedelta(days=d.day-1)
                r['fin']   = r['debut'] + relativedelta(years=1)
                return r
        return r


    @api.multi
    def get_top(self):
        ids=[]
        for obj in self:
            for l in obj.top_client_ids:
                ids.append(str(l.partner_id.id))
        return ids


    @api.multi
    def get_nouveaux_clients(self):
        cr = self._cr
        annee = self.get_annee()
        SQL="""
            SELECT id
            FROM res_partner
            WHERE 
                is_date_commande>='"""+str(annee['debut'])+"""' and
                is_date_commande<'"""+str(annee['fin'])+"""'
        """
        cr.execute(SQL)
        res = cr.fetchall()
        ids=[]
        for row in res:
            ids.append(str(row[0]))
        return ids


    @api.multi
    def get_ca_realise_nouveau(self,m):
        partner_ids=self.get_nouveaux_clients()
        return self.get_ca_realise(m,partner_ids)


    @api.multi
    def get_ca_realise_autre(self,m):
        ids1 = self.get_top()
        ids2 = self.get_nouveaux_clients()
        partner_ids = ids1 + ids2
        return self.get_ca_realise(m,partner_ids,not_in=True)


    @api.multi
    def get_ca_realise_top(self,m):
        partner_ids = self.get_top()
        return self.get_ca_realise(m,partner_ids)


    @api.multi
    def get_ca_realise(self,m,partner_ids=False,not_in=False):
        cr = self._cr
        periode = self.get_periode(m)
        SQL="""
            SELECT
                sum(ai.amount_untaxed)
            FROM account_invoice ai
            WHERE 
                ai.date_invoice>='"""+str(periode['debut'])+"""' and
                ai.date_invoice<'"""+str(periode['fin'])+"""' and
                ai.type='out_invoice' and
                ai.state in ('open','paid')
        """
        if partner_ids:
            partner_ids=','.join(partner_ids)
            if not_in:
                SQL=SQL+' and partner_id not in ('+partner_ids+') '
            else:
                SQL=SQL+' and partner_id in ('+partner_ids+') '
        cr.execute(SQL)
        res = cr.fetchall()
        val = 0
        for row in res:
            if row[0]:
                val=row[0]
        return self.val2html(val)


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

