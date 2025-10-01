
# this file runs the command int

import shopping_db

def menu():
    while True:
        print("\nShopping List Menu")
        print("1. Add Item")
        print("2. View Items")
        print("3. Delete Item")
        print("4. Quit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter item name: ")
            qty = input("Enter quantity: ")
            shopping_db.add_item(name, qty)
            print("Item added!")
        elif choice == "2":
            items = shopping_db.view_items()
            for row in items:
                print(row)
        elif choice == "3":
            item_id = input("Enter item id to delete: ")
            shopping_db.delete_item(item_id)
            print("Item deleted!")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

menu()
