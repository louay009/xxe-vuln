from flask import Flask, render_template
from models import db
from config import Config
from flask import Response, request
import xml.etree.ElementTree as ET
from models import Product
from flask_migrate import Migrate
app = Flask(__name__)
from lxml import etree
# Load configuration settings from Config class
app.config.from_object(Config)
migrate = Migrate(app, db)
# Initialize the database with the Flask app
db.init_app(app)

@app.route('/products.xml')
def products_xml():
    # Create the root element
    root = ET.Element('store')

    # Query the products from the database
    products = Product.query.all()
    
    # Loop through products and add them to the XML
    for product in products:
        product_element = ET.SubElement(root, 'product')
        
        name = ET.SubElement(product_element, 'name')
        name.text = product.name
        
        price = ET.SubElement(product_element, 'price')
        price.text = str(product.price)
        
        description = ET.SubElement(product_element, 'description')
        description.text = product.description
        
        stock = ET.SubElement(product_element, 'stock')
        stock.text = str(product.stock)
        
    # Convert the XML tree to a string
    xml_data = ET.tostring(root, encoding='utf-8', method='xml')

    # Return the XML as a response
    return Response(xml_data, mimetype='application/xml')


@app.route('/')
def home():
    # Dynamically generate the XML
    tree = ET.ElementTree(ET.fromstring(products_xml().data))  # Fetch the XML dynamically
    root = tree.getroot()

    # Extract products from the XML
    products = []
    products = Product.query.all()
    return render_template('home.html', products=products)

#product_info route
@app.route('/product_info', methods=['GET'])
def product_info():
    product_id = request.args.get('id')  # Get the product ID from the query string

    if product_id:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            return render_template('product_info.html', product=product)
        else:
            return "Product not found", 404
    else:
        return "No product ID provided", 400
     



@app.route('/check_stock', methods=['POST'])
def check_stock():
    # Get the XML request data
    xml_data = request.data  # Get the raw XML data
    print(xml_data)
    try:
        root = etree.fromstring(xml_data.encode('utf-8'))

        # Extract the product ID from the XML
        product_id = root.find('product_id').text
        print(product_id)
        # Here you can process the XXE entity
        xxe_content = root.text if root.tag == 'xxe' else 'No XXE detected'
        product = Product.query.filter_by(id=product_id).first()
        product_stock = Product.query.filter_by(id=product_id).first()
        print(product)
        # Simulate stock checking (or query the database)
        stock_info = f"Stock for Product ID {product_id}:  {product.stock} units left. XXE Content: {xxe_content}"
        return stock_info, 200

    except etree.XMLSyntaxError as e:
        print("Parse Error:", e)  # Log thue error for debugging
        return "Error parsing XML", 400
       


if __name__ == '__main__':
    app.run(debug=True)