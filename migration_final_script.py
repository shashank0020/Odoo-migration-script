import xmlrpclib

#LOGIN DETAILS
#ENTER YOUR LOGIN CREDENTIAL TO CONNECT
username = 'admin'
password = 'joan'
database = 'sun1'
sock_comm = xmlrpclib.ServerProxy('http://yourdomain/xmlrpc/common')
#sock_comm = xmlrpclib.ServerProxy('http://yourdomain/xmlrpc/common')
uid = sock_comm.login(database,username,password)
sock = xmlrpclib.ServerProxy('http://yourdomain/xmlrpc/object')
#sock = xmlrpclib.ServerProxy('http://yourdomain/xmlrpc/object')
print "WOW !!CONNECTION SUCCESSFULL"
#SO SEARCH
print 'SEARCHING SALE ORDERS......................'
ids = sock.execute(database,uid, password,'sale.order', 'search', [('state','=','draft'),('id','!=',1116)])
print "------------------TOTAL SALE ORDERS=",len(ids)
import ipdb;ipdb.set_trace()
for i in ids:
    
#darft-progress
    sock.exec_workflow (database, uid, password, 'sale.order','order_confirm',i)
    print '---------------YOUR ORDER IS CONFIRMED--------------'
    
#progres-invoice draft
    
    sock.exec_workflow (database, uid, password, 'sale.order','manual_invoice',i)
    print '---------------PUTTING INOVICE IN DRAFT STATE--------------'
#unlink purchase orders
    
    print '---------------REMOVE PURCHASE ORDERS QUOTATION(Import csv later)--------------'
    po_id=sock.execute(database,uid, password,'purchase.order', 'search', [])
    if po_id:
        for i1 in po_id:
            sock.execute(database,uid, password,'purchase.order', 'unlink', [i1])
    else:
        pass
#ignore shipping exceptioin
    sock.exec_workflow (database, uid, password, 'sale.order', 'ship_corrected', i)

#INVOICE SEARCH
    print '---------------IAM ALL READY FOR INVOCING--------------'
    
    sale_origin= sock.execute(database,uid, password,'sale.order', 'read',i, ['name']) 
    ac_ids = sock.execute(database,uid, password,'account.invoice', 'search', [('origin','=',sale_origin['name'])])
    for i2 in ac_ids:
        

#inv draft-progress
        
        sock.exec_workflow (database, uid, password, 'account.invoice', 'invoice_open', i2)
        print '---------------INOVICE IS OPEN--------------'
		#
        re_val=['amount_total','partner_id','period_id','reference']
        #read fields from account.invoice        
        res= sock.execute(database,uid, password,'account.invoice', 'read',i2, re_val)        
#register payment
        #import ipdb;ipdb.set_trace()
        reg_pay = sock.execute(database,uid, password,'account.invoice', 'invoice_pay_customer', [i2])
#create new coucher        
        vo_cr={'journal_id':7,'amount':res['amount_total'],'period':res['period_id'][0],'account_id':25,'partner_id':res['partner_id'][0]}
        vo_id=sock.execute(database,uid, password,'account.voucher','create',vo_cr)
        move_line_id=sock.execute(database,uid, password,'account.move.line', 'search', [('ref','=',res['reference']),('name','=','/')])
        vo_line={'voucher_id':vo_id,'account_id':8,'move_line_id':move_line_id[0],'amount':res['amount_total']}
#create voucher line        
        vo_line_cr=sock.execute(database,uid, password,'account.voucher.line','create',vo_line)
#pay invoice        
        pay_inv = sock.execute(database,uid, password,'account.voucher', 'button_proforma_voucher', [vo_id])
                
#state=paid        
        sock.exec_workflow (database, uid, password, 'account.voucher', 'proforma_voucher', vo_id)

        print '---------------INOVICED PAYED --------------'

#SO state=done
        state_val={'state':'done'}
        sock.execute (database, uid, password, 'sale.order','write',i,state_val)

#DO SEARCH
        print '---------------DELIVERING ORDERS TO CUSTOMER--------------'
        do_ids = sock.execute(database,uid, password,'stock.picking', 'search', [])

        for i3 in do_ids:
#force availiablity        
            sock.execute(database,uid, password,'stock.picking','force_assign',[i3])
            print '---------------ORDER FORCED TO DELIVER--------------'
#ready to deliver        
            sock.execute(database,uid, password,'stock.picking','action_process',[i3])
            print '---------------YOUR ORDER IS READY--------------'
            stock_move_id= sock.execute(database,uid, password,'stock.move', 'search', [('picking_id','=',i3)])
            for i4 in stock_move_id:
#state=delivered            
                sock.execute(database,uid, password,'stock.move','action_done',[i4])
                print '---------------VALIDATING PRODUCT--------------'
            

print '**************************GAME------------- OVER*****************'    

        
        


    
