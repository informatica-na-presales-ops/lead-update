#!/usr/bin/python3

import psycopg2
import json
import os

from flask import Flask, request, render_template

CONN_STRING     = os.getenv('CONN_STRING')
APIr            = { 'API': 'OK', 'APIVersion': 0.8 }

app = Flask(__name__)
   
@app.route('/edit/<lead_id>')
@app.route('/edit/<lead_id>/<label>')
def edit(lead_id, label=''):
    
    # Get Status from DB
    resp = getLead(lead_id)
    
    if resp['API'] != 'OK':
        return render_template('lead.html', lead_id=lead_id, label=label, error=json.dumps(resp))
    else:
        return render_template('lead.html', lead_id=lead_id, label=label, info=json.dumps(resp))

@app.route('/lead/<lead_id>', methods = ['GET'])
def getLead(lead_id):

    r = APIr.copy()
    r['lead_id'] = lead_id
    
    try:
    
        conn = psycopg2.connect(CONN_STRING)
        cur  = conn.cursor()
        
        cur.execute('SELECT status, dsr, presales, notes, EXTRACT(epoch from updated), dq_reason, opp_number FROM aseaton.lead_status WHERE sfdc_lead_id = %s', (lead_id,) )
        row = cur.fetchone()
        conn.close()
        
        if row == None:
            r['status'] = 'Unmanaged'
        else:
            r['status'] = row[0]
            r['dsr'] = row[1]
            r['presales'] = row[2]
            r['notes'] = row[3]
            r['updated'] = row[4]
            r['dq_reason'] = row[5]
            r['opp_number'] = row[6]
    
    except Exception as err:
        r['API'] = 'Error'
        r['error_type'] = type(err).__name__
        r['error_details'] = err.args        
    
    return r
    
@app.route('/lead/<lead_id>', methods = ['POST'])
def setLead(lead_id):

    r = APIr.copy()
    
    try:
        #r['raw'] = request
        
        req = request.get_json()
        
        r['lead_id'] = lead_id
        #r['request_body'] = req
        
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

# app.run(debug=False)

