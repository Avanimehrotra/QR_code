import qrcode

import subprocess



# Function to get user input for QR code customization

def get_user_input(prompt, default):

    user_input = input(prompt + f" (default is {default}): ")

    return user_input if user_input else default



# Get user input for QR code data

qr_data = input("Enter text or URL to encode in QR code: ")



# Get user input for QR code customization

fill_color = get_user_input("Enter fill color", "black")

back_color = get_user_input("Enter background color", "white")

error_correction = get_user_input("Enter error correction level (L, M, Q, or H)", "H")



# Get user input for border width and length

border_width = int(get_user_input("Enter border width", "4"))

box_size = int(get_user_input("Enter box size", "10"))



# Create a QRCode object with user-specified border width and box size

qr = qrcode.QRCode(version=1,

                   error_correction=qrcode.constants.ERROR_CORRECT_L,

                   box_size=box_size,

                   border=border_width)



# Add data to the QRCode

qr.add_data(qr_data)



# Make the QRCode

qr.make(fit=True)



# Create an image of the QRCode with user-specified colors

img = qr.make_image(fill_color=fill_color, back_color=back_color)



# Save the image to a file

file_name = "custom_qr_code.png"

img.save(file_name)



# Open the image using the default image viewer

subprocess.run(["open", file_name], check=True)