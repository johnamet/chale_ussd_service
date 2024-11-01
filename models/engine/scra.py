from datetime import datetime
import os
import io
import asyncio
import tempfile
from fpdf import FPDF, HTMLMixin
import pikepdf
from models.engine.qr_code_engine import QrCodeEngine
from PIL import Image
from aiofiles import open as aio_open


class Receipt(FPDF, HTMLMixin):
    """Class to generate and encrypt PDF receipts asynchronously for event tickets."""

    def __init__(self, data, paper_size='A4'):
        # Set page dimensions and element sizes based on paper size
        if paper_size == 'POS':
            page_width = 58  # POS receipt width in mm
            page_height = 100  # POS height (adjust as needed)
            self.qr_size = 30  # Smaller QR code size for POS
            self.font_size_main = 8
            self.margin_x = 5
            self.margin_y = 5
        else:
            page_width = 210  # Standard A4 width
            page_height = 297  # Standard A4 height
            self.qr_size = 100  # Larger QR code size for A4
            self.font_size_main = 14
            self.margin_x = 10
            self.margin_y = 10

        # Initialize the FPDF with custom page dimensions
        super().__init__(format=(page_width, page_height))

        self.data = data
        self.paper_size = paper_size
        self.logo_stream = None

    def add_static_elements(self):
        """Adds static elements like borders, title, and logo to the receipt."""
        self.set_line_width(0.5 if self.paper_size == 'POS' else 1)
        self.set_draw_color(0, 128, 0)
        self.rect(self.margin_x, self.margin_y, self.w - 2 * self.margin_x, self.h - 2 * self.margin_y)

        # Set title and logo
        self.set_title()
        self.set_logo()

    def set_title(self, title='Benny Osbon Limited'):
        """Sets the receipt title."""
        self.set_font("Helvetica", "B", self.font_size_main)
        self.cell(0, 10, title, ln=True, align="C")

    def load_logo(self, logo_path='./assets/web-logo.png'):
        """Load, resize, and cache the logo image."""
        if not self.logo_stream:
            with Image.open(logo_path) as img:
                resized_logo = img.resize((50, 50),
                                          Image.Resampling.LANCZOS) if self.paper_size == 'POS' else img.resize(
                    (150, 150))
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                resized_logo.save(temp_file, format="PNG")
                temp_file.close()
            self.logo_stream = temp_file.name
        return self.logo_stream

    def set_logo(self):
        """Place the logo in the PDF using the cached image stream."""
        logo = self.load_logo()
        x_position = (self.w - 50) / 2
        self.image(logo, x=x_position, y=self.margin_y, w=30 if self.paper_size == 'POS' else 50)

    def insert_qr_image(self):
        """Generates and inserts a QR code based on user data."""
        qr_engine = QrCodeEngine(self.data['reference'])
        qr_path = qr_engine.generate_code()
        x_position = (self.w - self.qr_size) / 2
        self.image(qr_path, x=x_position, y=35, w=self.qr_size, h=self.qr_size)

    def set_text(self, text, spacing, bold=True):
        """Adds text to the receipt, adjusting font size and positioning based on paper size."""
        self.set_font("Helvetica", "B" if bold else "", self.font_size_main)
        self.set_xy(self.margin_x, spacing)
        self.cell(0, 10, text, ln=True, align="C")

    def add_map_link(self):
        """Adds a clickable Google Maps link for the event location."""
        self.set_xy(self.margin_x, self.h - 20)
        self.set_font("Helvetica", "B", self.font_size_main - 2)
        self.set_text_color(0, 0, 255)
        self.cell(0, 10, "Event Location", align="C", link=self.data['event_coordinates'])

    async def generate_receipt(self):
        """Generates the receipt content dynamically based on paper size."""
        self.add_static_elements()

        # Add QR code and user details
        self.insert_qr_image()
        self.set_text(self.data['name'].upper(), spacing=70)
        self.set_text(f"Reference Number: {self.data['reference']}", spacing=90)
        self.set_text(f"Ticket ID: {self.data['ticket_id']}", spacing=110)
        self.set_text(f"Ticket Type: {self.data['ticket_type']}", spacing=130)

        start_time = self.data['start_date']
        end_time = self.data['end_date']
        self.set_text(f'{start_time} - {end_time}', spacing=150)
        self.add_map_link()

        pdf_bytes = self.output(dest="S").encode("latin1")
        return io.BytesIO(pdf_bytes)

    async def create_receipt(self):
        """Creates and encrypts the receipt, returning a URL and access password."""
        raw_pdf = await self.generate_receipt()
        temp_file_path = "/tmp/temp_receipt.pdf"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(raw_pdf.getbuffer())

        output = io.BytesIO()
        with pikepdf.open(temp_file_path) as pdf:
            pdf.save(output, encryption=pikepdf.Encryption(user=self.data['password']))

        os.remove(temp_file_path)
        output.seek(0)
        return output

    async def create_pos_receipt(self):
        """Generates a POS receipt without encryption."""
        pos_pdf = await self.generate_receipt()  # Reuse generate method for POS sizing
        return pos_pdf
