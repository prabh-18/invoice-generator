# Invoice Generator

A desktop application that generates professional PDF invoices and emails them directly to clients.

## Features
- GUI built with Tkinter for easy data entry
- Generates formatted PDF invoices using ReportLab
- Auto-increments invoice numbers
- Sends invoices via email directly from the app
- Configurable business details via config.json

## Tech Stack
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=flat)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red?style=flat)

## Installation
```bash
git clone https://github.com/prabh-18/invoice-generator.git
cd invoice-generator
pip install -r requirements.txt
python invoice_gui.py
```

## Usage
1. Fill in client name, items, and amounts
2. Click Generate Invoice
3. PDF is created and emailed automatically

## Project Structure
```
invoice-generator/
├── invoice_gui.py      # Main GUI application
├── pdf_generator.py    # PDF creation logic
├── helpers.py          # Utility functions
├── email_sender.py     # Email sending logic
├── config.json         # Business configuration
└── invoice_number.txt  # Auto-incrementing invoice counter
```
