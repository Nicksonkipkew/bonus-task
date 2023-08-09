To use the advanced features of this CRUD application, you would need to follow these steps:

Install Flask and other required dependencies if not already installed.
Save the code to a Python file, for example, app.py.
Ensure that you have SQLite installed or adjust the database configuration accordingly.
Run the Flask application by executing python app.py in the terminal.
Once the application is running, you can access it through a web browser at http://localhost:8080/ or the specified host and port.

To better understand the advanced features of this CRUD application, you can review the following routes and their functions:

/: Renders the index page, displaying the items associated with the logged-in user.
/delete/<int:item_id>: Handles the deletion of an item with the specified item_id.
/register: Handles user registration.
/login: Handles user login authentication.
/logout: Logs out the user by removing their session.
/search: Performs a search query based on user input.
/sort: Sorts the items based on the selected attribute.
/create: Creates a new item with the provided information and file upload.
/edit/<int:item_id>: Allows editing of an existing item.
By following the provided code and understanding the purpose of each route, you can leverage and customize the application's advanced features to suit your specific needs.

Remember to modify the secret key in the code to a more secure value before deploying the application to a production environment. Additionally, ensure proper security measures are implemented when handling user authentication and file uploads.