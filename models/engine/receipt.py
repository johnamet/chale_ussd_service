import io
import os
import tempfile

import pikepdf
from PIL import Image
from dotenv import load_dotenv
from fpdf import FPDF, HTMLMixin
import jwt

from models.engine.qr_code_engine import QrCodeEngine

load_dotenv()


class QRcodePDF(FPDF):
    def __init__(self, data):
        # Set up page size and element sizes for thermal paper
        pos_width_mm = 58  # Typical width for POS receipts in mm
        pos_height_mm = 100  # Adjust as necessary for desired height
        self.qr_size = 30  # Smaller QR code for POS receipts
        self.font_size_main = 6  # Smaller font for POS
        self.margin_x = 5  # Reduced margins
        self.margin_y = 5

        # Initialize FPDF with custom POS paper dimensions
        super().__init__(format=(pos_width_mm, pos_height_mm))

        self.data = data

    def _insert_qr_image(self):
        """Generates and inserts a QR code based on user phone data."""
        token = jwt.encode(self.data, os.get_env('JWT_SECRET'), algorithm='HS256')

        qr_engine = QrCodeEngine(token)
        qr_path = qr_engine.generate_code()  # Get path to QR code image file
        image_width, image_height = 25, 25
        x_position = (210 - image_width) / 2
        self.image(qr_path, x=x_position, y=35, w=image_width, h=image_height)

    async def generate_receipt(self):
        """Generates the receipt PDF content asynchronously."""
        self.add_page()
        self._insert_qr_image()
        pdf_bytes = self.output(dest="S").encode("latin1")
        return io.BytesIO(pdf_bytes)
    
    async def create_receipt(self):
        """Generates the POS receipt and returns it as an in-memory PDF file."""
        return await self.generate_receipt()

        



class Receipt(FPDF, HTMLMixin):
    """Class to generate and encrypt PDF receipts asynchronously for event tickets."""

    def __init__(self, data, paper_size="A4"):
        super().__init__()
        self.data = data
        self.logo_stream = None
        self.paper_size = paper_size

    def _add_static_elements(self):
        """Adds static elements like borders, title, and logo to the receipt."""
        self._set_borders()
        self._set_title()
        self._set_logo()

    def _set_borders(self):
        """Draws border for the receipt."""
        self.set_line_width(1)
        self.set_draw_color(0, 128, 0)
        self.rect(10, 10, 190, 277)

    def _set_title(self, title='Benny Osbon Limited.'):
        """Sets the receipt title."""
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, title, ln=True, align="C")

    def _load_logo(self, logo_path='./assets/web-logo.png'):
        """Load, resize, and cache the logo image to reduce lag."""
        if not self.logo_stream:
            with Image.open(logo_path) as img:
                resized_logo = img.resize((150, 150), Image.Resampling.LANCZOS)
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                resized_logo.save(temp_file, format="PNG")
                temp_file.close()
            return temp_file.name

    def _set_logo(self):
        """Place the logo in the PDF using the cached image stream."""
        logo = self._load_logo()  # Ensure logo is loaded and cached
        x_position = (210 - 50) / 2
        self.image(logo, x=x_position, y=5, w=50, h=50)

    def _insert_qr_image(self):
        """Generates and inserts a QR code based on user phone data."""
        qr_engine = QrCodeEngine(self.data['reference'])
        qr_path = qr_engine.generate_code()  # Get path to QR code image file
        image_width, image_height = 100, 100
        x_position = (210 - image_width) / 2
        self.image(qr_path, x=x_position, y=35, w=image_width, h=image_height)

    def _set_text(self, text, font_size=14, spacing=100, bold=True, wrap_width=190):
        """Adds HTML-formatted text to the receipt, centering and wrapping lines as needed."""
        self.set_font("Helvetica", "B" if bold else "", font_size)

        # Set the x position to the starting point
        self.set_xy(10, spacing)

        # First, we will create a temporary buffer to store the multi-cell output
        buffer = io.StringIO()

        # Parse and add HTML content
        parser = HTMLTextParser(self, wrap_width)
        parser.feed(text)

        # Get the total height after wrapping
        total_height = parser.total_height  # Assuming your HTML parser can track this

        # Calculate the x position for center alignment
        self.set_xy(10, spacing)  # Reset to the original position
        center_x = (210 - wrap_width) / 2  # Centering based on wrap width
        self.set_x(center_x)

        # Render each line to ensure wrapping
        for line in buffer.getvalue().splitlines():
            self.multi_cell(wrap_width, 10, line, align="C")

        # Move the cursor down by total_height after rendering
        self.set_y(spacing + total_height)

    def _add_map_link(self):
        """Adds a clickable Google Maps link to the event location in the PDF."""
        self.set_xy(10, 265)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 0, 255)
        self.cell(0, 10, "Click here for Event Location", align="C", link=self.data['event_coordinates'])

    def _add_phone_link(self):
        # Add a clickable phone number
        phone_link = f"tel:{os.getenv('CUSTOMER_SERVICE_PHONE')}"  # Format phone number for dialing
        self.set_xy(10, 255)  # Position below the map link
        self.cell(0, 10, f"{os.getenv('CUSTOMER_SERVICE_ADDRESS')}", align="C", link=phone_link)

    async def generate_receipt(self):
        """Generates the receipt PDF content asynchronously."""
        self.add_page()
        self._add_static_elements()

        # Add dynamic elements
        self._insert_qr_image()
        self._set_text(self.data['name'].upper(), font_size=16, spacing=133)

        start_time = self.data['start_date']
        end_time = self.data['end_date']
        self._set_text(f'{start_time} - {end_time}', font_size=14, spacing=140)
        self._set_text(f"For event information, Contact",
                       spacing=250,
                       font_size=10, bold=False)
        self._add_phone_link()

        # Ticket and user details
        self._set_text(self.data['ticket_id'], font_size=12, spacing=125)
        self._set_text(self.data['ticket_type'], font_size=12, spacing=147)
        self._set_text("Description:", font_size=14, spacing=152)
        self._set_text(self.data['description'], font_size=8, spacing=160, bold=False)
        self._set_text(f"Ticket ID: {self.data['ticket_id']}", spacing=210)
        self._set_text(f"Ticket Holder: {self.data['name'].upper()}", spacing=220)
        self._set_text(f"Reference Number: {self.data['reference']}", spacing=230)
        self._set_text(f"Telephone Number: {self.data['phone']}", spacing=240)

        self._add_map_link()

        pdf_bytes = self.output(dest="S").encode("latin1")
        return io.BytesIO(pdf_bytes)

    async def create_receipt(self):
        """Creates and encrypts the receipt, returning a URL and access password."""
        raw_pdf = await self.generate_receipt()  # Generate the PDF as BytesIO

        # Write raw PDF to a temporary file to ensure compatibility with pikepdf
        temp_file_path = "/tmp/temp_receipt.pdf"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(raw_pdf.getbuffer())

        # Encrypt and save the PDF to an output BytesIO stream
        output = io.BytesIO()
        with pikepdf.open(temp_file_path) as pdf:
            pdf.save(output, encryption=pikepdf.Encryption(user=self.data['password']))

        # Remove the temporary file
        os.remove(temp_file_path)

        output.seek(0)  # Reset to the start of the stream for reading
        return output


class POSReceipt(FPDF, HTMLMixin):
    """Class to generate a POS-sized receipt optimized for thermal printers."""

    def __init__(self, data):
        # Set up page size and element sizes for thermal paper
        pos_width_mm = 58  # Typical width for POS receipts in mm
        pos_height_mm = 100  # Adjust as necessary for desired height
        self.qr_size = 30  # Smaller QR code for POS receipts
        self.font_size_main = 6  # Smaller font for POS
        self.margin_x = 5  # Reduced margins
        self.margin_y = 5

        # Initialize FPDF with custom POS paper dimensions
        super().__init__(format=(pos_width_mm, pos_height_mm))

        self.data = data
        self.logo_stream = None

    def add_static_elements(self):
        """Adds static elements like borders, title, and logo for the POS receipt."""
        self.set_line_width(0.5)
        self.set_draw_color(0, 128, 0)
        self.rect(self.margin_x, self.margin_y, self.w - 2 * self.margin_x, self.h - 2 * self.margin_y)

        # Add title and logo
        self.set_title()
        self.set_logo()

    def set_title(self, title='Benny Osbon Limited'):
        """Sets the receipt title with smaller text for POS size."""
        self.set_font("Helvetica", "B", self.font_size_main - 2)
        self.cell(0, 1, title, ln=True, align="C")

    def load_logo(self, logo_path='./assets/web-logo.png'):
        """Load, resize, and cache the logo image for POS dimensions."""
        if not self.logo_stream:
            with Image.open(logo_path) as img:
                resized_logo = img.resize((100, 100), Image.Resampling.LANCZOS)
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                resized_logo.save(temp_file, format="PNG")
                temp_file.close()
            self.logo_stream = temp_file.name
        return self.logo_stream

    def set_logo(self):
        """Place the logo in the PDF using the cached image stream."""
        logo = self.load_logo()
        x_position = (self.w - 30) / 2
        self.image(logo, x=x_position, y=2.5, w=30, h=30)

    def insert_qr_image(self):
        """Generates and inserts a QR code based on user data."""
        qr_engine = QrCodeEngine(self.data['reference'])
        qr_path = qr_engine.generate_code()
        x_position = (self.w - self.qr_size) / 2
        self.image(qr_path, x=x_position, y=20, w=self.qr_size, h=self.qr_size)

    def set_text(self, text, spacing, bold=True):
        """Adds text to the receipt with POS-sized adjustments."""
        self.set_font("Helvetica", "B" if bold else "", self.font_size_main)
        self.set_xy(self.margin_x + 5, spacing)
        self.cell(0, 10, text, ln=True, align="C")

    def _add_phone_link(self):
        # Add a clickable phone number
        phone_link = f"tel:{os.getenv('CUSTOMER_SERVICE_PHONE', '233 27 517 7177')}"  # Format phone number for dialing
        self.set_xy(self.margin_x + 5, 69.95)  # Position below the map link
        self.cell(0, 10, f"Call us on:  {os.getenv('CUSTOMER_SERVICE_PHONE')}", align="C", link=phone_link)

    async def generate_receipt(self):
        """Generates the receipt content based on POS dimensions."""
        self.add_page()
        self.add_static_elements()

        # Add QR code and user details
        self.insert_qr_image()
        self.set_text(self.data['event_name'].upper(), 44)
        self.set_text(self.data['name'].upper(), spacing=47)
        self.set_text(f"Reference Number: {self.data['reference']}", spacing=50)
        self.set_text(f"Ticket ID: {self.data['ticket_id']}", spacing=53)
        self.set_text(f"Ticket Type: {self.data['ticket_type']}", spacing=59)

        start_time = self.data['start_date']
        end_time = self.data['end_date']
        self.set_text(f'{start_time}'.upper(), spacing=62)
        self.set_text('TO', spacing=65)
        self.set_text(f'{end_time}'.upper(), spacing=68)

        self._add_phone_link()

        pdf_bytes = self.output(dest="S").encode("latin1")
        return io.BytesIO(pdf_bytes)

    async def create_receipt(self):
        """Generates the POS receipt and returns it as an in-memory PDF file."""
        return await self.generate_receipt()


from html.parser import HTMLParser


class HTMLTextParser(HTMLParser):
    """Simple HTML parser for basic tag handling in FPDF."""

    def __init__(self, pdf, wrap_width):
        super().__init__()
        self.pdf = pdf
        self.wrap_width = wrap_width
        self.font_style = ""
        self.total_height = 0

    def handle_starttag(self, tag, attrs):
        """Apply font styles based on HTML tags."""
        if tag == "b":
            self.font_style = "B"
            self.pdf.set_font("Helvetica", "B")
        elif tag == "i":
            self.font_style = "I"
            self.pdf.set_font("Helvetica", "I")
        elif tag == "u":
            self.font_style = "U"
            self.pdf.set_font("Helvetica", "U")
        elif tag == "br":
            self.pdf.ln(5)  # Line break for <br> tag

    def handle_endtag(self, tag):
        """Reset font style after closing a tag."""
        if tag in ["b", "i", "u"]:
            self.font_style = ""
            self.pdf.set_font("Helvetica", "")

    def handle_data(self, data):
        """Render text data with the current style and track the height."""
        line_height = 10  # Define the height of each line
        lines = data.splitlines()  # Split the data into lines
        for line in lines:
            # Calculate the number of lines based on the wrap width
            num_lines = len(line) // self.wrap_width + 1
            self.total_height += num_lines * line_height  # Update total height
            self.pdf.multi_cell(self.wrap_width, line_height, line, align="C")
