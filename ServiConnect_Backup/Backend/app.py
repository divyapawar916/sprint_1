# ============================================================
# SERVICONNECT - FLASK APPLICATION
# ============================================================

# Import Flask and the functions we need
from flask import Flask, render_template, request, redirect, url_for, session

# Import our MySQL connection function
from database import get_db_connection

# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

# Create the Flask application object
app = Flask(
    __name__,
    template_folder="../Frontend/templates",
    static_folder="../Frontend/static"
)
# Secret key used by Flask to securely manage user sessions
app.secret_key = "serviconnect-secret-key"

# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    # Display the homepage
    return render_template("index.html")


# ============================================================
# REGISTRATION PAGE
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # --------------------------------------------------------
    # SHOW REGISTRATION PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        # Open the registration page
        return render_template("register.html")


    # --------------------------------------------------------
    # GET DATA FROM REGISTRATION FORM
    # --------------------------------------------------------

    # Get the full name entered by the user
    name = request.form.get("full_name")

    # Get the email entered by the user
    email = request.form.get("email")

    # Get the phone number entered by the user
    phone = request.form.get("phone")
   
    if not phone.isdigit() or len(phone) != 10:
        return render_template(
            "register.html",
            error="Contact number must contain exactly 10 digits."
        )
    
    # Get the selected account type
    role = request.form.get("account_type")

    # Get the password entered by the user
    password = request.form.get("password")


    # --------------------------------------------------------
    # CHECK REQUIRED FIELDS
    # --------------------------------------------------------

    # Make sure all fields contain data
    if not name or not email or not phone or not role or not password:

        # Show an error message
        return "Please fill in all required fields."


    # --------------------------------------------------------
    # CONNECT TO MYSQL
    # --------------------------------------------------------

    # Create a connection to the database
    connection = get_db_connection()

    # Create a cursor to execute SQL commands
    cursor = connection.cursor()


    # --------------------------------------------------------
    # INSERT USER INTO DATABASE
    # --------------------------------------------------------

    # SQL query for inserting a new user
    query = """
        INSERT INTO users
        (name, email, password, role, phone)
        VALUES (%s, %s, %s, %s, %s)
    """


    # Execute the SQL query
    cursor.execute(
        query,
        (name, email, password, role, phone)
    )


    # Save the new user
    connection.commit()


    # --------------------------------------------------------
    # CLOSE DATABASE CONNECTION
    # --------------------------------------------------------

    # Close the cursor
    cursor.close()

    # Close the database connection
    connection.close()


    # --------------------------------------------------------
    # REGISTRATION SUCCESS
    # --------------------------------------------------------

    # Send the user to the login page
    return redirect(url_for("login"))


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # SHOW LOGIN PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        # Display login.html
        return render_template("login.html")


    # --------------------------------------------------------
    # GET LOGIN DATA
    # --------------------------------------------------------

    # Get email from the login form
    email = request.form.get("email")

    # Get password from the login form
    password = request.form.get("password")


    # --------------------------------------------------------
    # CHECK EMPTY FIELDS
    # --------------------------------------------------------

    if not email or not password:

        # Show an error message
        return "Please enter email and password."


    # --------------------------------------------------------
    # CONNECT TO MYSQL
    # --------------------------------------------------------

    # Connect to our database
    connection = get_db_connection()

    # Create a cursor
    # dictionary=True allows us to access user information by column name
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    # SQL query to find a matching email and password
    query = """
        SELECT *
        FROM users
        WHERE email = %s
        AND password = %s
    """


    # Execute the query
    cursor.execute(
        query,
        (email, password)
    )


    # Get the matching user
    user = cursor.fetchone()


    # --------------------------------------------------------
    # CLOSE DATABASE CONNECTION
    # --------------------------------------------------------

    # Close cursor
    cursor.close()

    # Close connection
    connection.close()


    # --------------------------------------------------------
    # CHECK LOGIN RESULT
    # --------------------------------------------------------

    # Check if a matching user was found
    if user:

        # ----------------------------------------------------
        # SAVE USER INFORMATION IN SESSION
        # ----------------------------------------------------

        # Save the user's ID in the session
        session["user_id"] = user["user_id"]

        # Save the user's name in the session
        session["user_name"] = user["name"]

        # Save the user's email in the session
        session["user_email"] = user["email"]

        # Save the user's role in the session
        session["user_role"] = user["role"]


        # ----------------------------------------------------
        # REDIRECT TO DASHBOARD
        # ----------------------------------------------------

        # Send the logged-in user to the dashboard
        return redirect(url_for("dashboard"))

    else:

        # No matching user was found
        return "Invalid email or password."

# ============================================================
# MY PROFILE
# ============================================================

@app.route("/profile")
def profile():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET LOGGED-IN USER
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            user_id,
            name,
            email,
            phone,
            role,
            created_at
        FROM users
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # CHECK USER
    # --------------------------------------------------------

    if user is None:
        return "User profile not found."


    # --------------------------------------------------------
    # SHOW PROFILE PAGE
    # --------------------------------------------------------

    return render_template(
        "profile.html",
        user=user
    )

# ============================================================
# TERMS AND CONDITIONS
# ============================================================

@app.route("/terms")
def terms():
    return render_template("terms.html")

# ============================================================
# EDIT PROFILE
# ============================================================

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET CURRENT USER
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            user_id,
            name,
            email,
            phone,
            role
        FROM users
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()


    if user is None:

        cursor.close()
        connection.close()

        return "User profile not found."


    # --------------------------------------------------------
    # UPDATE PROFILE
    # --------------------------------------------------------

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]


        cursor.execute(
            """
            UPDATE users
            SET
                name = %s,
                email = %s,
                phone = %s
            WHERE user_id = %s
            """,
            (
                name,
                email,
                phone,
                session["user_id"]
            )
        )


        connection.commit()


        cursor.close()
        connection.close()


        return redirect(url_for("profile"))


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW EDIT PROFILE PAGE
    # --------------------------------------------------------

    return render_template(
        "edit_profile.html",
        user=user
    )

# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.route("/dashboard")
def dashboard():

    # --------------------------------------------------------
    # CHECK IF USER IS LOGGED IN
    # --------------------------------------------------------

    # Check whether the user's ID exists in the session
    if "user_id" not in session:

        # If the user is not logged in,
        # send them back to the login page
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # GET USER INFORMATION
    # --------------------------------------------------------

    # Get the user's name from the session
    user_name = session["user_name"]

    # Get the user's role from the session
    user_role = session["user_role"]


    # --------------------------------------------------------
    # OPEN DASHBOARD PAGE
    # --------------------------------------------------------

    # Send the user's information to dashboard.html
    return render_template(
        "dashboard.html",
        user_name=user_name,
        user_role=user_role
    )
# ============================================================
# FIND SERVICES PAGE
# ============================================================

@app.route("/services")
def services():

    # Check whether the user is logged in
    if "user_id" not in session:

        # If the user is not logged in,
        # send them to the login page
        return redirect(url_for("login"))


    # Check whether the logged-in user is a customer
    if session["user_role"] != "customer":

        # Providers cannot access the customer services page
        return redirect(url_for("dashboard"))


    # Open the services page
    return render_template("services.html")

# ============================================================
# ADD SERVICE PAGE
# ============================================================

@app.route("/add-service", methods=["GET", "POST"])
def add_service():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure a user is logged in
    if "user_id" not in session:

        # Send the user to the login page
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only service providers can add services
    if session.get("user_role") != "provider":

        # Send customers back to their dashboard
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # SHOW FORM
    # --------------------------------------------------------

    # Display the form when the page is opened
    if request.method == "GET":

        return render_template("add_service.html")


    # --------------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------------

    # Get service name from the form
    service_name = request.form.get("service_name")

    # Get category from the form
    category = request.form.get("category")

    # Get price from the form
    price = request.form.get("price")

    # Get description from the form
    description = request.form.get("description")

    # Get availability from the form
    availability = request.form.get("availability")


    # --------------------------------------------------------
    # GET LOGGED-IN USER ID
    # --------------------------------------------------------

    # Get the ID of the currently logged-in user
    user_id = session["user_id"]


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Create a connection to MySQL
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # FIND PROVIDER ID
    # --------------------------------------------------------

    # Find the provider_id belonging to this user
    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (user_id,)
    )


    # Get the provider record
    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER PROFILE
    # --------------------------------------------------------

    # Make sure the provider profile exists
    if provider is None:

        # Close cursor
        cursor.close()

        # Close database connection
        connection.close()

        # Show an error message
        return "Provider profile not found."


    # Get the actual provider ID
    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # INSERT SERVICE INTO DATABASE
    # --------------------------------------------------------

    # SQL query for inserting the service
    query = """
        INSERT INTO services
        (
            provider_id,
            service_name,
            category,
            price,
            description,
            availability
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """


    # Execute the INSERT query
    cursor.execute(
        query,
        (
            provider_id,
            service_name,
            category,
            price,
            description,
            availability
        )
    )


    # --------------------------------------------------------
    # SAVE CHANGES
    # --------------------------------------------------------

    # Save the new service in MySQL
    connection.commit()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    # Close cursor
    cursor.close()

    # Close database connection
    connection.close()


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    # Return to the dashboard after successful insertion
    return redirect(url_for("dashboard"))
# ============================================================
# MY SERVICES PAGE
# ============================================================

@app.route("/my-services")
def my_services():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:

        # Send the user to the login page
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only providers can access My Services
    if session.get("user_role") != "provider":

        # Send customers back to their dashboard
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # GET LOGGED-IN USER ID
    # --------------------------------------------------------

    # Get the current user's ID
    user_id = session["user_id"]


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Connect to MySQL
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # FIND PROVIDER ID
    # --------------------------------------------------------

    # Find the provider_id connected to this user
    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (user_id,)
    )


    # Get provider information
    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER PROFILE
    # --------------------------------------------------------

    # If the provider profile doesn't exist
    if provider is None:

        # Close database resources
        cursor.close()
        connection.close()

        # Show an error message
        return "Provider profile not found."


    # Get the actual provider ID
    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # GET SERVICES
    # --------------------------------------------------------

    # Get all services belonging to this provider
    cursor.execute(
        """
        SELECT
            service_id,
            service_name,
            category,
            price,
            description,
            availability
        FROM services
        WHERE provider_id = %s
        ORDER BY service_id DESC
        """,
        (provider_id,)
    )


    # Store all services
    services = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    # Close cursor
    cursor.close()

    # Close database connection
    connection.close()


    # --------------------------------------------------------
    # SHOW MY SERVICES PAGE
    # --------------------------------------------------------

    # Send services to the HTML page
    return render_template(
        "my_services.html",
        services=services
    )

# ============================================================
# BROWSE SERVICES PAGE - CUSTOMER
# ============================================================

# ============================================================
# BROWSE SERVICES PAGE
# ============================================================

@app.route("/browse-services")
def browse_services():

    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET AVAILABLE SERVICES
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            s.service_id,
            s.service_name,
            s.category,
            s.price,
            s.description,
            s.availability,
            sp.business_name,
            sp.service_area
        FROM services s
        JOIN service_providers sp
            ON s.provider_id = sp.provider_id
        WHERE s.availability = 'Available'
        ORDER BY s.service_id DESC
        """
    )

    services = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW BROWSE SERVICES PAGE
    # --------------------------------------------------------

    return render_template(
        "browse_services.html",
        services=services
    )

# ============================================================
# BROWSE PROVIDERS PAGE
# ============================================================

@app.route("/providers")
def browse_providers():

    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET APPROVED PROVIDERS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            sp.provider_id,
            sp.business_name,
            sp.service_area,
            sp.experience,
            sp.description
        FROM service_providers sp
        WHERE sp.status = 'approved'
        ORDER BY sp.provider_id DESC
        """
    )

    providers = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW PROVIDERS PAGE
    # --------------------------------------------------------

    return render_template(
        "providers.html",
        providers=providers
    )

# ============================================================
# ABOUT PAGE
# ============================================================

@app.route("/about")
def about():

    return render_template("about.html")

# ============================================================
# BOOK SERVICE
# ============================================================

@app.route("/book-service/<int:service_id>", methods=["GET", "POST"])
def book_service(service_id):

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:

        # Send the user to the login page
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only customers can book a service
    if session.get("user_role") != "customer":

        # Send providers back to their dashboard
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Use the existing database connection function
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET SERVICE DETAILS
    # --------------------------------------------------------

    # Find the selected service and its provider information
    cursor.execute(
        """
        SELECT
            s.service_id,
            s.service_name,
            sp.business_name
        FROM services s
        JOIN service_providers sp
            ON s.provider_id = sp.provider_id
        WHERE s.service_id = %s
        """,
        (service_id,)
    )

    # Get the service information
    service = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK SERVICE
    # --------------------------------------------------------

    # If the service does not exist
    if service is None:

        # Close database resources
        cursor.close()
        connection.close()

        # Show an error message
        return "Service not found."


    # --------------------------------------------------------
    # HANDLE BOOKING FORM
    # --------------------------------------------------------

    if request.method == "POST":

        # Get booking date from the form
        booking_date = request.form["booking_date"]

        # Get booking time from the form
        booking_time = request.form["booking_time"]

        # Get service address from the form
        address = request.form["address"]

        # Get additional notes from the form
        notes = request.form.get("notes", "")


        # ----------------------------------------------------
        # INSERT BOOKING
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO bookings
            (
                customer_id,
                service_id,
                booking_date,
                booking_time,
                address,
                notes,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'pending'
            )
            """,
            (
                session["user_id"],
                service_id,
                booking_date,
                booking_time,
                address,
                notes
            )
        )


        # Save the booking in the database
        connection.commit()


        # Close database resources
        cursor.close()
        connection.close()


        # After booking, return to the customer's dashboard
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CLOSE DATABASE FOR GET REQUEST
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW BOOKING PAGE
    # --------------------------------------------------------

    return render_template(
        "book_service.html",
        service=service
    )

# ============================================================
# FORGOT PASSWORD
# ============================================================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is None:
            return render_template(
                "forgot_password.html",
                error="Email address not found."
            )

        # For now, continue to the reset-password page
        return redirect(
            url_for(
                "reset_password",
                user_id=user["user_id"]
            )
        )

    return render_template("forgot_password.html")
# ============================================================
# RESET PASSWORD
# ============================================================

@app.route("/reset-password/<int:user_id>", methods=["GET", "POST"])
def reset_password(user_id):

    if request.method == "POST":

        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Check whether both passwords match
        if new_password != confirm_password:

            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )

        # Update password in database
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
            """,
            (new_password, user_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        # Return to login after successful reset
        return redirect(url_for("login"))

    return render_template(
        "reset_password.html"
    )

# ============================================================
# PROVIDER BOOKINGS PAGE
# ============================================================

@app.route("/provider-bookings")
def provider_bookings():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:

        # Send the user to the login page
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only providers can access this page
    if session.get("user_role") != "provider":

        # Send customers back to their dashboard
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # GET LOGGED-IN USER ID
    # --------------------------------------------------------

    # Get the current provider's user ID
    user_id = session["user_id"]


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Use the existing database connection function
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # FIND PROVIDER ID
    # --------------------------------------------------------

    # Find the provider profile belonging to the logged-in user
    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (user_id,)
    )

    # Get provider information
    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER PROFILE
    # --------------------------------------------------------

    # If provider profile does not exist
    if provider is None:

        # Close database resources
        cursor.close()
        connection.close()

        # Show an error message
        return "Provider profile not found."


    # Get the actual provider ID
    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # GET PROVIDER BOOKINGS
    # --------------------------------------------------------

    # Get bookings for services belonging to this provider
    cursor.execute(
        """
        SELECT
            b.booking_id,
            b.booking_date,
            b.booking_time,
            b.address,
            b.notes,
            b.status,

            s.service_name,

            u.name AS customer_name,
            u.phone AS customer_phone

        FROM bookings b

        JOIN services s
            ON b.service_id = s.service_id

        JOIN users u
            ON b.customer_id = u.user_id

        WHERE s.provider_id = %s

        ORDER BY b.booking_id DESC
        """,
        (provider_id,)
    )


    # Store all bookings
    bookings = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    # Close cursor
    cursor.close()

    # Close database connection
    connection.close()


    # --------------------------------------------------------
    # SHOW PROVIDER BOOKINGS PAGE
    # --------------------------------------------------------

    # Send bookings to the HTML page
    return render_template(
        "provider_bookings.html",
        bookings=bookings
    )
# ============================================================
# UPDATE BOOKING STATUS
# ============================================================

@app.route(
    "/update-booking-status/<int:booking_id>/<status>",
    methods=["POST"]
)
def update_booking_status(booking_id, status):

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only providers can update booking status
    if session.get("user_role") != "provider":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # ALLOWED STATUSES
    # --------------------------------------------------------

    # These are the only statuses a provider can set
    allowed_statuses = [
        "accepted",
        "rejected",
        "completed"
    ]

    # Prevent invalid status values
    if status not in allowed_statuses:
        return "Invalid booking status."


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Use the existing database connection
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # FIND PROVIDER
    # --------------------------------------------------------

    # Get the logged-in provider's provider_id
    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    # Get provider information
    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER PROFILE
    # --------------------------------------------------------

    if provider is None:

        cursor.close()
        connection.close()

        return "Provider profile not found."


    # Get the actual provider ID
    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # UPDATE ONLY PROVIDER'S BOOKING
    # --------------------------------------------------------

    cursor.execute(
        """
        UPDATE bookings b
        JOIN services s
            ON b.service_id = s.service_id

        SET b.status = %s

        WHERE b.booking_id = %s
        AND s.provider_id = %s
        """,
        (
            status,
            booking_id,
            provider_id
        )
    )


    # Save the status change
    connection.commit()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # RETURN TO BOOKINGS
    # --------------------------------------------------------

    return redirect(url_for("provider_bookings"))
# ============================================================
# CUSTOMER MY BOOKINGS PAGE
# ============================================================

@app.route("/my-bookings")
def my_bookings():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only customers can access My Bookings
    if session.get("user_role") != "customer":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Use the existing database connection function
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET CUSTOMER BOOKINGS
    # --------------------------------------------------------

    # Get all bookings made by the logged-in customer
    cursor.execute(
        """
        SELECT
            b.booking_id,
            b.booking_date,
            b.booking_time,
            b.address,
            b.notes,
            b.status,

            s.service_name,

            sp.business_name

        FROM bookings b

        JOIN services s
            ON b.service_id = s.service_id

        JOIN service_providers sp
            ON s.provider_id = sp.provider_id

        WHERE b.customer_id = %s

        ORDER BY b.booking_id DESC
        """,
        (session["user_id"],)
    )


    # Store all customer bookings
    bookings = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    # Close cursor
    cursor.close()

    # Close database connection
    connection.close()


    # --------------------------------------------------------
    # SHOW MY BOOKINGS PAGE
    # --------------------------------------------------------

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )
# ============================================================
# CANCEL BOOKING
# ============================================================

@app.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only customers can cancel their bookings
    if session.get("user_role") != "customer":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Use the existing database connection
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # CANCEL BOOKING
    # --------------------------------------------------------

    # Update only the logged-in customer's pending booking
    cursor.execute(
        """
        UPDATE bookings

        SET status = 'cancelled'

        WHERE booking_id = %s
        AND customer_id = %s
        AND status = 'pending'
        """,
        (
            booking_id,
            session["user_id"]
        )
    )


    # Save the change
    connection.commit()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # RETURN TO MY BOOKINGS
    # --------------------------------------------------------

    return redirect(url_for("my_bookings"))

# ============================================================
# CUSTOMER MY REVIEWS PAGE
# ============================================================

@app.route("/my-reviews")
def my_reviews():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only customers can access My Reviews
    if session.get("user_role") != "customer":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Use the existing database connection
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET CUSTOMER REVIEWS
    # --------------------------------------------------------

    # Get reviews submitted by the logged-in customer
    cursor.execute(
        """
        SELECT
            r.review_id,
            r.rating,
            r.comment,
            r.review_date,

            s.service_name,

            sp.business_name

        FROM reviews r

        JOIN bookings b
            ON r.booking_id = b.booking_id

        JOIN services s
            ON r.provider_id = s.provider_id
            AND b.service_id = s.service_id

        JOIN service_providers sp
            ON r.provider_id = sp.provider_id

        WHERE r.customer_id = %s

        ORDER BY r.review_id DESC
        """,
        (session["user_id"],)
    )


    # Store all reviews
    reviews = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()

    connection.close()


    # --------------------------------------------------------
    # SHOW MY REVIEWS PAGE
    # --------------------------------------------------------

    return render_template(
        "my_reviews.html",
        reviews=reviews
    )
# ============================================================
# WRITE REVIEW
# ============================================================

@app.route("/write-review/<int:booking_id>", methods=["GET", "POST"])
def write_review(booking_id):

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only customers can write reviews
    if session.get("user_role") != "customer":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    # Create dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET COMPLETED BOOKING
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            b.booking_id,
            b.customer_id,
            b.service_id,
            b.status,

            s.service_name,

            sp.provider_id,
            sp.business_name

        FROM bookings b

        JOIN services s
            ON b.service_id = s.service_id

        JOIN service_providers sp
            ON s.provider_id = sp.provider_id

        WHERE b.booking_id = %s
        AND b.customer_id = %s
        """,
        (
            booking_id,
            session["user_id"]
        )
    )


    # Get booking information
    booking = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK BOOKING
    # --------------------------------------------------------

    # Make sure the booking belongs to this customer
    if booking is None:

        cursor.close()
        connection.close()

        return "Booking not found."


    # --------------------------------------------------------
    # CHECK COMPLETED STATUS
    # --------------------------------------------------------

    # Reviews are allowed only after completion
    if booking["status"] != "completed":

        cursor.close()
        connection.close()

        return "You can review only completed bookings."


    # --------------------------------------------------------
    # CHECK EXISTING REVIEW
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT review_id
        FROM reviews
        WHERE booking_id = %s
        AND customer_id = %s
        """,
        (
            booking_id,
            session["user_id"]
        )
    )


    # Check whether a review already exists
    existing_review = cursor.fetchone()


    if existing_review is not None:

        cursor.close()
        connection.close()

        return "You have already reviewed this booking."


    # --------------------------------------------------------
    # SUBMIT REVIEW
    # --------------------------------------------------------

    if request.method == "POST":

        # Get rating from form
        rating = request.form.get("rating")

        # Get comment from form
        comment = request.form.get("comment")


        # ----------------------------------------------------
        # VALIDATE RATING
        # ----------------------------------------------------

        try:

            rating = int(rating)

        except (TypeError, ValueError):

            cursor.close()
            connection.close()

            return "Please select a valid rating."


        # Rating must be between 1 and 5
        if rating < 1 or rating > 5:

            cursor.close()
            connection.close()

            return "Rating must be between 1 and 5."


        # ----------------------------------------------------
        # INSERT REVIEW
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO reviews (
                booking_id,
                customer_id,
                provider_id,
                rating,
                comment,
                review_date
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
            """,
            (
                booking_id,
                session["user_id"],
                booking["provider_id"],
                rating,
                comment
            )
        )


        # Save review
        connection.commit()


        # ----------------------------------------------------
        # CLOSE DATABASE
        # ----------------------------------------------------

        cursor.close()
        connection.close()


        # ----------------------------------------------------
        # RETURN TO MY REVIEWS
        # --------------------------------------------------------

        return redirect(url_for("my_reviews"))


    # --------------------------------------------------------
    # CLOSE DATABASE FOR GET REQUEST
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW REVIEW FORM
    # --------------------------------------------------------

    return render_template(
        "write_review.html",
        booking=booking
    )
# ============================================================
# PROVIDER REVIEWS PAGE
# ============================================================

@app.route("/provider-reviews")
def provider_reviews():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only providers can access provider reviews
    if session.get("user_role") != "provider":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    # Create dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET PROVIDER ID
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER PROFILE
    # --------------------------------------------------------

    if provider is None:

        cursor.close()
        connection.close()

        return "Provider profile not found."


    # Get provider ID
    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # GET CUSTOMER REVIEWS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            r.review_id,
            r.rating,
            r.comment,
            r.review_date,

            s.service_name,

            u.name AS customer_name

        FROM reviews r

        JOIN bookings b
            ON r.booking_id = b.booking_id

        JOIN services s
            ON b.service_id = s.service_id

        JOIN users u
            ON r.customer_id = u.user_id

        WHERE r.provider_id = %s

        ORDER BY r.review_id DESC
        """,
        (provider_id,)
    )


    # Store all reviews
    reviews = cursor.fetchall()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()

    connection.close()


    # --------------------------------------------------------
    # SHOW PROVIDER REVIEWS PAGE
    # --------------------------------------------------------

    return render_template(
        "provider_reviews.html",
        reviews=reviews
    )

# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    # Clear all login information from the session
    session.clear()

    # Send the user back to the login page
    return redirect(url_for("login"))

# ============================================================
# EDIT SERVICE
# ============================================================

@app.route("/edit-service/<int:service_id>", methods=["GET", "POST"])
def edit_service(service_id):

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure a user is logged in
    if "user_id" not in session:

        # Send the user to the login page
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only service providers can edit services
    if session.get("user_role") != "provider":

        # Send other users back to their dashboard
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    # Connect to MySQL
    connection = get_db_connection()

    # Create a dictionary cursor
    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # FIND PROVIDER ID
    # --------------------------------------------------------

    # Get the logged-in user's ID
    user_id = session["user_id"]

    # Find the provider_id belonging to this user
    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (user_id,)
    )

    # Get provider information
    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER PROFILE
    # --------------------------------------------------------

    if provider is None:

        # Close database resources
        cursor.close()
        connection.close()

        return "Provider profile not found."


    # Get the actual provider ID
    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # GET SERVICE
    # --------------------------------------------------------

    # Get only the service that belongs to this provider
    cursor.execute(
        """
        SELECT
            service_id,
            service_name,
            category,
            price,
            description,
            availability
        FROM services
        WHERE service_id = %s
        AND provider_id = %s
        """,
        (service_id, provider_id)
    )

    # Store the service
    service = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK SERVICE
    # --------------------------------------------------------

    if service is None:

        # Close database resources
        cursor.close()
        connection.close()

        return "Service not found."


    # --------------------------------------------------------
    # UPDATE SERVICE
    # --------------------------------------------------------

    if request.method == "POST":

        # Get updated service name
        service_name = request.form.get("service_name")

        # Get updated category
        category = request.form.get("category")

        # Get updated price
        price = request.form.get("price")

        # Get updated description
        description = request.form.get("description")

        # Get updated availability
        availability = request.form.get("availability")


        # Update the service in MySQL
        cursor.execute(
            """
            UPDATE services
            SET
                service_name = %s,
                category = %s,
                price = %s,
                description = %s,
                availability = %s
            WHERE service_id = %s
            AND provider_id = %s
            """,
            (
                service_name,
                category,
                price,
                description,
                availability,
                service_id,
                provider_id
            )
        )


        # Save changes
        connection.commit()


        # Close database resources
        cursor.close()
        connection.close()


        # Return to My Services
        return redirect(url_for("my_services"))


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW EDIT PAGE
    # --------------------------------------------------------

    return render_template(
        "edit_service.html",
        service=service
    )

# ============================================================
# DELETE SERVICE
# ============================================================

@app.route("/delete-service/<int:service_id>", methods=["POST"])
def delete_service(service_id):

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    # Make sure a user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    # Only providers can delete services
    if session.get("user_role") != "provider":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET PROVIDER ID
    # --------------------------------------------------------

    user_id = session["user_id"]

    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (user_id,)
    )

    provider = cursor.fetchone()


    # --------------------------------------------------------
    # CHECK PROVIDER
    # --------------------------------------------------------

    if provider is None:

        cursor.close()
        connection.close()

        return "Provider profile not found."


    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # DELETE SERVICE
    # --------------------------------------------------------

    # Delete ONLY if the service belongs to the logged-in
    # provider.
    cursor.execute(
        """
        DELETE FROM services
        WHERE service_id = %s
        AND provider_id = %s
        """,
        (service_id, provider_id)
    )


    # Save the deletion
    connection.commit()


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # RETURN TO MY SERVICES
    # --------------------------------------------------------

    return redirect(url_for("my_services"))
# ============================================================
# PROVIDER EARNINGS
# ============================================================

@app.route("/provider-earnings")
def provider_earnings():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # CHECK PROVIDER ROLE
    # --------------------------------------------------------

    if session.get("user_role") != "provider":
        return redirect(url_for("dashboard"))


    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    # --------------------------------------------------------
    # GET PROVIDER ID
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT provider_id
        FROM service_providers
        WHERE user_id = %s
        """,
        (session["user_id"],)
    )

    provider = cursor.fetchone()


    if provider is None:

        cursor.close()
        connection.close()

        return "Provider profile not found."


    provider_id = provider["provider_id"]


    # --------------------------------------------------------
    # GET COMPLETED BOOKINGS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            b.booking_id,
            b.booking_date,

            s.service_name,
            s.price,

            u.name AS customer_name

        FROM bookings b

        JOIN services s
            ON b.service_id = s.service_id

        JOIN users u
            ON b.customer_id = u.user_id

        WHERE s.provider_id = %s
        AND b.status = 'completed'

        ORDER BY b.booking_id DESC
        """,
        (provider_id,)
    )

    bookings = cursor.fetchall()


    # --------------------------------------------------------
    # CALCULATE EARNINGS
    # --------------------------------------------------------

    total_earnings = sum(
        float(booking["price"] or 0)
        for booking in bookings
    )

    completed_count = len(bookings)


    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()


    # --------------------------------------------------------
    # SHOW EARNINGS PAGE
    # --------------------------------------------------------

    return render_template(
        "provider_earnings.html",
        bookings=bookings,
        total_earnings=total_earnings,
        completed_count=completed_count
    )

# ============================================================
# START FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    # Start the Flask server
    app.run(debug=True)


