#!/usr/bin/python3

import psycopg2
import json
import os

from flask import Flask, request, render_template

CONN_STRING     = os.getenv('CONN_STRING')
APIr            = { 'API': 'OK', 'APIVersion': 1.0 }

app = Flask(__name__)
   
@app.route('/edit/<lead_id>')
@app.route('/edit/<lead_id>/<label>')
def edit(lead_id, label=''):
    
    # Get Status from DB
    resp = getLead(lead_id, True)
    
    if resp['API'] != 'OK':
        return render_template('lead.html', lead_id=lead_id, label=label, error=json.dumps(resp))
    else:
        return render_template('lead.html', lead_id=lead_id, label=label, info=resp)

@app.route('/lead/<lead_id>', methods = ['GET'])
@app.route('/lead/<lead_id>/<int:picklist>', methods = ['GET'])
def getLead(lead_id, picklist=False):

    r = APIr.copy()
    r['lead_id'] = lead_id
    
    try:
    
        # Connect and get lead info (if exists)
        conn = psycopg2.connect(CONN_STRING)
        cur  = conn.cursor()
        
        cur.execute('SELECT status, dsr, presales, notes, EXTRACT(epoch from updated), dq_reason, opp_number FROM aseaton.lead_status WHERE sfdc_lead_id = %s', (lead_id,) )
        row = cur.fetchone()
                
        if row == None:
            r['status'] = 'Unmanaged'
        else:
            r['status'] = row[0]
            r['dsr'] = noneToEmpty(row[1])
            r['presales'] = noneToEmpty(row[2])
            r['notes'] = noneToEmpty(row[3])
            r['updated'] = noneToEmpty(row[4])
            r['dq_reason'] = noneToEmpty(row[5])
            r['opp_number'] = noneToEmpty(row[6])
           
        # Get picklist values for HTML dropdowns
        if(picklist):
            status = []
            dq_reason = []
            dsr = []
            presales = []
            
            cur.execute("SELECT pn, pv FROM aseaton.lead_params WHERE type = 'lov' ORDER BY pn, pv")
            rows = cur.fetchall()
            
            for row in rows:
                if row[0] == 'status':
                    status.append(row[1])
                    
                if row[0] == 'dq_reason':
                    dq_reason.append(row[1])
            
                if row[0] == 'dsr':
                    dsr.append(row[1])
                    
                if row[0] == 'presales':
                    presales.append(row[1])
            
            r['picklist'] = { "status": status, "dq_reason": dq_reason, "dsr": dsr, "presales": presales }
            
        conn.close()
    
    except Exception as err:
        r['API'] = 'Error'
        r['error_type'] = type(err).__name__
        r['error_details'] = err.args        
    
    return r
    
@app.route('/lead/<lead_id>', methods = ['POST'])
def setLead(lead_id):

    r = APIr.copy()
    
    try:
        req = request.get_json()
        
        r['lead_id'] = lead_id
        
        opp_number = emptyToNone(req['opp_number'])
        dq_reason = emptyToNone(req['dq_reason'])
        dsr = emptyToNone(req['dsr'])
        presales = emptyToNone(req['presales'])
        notes = emptyToNone(req['notes'])
        
        conn = psycopg2.connect(CONN_STRING)
        cur  = conn.cursor()
        
        cur.execute('INSERT INTO aseaton.lead_status (sfdc_lead_id, status, opp_number, dq_reason, dsr, presales, notes) values (%s, %s, %s, %s, %s, %s, %s) '
                    'on conflict (sfdc_lead_id) do update set status = EXCLUDED.status,'
                    'opp_number = EXCLUDED.opp_number, '
                    'dq_reason = EXCLUDED.dq_reason, '
                    'dsr = EXCLUDED.dsr, '
                    'presales = EXCLUDED.presales, '
                    'notes = EXCLUDED.notes, '
                    'updated = NOW()', (lead_id, req['status'], opp_number, dq_reason, dsr, presales, notes) )
                    
        cur.execute('INSERT INTO aseaton.lead_status_history (sfdc_lead_id, status, opp_number, dq_reason, dsr, presales, notes) values (%s, %s, %s, %s, %s, %s, %s) '
                    , (lead_id, req['status'], opp_number, dq_reason, dsr, presales, notes) )                    
        
        conn.commit()
        conn.close()
            
    except Exception as err:
        r['API'] = 'Error'
        r['errorType'] = type(err).__name__
        r['errorDetails'] = err.args        
    
    return r

def emptyToNone(val):

    if val == '':
        return None
    else:
        return val
        
def noneToEmpty(val):

    if val == None:
        return ''
    else:
        return val


