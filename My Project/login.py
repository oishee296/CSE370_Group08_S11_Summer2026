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

#Aryan-----------------------------------------------------------------------
@app.route('/manage_zones', methods=['GET'])
def manage_zones():
    if 'username' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
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
    
    cursor.execute("SELECT MAX(ZoneId) FROM disasterzones")
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1
    
    sql = """INSERT INTO disasterzones (ZoneId, name, location, severity, warehouseID, status) 
             VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (new_id, name, location, severity, warehouse_id, status))
    conn.commit()
    
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
    cursor.execute("UPDATE disasterzones SET status = %s WHERE ZoneId = %s", (new_status, zone_id))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('manage_zones'))

# ----------------------------------------------------------------------------------

#Oishee's Features
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
        
#4 expiry_auditor

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
        ORDER BY ExpirationDate ASC
    """
    cursor.execute(sql)
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('expiry_auditor.html', items=items)

#------------------------------------------------



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_choice = request.form['role']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            sql = "INSERT INTO User (username, password, regDate, isActive) VALUES (%s, %s, NOW(), 1)"
            cursor.execute(sql, (username, password))
            
            if role_choice == 'Admin':
                cursor.execute("INSERT INTO Admin (Username, dept, accessLevel) VALUES (%s, 'General Relief', 'Standard')", (username,))
            else:
                cursor.execute("INSERT INTO Customer (Username) VALUES (%s)", (username,))
                
            conn.commit()
            return "Registration successful! <a href='/login'>Click here to login</a>"
        except Exception as err:
            conn.rollback()
            return f"Error: Could not register user. Username might already exist. Details: {err}"
        finally:
            cursor.close()
            conn.close()
            
    return render_template('signup.html')


@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    username = session['username']
    role = session.get('role')
    v_status = None
    my_deployment = None
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Admin WHERE Username = %s", (username,))
    is_admin = cursor.fetchone()
    
    if is_admin:
        session['role'] = 'Admin'
    else:
        cursor.execute("SELECT VolunteerID, AvailabilityStatus FROM Volunteers WHERE Username = %s", (username,))
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
            cursor.execute("SELECT * FROM Customer WHERE Username = %s", (username,))
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

