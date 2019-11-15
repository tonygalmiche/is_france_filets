# -*- coding: utf-8 -*-
from openerp import models,fields,api
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


class IsSuiviBudget(models.Model):
    _name='is.suivi.budget'
    _order='name desc'

    name                     = fields.Char(u"Titre du document", required=True)
    commentaire              = fields.Text(u"Commentaires et objectifs")
    taux_transformation      = fields.Integer(u"Taux de transformation")
    montant_facture          = fields.Integer(u"Montant facture minimum à prendre en compte")
    objectif_autre           = fields.Integer(u"Objectif autres clients")
    objectif_new_affaire_val = fields.Integer(u"Objectif nouvelles affaires (en valeur)")
    objectif_new_affaire_pou = fields.Integer(u"Objectif nouvelles affaires (en pourcentage)")
    mois_ids                 = fields.One2many('is.suivi.budget.mois', 'suivi_id', u"Mois du suivi budget"  , copy=True)
    top_client_ids           = fields.One2many('is.suivi.budget.top.client', 'suivi_id', u"Top Client"      , copy=True)
    secteur_activite_ids     = fields.One2many('is.suivi.budget.secteur.activite', 'suivi_id', u"Secteur d'activité", copy=True)
    date_debut               = fields.Date(u"Date début (Journal des ventes)")
    date_fin                 = fields.Date(u"Date fin (Journal des ventes)")

    @api.multi
    def get_journal_vente_html(self):
        cr = self._cr
        for obj in self:
            new_partner_ids = obj.get_nouveaux_clients()
            top_partner_ids=[]
            for line in obj.top_client_ids:
                top_partner_ids.append(line.partner_id.id)
            SQL="""
                SELECT
                    rp.name,
                    ir.name,
                    io.name,
                    ai.date_invoice,
                    ai.number,
                    ai.amount_untaxed,
                    ai.partner_id
                FROM account_invoice ai inner join res_partner     rp on ai.partner_id=rp.id
                                        left outer join is_region  ir on rp.is_region_id=ir.id
                                        left outer join is_origine io on rp.is_origine_id=io.id
                WHERE 
                    ai.date_invoice>='"""+str(obj.date_debut)+"""' and
                    ai.date_invoice<='"""+str(obj.date_fin)+"""' and
                    ai.type='out_invoice' and
                    ai.state in ('open','paid') and
                    ai.amount_untaxed>0
                ORDER BY ai.number desc
            """
            cr.execute(SQL)
            res = cr.fetchall()
            html=u'<table style="border:1px solid black; width:100%;border-collapse: collapse;">'
            html+=u'<tr><th>N°</th><th>Client</th><th>Région</th><th>Origine</th><th>Date</th><th>Facture</th><th>Total HT</th></tr>'
            ct=0
            total=0
            cde_moyenne = 0
            top = 0
            #clair_top = 0
            nouveau = 0
            so = 0
            autre = 0
            for row in res:
                color_partner=u''
                partner_id = row[6]
                if partner_id in top_partner_ids:
                    color_partner = u'LightPink'
                    top+=row[5]

                if str(partner_id) in new_partner_ids:
                    color_partner = u'Khaki'
                    nouveau+=row[5]

                color_region=u''
                if row[1]=='SO' or row[1]=='SE':
                    color_region = u'LightGreen'
                    so+=row[5]

                ct+=1
                amount_untaxed = '{:,.0f}'.format(row[5]).replace(","," ").replace(".",",")
                html+=u'<tr>'
                html+=u'<td style="text-align:center">'+str(ct)+u'</td>'
                html+=u'<td style="text-align:left;background-color:'+color_partner+u'">'+row[0]+u'</td>'
                html+=u'<td style="text-align:center;background-color:'+color_region+u'">'+str(row[1] or '')+u'</td>'
                html+=u'<td style="text-align:center">'+str(row[2] or '')+u'</td>'
                html+=u'<td style="text-align:center">'+str(row[3])+u'</td>'
                html+=u'<td style="text-align:center">'+str(row[4])+u'</td>'
                html+=u'<td style="text-align:right">'+str(amount_untaxed)+u' €</td>'
                html+=u'</tr>'
                total+=row[5]


            cde_moyenne = total / len(res)
            autre = total - nouveau

            total = '{:,.0f}'.format(total).replace(","," ").replace(".",",")
            html+=u'<tr><th colspan="6" style="text-align:right">Total : </th><th style="text-align:right">'+total+u' €</th></tr>'

            html+=u'</table><br />'

            html+=u'<table style="border:1px solid black; width:30%;border-collapse: collapse;">'


            cde_moyenne = '{:,.0f}'.format(cde_moyenne).replace(","," ").replace(".",",")
            html+=u'<tr style="background-color:white"><td style="text-align:left">Cde moyenne : </td><td style="text-align:right">'+cde_moyenne+u' €</td></tr>'

            top = '{:,.0f}'.format(top).replace(","," ").replace(".",",")
            html+=u'<tr style="background-color:LightPink"><td style="text-align:left">Top : </td><td style="text-align:right">'+top+u' €</td></tr>'

            #clair_top = '{:,.0f}'.format(clair_top).replace(","," ").replace(".",",")
            #html+=u'<tr style="background-color:white"><td style="text-align:left">Clair Top : </td><td style="text-align:right">'+clair_top+u' €</td></tr>'

            nouveau = '{:,.0f}'.format(nouveau).replace(","," ").replace(".",",")
            html+=u'<tr style="background-color:Khaki"><td style="text-align:left">Nouveau : </td><td style="text-align:right">'+nouveau+u' €</td></tr>'

            so = '{:,.0f}'.format(so).replace(","," ").replace(".",",")
            html+=u'<tr style="background-color:LightGreen"><td style="text-align:left">SO / SE : </td><td style="text-align:right">'+so+u' €</td></tr>'

            autre = '{:,.0f}'.format(autre).replace(","," ").replace(".",",")
            html+=u'<tr style="background-color:white"><td style="text-align:left">Autres clients : </td><td style="text-align:right">'+autre+u' €</td></tr>'


            html+=u'</table>'

            return html


    @api.multi
    def get_html(self):
        now = datetime.now()
        mois=[]
        tab={}
        for obj in self:
            html=u'<table style="border:1px solid black; width:100%;border-collapse: collapse;">'
            html+=u'<tr><td>Mois</td>'
            for m in obj.mois_ids:
                html+=u'<th>'+obj.get_periode(m)['mois']+u'</th>'
            html+=u'<td>Total</td>'
            html+=u'<td>Objectifs</td>'
            html+=u'</tr>'

            html+='<tr><td>CA Budget</td>'
            total = 0
            for m in obj.get_mois():
                total+=m.ca_budget
                html+=u'<td class="style1">' + m.ca_budget_html +u'</td>'
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td colspan="15" class="titre">CA Prévisionnel</td></tr>'

            html+=u'<tr><td>Carnet de commande (ferme)</td>'
            tab['ca_carnet_commande_ferme']={}
            total_carnet_commande = 0
            for m in obj.get_mois():
                periode = self.get_periode(m)
                if periode['fin']>now:
                    val = obj.get_ca_commande_ferme(m)
                    html+=u'<td class="style1" style="background-color:LemonChiffon;">'+obj.val2html(val)+u'</td>'
                else:
                    val = obj.get_ca_realise(m)
                    html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total_carnet_commande+=val
                tab['ca_carnet_commande_ferme'][m.mois] = val
            html+=u'<td class="style1">'+obj.val2html(total_carnet_commande)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Prévisionnel (avec taux transformation)</td>'
            tab['ca_carnet_commande_prev']={}
            total = 0
            for m in obj.get_mois():
                val = obj.get_ca_commande_prev(m)
                tab['ca_carnet_commande_prev'][m.mois] = val
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>TOTAL Prévision</td>'
            tab['total_prevision']={}
            total = 0
            for m in obj.get_mois():
                val = tab['ca_carnet_commande_ferme'][m.mois] + tab['ca_carnet_commande_prev'][m.mois]
                tab['total_prevision'][m.mois] = val
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Écart avec budget</td>'
            total = 0
            for m in obj.get_mois():
                val = tab['total_prevision'][m.mois]  - m.ca_budget
                html+=u'<td class="style1">'+obj.val2htmlcolor(val,u'€')+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td colspan="15" class="titre">CA Réalisé</td></tr>'
            html+=u'<tr><td>CA Réalisé HT</td>'

            tab['ca_realise']={}
            total = 0
            for m in obj.get_mois():
                val =  obj.get_ca_realise(m)
                tab['ca_realise'][m.mois] = val
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Écart avec budget en valeur</td>'
            total = 0
            for m in obj.get_mois():
                val =  tab['ca_realise'][m.mois] - m.ca_budget
                html+=u'<td class="style1">'+obj.val2htmlcolor(val,u'€')+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Écart avec budget en % </td>'
            total = 0
            for m in obj.get_mois():
                #=100*(1-90000/83713)
                val = 0
                if tab['ca_realise'][m.mois]>0:
                    val =  100*(1 - m.ca_budget / tab['ca_realise'][m.mois])
                html+=u'<td class="style1">'+obj.val2htmlcolor(val,u'%')+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td colspan="15" class="titre">Résultat réalisé</td></tr>'
            html+=u'<tr><td>RE  prévisionnel en valeur</td>'
            total = 0
            for m in obj.get_mois():
                html+=u'<td class="style1">'+m.re_previsionnel_html+u'</td>'
                total+=m.re_previsionnel
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>RE  réalisé en valeur</td>'
            total = 0
            for m in obj.get_mois():
                html+=u'<td class="style1">'+m.re_realise_html+u'</td>'
                total+=m.re_realise
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td colspan="15" class="titre">Indicateur de carnet Cde</td></tr>'

            html+=u'<tr><td>Cde Moyenne</td>'
            total = 0
            for m in obj.get_mois():
                val = obj.get_commande_moyenne(m)
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Facture > '+str(obj.montant_facture)+u' € (en quantité)</td>'
            total = 0
            for m in obj.get_mois():
                val = obj.get_nb_factures_30k(m)
                html+=u'<td class="style1">'+str(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+str(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td colspan="15" class="titre">Suivi  Top Clients (11)</td></tr>'
            total_objectif = 0
            for c in obj.get_clients():
                html+=u'<tr><td>'+c.partner_id.name+u'</td>'
                total = 0

                for m in obj.get_mois():
                    periode = self.get_periode(m)
                    if periode['fin']>now:
                        val = obj.get_ca_commande_ferme(m,[str(c.partner_id.id)])
                        html+=u'<td class="style1" style="background-color:LemonChiffon;">'+obj.val2html(val)+u'</td>'
                    else:
                        val = obj.get_ca_realise(m,[str(c.partner_id.id)])
                        html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                    total+=val
                html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
                html+=u'<td class="style1">'+obj.val2html(c.objectif)+'</td>'
                html+=u'</tr>'
                total_objectif+=c.objectif

            html+=u'<tr><td>Total</td>'
            total = 0
            for m in obj.get_mois():
                periode = self.get_periode(m)
                val = obj.get_ca_realise_top(m)
                if periode['fin']>now:
                    html+=u'<td class="style1" style="background-color:LemonChiffon;"><b>'+obj.val2html(val)+u'</b></td>'
                else:
                    html+=u'<td class="style1"><b>'+obj.val2html(val)+u'</b></td>'
                total+=val
            html+=u'<td class="style1"><b>'+obj.val2html(total)+u'</b></td>'
            html+=u'<td class="style1"><b>'+obj.val2html(total_objectif)+u'</b></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Autres clients</td>'
            total = 0
            for m in obj.get_mois():
                val = obj.get_ca_realise_autre(m)
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td class="style1">'+obj.val2html(obj.objectif_autre)+'</td>'
            html+=u'</tr>'



            html+=u'<tr><td colspan="15" class="titre">Suivi Secteurs d\'activités</td></tr>'
            total_objectif = 0
            for s in obj.get_secteurs():
                html+=u'<tr><td>'+s.secteur_activite_id.name+u'</td>'
                total = 0
                for m in obj.get_mois():
                    periode = self.get_periode(m)
                    if periode['fin']>now:
                        #val = obj.get_ca_commande_ferme(m)
                        val = obj.get_ca_commande_ferme(m,secteur_activite_id=s.secteur_activite_id.id)
                        html+=u'<td class="style1" style="background-color:LemonChiffon;">'+obj.val2html(val)+u'</td>'
                    else:
                        val = obj.get_ca_realise(m,secteur_activite_id=s.secteur_activite_id.id)
                        html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                    total+=val
                html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
                html+=u'<td class="style1">'+obj.val2html(s.objectif)+'</td>'
                html+=u'</tr>'


            html+=u'<tr><td colspan="15" class="titre">Nouvelles affaires</td></tr>'
            html+=u'<tr><td>En Valeur</td>'
            total_nouvelles_affaires = 0
            for m in obj.get_mois():
                val = obj.get_ca_realise_nouveau(m)
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total_nouvelles_affaires+=val
            html+=u'<td class="style1">'+obj.val2html(total_nouvelles_affaires)+'</td>'
            html+=u'<td class="style1">'+obj.val2html(obj.objectif_new_affaire_val)+'</td>'
            html+=u'</tr>'

            html+=u'<tr><td>En % du CA mensuel</td>'
            for m in obj.get_mois():
                html+=u'<td class="style1">'+str(obj.get_ca_realise_nouveau_pourcent(m))+u' %</td>'
            pourentage_nouvelles_affaires=0
            if total_carnet_commande>0:
                pourentage_nouvelles_affaires = int(round(100*total_nouvelles_affaires/total_carnet_commande))
            html+=u'<td class="style1">'+str(pourentage_nouvelles_affaires)+u' %</td>'
            html+=u'<td class="style1">'+obj.val2html(obj.objectif_new_affaire_pou,unite=u'%')+'</td>'
            html+=u'</tr>'

            html+=u'<tr><td colspan="15" class="titre">Dont CA Sud Ouest et Sud Est</td></tr>'
            html+=u'<tr><td>Objectif mensuel</td>'
            total = 0
            for m in obj.get_mois():
                val = m.objectif_ca_sud
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'

            html+=u'<tr><td>Réalisé en Valeur</td>'
            total = 0
            for m in obj.get_mois():
                val = obj.get_ca_realise_sud(m)
                html+=u'<td class="style1">'+obj.val2html(val)+u'</td>'
                total+=val
            html+=u'<td class="style1">'+obj.val2html(total)+u'</td>'
            html+=u'<td></td>'
            html+=u'</tr>'
            html+=u'</table>'
            return html


    @api.multi
    def val2html(self,val,style='',unite=u'€'):
        html=''
        if val:
            html=u'<span style="'+style+'">'+'{:,.0f}'.format(val).replace(","," ").replace(".",",")+u' '+unite+u'</span>'
        return html


    @api.multi
    def val2htmlcolor(self,val,unite=u'€'):
        color='green'
        if val<0:
            color='red'
        html=''
        if val:
            html=u'<span style="color:'+color+'">'+'{:,.0f}'.format(val).replace(","," ").replace(".",",")+u' '+unite+u'</span>'
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

                #m.ca_carnet_commande_ferme = self.get_ca_commande_ferme(m)
                #m.ca_carnet_commande_prev  = self.get_ca_commande_prev(m)
                #m.total_prevision          = m.ca_carnet_commande_ferme + m.ca_carnet_commande_prev
                #m.ecart_budget = m.total_prevision - m.ca_budget



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
    def get_secteurs(self):
        secteurs=[]
        for obj in self:
            for line in obj.secteur_activite_ids:
                secteurs.append(line)
        return secteurs


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
            SELECT id,name
            FROM res_partner
            WHERE 
                is_date_commande>='"""+str(annee['debut'])+"""' and
                is_date_commande<'"""+str(annee['fin'])+"""'
            ORDER BY name
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
        val=self.get_ca_realise(m,partner_ids)
        return val


    @api.multi
    def get_ca_realise_nouveau_pourcent(self,m):
        partner_ids=self.get_nouveaux_clients()
        nouveau = self.get_ca_realise(m,partner_ids)
        total   = self.get_ca_realise(m)
        val=0
        if total>0:
            val = int(round(100 * nouveau / total))
        return val


    @api.multi
    def get_ca_realise_autre(self,m):
        ids1 = self.get_top()
        ids2 = self.get_nouveaux_clients()
        partner_ids = ids1 + ids2
        val = self.get_ca_realise(m,partner_ids,not_in=True)
        return val


    @api.multi
    def get_ca_realise_top(self,m):
        partner_ids = self.get_top()
        val = self.get_ca_realise(m,partner_ids)
        return val


    @api.multi
    def get_ca_realise(self,m,partner_ids=False,not_in=False,secteur_activite_id=False):
        cr = self._cr
        periode = self.get_periode(m)
        SQL="""
            SELECT
                sum(ai.amount_untaxed)
            FROM account_invoice ai inner join res_partner rp on ai.partner_id=rp.id
            WHERE 
                ai.date_invoice>='"""+str(periode['debut'])+"""' and
                ai.date_invoice<'"""+str(periode['fin'])+"""' and
                ai.type='out_invoice' and
                ai.state in ('open','paid')
        """
        if secteur_activite_id:
            SQL=SQL+' and rp.is_secteur_activite_id='+str(secteur_activite_id)+' '
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
        return val


    @api.multi
    def get_ca_realise_sud(self,m):
        cr = self._cr
        periode = self.get_periode(m)
        SQL="""
            SELECT
                sum(ai.amount_untaxed)
            FROM account_invoice ai inner join res_partner rp on ai.partner_id=rp.id
                                    inner join is_region   ir on rp.is_region_id=ir.id
            WHERE 
                ai.date_invoice>='"""+str(periode['debut'])+"""' and
                ai.date_invoice<'"""+str(periode['fin'])+"""' and
                ai.type='out_invoice' and
                ai.state in ('open','paid') and
                ir.name in ('SE','SO') 
        """
        cr.execute(SQL)
        res = cr.fetchall()
        val = 0
        for row in res:
            if row[0]:
                val=row[0]
        return val


    @api.multi
    def get_commande_moyenne(self,m):
        """Ca facturé sur la période / Nombre de factures"""
        cr = self._cr
        periode = self.get_periode(m)
        SQL="""
            SELECT
                sum(ai.amount_untaxed)/count(*)
            FROM account_invoice ai
            WHERE 
                ai.date_invoice>='"""+str(periode['debut'])+"""' and
                ai.date_invoice<'"""+str(periode['fin'])+"""' and
                ai.type='out_invoice' and
                ai.state in ('open','paid')
        """
        cr.execute(SQL)
        res = cr.fetchall()
        val = 0
        for row in res:
            if row[0]:
                val=row[0]
        return val


    @api.multi
    def get_nb_factures_30k(self,m):
        """Nombre de factures supérieures au paramètre indiqué (30K€)"""
        cr = self._cr
        for obj in self:
            periode = self.get_periode(m)
            SQL="""
                SELECT count(*)
                FROM account_invoice ai
                WHERE 
                    ai.date_invoice>='"""+str(periode['debut'])+"""' and
                    ai.date_invoice<'"""+str(periode['fin'])+"""' and
                    ai.type='out_invoice' and
                    ai.state in ('open','paid') and
                    ai.amount_untaxed>"""+str(obj.montant_facture)+"""
            """
            cr.execute(SQL)
            res = cr.fetchall()
            val = 0
            for row in res:
                if row[0]:
                    val=row[0]
            return val


    @api.multi
    def get_ca_commande_ferme(self,m,partner_ids=False,not_in=False,secteur_activite_id=False):
        cr = self._cr
        periode = self.get_periode(m)
        #Prise en compte du retard de 90 jours
        debut = periode['debut']
        if debut<=datetime.now():
            debut = debut - timedelta(days=90)
        val = 0
        SQL="""
            SELECT
                sum(so.amount_untaxed)
            FROM sale_order so inner join res_partner rp on so.partner_id=rp.id
            WHERE 
                so.is_date_previsionnelle>='"""+str(debut)+"""' and
                so.is_date_previsionnelle<'"""+str(periode['fin'])+"""' and
                so.state='sale' and invoice_status='to invoice'
        """
        if secteur_activite_id:
            SQL=SQL+' and rp.is_secteur_activite_id='+str(secteur_activite_id)+' '
        if partner_ids:
            partner_ids=','.join(partner_ids)
            if not_in:
                SQL=SQL+' and partner_id not in ('+partner_ids+') '
            else:
                SQL=SQL+' and partner_id in ('+partner_ids+') '
        cr.execute(SQL)
        res = cr.fetchall()
        for row in res:
            if row[0]:
                val=row[0]
        return val



    @api.multi
    def get_ca_commande_prev(self,m):
        cr = self._cr
        for obj in self:
            periode = self.get_periode(m)
            now = datetime.now()
            debut = periode['debut']
            fin   = periode['fin']
            val = 0
            if fin>now:
                SQL="""
                    SELECT
                        sum(so.amount_untaxed)
                    FROM sale_order so
                    WHERE 
                        so.is_date_previsionnelle>='"""+str(periode['debut'])[:10]+"""' and
                        so.is_date_previsionnelle<'"""+str(periode['fin'])[:10]+"""' and
                        so.state in ('draft','sent')
                """
                cr.execute(SQL)
                res = cr.fetchall()

                for row in res:
                    if row[0]:
                        val=row[0] * obj.taux_transformation/100
            #else:
            #    val = self.get_ca_realise(m)
            return val




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



class IsSuiviBudgetSecteurActivite(models.Model):
    _name='is.suivi.budget.secteur.activite'
    _order='secteur_activite_id'

    suivi_id            = fields.Many2one('is.suivi.budget', 'Suivi Budget', required=True, ondelete='cascade',index=True)
    secteur_activite_id = fields.Many2one('is.secteur.activite', u"Secteur d'activité")
    objectif            = fields.Integer(u"Objectif")



