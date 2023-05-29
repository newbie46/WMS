import tkinter.messagebox as messagebox


def validate_input(product_name, product_description, product_category, product_price, product_quantity,
                   product_supplier, product_weight):
    if not product_name:
        messagebox.showerror("Validation Error", "Product name is required.")
        return False

    if len(product_name) > 100:
        messagebox.showerror("Data Error", "Product Name is too long (maximum length: 100 characters)")
        return False

    if not product_description:
        messagebox.showerror("Validation Error", "Product description is required.")
        return False

    if not product_category:
        messagebox.showerror("Validation Error", "Product category is required.")
        return False

    if not product_price:
        messagebox.showerror("Validation Error", "Product price is required.")
        return False

    if not product_quantity:
        messagebox.showerror("Validation Error", "Product quantity is required.")
        return False

    if not product_supplier:
        messagebox.showerror("Validation Error", "Product supplier is required.")
        return False

    if len(product_supplier) > 200:
        messagebox.showerror("Data Error", "Product Supplier is too long (maximum length: 200 characters)")
        return False

    if not product_weight:
        messagebox.showerror("Validation Error", "Product weight is required.")
        return False

    try:
        float(product_price)
    except ValueError:
        messagebox.showerror("Validation Error", "Invalid numeric value in product price.")
        return False

    try:
        int(product_quantity)
    except ValueError:
        messagebox.showerror("Validation Error", "Invalid numeric value in product quantity.")
        return False

    try:
        float(product_weight)
    except ValueError:
        messagebox.showerror("Validation Error", "Invalid numeric value in product weight.")
        return False

    return True
