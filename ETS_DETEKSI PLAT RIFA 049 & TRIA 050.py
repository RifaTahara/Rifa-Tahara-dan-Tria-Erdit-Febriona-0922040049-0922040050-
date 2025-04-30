import cv2 as cv 
import imutils as im 
import pytesseract
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# library :
# cv Untuk pengolahan citra
# imultils : Mempermudah resize dan manipulasi gambar.
# pytesseract: Untuk mengenali teks dari gambar (OCR).
# tkinter: Library GUI bawaan Python.
# filedialog & messagebox: Untuk memilih file dan menampilkan popup pesan.
# PIL (Pillow): Untuk manipulasi gambar dan konversi ke format Tkinter.


# Path ke Tesseract (ubah jika berbeda)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Fungsi Deteksi Plat
def deteksi_plat(path):
    try:
        status_label.config(text=" Memproses gambar", fg="blue")
        root.update_idletasks()

        image = cv.imread(path)
        image = im.resize(image, width=500)

        # Membaca dan mengubah ukuran gambar agar lebih mudah diproses
        # Lalu konversi ke grayscale, lalu blur (filter bilateral) untuk mengurangi noise
        # Canny Edge Detection untuk mendeteksi tepi gambar (plat)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        blur = cv.bilateralFilter(gray, 11, 17, 17)
        edges = cv.Canny(blur, 170, 200)

        (cnts, _) = cv.findContours(edges.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv.contourArea, reverse=True)[:30]

        NumberPlateCnt = None

        # Mencari kontur pada gambar 
        for c in cnts:
            peri = cv.arcLength(c, True)
            approx = cv.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                NumberPlateCnt = approx
                break
        # mencari kontur berbentuk persegi empat 
        if NumberPlateCnt is not None:
            mask = cv.drawContours(image.copy(), [NumberPlateCnt], -1, (0, 255, 0), 3)

            # Ekstrak area plat untuk OCR
            x, y, w, h = cv.boundingRect(NumberPlateCnt)
            plat_area = gray[y:y + h, x:x + w]

            # OCR
            hasil_ocr = pytesseract.image_to_string(plat_area, config='--psm 8 --oem 3')
            hasil_ocr = hasil_ocr.strip()

            # Tampilkan hasil
            hasil_label.config(text="Hasil OCR: " + hasil_ocr)
            status_label.config(text="✅ Plat nomor terdeteksi!", fg="green")

            # Simpan dan tampilkan gambar hasil
            cv.imwrite("hasil_deteksi.jpg", mask)
            tampilkan_gambar("hasil_deteksi.jpg")

        else:
            hasil_label.config(text="Hasil OCR: -")
            status_label.config(text="⚠️ Plat nomor tidak ditemukan.", fg="red")
            messagebox.showinfo("Hasil", "Plat nomor tidak ditemukan.")

    except Exception as e:
        hasil_label.config(text="Hasil OCR: -")
        status_label.config(text="❌ Terjadi kesalahan.", fg="red")
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")

# Fungsi tampilkan gambar di GUI
def tampilkan_gambar(path):
    img = Image.open(path)
    img = img.resize((250, 100))
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk

# Fungsi pilih file
def pilih_file():
    file_path = filedialog.askopenfilename(
        title="Pilih Gambar Plat Nomor",
        filetypes=[("Gambar", "*.jpg *.jpeg *.png *.bmp")]
    )
    if file_path:
        status_label.config(text="📂 Gambar dipilih: " + file_path.split("/")[-1], fg="black")
        root.update_idletasks()
        deteksi_plat(file_path)

# GUI
root = tk.Tk()
root.title("Licence Plate Recognition")
root.geometry("500x400")
root.configure(bg="white")

judul = tk.Label(root, text="Licence Plate Recognition", font=("Helvetica", 16, "bold"), fg="white", bg="#A020F0")
judul.pack(fill=tk.X)

upload_btn = tk.Button(root, text="Upload Image", command=pilih_file, bg="#b0f0e7", width=20)
upload_btn.pack(pady=10)

image_label = tk.Label(root, bg="white")
image_label.pack(pady=5)

hasil_label = tk.Label(root, text="Hasil OCR: -", font=("Helvetica", 12), bg="white", fg="black")
hasil_label.pack(pady=5)

status_label = tk.Label(root, text="", font=("Helvetica", 10), bg="white")
status_label.pack(pady=5)

root.mainloop()

# menggunakan 2 kombinasi, pengolahan citra dan OCR.
# pra pemrosesan citra menggunakan threst dan di konversi ke greyscale
# bilateral filter mengurangi noise dan canny deteksi tepi
# kontur untuk deteksi persegi panjang
# diekstrak dan di tesseract mengenali teks pada plat