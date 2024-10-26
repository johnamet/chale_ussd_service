#!/usr/bin/env python3
"""
"""

import os
import qrcode
from PIL import Image
from datetime import datetime


class QrCodeEngine:

    def __init__(self, user_id):
        self.user_id = user_id

    def generate_code(self):
        # Define paths and variables
        logo_path = './assets/chale.png'  # Path to your logo image
        code = f"{self.user_id}-{datetime.now().timestamp()}"
        file_name = f'qrcode_{code}.png'
        file_path = os.path.join(os.getenv('QR_CODE_DIR', './qrcodes'), file_name)

        # os.makedirs(os.getenv('QR_CODE_DIR', './qrcodes'))

        # Generate the QR code with overlay as before
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(code)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white').convert('RGBA')

        # Open and resize the logo
        logo = Image.open(logo_path)
        logo_size = (qr_img.size[0] // 4, qr_img.size[1] // 4)
        logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

        # Center and overlay the logo
        logo_position = (
            (qr_img.size[0] - logo.size[0]) // 2,
            (qr_img.size[1] - logo.size[1]) // 2
        )
        qr_img.paste(logo, logo_position, logo)
        qr_img.save(file_path, 'PNG')

        # Generate and return the URL to access the image
        server_address = os.getenv('SERVER_ADDRESS', 'http://localhost:7000/api/v1/chale/services')
        qr_code_url = f"{server_address}/qr_code/{file_name}"

        return qr_code_url, file_name
