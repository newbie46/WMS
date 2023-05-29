from tkinter import *
from database_connection import connect_to_database, close_connection
import tkinter.messagebox as messagebox
from tkinter import ttk
from validation import validate_input


root = Tk()
root.resizable(width=False, height=False)
root.title("Inventory management system")

# Connect to MySQL, delete line 15 when you create database and then return it back when database is created
conn, c = connect_to_database()  # Call the connect_to_database function to establish the connection

# Create a database
c.execute("CREATE DATABASE IF NOT EXISTS wms")

# Create a table
c.execute("CREATE TABLE IF NOT EXISTS warehouse (product_name VARCHAR(255), \
        product_description TEXT, \
        product_category VARCHAR(255), \
        product_unit_price DECIMAL(20, 2), \
        product_quantity INT, \
        product_supplier VARCHAR(255), \
        product_weight DECIMAL(20, 2), \
        product_id INT AUTO_INCREMENT PRIMARY KEY)")


# Create the top frame
top_frame = Frame(root)
top_frame.pack(fill=X)

# Create label in the top frame
program_name_label = Label(top_frame, text="Inventory Management System", font=("Arial", 20))
program_name_label.pack(side=LEFT, padx=10, pady=10)

# Create the content frame
content_frame = Frame(root)
content_frame.pack(side=LEFT, padx=10, pady=10)

# Create the buttons frame
buttons_frame = Frame(root)
buttons_frame.pack(side=LEFT, padx=10, pady=10)


def apply_style():
    # Create a style object
    style_main = ttk.Style()

    # Configure the style for the buttons
    style_main.configure("TButton",
                         foreground='#1D267D',
                         background='#4CAF50',
                         font=('Arial', 12, 'bold'),
                         borderwidth=2)


# Clear text fields
def clear_fields():
    product_name_box.delete(0, END)
    product_description_box.delete("1.0", END)
    product_category_combobox.set("")
    product_price_box.delete(0, END)
    product_quantity_box.delete(0, END)
    product_supplier_box.delete(0, END)
    product_weight_box.delete(0, END)


# Add product to database
def add_product():
    product_name = product_name_box.get()
    product_description = product_description_box.get("1.0", "end-1c")
    product_category = product_category_combobox.get()
    product_price = product_price_box.get()
    product_quantity = product_quantity_box.get()
    product_supplier = product_supplier_box.get()
    product_weight = product_weight_box.get()

    # Validate the input values
    if not validate_input(product_name, product_description, product_category, product_price, product_quantity,
                          product_supplier, product_weight):
        return

    # Add data about product to database
    sql_command = "INSERT INTO warehouse (product_name, product_description, product_category, product_unit_price," \
                  " product_quantity, product_supplier, product_weight) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (product_name_box.get(), product_description_box.get("1.0", "end-1c"), product_category_combobox.get(),
              product_price_box.get(), product_quantity_box.get(), product_supplier_box.get(),
              product_weight_box.get())

    c.execute(sql_command, values)
    conn.commit()

    # Clear fields
    clear_fields()

    # Show success message
    messagebox.showinfo("Info", "Product added successfully")


# Show all products
def show_products():
    root.withdraw()

    show = Toplevel()
    show.title("All products")

    # Get the screen width and height
    screen_width = show.winfo_screenwidth()
    screen_height = show.winfo_screenheight()

    # Set the window size to fit the screen
    show.geometry(f"{screen_width}x{screen_height}")

    apply_style()

    # Create the top frame
    top_frame1 = Frame(show)
    top_frame1.pack(fill=X)

    # Create Treeview widget with column headers
    tree = ttk.Treeview(show)
    tree["columns"] = ("name", "description", "category", "unit_price", "quantity", "supplier", "weight", "id")
    tree.heading("name", text="Product Name")
    tree.heading("description", text="Description")
    tree.heading("category", text="Category")
    tree.heading("unit_price", text="Unit Price")
    tree.heading("quantity", text="Quantity")
    tree.heading("supplier", text="Supplier")
    tree.heading("weight", text="Weight")
    tree.heading("id", text="Product Id")

    # Configure column widths and anchor
    tree.column("name", width=200, minwidth=200, anchor="center")
    tree.column("description", width=400, minwidth=400, anchor="center")
    tree.column("category", width=200, minwidth=200, anchor="center")
    tree.column("unit_price", width=60, minwidth=60, anchor="center")
    tree.column("quantity", width=60, minwidth=60, anchor="center")
    tree.column("supplier", width=100, minwidth=100, anchor="center")
    tree.column("weight", width=60, minwidth=60, anchor="center")
    tree.column("id", width=40, minwidth=40, anchor="center")

    # Remove the first blank column
    tree["show"] = "headings"

    # Create scrollbars
    scrollbar_y = ttk.Scrollbar(show, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x = ttk.Scrollbar(show, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Show data
    c.execute("SELECT * FROM warehouse")
    products_data = c.fetchall()

    for product in products_data:
        tree.insert("", "end", values=product)

    tree.pack(side="left", expand=True, fill="both")

    # Delete product from database
    def delete_product():
        # Retrieve the selected item from the Treeview
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected.")
            show.focus()
            return

        # Confirm the deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this product?")

        if confirm:
            # Retrieve the product ID of the selected item
            product_id = tree.item(selected_item)["values"][-1]

            # Delete the product from the database
            c.execute("DELETE FROM warehouse WHERE product_id = %s", (product_id,))
            conn.commit()

            # Remove the item from the Treeview
            tree.delete(selected_item)

            messagebox.showinfo("Info", "Product deleted successfully.")

            show.focus()

    # Edit information about product
    def edit_product():
        # Retrieve the selected item from the Treeview
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected.")
            show.focus()
            return

        # Open a new window for editing
        edit_window = Toplevel()
        edit_window.title("Edit Product")
        edit_window.geometry("400x300")

        # Retrieve the data of the selected item
        item_data = tree.item(selected_item)["values"]

        # Create fields for editing
        product_name_label_edit = Label(edit_window, text="Product name", font=("Arial", 16))
        product_name_label_edit.grid(row=0, column=0, sticky=W, padx=10)

        product_description_label_edit = Label(edit_window, text="Description", font=("Arial", 16))
        product_description_label_edit.grid(row=1, column=0, sticky=W, padx=10)

        product_category_label_edit = Label(edit_window, text="Category", font=("Arial", 16))
        product_category_label_edit.grid(row=2, column=0, sticky=W, padx=10)

        product_price_label_edit = Label(edit_window, text="Price", font=("Arial", 16))
        product_price_label_edit.grid(row=3, column=0, sticky=W, padx=10)

        product_quantity_label_edit = Label(edit_window, text="Quantity", font=("Arial", 16))
        product_quantity_label_edit.grid(row=4, column=0, sticky=W, padx=10)

        product_supplier_label_edit = Label(edit_window, text="Supplier", font=("Arial", 16))
        product_supplier_label_edit.grid(row=5, column=0, sticky=W, padx=10)

        product_weight_label_edit = Label(edit_window, text="Weight", font=("Arial", 16))
        product_weight_label_edit.grid(row=6, column=0, sticky=W, padx=10)

        product_name_box_edit = Entry(edit_window, width=30)
        product_name_box_edit.grid(row=0, column=1, pady=5)

        product_description_box_edit = Text(edit_window, height=4, width=22)
        product_description_box_edit.grid(row=1, column=1, pady=5)

        product_price_box_edit = Entry(edit_window, width=30)
        product_price_box_edit.grid(row=3, column=1, pady=5)

        product_quantity_box_edit = Entry(edit_window, width=30)
        product_quantity_box_edit.grid(row=4, column=1, pady=5)

        product_supplier_box_edit = Entry(edit_window, width=30)
        product_supplier_box_edit.grid(row=5, column=1, pady=5)

        product_weight_box_edit = Entry(edit_window, width=30)
        product_weight_box_edit.grid(row=6, column=1, pady=5)

        # Create list for combobox
        product_categories1 = [
            "Fruits",
            "Vegetables",
            "Meat and Poultry",
            "Dairy and Eggs",
            "Bakery and Bread",
            "Canned and Jarred Goods",
            "Grains, Rice, and Pasta",
            "Frozen Foods",
            "Beverages",
            "Snacks and Sweets",
            "Condiments and Sauces",
            "Spices and Seasonings",
            "Cooking Oils and Vinegars",
            "Breakfast Foods",
            "Baby and Toddler Food",
            "Health and Wellness Products",
            "Cleaning Supplies",
            "Personal Care Products",
            "Pet Food and Supplies",
            "Miscellaneous"
        ]
        # Create combobox for categories
        product_category_combobox_edit = ttk.Combobox(edit_window, width=27, values=product_categories)
        product_category_combobox_edit.current(19)
        product_category_combobox_edit.grid(row=2, column=1)

        show.focus()

        # Update the item in the database
        def update_product():
            new_product_name = product_name_box_edit.get()
            new_product_description = product_description_box_edit.get("1.0", "end-1c")
            new_product_category = product_category_combobox_edit.get()
            new_product_price = product_price_box_edit.get()
            new_product_quantity = product_quantity_box_edit.get()
            new_product_supplier = product_supplier_box_edit.get()
            new_product_weight = product_weight_box_edit.get()

            # Validate the input values
            if not validate_input(new_product_name, new_product_description, new_product_category, new_product_price,
                                  new_product_quantity, new_product_supplier, new_product_weight):
                return

            # Update the database with the new values
            c.execute(
                "UPDATE warehouse SET product_name = %s, product_description = %s, product_category = %s, product_unit_price = %s, product_quantity = %s, product_supplier = %s, product_weight = %s WHERE product_id = %s",
                (new_product_name, new_product_description, new_product_category, new_product_price,
                 new_product_quantity, new_product_supplier, new_product_weight, item_data[7]))

            conn.commit()
            messagebox.showinfo("Info", "Product updated successfully")
            edit_window.destroy()
            show.focus()

        # Retrieve the data of the selected item
        item_data = tree.item(selected_item)["values"]

        # Set the values of the entry boxes and combobox based on item_data
        product_name_box_edit.insert(0, item_data[0])
        product_description_box_edit.insert("1.0", item_data[1])
        product_category_combobox_edit.set(item_data[2])
        product_price_box_edit.insert(0, item_data[3])
        product_quantity_box_edit.insert(0, item_data[4])
        product_supplier_box_edit.insert(0, item_data[5])
        product_weight_box_edit.insert(0, item_data[6])

        # Create the "Update" button
        update_button = ttk.Button(edit_window, text="Update", style="TButton", command=update_product)
        update_button.grid(row=7, column=1)

    def return_to_main_window():
        # Close the "Show products" window
        show.destroy()

        # Focus the main window
        root.deiconify()

    def refresh_data():
        # Clear existing treeview data
        tree.delete(*tree.get_children())

        # Retrieve updated data from the database
        c.execute("SELECT * FROM warehouse")
        products_data_refresh = c.fetchall()

        # Insert the updated data into the Treeview
        for x in products_data_refresh:
            tree.insert("", "end", values=x)

    # Close the program when show window is closed
    def close_show_window():
        close_window()

    show.protocol("WM_DELETE_WINDOW", close_show_window)

    # Create search fields
    search_name_label = Label(top_frame1, text="Product Name:", font=("Arial", 14))
    search_name_label.grid(row=0, column=0, padx=10)

    search_name_entry = Entry(top_frame1, width=30)
    search_name_entry.grid(row=0, column=1, padx=10)

    category_label = Label(top_frame1, text="Category:", font=("Arial", 14))
    category_label.grid(row=0, column=2, padx=10)

    category_values = [""] + product_categories  # Add blank space as the first option
    category_combobox = ttk.Combobox(top_frame1, width=27, values=category_values)
    category_combobox.current(0)  # Set the blank space as the default
    category_combobox.grid(row=0, column=3, padx=10)

    search_id_label = Label(top_frame1, text="Product ID:", font=("Arial", 14))
    search_id_label.grid(row=0, column=4, padx=10)

    search_id_entry = Entry(top_frame1, width=30)
    search_id_entry.grid(row=0, column=5, padx=34)

    # Create buttons
    search_button = ttk.Button(top_frame1, text="Search", style="TButton", width=18, command=lambda: perform_search(tree,
                                                                                     search_id_entry.get(),
                                                                                     category_combobox.get(),
                                                                                     search_name_entry.get()))
    search_button.grid(row=0, column=6)

    edit_button = ttk.Button(top_frame1, text="Edit", style="TButton", width=18, command=edit_product)
    edit_button.grid(row=0, column=7)

    delete_button = ttk.Button(top_frame1, text="Delete", style="TButton", width=18, command=delete_product)
    delete_button.grid(row=0, column=8)

    refresh_button = ttk.Button(top_frame1, text="Refresh", style="TButton", width=18, command=refresh_data)
    refresh_button.grid(row=0, column=9)

    return_button = ttk.Button(top_frame1, text="Return", style="TButton", width=18, command=return_to_main_window)
    return_button.grid(row=0, column=10)


def perform_search(tree, product_id, category, name):
    # Clear existing treeview data
    tree.delete(*tree.get_children())

    # Construct the SQL query based on the provided search parameters
    sql_query = "SELECT * FROM warehouse"

    conditions = []
    placeholders = []

    if product_id:
        conditions.append("product_id = %s")
        placeholders.append(product_id)

    if category:
        conditions.append("product_category = %s")
        placeholders.append(category)

    if name:
        conditions.append("product_name LIKE %s")
        placeholders.append('%' + name + '%')

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)

    # Execute the query with the placeholders and update the Treeview with the search results
    c.execute(sql_query, placeholders)
    search_results = c.fetchall()

    for product in search_results:
        tree.insert("", "end", values=product)


def close_window():
    close_connection(conn)
    root.destroy()


apply_style()
# Create fields
product_name_label = Label(content_frame, text="Product name", font=("Arial", 16))
product_name_label.grid(row=0, column=0, sticky=W, padx=10)
product_name_box = Entry(content_frame, width=30)
product_name_box.grid(row=0, column=1, pady=5)

product_description_label = Label(content_frame, text="Description", font=("Arial", 16))
product_description_label.grid(row=1, column=0, sticky=W, padx=10)
product_description_box = Text(content_frame, height=4, width=22)
product_description_box.grid(row=1, column=1, pady=5)

product_category_label = Label(content_frame, text="Category", font=("Arial", 16))
product_category_label.grid(row=2, column=0, sticky=W, padx=10)
# Create list for combobox
product_categories = [
    "Fruits",
    "Vegetables",
    "Meat and Poultry",
    "Dairy and Eggs",
    "Bakery and Bread",
    "Canned and Jarred Goods",
    "Grains, Rice, and Pasta",
    "Frozen Foods",
    "Beverages",
    "Snacks and Sweets",
    "Condiments and Sauces",
    "Spices and Seasonings",
    "Cooking Oils and Vinegars",
    "Breakfast Foods",
    "Baby and Toddler Food",
    "Health and Wellness Products",
    "Cleaning Supplies",
    "Personal Care Products",
    "Pet Food and Supplies",
    "Miscellaneous"
]
# Create combobox for categories
product_category_combobox = ttk.Combobox(content_frame, width=27, values=product_categories)
product_category_combobox.current(19)
product_category_combobox.grid(row=2, column=1)

product_price_label = Label(content_frame, text="Price", font=("Arial", 16))
product_price_label.grid(row=3, column=0, sticky=W, padx=10)
product_price_box = Entry(content_frame, width=30)
product_price_box.grid(row=3, column=1, pady=5)

product_quantity_label = Label(content_frame, text="Quantity", font=("Arial", 16))
product_quantity_label.grid(row=4, column=0, sticky=W, padx=10)
product_quantity_box = Entry(content_frame, width=30)
product_quantity_box.grid(row=4, column=1, pady=5)

product_supplier_label = Label(content_frame, text="Supplier", font=("Arial", 16))
product_supplier_label.grid(row=5, column=0, sticky=W, padx=10)
product_supplier_box = Entry(content_frame, width=30)
product_supplier_box.grid(row=5, column=1, pady=5)

product_weight_label = Label(content_frame, text="Weight", font=("Arial", 16))
product_weight_label.grid(row=6, column=0, sticky=W, padx=10)
product_weight_box = Entry(content_frame, width=30)
product_weight_box.grid(row=6, column=1, pady=5)

# Create buttons
show_products_button = ttk.Button(buttons_frame, text="SHOW PRODUCTS", style="TButton", command=show_products)
show_products_button.grid(row=1, column=0, padx=10, pady=10, sticky=W+E)

add_product_button = ttk.Button(buttons_frame, text="ADD PRODUCT", style="TButton", command=add_product)
add_product_button.grid(row=3, column=0, padx=10, pady=10, sticky=W+E)

clear_fields_button = ttk.Button(buttons_frame, text="CLEAR", style="TButton", command=clear_fields)
clear_fields_button.grid(row=5, column=0, padx=10, pady=10, sticky=W+E)

root.protocol("WM_DELETE_WINDOW", close_window)

root.mainloop()
