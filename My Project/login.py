import os
from flask import Flask, request, redirect, render_template, session, url_for
from DBConnect import get_db_connection

app = Flask(__name__)
app.secret_key = os.urandom(24)


#Shadeed---------------------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM User WHERE username = %s AND password = %s AND isActive = 1"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("SELECT * FROM Admin WHERE Username = %s", (username,))
            is_admin = cursor.fetchone()
            
            cursor.execute("SELECT * FROM Customer WHERE Username = %s", (username,))
            is_customer = cursor.fetchone()
            
            session['username'] = username
            if is_admin:
                session['role'] = 'Admin'
            elif is_customer:
                cursor.execute("SELECT * FROM Volunteers WHERE Username = %s", (username,))
                if cursor.fetchone():
                    session['role'] = 'Volunteer'
                else:
                    session['role'] = 'Customer'
            else:
                session['role'] = 'User'
                
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        else:
            cursor.close()
            conn.close()
            return render_template('login.html', error="Invalid username or password.")
            
    return render_template('login.html')






@app.route('/become_volunteer', methods=['GET', 'POST'])
def become_volunteer():
    if 'username' not in session or session.get('role') != 'Customer':
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        full_name = request.form['full_name']
        vol_type = request.form['volunteer_type']
        specialty = request.form['specialty']
        cert_level = request.form['cert_level']
        med_specialty = request.form['med_specialty']
        license_num = request.form['license']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                INSERT INTO Volunteers (Username, FullName, AvailabilityStatus, VolunteerType, specialty, certificationLevel, medicalSpecialty, license)
                VALUES (%s, %s, 'Pending', %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (session['username'], full_name, vol_type, specialty, cert_level, med_specialty, license_num))
            conn.commit()
            
            return render_template('become_volunteer.html', success=True)
            
        except Exception as err:
            conn.rollback()
            return f"Error updating volunteer role: {err}"
        finally:
            cursor.close()
            conn.close()
            
    return render_template('become_volunteer.html')


@app.route('/volunteer_monitoring')
def volunteer_monitoring():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT v.VolunteerID, v.Username, v.FullName, v.specialty, v.AvailabilityStatus,
               IFNULL(history_counts.hrs, 0) AS total_hours
        FROM Volunteers v
        LEFT JOIN (
            SELECT VolunteerID, SUM(hours_earned) as hrs 
            FROM deployment_history GROUP BY VolunteerID
        ) history_counts ON v.VolunteerID = history_counts.VolunteerID
        ORDER BY field(v.AvailabilityStatus, 'Pending') DESC, total_hours DESC
    """
    cursor.execute(sql)
    volunteers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('volunteer_monitoring.html', volunteers=volunteers)



@app.route('/approve_volunteer/<int:volunteer_id>', methods=['POST'])
def approve_volunteer(volunteer_id):
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE Volunteers SET AvailabilityStatus = 'Available' WHERE VolunteerID = %s", (volunteer_id,))
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f"Error approving volunteer: {err}")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('volunteer_monitoring'))


@app.route('/remove_volunteer/<int:volunteer_id>', methods=['POST'])
def remove_volunteer(volunteer_id):
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM volunteers_deployedto_dzones WHERE VolunteerID = %s", (volunteer_id,))
        cursor.execute("DELETE FROM Volunteers WHERE VolunteerID = %s", (volunteer_id,))
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f"Error removing volunteer: {err}")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('volunteer_monitoring'))


@app.route('/deploy_volunteer', methods=['GET', 'POST'])
def deploy_volunteer():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    selected_volunteer_id = request.args.get('volunteer_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT VolunteerID, FullName, specialty FROM Volunteers WHERE AvailabilityStatus = 'Available'")
    available_vols = cursor.fetchall()
    
    cursor.execute("SELECT ZoneId, name, location, severity FROM disasterzones")
    zones = cursor.fetchall()
    
    user_specialty = ""
    if selected_volunteer_id:
        cursor.execute("SELECT specialty FROM Volunteers WHERE VolunteerID = %s", (selected_volunteer_id,))
        result = cursor.fetchone()
        if result:
            user_specialty = result['specialty']
            
    cursor.close()
    conn.close()
    
    return render_template('deploy_volunteer.html', volunteers=available_vols, zones=zones, selected_id=selected_volunteer_id, primary_specialty=user_specialty)


@app.route('/process_deployment', methods=['POST'])
def process_deployment():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    volunteer_id = request.form['volunteer_id']
    zone_id = request.form['zone_id']
    role = request.form['role']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql_deploy = """
            INSERT INTO volunteers_deployedto_dzones (`VolunteerID`, `ZoneId`, `current_role`, `hours_contributed`, `deployed_at`)
            VALUES (%s, %s, %s, 0, NOW())
        """
        cursor.execute(sql_deploy, (volunteer_id, zone_id, role))
        cursor.execute("UPDATE Volunteers SET AvailabilityStatus = 'Deployed' WHERE VolunteerID = %s", (volunteer_id,))
        conn.commit()
        return redirect(url_for('volunteer_monitoring'))
    except Exception as err:
        conn.rollback()
        return f"Database Error: Could not complete deployment. Details: {err}"
    finally:
        cursor.close()
        conn.close()


@app.route('/active_deployments')
def active_deployments():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT d.VolunteerID, d.ZoneId, d.current_role, d.hours_contributed, d.deployed_at,
               v.FullName, dz.name AS zone_name, dz.location
        FROM volunteers_deployedto_dzones d
        JOIN Volunteers v ON d.VolunteerID = v.VolunteerID
        JOIN disasterzones dz ON d.ZoneId = dz.ZoneId
    """
    cursor.execute(sql)
    deployments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('active_deployments.html', deployments=deployments)


@app.route('/release_volunteer/<int:volunteer_id>/<int:zone_id>', methods=['POST'])
def release_volunteer(volunteer_id, zone_id):
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT deployed_at FROM volunteers_deployedto_dzones WHERE VolunteerID = %s AND ZoneId = %s", (volunteer_id, zone_id))
        deployment = cursor.fetchone()
        
        if deployment:
            cursor.execute("SELECT TIMESTAMPDIFF(HOUR, %s, NOW()) AS hours_spent", (deployment['deployed_at'],))
            result = cursor.fetchone()
            calculated_hours = result['hours_spent'] if result and result['hours_spent'] is not None else 0
            if calculated_hours < 1:
                calculated_hours = 1
                
            cursor.execute("""
                INSERT INTO deployment_history (VolunteerID, hours_earned)
                VALUES (%s, %s)
            """, (volunteer_id, calculated_hours))
            
            cursor.execute("DELETE FROM volunteers_deployedto_dzones WHERE VolunteerID = %s AND ZoneId = %s", (volunteer_id, zone_id))
            cursor.execute("UPDATE Volunteers SET AvailabilityStatus = 'Available' WHERE VolunteerID = %s", (volunteer_id,))
            
        conn.commit()
        return redirect(url_for('volunteer_monitoring'))
    except Exception as err:
        conn.rollback()
        return f"Database Error: Could not release asset. Details: {err}"
    finally:
        cursor.close()
        conn.close()



@app.route('/volunteer/toggle_availability', methods=['POST'])
def toggle_availability():
    if 'username' not in session or session.get('role') != 'Volunteer':
        return redirect(url_for('login'))
        
    current_status = request.form.get('current_status')
    username = session['username']
    
    new_status = 'Unavailable' if current_status == 'Available' else 'Available'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE Volunteers SET AvailabilityStatus = %s WHERE Username = %s AND AvailabilityStatus != 'Deployed'", (new_status, username))
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f"Error toggling availability: {err}")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('home'))

@app.route('/view_disaster_zones')
def view_disaster_zones():
    if 'username' not in session or session.get('role') not in ['Customer', 'Volunteer']:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT ZoneId, status, name, location, severity, warehouseID, dispatchTimeStamp 
        FROM disasterzones 
        ORDER BY severity DESC
    """
    cursor.execute(sql)
    zones = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('view_disaster_zones.html', zones=zones)

#Aryan-----------------------------------------------------------------------

#1. Disaster zone & shipment tracking
@app.route('/manage_zones', methods=['GET'])
def manage_zones():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    #based on severity highest one is shown
    cursor.execute("SELECT * FROM disasterzones ORDER BY severity DESC")
    zones = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('manage_zones.html', zones=zones)


@app.route('/add_zone', methods=['POST'])
def add_zone():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    name = request.form['name']
    location = request.form['location']
    severity = request.form['severity']
    warehouse_id = request.form['warehouseID']
    status = 'Pending' 
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(ZoneId) FROM disasterzones")
        max_id = cursor.fetchone()[0]
        new_id = 1 if max_id is None else max_id + 1
        
        sql = """
            INSERT INTO disasterzones (ZoneId, name, location, severity, warehouseID, status) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (new_id, name, location, severity, warehouse_id, status))
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f"Error adding zone: {err}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('manage_zones'))
    

@app.route('/update_zone/<int:zone_id>', methods=['POST'])
def update_zone(zone_id):
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    new_status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE disasterzones SET status = %s WHERE ZoneId = %s", (new_status, zone_id))
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f"Error updating zone status: {err}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('manage_zones'))


#2. dispatch shipment (resource allocation)
@app.route('/dispatch_shipment/<int:zone_id>', methods=['GET', 'POST'])
def dispatch_shipment(zone_id):
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        item_id = request.form['item_id']
        dispatch_qty = int(request.form['quantity'])

        try:
            # check if enough stock exists first
            cursor.execute("SELECT Quantity FROM inventoryitems WHERE ItemId = %s", (item_id,))
            item_data = cursor.fetchone()
            
            if not item_data or item_data['Quantity'] < dispatch_qty:
                return "Error: Insufficient stock for this dispatch."

            # get the assigned warehouse ID for this zone
            cursor.execute("SELECT warehouseID FROM disasterzones WHERE ZoneId = %s", (zone_id,))
            zone_data = cursor.fetchone()
            warehouse_id = zone_data['warehouseID'] if zone_data else 0

            # deduct from inventory
            update_sql = "UPDATE inventoryitems SET Quantity = Quantity - %s WHERE ItemId = %s"
            cursor.execute(update_sql, (dispatch_qty, item_id))
            
            # log the shipment dispatch into our new table
            log_sql = """
                INSERT INTO shipmentlog (ItemId, ZoneId, WID, QuantityShipped, DispatchedBy, DispatchedAt) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(log_sql, (item_id, zone_id, warehouse_id, dispatch_qty, session['username']))
            
            # automatically update zone status to dispatched
            cursor.execute(
                "UPDATE disasterzones SET status = 'Dispatched', dispatchTimeStamp = NOW() WHERE ZoneId = %s", 
                (zone_id,)
            )
            
            conn.commit()
            return redirect(url_for('manage_zones'))

        except Exception as err:
            conn.rollback()
            return f"Transaction Failed: {err}"
        finally:
            cursor.close()
            conn.close()
            
    # GET method - fetch inventory for the dropdown
    try:
        fetch_inventory_sql = """
            SELECT i.ItemId, i.ItemName, i.Quantity, i.Category 
            FROM inventoryitems i
            JOIN warehouse_contains_inventoryitems wci ON i.ItemId = wci.ItemId
            JOIN warehouses w ON w.WID = wci.WID
            JOIN disasterzones dz ON dz.warehouseID = w.WID
            WHERE dz.ZoneId = %s AND i.Quantity > 0
        """
        cursor.execute(fetch_inventory_sql, (zone_id,))
        available_items = cursor.fetchall()
        
        cursor.execute("SELECT * FROM disasterzones WHERE ZoneId = %s", (zone_id,))
        zone = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    
    return render_template('dispatch_shipment.html', items=available_items, zone=zone)

#3. live disaster zone analytics & resource report
@app.route('/zone_analytics')
def zone_analytics():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Complex Aggregation Query calculating live stats per disaster zone
        analytics_sql = """
            SELECT 
                dz.ZoneId, 
                dz.name, 
                dz.location,
                dz.severity, 
                dz.status,
                COUNT(DISTINCT vd.VolunteerID) AS active_personnel,
                COALESCE(SUM(TIMESTAMPDIFF(HOUR, vd.deployed_at, NOW())), 0) AS live_hours_contributed,
                COALESCE(sl.total_shipped, 0) AS total_items_dispatched
            FROM disasterzones dz
            LEFT JOIN volunteers_deployedto_dzones vd ON dz.ZoneId = vd.ZoneId
            LEFT JOIN (
                SELECT ZoneId, SUM(QuantityShipped) AS total_shipped
                FROM shipmentlog GROUP BY ZoneId
            ) sl ON dz.ZoneId = sl.ZoneId
            GROUP BY dz.ZoneId, dz.name, dz.location, dz.severity, dz.status, sl.total_shipped
            ORDER BY dz.severity DESC, active_personnel DESC
        """
        cursor.execute(analytics_sql)
        analytics = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
    
    return render_template('zone_analytics.html', analytics=analytics)

# ----------------------------------------------------------------------------------

#Oishee's Features
##INVENTORY
#1. add inventory
@app.route('/add_inventory_item', methods=['GET', 'POST'])
def add_inventory_item():
   
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        category = request.form['category']
        expiration_date = request.form['expiration_date']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            sql = """
                INSERT INTO InventoryItems
                (ItemName, Quantity, Category, ExpirationDate)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                sql,
                (item_name, quantity, category, expiration_date)
            )
            conn.commit()

        except Exception as err:
            conn.rollback()
            return f"Error adding inventory item: {err}"

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('home'))

    return render_template('add_inventory_item.html')

#2. edit inventory

@app.route('/edit_inventory_item/<int:item_id>',methods= ['GET','POST'])
def edit_inventory_item(item_id):
    if 'username' not in session or session.get('role')!= 'Admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        quantity = request.form['quantity']
        expiration_date = request.form['expiration_date']

        sql = """
         UPDATE InventoryItems
         SET ItemName = %s, Category = %s, Quantity = %s,
         ExpirationDate = %s
         WHERE ItemId = %s
         """
        cursor.execute(sql,(item_name,category,quantity,expiration_date,item_id))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('expiry_auditor')) #eta keno redirect hocche?
    cursor.execute(
        "SELECT * FROM InventoryItems where ItemId =%s",
        (item_id,)
    )
    item = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_inventory_item.html',item=item)
    
#3.delete inventory item
@app.route('/delete_inventory_item/<int:item_id>',methods=['POST'])
def delete_inventory_item(item_id):
    if 'username' not in session or session.get('role')!='Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM InventoryItems where ItemId= %s",
        (item_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('expiry_auditor'))
        
#4. expiry_auditor -- ++restock alert

@app.route('/expiry_auditor')
def expiry_auditor():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT ItemId, ItemName, ExpirationDate, Quantity, Category,
               DATEDIFF(ExpirationDate, CURDATE()) AS days_remaining,
               CASE
                   WHEN Quantity<=10 THEN '!!RESTOCK NEEDED!!'
                   ELSE 'Stock Available :)'
                END AS RestockStatus
        FROM InventoryItems
        ORDER BY ItemId ASC,ExpirationDate ASC
    """
    cursor.execute(sql)
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('expiry_auditor.html', items=items)

#5.update stock
@app.route('/update_stock/<int:item_id>',methods=['POST'])
def update_stock(item_id):
    if 'username' not in session or session.get('role')!= 'Admin':
        return redirect(url_for('login'))

    amount = int(request.form['amount'])
    action = request.form['action']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True,buffered=True)

    #current quantity pacchi ekhane
    cursor.execute(
        "SELECT Quantity FROM InventoryItems WHERE ItemId = %s",
        (item_id,)
    )
    item = cursor.fetchone()

    if item:
        current_quantity = item['Quantity']

        if action== 'add':
            new_quantity = current_quantity + amount
        elif action== 'remove':
            new_quantity = current_quantity - amount

            if new_quantity<0 :
                new_quantity = 0
        else:
            new_quantity = current_quantity
        cursor.execute(
            "UPDATE InventoryItems SET Quantity =%s WHERE ItemId = %s",
            (new_quantity,item_id)
        )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('expiry_auditor'))

#WAREHOUSE
#5.manage warehouses ---- for viewing
@app.route('/manage_warehouses')
def manage_warehouses():
    if 'username' not in session or session.get('role')!='Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor= conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT *FROM Warehouses order by WID ASC"
    )

    warehouses = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('manage_warehouses.html',warehouses=warehouses)

#6.Register a warehouse
@app.route('/add_warehouse', methods=['GET','POST'])
def add_warehouse():
    if 'username' not in session or session.get('role')!='Admin':
        return redirect(url_for('login'))
    
    if request.method== 'POST':
        manager = request.form['manager']
        capacity = request.form['capacity']
        contact = request.form['contact']

        conn = get_db_connection()
        cursor= conn.cursor()

        cursor.execute(
            """INSERT INTO Warehouses (Manager,Capacity,Contact)
                values (%s,%s,%s)
            """,(manager,capacity,contact)
        )

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('manage_warehouses'))
    
    return render_template('add_warehouse.html')

#7.Edit Warehouse
@app.route('/edit_warehouse/<int:wid>',methods= ['GET','POST'])
def edit_warehouse(wid):
    if 'username' not in session or session.get('role')!='Admin':
      return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        manager = request.form['manager']
        capacity = request.form['capacity']
        contact = request.form['contact']

        cursor.execute(
            """
            UPDATE Warehouses
            set Manager=%s, Capacity= %s, Contact= %s
            where WID = %s
            """,(manager,capacity,contact,wid)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('manage_warehouses'))

    cursor.execute(
        "SELECT *FROM Warehouses where WID= %s",
        (wid,)
    )
    warehouse= cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('edit_warehouse.html',warehouse=warehouse)


#8.Delete a warehouse
@app.route('/delete_warehouse/<int:wid>',methods= ['POST'])
def delete_warehouse(wid):
    if 'username' not in session or session.get('role')!='Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "DELETE from Warehouses where WID=%s",
        (wid,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('manage_warehouses'))
    
    
#9.Assign Inventory item to a warehouse 
@app.route('/assign_item/<int:wid>',methods=['GET','POST'])
def assign_item(wid):
   if 'username' not in session or session.get('role')!='Admin':
        return redirect(url_for('login')) 

   
   conn = get_db_connection()
   cursor = conn.cursor(dictionary=True)

   if request.method =='POST':
       item_id = request.form['item_id']
       shelf_location = request.form['shelf_location']

       cursor.execute(
            """
            INSERT INTO warehouse_contains_inventoryitems (ItemId,WID, shelf_location)
            values (%s,%s,%s)
            """,
            (item_id,wid,shelf_location)
        )
       conn.commit()
       cursor.close()
       conn.close()
       return redirect(url_for('manage_warehouses'))

   ###ekhane we get all inv items for the dropdown
   cursor.execute(
       """
       SELECT ItemId, ItemName
       from InventoryItems 
       ORDER by ItemName ASC
       """
   )
   items = cursor.fetchall()

   cursor.close()
   conn.close()

   return render_template('assign_item.html',wid=wid, items=items)

#10.viewing warehouse inventories
@app.route('/warehouse/<int:wid>/inventory')
def warehouse_inventory(wid):
    if 'username' not in session or session.get('role')!='Admin':
        return redirect(url_for('login')) 

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT *FROM warehouses where WID=%s",
        (wid,)
    )
    warehouse = cursor.fetchone()

    #warehouse er bhitorer items pacchi
    cursor.execute(
        """
        SELECT i.ItemId, i.ItemName, i.Category, i.Quantity,
        i.ExpirationDate, wci.shelf_location
        FROM warehouse_contains_inventoryitems wci
        JOIN inventoryitems i ON wci.ItemId = i.ItemId
        WHERE wci.WID = %s
    """,(wid,)
    )
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('warehouse_inventory.html',warehouse=warehouse,items=items)

    



   
    




#------------------------------------------------




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            sql = "INSERT INTO user (username, password, regDate, isActive) VALUES (%s, %s, NOW(), 1)"
            cursor.execute(sql, (username, password))
            
            cursor.execute("INSERT INTO customer (Username) VALUES (%s)", (username,))
                
            conn.commit()
            return "Registration successful! <a href='/login'>Click here to login</a>"
        except Exception as err:
            conn.rollback()
            return f"Error: Could not register user. Details: {err}"
        finally:
            cursor.close()
            conn.close()
            
    return render_template('signup.html')



@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    username = session['username']
    v_status = None
    my_deployment = None
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM admin WHERE Username = %s", (username,))
    is_admin = cursor.fetchone()
    
    if is_admin:
        session['role'] = 'Admin'
    else:
        cursor.execute("SELECT VolunteerID, AvailabilityStatus FROM volunteers WHERE Username = %s", (username,))
        volunteer_record = cursor.fetchone()
        if volunteer_record:
            session['role'] = 'Volunteer'
            v_status = volunteer_record['AvailabilityStatus']
            
            if v_status == 'Deployed':
                sql_dep = """
                    SELECT d.current_role, d.deployed_at, dz.name AS zone_name, dz.location, dz.severity
                    FROM volunteers_deployedto_dzones d
                    JOIN disasterzones dz ON d.ZoneId = dz.ZoneId
                    WHERE d.VolunteerID = %s
                """
                cursor.execute(sql_dep, (volunteer_record['VolunteerID'],))
                my_deployment = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM customer WHERE Username = %s", (username,))
            if cursor.fetchone():
                session['role'] = 'Customer'
            else:
                session['role'] = 'User'
                
    cursor.close()
    conn.close()
    
    return render_template('home.html', name=username, role=session.get('role'), volunteer_status=v_status, assignment=my_deployment)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

