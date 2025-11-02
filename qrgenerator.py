import tkinter as tk
from tkinter import messagebox, filedialog
from urllib.parse import quote_plus
from urllib.request import urlopen, Request
from io import BytesIO
from base64 import b64encode
import os

def fetch_qr_image(data: str, size: int = 300):
    base = "https://api.qrserver.com/v1/create-qr-code/"
    params = f"?size={size}x{size}&data={quote_plus(data)}"
    url = base + params
    req = Request(url, headers={"User-Agent": "Python QR Generator"})
    with urlopen(req) as response:
        return response.read() 

def decode_qr_image(file_path: str):
    """
    Sends image to qrserver.com decode API and returns the decoded text.
    """
    url = "https://api.qrserver.com/v1/read-qr-code/"
    with open(file_path, "rb") as f:
        data = f.read()
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()

    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("User-Agent", "Python QR Decoder")

    with urlopen(req) as resp:
        result = resp.read().decode("utf-8", errors="ignore")

    if '"data":"' in result:
        start = result.find('"data":"') + 8
        end = result.find('"', start)
        return result[start:end].replace("\\n", "\n").replace("\\/", "/")
    return None

def generate_qr():
    text = entry_text.get().strip()
    if not text:
        messagebox.showwarning("Warning", "Please enter some text or a URL.")
        return
    try:
        size = int(entry_size.get())
        if size < 100 or size > 1000:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Warning", "Size must be between 100 and 1000.")
        return

    try:
        img_data = fetch_qr_image(text, size)
        b64_data = b64encode(img_data)
        photo = tk.PhotoImage(data=b64_data)
        qr_label.config(image=photo, text="")
        qr_label.image = photo
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate QR:\n{e}")


def save_qr():
    text = entry_text.get().strip()
    if not text:
        messagebox.showwarning("Warning", "Generate a QR first.")
        return
    try:
        size = int(entry_size.get())
    except ValueError:
        size = 300

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )
    if not file_path:
        return

    try:
        img_data = fetch_qr_image(text, size)
        with open(file_path, "wb") as f:
            f.write(img_data)
        messagebox.showinfo("Saved", f"QR code saved to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save QR:\n{e}")


def decode_qr():
    file_path = filedialog.askopenfilename(
        title="Select a QR image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All files", "*.*")]
    )
    if not file_path:
        return
    try:
        result = decode_qr_image(file_path)
        if result:
            messagebox.showinfo("Decoded QR", f"Decoded text:\n\n{result}")
            entry_text.delete(0, tk.END)
            entry_text.insert(0, result)
        else:
            messagebox.showwarning("Warning", "No QR code detected in that image.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decode:\n{e}")

root = tk.Tk()
root.title("QR Code Generator & Decoder")
root.geometry("420x560")
root.resizable(False, False)

tk.Label(root, text="Enter text or URL:", font=("Arial", 12)).pack(pady=10)
entry_text = tk.Entry(root, width=45)
entry_text.pack(pady=5)

tk.Label(root, text="Size (100–1000 px):", font=("Arial", 12)).pack(pady=5)
entry_size = tk.Entry(root, width=10)
entry_size.insert(0, "300")
entry_size.pack(pady=5)

tk.Button(root, text="Generate QR", command=generate_qr, bg="#4CAF50", fg="white", width=20).pack(pady=10)
tk.Button(root, text="Save QR", command=save_qr, bg="#2196F3", fg="white", width=20).pack(pady=5)
tk.Button(root, text="Decode QR from File", command=decode_qr, bg="#FF9800", fg="white", width=20).pack(pady=10)

qr_label = tk.Label(root, text="Your QR will appear here", width=300, height=300)
qr_label.pack(pady=20)

tk.Label(root, text="(No external libraries — uses free web APIs)", font=("Arial", 9), fg="gray").pack(side="bottom", pady=5)

root.mainloop()