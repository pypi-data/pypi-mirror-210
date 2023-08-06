from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

class FlaskSuper:
    """
    A web framework built on top of Flask.
    """

    def __init__(self):
        """
        Initializes the FlaskPlus web framework.
        """
        self.App = Flask(__name__, template_folder="html")
        self.App.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Replace with your database URI
        self.db = SQLAlchemy(self.App)
        self.middleware = []

    def route(self, url, methods=None):
        """
        Decorator for registering a route in the Flask application.

        Args:
            url (str): The URL path for the route.
            methods (list, optional): List of HTTP methods to be supported by the route. Defaults to ['GET'].

        Returns:
            function: The decorator function.

        Example:
            @app.route('/example', methods=['GET', 'POST'])
            def example_route():
                if request.method == 'POST':
                    data = request.form['data']
                    # Process the data
                return 'Example route'
        """
        methods = methods or ['GET']

        def decorator(func):
            self.App.route(url, methods=methods)(func)
            return func

        return decorator

    def render(self, name, **kwargs):
        """
        Renders an HTML template with the given name and context variables.

        Args:
            name (str): The name of the HTML template to render.
            **kwargs: Context variables to be passed to the template.

        Returns:
            str: The rendered HTML content.

        Example:
            # Passing a single variable
            return app.render('index.html', title='Home')

            # Passing multiple variables
            return app.render('index.html', title='Home', user=current_user)
        """
        return render_template(name, **kwargs)

    def use_middleware(self, middleware_func):
        """
        Adds a middleware function to the list of middleware functions to be executed before each request.

        Args:
            middleware_func (function): The middleware function to be added.

        Example:
            def logging_middleware():
                # Perform logging operations

            app.use_middleware(logging_middleware)
        """
        self.middleware.append(middleware_func)

    def run(self, debug=True):
        """
        Runs the Flask application.

        Args:
            debug (bool, optional): Enable or disable debug mode. Defaults to True.

        Example:
            app.run(debug=True)
        """
        for middleware in self.middleware:
            self.App.before_request(middleware)

        self.App.run(debug=debug)