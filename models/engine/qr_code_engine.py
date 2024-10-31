#!/usr/bin/env python3
"""
QrCodeEngine - Generates QR codes with embedded logos for event tickets.

This class creates a QR code based on unique user data and overlays a logo in the center.
"""

import io
import os
import qrcode
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
import tempfile

load_dotenv()

class QrCodeEngine:
    """Class for generating QR codes with embedded logos."""

    def __init__(self, reference):
        """
        Initializes the QrCodeEngine with the user's ID.
        
        Parameters:
            user_id (str): Unique identifier for the user.
        """
        self.reference = reference


    def generate_code(self):
        """
        Generates a QR code containing a unique code based on the user's ID and a timestamp.
        
        Returns:
            str: Path to the temporary file containing the QR code image.
        """
        logo_path = './assets/chale.png'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(self.reference)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white').convert('RGBA')

        with Image.open(logo_path) as logo:
            logo_size = (qr_img.size[0] // 4, qr_img.size[1] // 4)
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            logo_position = (
                (qr_img.size[0] - logo.size[0]) // 2,
                (qr_img.size[1] - logo.size[1]) // 2
            )
            qr_img.paste(logo, logo_position, logo)

        # Create a temporary file to store the QR code
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        qr_img.save(temp_file, format='PNG')
        temp_file.close()

        return temp_file.name  # Return the file path for use in FPDF
